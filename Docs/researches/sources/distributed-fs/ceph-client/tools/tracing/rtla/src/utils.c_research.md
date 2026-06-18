# sources/distributed-fs/ceph-client/tools/tracing/rtla/src/utils.c

## Purpose

`utils.c` implements shared rtla helpers for logging, fatal allocation, number and duration parsing, CPU-set parsing, scheduler policy setup, procfs process discovery, cgroup assignment, CPU DMA latency, optional cpupower idle-state control, automatic housekeeping affinity, optional-argument parsing, and strict integer conversion.

## Important APIs, Types, and Functions

Important public functions include `err_msg()`, `debug_msg()`, `fatal()`, `get_llong_from_str()`, `get_duration()`, `parse_cpu_set()`, `parse_stack_format()`, `parse_seconds_duration()`, `parse_ns_duration()`, `parse_prio()`, `__set_sched_attr()`, `set_comm_sched_attr()`, `set_cpu_dma_latency()`, cpupower helpers, `set_pid_cgroup()`, `set_comm_cgroup()`, `auto_house_keeping()`, `parse_optional_arg()`, `strtoi()`, `calloc_fatal()`, `reallocarray_fatal()`, and `strdup_fatal()`.

## Control Flow and Data Flow

Parsing helpers convert command strings into numeric seconds, nanoseconds, CPU masks, stack-format enums, or `sched_attr` fields. Scheduler helpers discover PIDs by scanning `/proc/*/comm` for a prefix and apply `sched_setattr`. Cgroup helpers locate the cgroup v2 mount in `/proc/mounts`, derive either the caller's cgroup or a named cgroup, then write PIDs into `cgroup.procs`. Housekeeping computes CPUs available to rtla but outside monitored CPUs and sets process affinity there.

## State and Persistence Behavior

`config_debug` controls debug logging globally. `set_cpu_dma_latency()` persists latency constraints while its fd remains open. Cpupower support stores idle disable state in static arrays so later restoration can return CPUs to their prior state. Scheduler, affinity, and cgroup changes persist in kernel process state until changed or processes exit.

## Dependencies and Integration Points

The file depends on libc, `/proc`, cgroup v2, Linux scheduler syscalls, `/dev/cpu_dma_latency`, optional libcpupower, and `common.h` globals like `nr_cpus`. It is used by rtla command parsing, timerlat user threads, tracer workload setup, and tests.

## Risks and Edge Cases

`get_llong_from_str()` accepts trailing nonnumeric text because it only checks conversion start and errno. `parse_seconds_duration()` ignores unknown suffixes rather than failing. `parse_ns_duration()` is stricter and supports colon-delimited deadline specs. `/proc` scanning races with process exit. Cgroup helpers assume cgroup v2. Cpupower state restoration must run on cleanup paths or idle states can remain disabled. `auto_house_keeping()` fails when no non-monitored CPU remains in affinity.

## Test Signals

Existing Check tests cover `strtoi()`, `parse_cpu_set()`, and `parse_prio()`. Additional useful tests include duration parsing, optional argument parsing, cgroup path derivation with mocked files, procfs prefix matching, `auto_house_keeping()` CPU-mask cases, cpupower save/restore error paths, and allocation-fatal behavior.
