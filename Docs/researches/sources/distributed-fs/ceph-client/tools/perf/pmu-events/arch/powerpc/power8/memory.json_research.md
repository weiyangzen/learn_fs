# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power8/memory.json

## Purpose

This file defines 35 POWER8 raw PMU events for memory and nest-facing behavior. It covers chip/group/system pump prediction and misprediction for demand loads and broader request classes, data reloads from local/remote/distant memory and L4, data-side PTE sourcing from distant or remote memory, L3 castout, memory reads, prefetches and RWITM, memory locality thresholds, and the nest reference clock.

## APIs, types, and schema

Entries use `EventCode`, `EventName`, `BriefDescription`, and `PublicDescription`. Representative names include `PM_DATA_FROM_LMEM`, `PM_DATA_FROM_RMEM`, `PM_DATA_FROM_DMEM`, `PM_DATA_FROM_RL4`, `PM_DATA_FROM_MEMORY`, `PM_DATA_*_PUMP_*`, `PM_*PUMP_*`, `PM_DPTEG_FROM_*`, `PM_MEM_READ`, `PM_MEM_PREF`, `PM_MEM_RWITM`, `PM_MEM_CO`, and `PM_NEST_REF_CLK`.

## Control flow and integration

Perf generation compiles these memory events into POWER8 PMU tables. Runtime users use them to study memory locality, pump prediction, coherence traffic, and memory-controller-facing activity. Some events are demand-load specific while others cover all data types excluding data prefetch, so correct selection depends on the analysis question.

## State and persistence

The file is static metadata. Event names, codes, and descriptions persist into generated perf metadata. The events measure runtime hardware state such as pump prediction and memory traffic, but that state is not persisted in the JSON.

## Dependencies

Dependencies include POWER8 memory hierarchy and nest PMU semantics, L4/cache topology, local/remote/distant node definitions, pump-scope prediction, and perf's event generation pipeline. Integration points are generated `pmu-events.c`, `perf list`, `perf stat`, and any external tooling that groups POWER8 memory events.

## Risks

Pump-scope names are similar and easy to confuse, especially demand-load-specific `PM_DATA_*` counters versus broader `PM_*` counters. `PM_NEST_REF_CLK` requires a documented multiplier to obtain PB cycles, so raw values can be misread. Topology-dependent local/remote/distant semantics vary by machine configuration. Description typos should not be treated as semantic changes but can affect user-facing docs.

## Test signals

Use JSON validation, event-code uniqueness, PMU generation, and runtime event-open checks. Hardware tests should compare broad memory reads with source-specific reload counters where feasible and should include representative pump prediction and misprediction events.
