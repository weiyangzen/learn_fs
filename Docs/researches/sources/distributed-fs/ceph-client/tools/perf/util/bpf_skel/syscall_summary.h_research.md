# sources/distributed-fs/ceph-client/tools/perf/util/bpf_skel/syscall_summary.h

## sources/distributed-fs/ceph-client/tools/perf/util/bpf_skel/syscall_summary.h

Purpose: this header defines the map ABI for syscall summary BPF collection.

Important types: `enum syscall_aggr_mode` selects thread, CPU, or cgroup aggregation. `struct syscall_key` combines cgroup id, cpu-or-tid, and syscall number. `struct syscall_stats` stores total time, squared sum, max/min, count, and error count.

Control flow and state: no executable logic. BPF writes `syscall_stats` rows keyed by `syscall_key`; user space reads and formats them.

Dependencies and integration: included by `syscall_summary.bpf.c` and the corresponding user-space summary reader.

Risks: struct layout changes break map compatibility. `cpu_or_tid` has mode-dependent meaning, so user-space readers must use the same aggregation mode used at collection time.

Test signals: map layout compile checks and functional runs for all aggregation modes.
