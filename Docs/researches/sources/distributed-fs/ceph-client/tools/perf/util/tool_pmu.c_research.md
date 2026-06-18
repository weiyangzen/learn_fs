# sources/distributed-fs/ceph-client/tools/perf/util/tool_pmu.c

## Purpose

`tool_pmu.c` implements perf's synthetic `tool` PMU. These events are computed by userspace rather than programmed in the kernel and expose elapsed time, user/system CPU time, topology counts, PMEM presence, SMT status, TSC frequency, and target-mode indicators.

## Important APIs, Types, and Functions

Event mapping functions are `tool_pmu__event_to_str()`, `tool_pmu__str_to_event()`, `tool_pmu__skip_event()`, `tool_pmu__num_skip_events()`, `perf_pmu__is_tool()`, `evsel__is_tool()`, `evsel__tool_event()`, and `evsel__tool_pmu_event_name()`. Open/read functions are `evsel__tool_pmu_prepare_open()`, `evsel__tool_pmu_open()`, `tool_pmu__read_event()`, `evsel__tool_pmu_read()`, and `tool_pmu__new()`. Internal parsers read fields from `/proc/stat` and `/proc/<pid>/stat`.

## Control Flow and State

Architecture filters hide `slots` off arm64 and `system_tsc_freq` off x86. Duration events record `rdclock()` at open and emit elapsed nanoseconds only for CPU 0/thread 0. User/system time events open procfs files for each relevant CPU/thread and store starting ticks in `evsel->start_times`; reads seek back to offset zero, read current fields, convert clock ticks to nanoseconds, and report deltas. Static topology events compute values only on CPU 0/thread 0 and write zero elsewhere to avoid aggregation multiplication.

## Dependencies and Integration Points

It depends on evsel counts, xyarray, thread maps, CPU maps, topology, SMT, cgroup fd state, stat configuration, sysfs/procfs, TSC helpers, and the common PMU event table. It integrates with `perf stat` and event parsing under the `tool/` PMU.

## State and Persistence Behavior

State lives in evsel fields: `start_time`, `start_times`, fd array, `pid_stat`, counts, and previous raw counts. PMEM detection is cached statically after checking ACPI NFIT.

## Risks and Test Signals

Risks include fragile procfs field parsing, incorrect CPU/thread aggregation, stale fd ownership on partial open failure, clock tick conversion precision, and platform-specific event visibility. Tests should cover all event names, skipped events per architecture, duration no-sampling validation, per-process and per-CPU user/system deltas, topology events with CPU filters, cgroup pid handling, and lost-count behavior when a synthetic read fails.
