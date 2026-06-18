
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/skylakex/cache.json

## Purpose

This file defines 157 Skylake-X server cache and memory-hierarchy core PMU events. It covers L1D replacements and pending misses, L2 line movement and request classes, longest-latency cache references/misses, retired load/store categories, L3 hit/miss attribution, offcore requests/outstanding requests/responses, snoop/coherency responses, store queue pressure, split locks, software prefetch accesses, and IDI writeback transitions.

The event inventory includes families such as `L1D.*`, `L1D_PEND_MISS.*`, `L2_LINES_*`, `L2_RQSTS.*`, `LONGEST_LAT_CACHE.*`, `MEM_INST_RETIRED.*`, `MEM_LOAD_RETIRED.*`, `MEM_LOAD_L3_HIT_RETIRED.*`, `MEM_LOAD_L3_MISS_RETIRED.*`, `OFFCORE_REQUESTS*`, `OFFCORE_RESPONSE*`, `CORE_SNOOP_RESPONSE.*`, `SQ_MISC.SPLIT_LOCK`, and `SW_PREFETCH_ACCESS.*`.

## Important Schema Fields and APIs

The file uses the perf raw event schema:

- `EventName`: public alias.
- `EventCode` and `UMask`: raw core event selector and subevent mask.
- `Counter`: allowed programmable counters.
- `CounterMask`: present on 7 rows for thresholded cycle/count behavior.
- `AnyThread`: present on one row for any-thread counting.
- `PEBS` and `Data_LA`: present on 24 rows, indicating precise sampling and load-address support.
- `MSRIndex` and `MSRValue`: present on 73 offcore-response rows. These program model-specific offcore response filter registers.
- `SampleAfterValue`: default sampling period for all 157 rows.
- `Deprecated`: present on one row, warning that the alias should not be preferred.
- `Errata`: present on 2 rows and appended by `jevents.py` to generated descriptions.
- `BriefDescription` and `PublicDescription`: user-facing descriptions.

`jevents.py` lowers `AnyThread` to `any=...`, `CounterMask` to `cmask=...`, `MSRIndex`/`MSRValue` to extra MSR programming metadata, `PEBS` to precise-event metadata, and `Data_LA` to an additional address-support note.

## Control Flow and Data Flow

The descriptor flow is JSON -> `JsonEvent` parsing in `jevents.py` -> generated C PMU table -> runtime perf alias matching for Skylake-X CPUs. For simple cache events, perf programs `EventCode`/`UMask` directly. For `OFFCORE_RESPONSE.*` aliases, perf must also program the offcore response MSR filter specified by `MSRIndex` and `MSRValue`; these aliases represent filtered offcore transaction classes rather than only the base event code.

The data feeds direct `perf stat -e` usage, sampling with PEBS-capable memory events, and Skylake-X metrics such as server memory bandwidth, latency, cache hit/miss, snoop, and topdown analyses in adjacent `skx-metrics.json` or generated metric files.

## State and Persistence

The file has no mutable state. Persistent output is generated perf metadata embedded in build artifacts. Runtime state includes core PMU counters, optional precise event records, data linear-address samples for `Data_LA` events, and offcore MSR filter state while perf owns the event.

## Dependencies and Integration Points

This file depends on Skylake-X server core PMU encodings, PEBS support, offcore response MSR definitions, and the kernel perf driver accepting the generated event configuration. Integration points include `jevents.py`, `metric.py` for metrics referencing these aliases, `arch/x86/mapfile.csv`, generated `pmu-events.c`, `perf list`, `perf stat`, and `perf record`.

It also integrates with Skylake-X `counter.json`: many events specify legal generic counters, and the platform has four generic core counters plus fixed counters according to that capacity file. Offcore events may contend for limited MSR/filter resources and cannot always be scheduled freely with other offcore filters.

## Risks

The largest risks are offcore filter correctness and schedulability. `MSRIndex`/`MSRValue` mistakes can silently select the wrong request/response class, and multiple offcore events may conflict on limited filter registers. PEBS/Data_LA rows have privilege, kernel, and hardware constraints; they may not sample addresses in all contexts. Counter restrictions, `AnyThread`, and `CounterMask` can alter meaning or prevent event groups from scheduling. Server Skylake-X cache/coherency semantics differ from client Skylake, so copying events between directories can produce invalid aliases or metrics.

## Test Signals

Build validation should parse JSON and regenerate `pmu-events.c` without duplicate or invalid aliases. Runtime tests should cover `perf list` for each major family, `perf stat -e` for simple L1/L2/L3 events, an offcore response alias with expected traffic, and PEBS sampling for a `MEM_LOAD_*` row. Metric smoke tests should run server cache/memory metrics that depend on these events and check that counter grouping does not fail due to offcore or PEBS constraints.
