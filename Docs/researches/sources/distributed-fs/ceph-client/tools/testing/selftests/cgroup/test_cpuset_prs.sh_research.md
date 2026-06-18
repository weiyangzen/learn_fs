# sources/distributed-fs/ceph-client/tools/testing/selftests/cgroup/test_cpuset_prs.sh

## Purpose

`test_cpuset_prs.sh` is a large bash kselftest for cgroup v2 cpuset partition root state. It validates local and remote partition transitions, CPU exclusivity, isolated partitions, CPU hotplug invalidation/recovery, scheduler-domain isolation, and inotify generation for invalid partition states. The complete 1212-line script was read.

## Important APIs, Types, and Functions

Important data sets are `TEST_MATRIX`, `REMOTE_TEST_MATRIX`, and `SETUP_A123_PARTITIONS`. Key functions include `skip_test()`, `cleanup()`, `pause()`, `console_msg()`, `test_partition()`, `test_effective_cpus()`, `test_add_proc()`, `write_cpu_online()`, `set_ctrl_state()`, `set_ctrl_state_noerr()`, `online_cpus()`, `reset_cgroup_states()`, `dump_states()`, `set_cgroup_dir()`, `check_effective_cpus()`, `check_cgroup_states()`, `check_isolcpus()`, `test_fail()`, `null_isolcpus_check()`, `check_test_results()`, `run_state_test()`, `run_remote_state_test()`, `test_isolated()`, `wait_inotify()`, and `test_inotify()`.

## Control Flow

The script requires root, finds the cgroup2 mount, requires at least 8 CPUs, optionally enables sched verbose debug output, enables cpuset at the root, and performs a preliminary skip if existing child cpusets prevent root partition creation. It then runs matrix-driven local hierarchy tests, remote hierarchy tests, explicit isolated partition transitions, and inotify verification. State commands like `C`, `X`, `CX`, `P`, `O`, and `T` map to writes to `cpuset.cpus`, `cpuset.cpus.exclusive`, `cpuset.cpus.partition`, CPU online files, and `cgroup.procs`.

## State and Persistence Behavior

The script mutates root cgroup subtree control, creates/removes multiple cgroup trees, writes cpuset CPU masks and partition states, offlines/onlines CPUs, may write `/sys/kernel/debug/sched/verbose`, writes to `/dev/console`, and uses temp files under `/tmp`. Trap cleanup restores CPU online state, removes cgroups, and restores sched debug verbosity.

## Dependencies and Integration Points

It depends on bash, cgroup v2 cpuset files, `/sys/devices/system/cpu/*/online`, `/sys/devices/system/cpu/isolated`, optional `/sys/kernel/debug/sched/domains`, optional `wait_inotify` helper binary, `lscpu`, `awk`, `sed`, `grep`, `sort`, `uniq`, and root privileges.

## Risks and Edge Cases

This is intentionally fragile under slow machines, CPU hotplug restrictions, existing cpuset usage, boot-time isolated CPUs overlapping 0-8, or missing debugfs. It uses fixed delays and global CPU online changes, so failures can be environmental. Cleanup must restore offlined CPUs to avoid host disruption.

## Test Signals

Signals include all matrix rows passing expected write success/failure, exact effective CPU masks, exact partition state mappings (`member`, `root`, `isolated`, and invalid variants), expected isolated CPU lists from both cpuset and scheduler-domain views, successful isolated transition sequence, and inotify notification when a partition becomes invalid.
