# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/lunarlake/virtual-memory.json

## Purpose

`virtual-memory.json` defines 48 Lunar Lake events for TLB and page-walk behavior. It covers demand-load, store, and instruction-side TLB misses; STLB hits; page walks completed by page size; active and pending page walks; atom-specific load-head stalls; page-walker cache hits; and STLB flush attempts. The catalog is used to diagnose address-translation overhead and memory-side frontend/backend stalls.

## Important APIs, Types, And Data Shape

The file is a JSON array using `EventName`, `Unit`, `EventCode`, `UMask`, `Counter`, `CounterMask`, `BriefDescription`, `PublicDescription`, and `SampleAfterValue`. It contains both `cpu_atom` and `cpu_core` encodings for shared names such as `DTLB_LOAD_MISSES.STLB_HIT`, `DTLB_*_WALK_COMPLETED`, `DTLB_*_WALK_PENDING`, and `ITLB_MISSES.*`. Core walk-active events use `CounterMask: "1"` to count cycles with at least one page miss handler active.

## Control Flow

The perf generator assigns topic `virtual-memory`, converts each object into a generated event alias, and preserves unit-specific encodings. At runtime, users can collect aliases per PMU, while higher-level top-down metrics can combine these events with pipeline and cache stalls to explain memory-bound behavior.

## State And Persistence

The JSON is static. Generated aliases persist event codes and unit-specific masks. Runtime state is limited to configured PMU counters. There is no cross-run persistence in the source or generated table.

## Dependencies And Integration Points

Dependencies include Lunar Lake hybrid PMU encodings, page miss handler semantics, and perf JSON generation. Integration points include `perf list virtual-memory`, top-down memory/TLB metrics, `metricgroups.json` groups such as `MemoryTLB`, `tma_dtlb_load_group`, `tma_dtlb_store_group`, and `tma_itlb_misses_group`, plus tests that verify generated event aliases.

## Risks

The same event name can use different event codes and masks on atom and core PMUs, so unit-aware lookup is required. Some atom-only events such as `LD_HEAD.DTLB_MISS`, `PAGE_WALKER_LOADS.*`, and `TLB_FLUSHES.STLB_ANY` should not be assumed available on core PMUs. `WALK_PENDING` style events count outstanding walks per cycle, while `WALK_COMPLETED` counts completions; mixing them in ratios without unit care can produce misleading metrics.

## Test Signals

Validation should check array length 48, both units present, and expected groups of DTLB load, DTLB store, and ITLB events. Runtime tests include `perf list virtual-memory`, targeted collection of `dtlb_load_misses.walk_completed`, and hybrid-specific checks for atom-only aliases. Metric validation should compare TLB miss rates under workloads with known page-size or working-set changes.
