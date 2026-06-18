# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/skylake/frontend.json

## Purpose

`frontend.json` defines 49 Skylake frontend PMU events for instruction fetch, decode, decoded-stream-buffer delivery, MITE delivery, microcode sequencer delivery, frontend latency, and under-delivery of uops to the backend. It supports top-down and direct frontend bottleneck analysis through perf aliases.

The major clusters are `FRONTEND_RETIRED.*` latency and miss events, `IDQ.*` instruction-decode-queue delivery events, `IDQ_UOPS_NOT_DELIVERED.*` backend supply shortfall events, instruction-cache tag/data events, and DSB-to-MITE switch penalties.

## Important schema/API surface

The descriptor entries use normal perf event fields:

- `EventName`: examples include `BACLEARS.ANY`, `DECODE.LCP`, `DSB2MITE_SWITCHES.COUNT`, `FRONTEND_RETIRED.LATENCY_GE_16`, `ICACHE_64B.IFTAG_MISS`, `IDQ.DSB_UOPS`, `IDQ.MITE_UOPS`, and `IDQ_UOPS_NOT_DELIVERED.CORE`.
- `EventCode`/`UMask`: raw PMU event selector and mask. `FRONTEND_RETIRED.*` entries use MSR-based precise frontend latency filtering rather than ordinary masks alone.
- `MSRIndex`/`MSRValue`: `FRONTEND_RETIRED.*` entries use MSR index `0x3F7` with latency/miss-specific values.
- `PEBS`: precise frontend-retired events are marked with PEBS levels, with `LATENCY_GE_1` carrying `PEBS: 2` and most other frontend-retired variants carrying `PEBS: 1`.
- `CounterMask`, `AnyThread`, `EdgeDetect`, and `Invert`: used by cycle-style IDQ and delivery events.
- `BriefDescription`, `PublicDescription`, and `SampleAfterValue`: expose frontend-analysis semantics to users.

## Control flow and integration

The file is consumed by perf's Skylake event alias layer. When a user selects frontend aliases, perf programs generic PMU counters. For `FRONTEND_RETIRED.*` aliases, perf must also program frontend latency/miss filtering through the `0x3F7` MSR value. That extra-register path is comparable to offcore-response events in `cache.json` and `memory.json`, but it targets frontend retirement qualification rather than memory suppliers.

The event set integrates strongly with top-down microarchitecture analysis. `IDQ_UOPS_NOT_DELIVERED.*` and `IDQ.*` provide frontend-bound signals that can feed higher-level metrics, while `ICACHE_*`, `DECODE.LCP`, and `DSB2MITE_SWITCHES.*` help decompose fetch latency, decode stalls, and uop-cache transitions.

## State and persistence behavior

The JSON is static metadata. Runtime state consists of selected PMU counters, optional frontend MSR filters, PEBS records when sampling precise events, and perf's event scheduling metadata. No state is persisted by this file.

## Dependencies

The file depends on Skylake frontend PMU semantics, kernel support for PEBS and the frontend event extra register, perf's JSON schema, and the CPU model map selecting this file only for compatible Skylake systems. Some event meanings also depend on SMT and pipeline delivery width assumptions used by top-down metrics.

## Risks and maintenance notes

The most important risk is extra-register correctness. Incorrect `MSRValue` values for `FRONTEND_RETIRED.LATENCY_GE_*` or miss events would silently change the latency threshold or miss class being sampled. Because many latency entries differ by small mask changes, tests need to inspect values rather than only names.

Precise sampling requirements can make frontend-retired aliases unavailable or approximate on some kernels or virtual machines. Tools should preserve the `PEBS` markings and should not assume every frontend event is equally usable in counting and sampling modes.

Naming drift is another risk: `IDQ.ALL_*`, `IDQ.*`, and `IDQ_UOPS_NOT_DELIVERED.*` sound similar but measure different delivery conditions. Metric expressions should reference exact event names and not pattern-match broad prefixes without checking definitions.

## Test signals

Validation should include JSON syntax, required field checks, and generated perf alias tests. Runtime smoke tests on Skylake hardware should cover `IDQ_UOPS_NOT_DELIVERED.CORE`, `IDQ.MITE_UOPS`, `IDQ.DSB_UOPS`, `ICACHE_64B.IFTAG_MISS`, and at least one `FRONTEND_RETIRED.LATENCY_GE_*` event that exercises MSR index `0x3F7`.
