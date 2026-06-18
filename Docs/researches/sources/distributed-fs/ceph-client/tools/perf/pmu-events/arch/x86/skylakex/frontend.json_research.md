# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/skylakex/frontend.json

## Purpose

`frontend.json` is a Skylake Server PMU event manifest for front-end pipeline behavior. It defines 49 core PMU aliases covering branch resteers, length-changing-prefix decode stalls, DSB-to-MITE transitions, retired-instruction front-end miss attribution, instruction-cache/tag stalls, IDQ delivery source, microcode sequencer delivery, and front-end uop delivery starvation.

The file is consumed as data by `tools/perf/pmu-events/jevents.py`; it is not executable code. During the perf build, `jevents.py` walks model JSON files, assigns the topic from the filename (`frontend`), converts every JSON object into a `JsonEvent`, and emits generated C table entries in `pmu-events.c`. At runtime those entries become perf aliases visible through `perf list` and usable in `perf stat -e <event>`.

## Important Schema, APIs, and Event Families

The important contract is the perf PMU JSON schema:

- `EventName` is the exported perf alias, lower-cased by `JsonEvent`.
- `EventCode` and `UMask` become the low-level `event=` and `umask=` fields.
- `Counter`, `CounterMask`, `Invert`, and `EdgeDetect` constrain scheduling and event semantics.
- `SampleAfterValue` becomes the default sampling `period=`.
- `BriefDescription` and `PublicDescription` become short and long descriptions.
- `PEBS`, `MSRIndex`, and `MSRValue` mark precise events and special MSR encodings.

Key families are:

- `BACLEARS.ANY`, for branch-address-calculator/front-end resteers.
- `DECODE.LCP`, an alias of `ILD_STALL.LCP`, for length-changing-prefix stalls.
- `DSB2MITE_SWITCHES.*`, with `COUNT` and `PENALTY_CYCLES` on event `0xAB`.
- `FRONTEND_RETIRED.*`, 19 PEBS events on event `0xC6` using MSR `0x3F7` and `frontend=` values to classify DSB, iTLB, L1I, L2, STLB, latency, and bubble-slot exposure.
- `ICACHE_16B.*`, `ICACHE_64B.*`, and `ICACHE_TAG.STALLS`, for instruction fetch data/tag hits, misses, and stalls.
- `IDQ.*` and `IDQ_UOPS_NOT_DELIVERED.*`, for uop source cycles, MITE/DSB/MS delivery, and insufficient front-end delivery.

## Control Flow and Integration

`jevents.py` processes this file through `preprocess_one_file()` and `process_one_file()`. `read_json_events()` loads the JSON array with `object_hook=JsonEvent`, so each dictionary is converted immediately. The converter builds an event string from `EventCode`, `UMask`, `CounterMask`, `Invert`, `EdgeDetect`, `SampleAfterValue`, and any recognized MSR mapping. For `MSRIndex` `0x3F7`, the generated field is `frontend=<MSRValue>`.

The resulting events are appended to `_pending_events` for the SkylakeX model directory. When the directory table is flushed, perf emits aliases with topic `frontend`. `builtin-list.c` can print them, and `util/pmu.c` later matches the generated table against the runtime CPU selected through `arch/x86/mapfile.csv`, where SkylakeX is mapped from `GenuineIntel-6-55-[01234]` to the `skylakex` directory.

## State and Persistence Behavior

The source file itself is static repository data. Persistent derived state is the generated `pmu-events.c` built into perf, plus installed perf alias data. Runtime profiling state is handled by perf and the kernel PMU; this JSON file stores no counters or mutable state.

Default periods are part of the persisted alias contract. Most front-end cycle events use large periods such as `2000003`, while retired front-end PEBS events use `100007`. Changing these values does not change event meaning, but it changes default sampling behavior.

## Dependencies

This manifest depends on:

- Intel Skylake Server PMU event encodings, including event codes, umasks, cmasks, and MSR selectors.
- `jevents.py` support for recognized fields and the `0x3F7 -> frontend=` MSR mapping.
- perf generated table types declared under `tools/perf/pmu-events/pmu-events.h`.
- x86 model mapping in `tools/perf/pmu-events/arch/x86/mapfile.csv`.

## Risks and Edge Cases

The highest-risk area is the `FRONTEND_RETIRED.*` family because many aliases share `EventCode` `0xC6`, `UMask` `0x1`, and `MSRIndex` `0x3F7`; the `MSRValue` is what differentiates them. A wrong MSR value would still produce syntactically valid aliases but measure a different front-end condition.

The IDQ families rely heavily on `CounterMask` and sometimes `Invert`; schema-preserving validation is not enough to prove semantic correctness. The `DECODE.LCP` alias overlaps conceptually with `pipeline.json`'s `ILD_STALL.LCP`, so duplicate-looking aliases need to remain intentional.

Text descriptions include hardware-specific caveats and spelling quirks. `JsonEvent.fixdesc()` strips final punctuation and escapes text, so description-only diffs can affect generated C string tables and `perf list` output without changing measurement behavior.

## Test Signals

Useful validation signals are:

- `jq empty frontend.json` to verify JSON syntax.
- Build perf with jevents enabled and confirm generated `pmu-events.c` includes topic `frontend`.
- `perf list frontend` or raw `perf list` on a matching SkylakeX system to confirm aliases appear.
- `perf stat -e idq_uops_not_delivered.core,frontend_retired.latency_ge_16 <workload>` on supported hardware.
- Existing perf PMU tests in `tools/perf/tests/pmu-events.c`, which verify generated table and alias behavior for representative JSON input.
