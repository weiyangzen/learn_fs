# sources/distributed-fs/ceph-client/tools/perf/util/bpf_skel/syscall_summary.bpf.c

## sources/distributed-fs/ceph-client/tools/perf/util/bpf_skel/syscall_summary.bpf.c

Purpose: this BPF program records syscall latency and error statistics, aggregated by thread, CPU, or cgroup.

Important maps and globals: `syscall_trace_map` maps tid to syscall number and enter timestamp. `syscall_stats_map` maps `struct syscall_key` to `struct syscall_stats`. BSS `enabled` gates collection; rodata `aggr_mode` and `use_cgroup_v2` select aggregation and cgroup id lookup.

Control flow: `sys_enter` stores syscall number and timestamp by tid. `sys_exit` calls `do_exit(ret)`, which looks up the enter record, chooses key fields according to aggregation mode, computes duration, updates stats, and deletes the trace record. `sched_process_exit` also calls `do_exit(0)` to account in-flight syscalls for exiting tasks.

State and persistence: enter records persist only while a syscall is active. Stats persist in a hash map and maintain total time, squared sum, min/max, count, and error count.

Dependencies and integration: includes `syscall_summary.h`; user space must set aggregation rodata and read the stats map. Cgroup v1 lookup uses perf_event cgroup subsystem via CO-RE.

Risks: squared sum can overflow for long durations or high counts. Max/min updates are not atomic. If an enter event is missed, exit is ignored; if exit is missed, process-exit may account with ret zero. Cgroup lookup depends on kernel cgroup layout and perf subsystem id.

Test signals: run syscall summary by thread, CPU, and cgroup; generate failing syscalls; verify min/max/mean/stddev inputs; and test task exit during a blocking syscall.
