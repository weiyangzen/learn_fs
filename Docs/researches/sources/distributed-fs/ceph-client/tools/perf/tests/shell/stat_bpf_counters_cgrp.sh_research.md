## sources/distributed-fs/ceph-client/tools/perf/tests/shell/stat_bpf_counters_cgrp.sh

Purpose: validates `perf stat --bpf-counters --for-each-cgroup` with system-wide cgroup counting.
Important functions: `check_bpf_counter`, `find_cgroups`, and `check_system_wide_counted`.
Control flow: probes support using root cgroup, chooses common systemd slices or root/self cgroups, then runs CPU-clock counts for each selected cgroup and fails if any output contains `<not`.
State and persistence: no files.
Dependencies and integration: cgroup v1/v2 files under `/sys/fs/cgroup` and `/proc/self/cgroup`, BPF counters, and system-wide stat.
Risks: cgroup topology and permissions vary widely; result correctness is limited to non-`<not>` output, not value comparison.
Test signals: command success and counted cgroup rows.
