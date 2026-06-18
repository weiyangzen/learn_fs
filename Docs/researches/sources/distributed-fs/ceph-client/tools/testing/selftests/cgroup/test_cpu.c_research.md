# sources/distributed-fs/ceph-client/tools/testing/selftests/cgroup/test_cpu.c

## Purpose

`test_cpu.c` validates cgroup v2 CPU controller behavior: subtree propagation, CPU accounting, nice accounting, weight distribution under over/underprovisioning, nested weight aggregation, and `cpu.max` throttling. The complete 825-line file was read.

## Important APIs, Types, and Functions

Key types are `enum hog_clock_type`, `struct cpu_hogger`, and `struct cpu_hog_func_param`. Helpers include `hog_cpu_thread_func()`, `timespec_sub()`, `hog_cpus_timed()`, `run_cpucg_weight_test()`, `weight_hog_ncpus()`, `overprovision_validate()`, `underprovision_validate()`, and `run_cpucg_nested_weight_test()`. Tests include `test_cpucg_subtree_control`, `test_cpucg_stats`, `test_cpucg_nice`, weight tests, nested weight tests, `test_cpucg_max`, and `test_cpucg_max_nested`.

## Control Flow

`main()` finds cgroup v2, enables `+cpu` at the root when needed, and runs a table of tests. Workloads are child processes that spawn busy-loop threads for either process CPU time or wall-clock duration. After children exit, tests read `cpu.stat`, `cpu.weight`, and `cpu.max` effects and compare them with tolerance helpers.

## State and Persistence Behavior

The file creates temporary cgroups, writes `cgroup.subtree_control`, `cpu.weight`, and `cpu.max`, spawns CPU-burning processes, and reads accumulated controller statistics. State is kernel-resident and removed through cgroup destruction.

## Dependencies and Integration Points

It depends on cgroup v2 CPU controller files, scheduler CPU accounting, pthreads, `get_nprocs()`, `clock_gettime()`, `nanosleep()`, and `cgroup_util`.

## Risks and Edge Cases

Runtime-based accounting tests can be noisy on loaded hosts, virtual machines, or systems with unusual scheduling. Underprovisioned tests skip unless enough CPUs exist. Tolerances are generous for weight distribution but still assume stable CPU availability. `cpu.stat` field availability can vary by kernel.

## Test Signals

Expected signals include zero initial stats, `usage_usec` near expected burn time, `nice_usec` near niced workload time, proportional weight deltas under contention, equal-ish runtime without contention, nested child accounting matching leaf totals, and `cpu.max` limiting usage near calculated quota.
