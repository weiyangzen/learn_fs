# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/arrowlake/other.json

## Purpose

`other.json` defines Arrow Lake PMU aliases that do not fit cleanly into cache, memory, front-end, pipeline, virtual-memory, or floating-point topic files. It contains 21 event records: 16 `cpu_atom`, 4 `cpu_core`, and 1 `cpu_lowpower`.

The file covers bus locks, dynamic prefetch throttler state, streaming write offcore responses, queue promotion/fullness, hardware/page-fault assists, and a low-power last-branch-record compatibility alias.

## Important APIs, types, and data shape

The file is a standard event JSON array. Fields used are:

- `EventName`, `EventCode`, `UMask`, `Counter`, and `SampleAfterValue`.
- Optional `CounterMask`, particularly for cycle-style bus-lock aliases.
- `Unit`.
- Optional `MSRIndex` and `MSRValue` for `OCR.*` streaming write aliases.
- `Deprecated` on `LBR_INSERTS.ANY`.
- `BriefDescription` and optional `PublicDescription`.

There are 20 unique event names; only `OCR.STREAMING_WR.ANY_RESPONSE` appears for both `cpu_atom` and `cpu_core`.

## Event coverage

Atom aliases include:

- `BUS_LOCK.BLOCKED_CYCLES`, `.LOCK_CYCLES`, `.NON_SPLIT_LOCKS`, and `.SPLIT_LOCKS`.
- `DYNAMIC_PREFETCH_THROTTLER.LEVEL0_SOC` through `.LEVEL4_SOC`.
- `OCR.FULL_STREAMING_WR.ANY_RESPONSE`, `OCR.PARTIAL_STREAMING_WR.ANY_RESPONSE`, and `OCR.STREAMING_WR.ANY_RESPONSE`.
- `XQ_PROMOTION.ALL`, `.CRDS`, `.DRDS`, and `.RFOS`.

P-core aliases include `ASSISTS.HARDWARE`, `ASSISTS.PAGE_FAULT`, `OCR.STREAMING_WR.ANY_RESPONSE`, and `XQ.FULL`. The only low-power alias is deprecated `LBR_INSERTS.ANY`, described as an alias to `MISC_RETIRED.LBR_INSERTS`.

## Control flow and integration

`jevents.py` derives topic `other` from the filename and processes the file through the standard event parser. Generated entries become part of the Arrow Lake PMU event table selected by `mapfile.csv`. Runtime perf consumers see these names as normal event aliases.

The offcore streaming write aliases use the same extra-register path as `OCR.*` events in `cache.json` and `memory.json`. They depend on `MSRIndex` `0x1a6,0x1a7` and distinct `MSRValue` filters to classify full, partial, or general streaming writes.

## State and persistence behavior

The JSON is static source data. Runtime state appears only through PMU programming. `OCR.*` aliases program offcore response filter MSRs. Bus-lock and dynamic prefetch throttler aliases are read-only hardware counters from perf's perspective, but their values reflect global or SoC-level behavior that may be affected by other workloads on the system.

Deprecated metadata for `LBR_INSERTS.ANY` persists into generated tables and keeps old scripts working while pointing users toward `MISC_RETIRED.LBR_INSERTS`.

## Dependencies and integration points

The file depends on the same perf PMU event generation path as other event JSON files. It integrates with lock-contention, prefetch, assist, and offcore analysis workflows. Relevant metric group descriptions in `metricgroups.json` include `LockCont`, `Prefetches`, `Offcore`, `MachineClears`, `OS`, and possibly `Power` or `SoC` for dynamic prefetch throttler events.

Because this is a catch-all topic, it may overlap conceptually with several neighboring files. New events should be placed here only when no more specific topic matches, to preserve `perf list` usability.

## Risks and edge cases

The catch-all nature of the file is the biggest maintainability risk. It can accumulate unrelated aliases, making topic filtering less predictable. Offcore streaming write aliases are MSR-sensitive and must remain aligned with the correct response-filter values. Bus-lock events can be high-impact on production systems because they often indicate severe synchronization or split-lock behavior; descriptions should stay precise.

The deprecated low-power `LBR_INSERTS.ANY` alias is a compatibility surface. Removing it can break scripts even though a replacement name exists elsewhere. The dynamic prefetch throttler levels use a sequence of related names; adding or renumbering levels should be checked against hardware documentation so level semantics do not drift.

## Test signals

Baseline tests are JSON syntax validation and perf PMU event generation. Representative alias checks include `BUS_LOCK.SPLIT_LOCKS`, `DYNAMIC_PREFETCH_THROTTLER.LEVEL4_SOC`, `OCR.STREAMING_WR.ANY_RESPONSE`, `XQ_PROMOTION.ALL`, `ASSISTS.PAGE_FAULT`, and deprecated `LBR_INSERTS.ANY`. For `OCR.*` aliases, `perf list --details` should show the extra MSR filter data.
