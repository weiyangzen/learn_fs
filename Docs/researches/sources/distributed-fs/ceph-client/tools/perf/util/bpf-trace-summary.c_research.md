# sources/distributed-fs/ceph-client/tools/perf/util/bpf-trace-summary.c

Purpose: provides syscall latency summary support for perf trace using a BPF skeleton. It aggregates syscall counts, errors, total/min/avg/max latency, and relative standard deviation by CPU/global, thread, or cgroup.

Important APIs and functions: `trace_prepare_bpf_summary()` opens, configures, loads, and attaches the syscall summary skeleton. `trace_start_bpf_summary()` and `trace_end_bpf_summary()` toggle collection. `trace_print_bpf_summary()` reads the BPF map, aggregates entries in userspace hashmaps, sorts by total time, and prints formatted tables. `trace_cleanup_bpf_summary()` destroys the skeleton and releases cached cgroups.

Control flow: preparation sets aggregation mode in rodata and detects cgroup v2. During printing, the code iterates `syscall_stats_map` keys, looks up stats, dispatches to `update_thread_stats()`, `update_total_stats()`, or `update_cgroup_stats()`, copies hashmap values into an array, sorts groups by total time, sorts per-group syscall nodes by total time, and prints common columns.

State and persistence: global `skel` owns the loaded BPF object and maps. Global `cgroups` caches cgroup names for cgroup aggregation. Userspace aggregation state is temporary during print and freed before return. No report is persisted beyond the output stream.

Dependencies and integration points: depends on libbpf generated skeleton `syscall_summary.skel.h`, BPF map APIs, syscall table lookup, cgroup helpers, perf hashmaps, Linux time constants, and math for standard deviation.

Risks: `rel_stddev()` divides by average when count is at least two; zero total time could still produce zero average. `print_total_stats()` calls `print_common_stats(data[i], max_summary, fp)` for each single-node total item; the inner `max_summary` is harmless because each node count is one, but the naming can confuse review. Skeleton load/attach failures return `-1` without cleanup of already-opened skeleton in some paths. Cgroup names can disappear after collection.

Test signals: BPF summary tests for CPU/global, thread, and cgroup modes; zero/one/many syscall entries; unknown syscall numbers; error counts; cgroup v1/v2; sorting by total time; max-summary truncation; and cleanup after load/attach failure.
