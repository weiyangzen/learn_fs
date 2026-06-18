# sources/distributed-fs/ceph-client/tools/perf/util/tool_pmu.h

## Purpose

`tool_pmu.h` declares the synthetic userspace PMU interface.

## Important APIs, Types, and Functions

`enum tool_pmu_event` lists `duration_time`, `user_time`, `system_time`, topology and target indicator events, `slots`, and `system_tsc_freq`. `tool_pmu__for_each_event` iterates all real events. The header declares name conversion, skip logic, direct read, PMU/evsel classification, prepare/open/read hooks, CPU slots helper, and PMU construction.

## Control Flow and State

The enum values are stored in `perf_event_attr.config` for tool evsels, so ordering is part of the internal contract.

## Dependencies and Integration Points

It depends on `pmu.h`, evsel, thread maps, and CPU maps. Event parsing and stat reading use this header to identify synthetic events.

## Risks and Test Signals

Risks include enum/name table drift and architecture-specific skip mismatches. Tests should iterate the enum and validate names, reverse lookup, and PMU type classification.
