# subset-b-006825 Research

Grouped source research for Linux kselftest cgroup, clone3, connector, and core selftest build files under `sources/distributed-fs/ceph-client/tools/testing/selftests`. Each source file has a marker-delimited section for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/cgroup/lib/cgroup_util.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/cgroup/lib/cgroup_util.c

## Purpose

`cgroup_util.c` is the shared implementation library for cgroup kselftests. It wraps text I/O against cgroupfs/procfs/sysfs, discovers cgroup v1/v2 roots, creates/destroys test cgroups, migrates processes and threads, starts child workloads inside cgroups, and provides polling/inotify helpers used by the cgroup test binaries. The complete 676-line file was read for this report.

## Important APIs, Types, and Functions

The file exports `read_text()`, `write_text()`, `cg_name()`, `cg_name_indexed()`, `cg_control()`, `cg_read()`, `cg_write()`, `cg_open()`, `cg_write_numeric()`, `cg_read_long()`, `cg_read_long_fd()`, `cg_read_key_long()`, `cg_read_key_long_poll()`, `cg_read_lc()`, `cg_read_strcmp*()`, `cg_read_strstr()`, `cg_find_controller_root()`, `cg_find_unified_root()`, `cg_create()`, `cg_destroy()`, `cg_enter*()`, `cg_run()`, `cg_run_nowait()`, `cg_wait_for_proc_count()`, `cg_killall()`, `clone_into_cgroup()`, `clone_reap()`, `clone_into_cgroup_run_wait()`, `dirfd_open_opath()`, `proc_mount_contains()`, `cgroup_feature()`, `proc_read_text()`, `proc_read_strstr()`, `cg_prepare_for_wait()`, `memcg_prepare_for_wait()`, and `cg_wait_for()`. Global `cg_test_v1_named` switches named-v1 compatibility paths.

## Control Flow

The library is intentionally synchronous and file-oriented. Test code builds paths, reads or writes controller files, and checks numeric or string state. Process helpers either fork then write the child PID to `cgroup.procs`, or use `clone3(CLONE_INTO_CGROUP)` when available and fall back to fork migration on `ENOSYS`. Cleanup retries `rmdir()` after killing cgroup members when `EBUSY` is observed. Wait helpers set inotify watches before triggering state changes, then poll for `POLLIN` with EINTR retry.

## State and Persistence Behavior

The only owned global state is `cg_test_v1_named`; all other state is kernel state exposed through cgroupfs, procfs, sysfs, child processes, and transient allocated path strings returned to callers. Functions persist cgroup hierarchy changes, controller settings, process membership, and sysfs writes until cleanup or kernel action reverses them.

## Dependencies and Integration Points

It depends on libc/POSIX APIs, inotify, poll, signals, waitid/waitpid, cgroupfs, `/proc/self/mounts`, `/proc/mounts`, `/sys/kernel/cgroup/features`, and the local `clone3_selftests.h` syscall wrapper. It is included through `libcgroup.mk` into most cgroup selftest binaries.

## Risks and Edge Cases

The helpers return a mix of `-errno`, `-1`, PIDs, and kselftest exit codes, so callers must know each function's contract. `cg_control()` allocations inside `__prepare_for_wait()` are not freed, acceptable for short tests but still a leak. Mount parsing uses `strtok()` over `/proc/self/mounts`; unusual escaping or long mount tables could stress assumptions. Several wait loops use fixed retry budgets, making slow or overloaded systems a source of false failures. The fallback path for `CLONE_INTO_CGROUP` intentionally masks unsupported clone3 features as `ENOSYS`.

## Test Signals

Coverage is indirect through every cgroup selftest. Strong signals include successful root discovery, cgroup creation/destruction under load, process count waits, controller string/numeric reads, `CLONE_INTO_CGROUP` paths, cgroup event inotify waits, and cleanup of spawned workloads without leaked test cgroups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/cgroup/lib/cgroup_util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/cgroup/lib/include/cgroup_util.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/cgroup/lib/include/cgroup_util.h

## Purpose

`cgroup_util.h` is the public header for the cgroup kselftest utility library. It declares cgroupfs helpers, process-launch helpers, procfs helpers, wait helpers, constants, and small tolerance utilities shared by the cgroup controller tests. The complete 100-line file was read.

## Important APIs, Types, and Functions

Key constants/macros are `PAGE_SIZE`, `MB(x)`, `USEC_PER_SEC`, `NSEC_PER_SEC`, `TEST_UID`, `CG_THREADS_FILE`, `CG_NAMED_NAME`, `CG_PATH_FORMAT`, and `DEFAULT_WAIT_INTERVAL_US`. Inline helpers `values_close()` and `values_close_report()` compare expected and actual numeric metrics with percentage tolerance. The header declares all exported functions from `cgroup_util.c`, including cgroup path, read/write, process migration, clone3, kill, mount-feature, proc-read, and inotify wait APIs.

## Control Flow

The header has no standalone runtime flow. It shapes caller control flow by providing a uniform cgroup operation vocabulary and kselftest-friendly comparison helpers used in assertions across CPU, memory, freezer, pids, zswap, and cpuset tests.

## State and Persistence Behavior

No storage is owned by the header. It declares external `cg_test_v1_named`, which changes thread-file and `/proc/*/cgroup` path formatting for named v1 cgroup tests.

## Dependencies and Integration Points

It includes `stdbool.h` and `stdlib.h`; prototypes also require surrounding translation units to provide POSIX types such as `ssize_t`, `pid_t`, and `useconds_t`. It is consumed through `libcgroup.mk` and by cgroup test C sources.

## Risks and Edge Cases

`MB(x)` is a left shift and depends on integer width/type at the call site. `values_close()` divides by `(a + b)` and can understate tolerance for small values; `values_close_report()` handles zero only for reporting. The header omits `extern` on a few declarations but remains valid C.

## Test Signals

Compile coverage for all cgroup selftest binaries is the primary signal. Runtime signal comes from tolerance helpers accepting expected accounting variance while still catching controller regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/cgroup/lib/include/cgroup_util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/cgroup/lib/libcgroup.mk -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/cgroup/lib/libcgroup.mk

## Purpose

`libcgroup.mk` is the make fragment that builds the shared cgroup utility object for kselftest cgroup programs. The complete 19-line file was read.

## Important APIs, Types, and Functions

It defines `CGROUP_DIR`, `LIBCGROUP_C`, `LIBCGROUP_O`, `LIBCGROUP_O_DIRS`, appends `-I$(CGROUP_DIR)/lib/include` to `CFLAGS`, declares `EXTRA_HDRS` for `clone3_selftests.h`, adds a directory creation rule, compiles `lib/cgroup_util.c` into `$(OUTPUT)/lib/cgroup_util.o`, and appends that object to `EXTRA_CLEAN`.

## Control Flow

Make evaluates the object path, creates output subdirectories, then compiles `cgroup_util.c` with the common selftest compiler variables. Test Makefiles include this fragment to link `$(LIBCGROUP_O)` into generated programs.

## State and Persistence Behavior

It persists build artifacts under `$(OUTPUT)` and records cleanup metadata through `EXTRA_CLEAN`; it does not affect runtime test state.

## Dependencies and Integration Points

It depends on selftest `lib.mk` conventions (`selfdir`, `OUTPUT`, `CC`, `CFLAGS`, `CPPFLAGS`, `TARGET_ARCH`, `EXTRA_CLEAN`) and the clone3 helper header used by the utility library.

## Risks and Edge Cases

Incorrect `selfdir` or `OUTPUT` values break include and object paths. The `dirname | uniq` computation assumes a simple object list. Any change to `cgroup_util.c` dependencies must update `EXTRA_HDRS` or rely on broader make dependency behavior.

## Test Signals

Successful cgroup selftest builds and cleanup of `$(OUTPUT)/lib/cgroup_util.o` validate this fragment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/cgroup/lib/libcgroup.mk -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/cgroup/memcg_protection.m -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/cgroup/memcg_protection.m

## Purpose

`memcg_protection.m` is an Octave model for memory cgroup reclaim protection distribution. It simulates a one-level hierarchy used to justify expected `memory.low`/`memory.min` values in `test_memcontrol.c`. The complete 89-line script was read.

## Important APIs, Types, and Functions

The script defines inputs `E`, `n`, and `c` for parent effective protection, sibling nominal protection, and current consumption. It models reclaim with `cluster`, `alpha`, `epsilon`, and `timeout`, and records histories in `ch`, `eh`, and `rh`.

## Control Flow

For each iteration, it computes low usage, sibling protected share, effective protection normalized for overcommit, recursive unclaimed protection for overuse, reclaim pressure, protection-adjusted scan rate, cluster rounding, and updated consumption. It exits when reclaim drops below `epsilon` or when `timeout` is reached.

## State and Persistence Behavior

All state is in-memory Octave vectors. It prints final `t`, `c`, and `e` values but does not write files.

## Dependencies and Integration Points

It depends on `octave-cli` and the memory protection algorithm mirrored by Linux memory cgroup reclaim. Its expected output informs the comments and tolerance checks in `test_memcg_protection()`.

## Risks and Edge Cases

The model intentionally simplifies reclaim: all memory is reclaimable, only non-low reclaim is simulated, `memory.min` is zero, and sibling reclaim is parallel even though kernel reclaim is serialized. It is explanatory rather than a direct oracle for all kernels.

## Test Signals

Running `octave-cli memcg_protection.m` should converge near the usage values asserted by `test_memcontrol.c`, especially the 29M/21M/0M protected sibling behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/cgroup/memcg_protection.m -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/cgroup/test_core.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/cgroup/test_core.c

## Purpose

`test_core.c` tests core cgroup behavior: controller enablement constraints, threaded/domain topology, populated events, process and thread migration, destruction races, delegated permission checks, namespace-open permission semantics, and named v1 fallback. The complete 959-line file was read.

## Important APIs, Types, and Functions

Important helpers include `touch_anon()`, `alloc_and_touch_anon_noexit()`, `dummy_thread_fn()`, `migrating_thread_fn()`, `lesser_ns_open_thread_fn()`, `setup_named_v1_root()`, and `cleanup_named_v1_root()`. Test entries include `test_cgcore_destroy`, `test_cgcore_populated`, `test_cgcore_invalid_domain`, `test_cgcore_parent_becomes_threaded`, `test_cgcore_no_internal_process_constraint_on_threads`, `test_cgcore_top_down_constraint_enable`, `test_cgcore_top_down_constraint_disable`, `test_cgcore_internal_process_constraint`, `test_cgcore_proc_migration`, `test_cgcore_thread_migration`, `test_cgcore_lesser_euid_open`, and `test_cgcore_lesser_ns_open`.

## Control Flow

`main()` locates a cgroup v2 root and records `nsdelegate`; if unavailable it mounts a named v1 hierarchy at `/mnt/cg_selftest` and marks `cg_test_v1_named`. It enables the memory controller when present, then dispatches each table-driven test and reports kselftest pass/skip/fail. Individual tests create temporary hierarchies, modify `cgroup.type` and `cgroup.subtree_control`, migrate PIDs/threads, verify `/proc/*/cgroup`, exercise `clone3(CLONE_INTO_CGROUP)`, and clean up bottom-up.

## State and Persistence Behavior

The tests mutate cgroupfs hierarchy, controller state, process membership, file ownership, effective UID, cgroup namespace membership, and possibly mount a temporary named v1 cgroup. They preserve root membership by moving the process back before cleanup where needed.

## Dependencies and Integration Points

It depends on cgroup v2 semantics, optional named cgroup v1, memory and CPU controllers, pthreads, `clone()`, `clone3()`, cgroup namespaces, `nsdelegate`, POSIX credentials, and the shared cgroup utility library.

## Risks and Edge Cases

Several tests require root-like privileges or specific mount options and skip when unavailable. Permission tests are sensitive to `TEST_UID`, file ownership, and capability behavior. Thread migration and populated event checks can be timing-sensitive. A failed cleanup can leave test cgroups, so bottom-up destruction and root re-entry are important.

## Test Signals

Strong signals are kselftest pass lines for topology constraints, populated event transitions, threadgroup migration counts, single-thread migration procfs checks, expected `EOPNOTSUPP`/`EACCES`/`ENOENT` failures, and successful named-v1 fallback when v2 is unavailable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/cgroup/test_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/cgroup/test_cpu.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/cgroup/test_cpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/cgroup/test_cpuset.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/cgroup/test_cpuset.c

## Purpose

`test_cpuset.c` validates delegated cpuset controller permissions in cgroup v2. It checks that process migration authorization depends on parent path permissions and that unprivileged delegated subtree controller toggling performs implicit migration correctly. The complete 276-line file was read.

## Important APIs, Types, and Functions

Important helpers are `idle_process_fn()`, `do_migration_fn()`, `do_controller_fn()`, `test_cpuset_perms_object()`, `test_cpuset_perms_object_allow()`, `test_cpuset_perms_object_deny()`, and `test_cpuset_perms_subtree()`.

## Control Flow

`main()` finds cgroup v2, enables `+cpuset`, then runs three tests. Object migration tests create a parent with two children, chown relevant `cgroup.procs` files to `TEST_UID`, start a privileged object process, and run an unprivileged child that attempts migration. The subtree test chowns parent/child cgroup files and has an unprivileged child enable and disable cpuset, validating implicit process migration and controller visibility.

## State and Persistence Behavior

The tests mutate ownership of cgroup control files, controller enablement, process membership, and child process lifetimes. They clean up by killing spawned objects and destroying cgroups.

## Dependencies and Integration Points

It depends on cgroup v2 cpuset controller semantics, POSIX UID changes, file ownership, `cgroup.subtree_control`, `cgroup.controllers`, and `cgroup_util`.

## Risks and Edge Cases

The tests require root to chown cgroup files and create delegated conditions. They deliberately avoid setting child `cpuset.cpus`, so behavior is focused on permission checks rather than CPU mask validity. Cleanup depends on successful kill/reap of paused helper processes.

## Test Signals

Pass signals are allowed migration only when parent permissions are granted, denied migration without parent permission, and successful unprivileged `+cpuset`/`-cpuset` toggling in a delegated subtree with expected controller visibility changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/cgroup/test_cpuset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/cgroup/test_cpuset_prs.sh -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/cgroup/test_cpuset_prs.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/cgroup/test_cpuset_v1_base.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/cgroup/test_cpuset_v1_base.sh

## Purpose

`test_cpuset_v1_base.sh` is a basic root-only bash test for legacy cgroup v1 cpuset read/write interfaces. The complete 77-line script was read.

## Important APIs, Types, and Functions

It defines `skip_test()`, `write_test()`, `ITF_MATRIX`, and `run_test()`. The matrix covers `cpuset.cpus`, `cpuset.mem_exclusive`, `cpuset.mem_hardwall`, `cpuset.memory_migrate`, `cpuset.memory_spread_page`, `cpuset.memory_spread_slab`, `cpuset.mems`, `cpuset.sched_load_balance`, `cpuset.sched_relax_domain_level`, and root-only `cpuset.memory_pressure_enabled`.

## Control Flow

The script requires UID 0, locates a cpuset v1 mount via `mount -t cgroup`, creates `test$$`, iterates matrix entries, writes values to either the test cpuset or root cpuset, reads them back, and fails if the read value differs. It removes the test cgroup at the end and exits kselftest pass/skip/fail style.

## State and Persistence Behavior

It creates one cpuset v1 test directory and writes cpuset control files. Root-only memory pressure writes affect the mounted cpuset root and are not restored to their original values.

## Dependencies and Integration Points

It depends on bash, root, cpuset v1 mounted separately, standard shell tools, and v1 cpuset controller files.

## Risks and Edge Cases

The test assumes CPUs `0-1` and memory node `0` are valid. It stores `original` in `write_test()` but does not restore it. Hosts without CPU1 or with constrained cpuset root state can fail for environmental reasons.

## Test Signals

Pass is exact readback of each writable cpuset v1 control file value followed by successful removal of the test directory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/cgroup/test_cpuset_v1_base.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/cgroup/test_cpuset_v1_hp.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/cgroup/test_cpuset_v1_hp.sh

## Purpose

`test_cpuset_v1_hp.sh` tests a legacy cpuset v1 CPU hotplug case: when a cpuset loses all CPUs, tasks should be forced out to an ancestor. The complete 46-line script was read.

## Important APIs, Types, and Functions

The script defines `skip_test()` and uses shell flow around `CPUSET`, `TDIR`, `TASK`, and `/proc/$TASK/cpuset`.

## Control Flow

It requires root and a cpuset v1 mount, creates `test$$`, assigns CPU 1 and mem node 0, starts a sleeping task, moves the task into the cpuset, verifies `/proc/$TASK/cpuset`, offlines CPU1, waits, onlines CPU1, then verifies the task has moved to `/`.

## State and Persistence Behavior

It creates a v1 cpuset directory, spawns a background sleep process, writes CPU and memory masks, moves a task, and toggles `/sys/devices/system/cpu/cpu1/online`. It restores CPU1 online before checking but does not explicitly kill the sleep task.

## Dependencies and Integration Points

It depends on root, cpuset v1, CPU1 hotplug support, `/proc/$pid/cpuset`, bash, and sysfs CPU online controls.

## Risks and Edge Cases

The script assumes CPU1 exists and is hotpluggable. If offlining is blocked, CPU1 is absent, or hotplug migration is delayed, the test fails. Cleanup is minimal and can leave a task running if early exits occur.

## Test Signals

The key signal is `/proc/$TASK/cpuset` changing from `/$TDIR` to `/` after CPU1 is offlined and restored.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/cgroup/test_cpuset_v1_hp.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/cgroup/test_freezer.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/cgroup/test_freezer.c

## Purpose

`test_freezer.c` validates cgroup v2 freezer behavior across simple groups, nested trees, forkbombs, mkdir/rmdir, migration, ptrace/stopped/vfork states, and frozen time accounting. The complete 1512-line file was read.

## Important APIs, Types, and Functions

Helpers include `cg_check_frozen()`, `cg_freeze_nowait()`, `cg_enter_and_wait_for_frozen()`, `cg_freeze_wait()`, `child_fn()`, `forkbomb_fn()`, `proc_check_stopped()`, `vfork_fn()`, and `cg_check_freezetime()`. Tests include `test_cgfreezer_simple`, `tree`, `forkbomb`, `mkdir`, `rmdir`, `migrate`, `ptrace`, `stopped`, `ptraced`, `vfork`, and `time_*` variants for empty, simple, populate, migrate, parent, child, and nested cases.

## Control Flow

`main()` finds cgroup v2 and runs a table of 17 tests. Most tests create temporary hierarchies, start sleeping children, write `cgroup.freeze`, wait for `cgroup.events` inotify notifications, assert `frozen 0/1`, and destroy cgroups. Time accounting tests read `cgroup.stat.local` `frozen_usec` before and after freeze/unfreeze operations and compare monotonic relationships.

## State and Persistence Behavior

The file creates nested cgroups, spawns many child processes, freezes and unfreezes cgroups, kills cgroup members during destroy, attaches ptrace, sends `SIGSTOP`, uses `vfork()`, and reads freezer time counters. All persistent state is kernel cgroup/process state cleaned up by `cg_destroy()`.

## Dependencies and Integration Points

It depends on cgroup v2 `cgroup.freeze`, `cgroup.events`, `cgroup.stat.local`, inotify helpers, ptrace, process signals, vfork semantics, and `cgroup_util`.

## Risks and Edge Cases

Many tests are timing-sensitive and rely on freezer events within 10 seconds. `cgroup.stat.local frozen_usec` may be absent on older kernels, in which case time tests skip. Ptrace and stopped states can interact with host security policy. Forkbomb tests intentionally create extra processes, so robust cleanup is critical.

## Test Signals

Signals include correct frozen state transitions, descendants remaining frozen under parent freeze, successful kill after forkbomb freeze, inherited freeze state for new children, expected migration behavior between frozen/running groups, ptrace compatibility, stopped/vfork freeze success, and increasing or stable `frozen_usec` according to each scenario.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/cgroup/test_freezer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/cgroup/test_hugetlb_memcg.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/cgroup/test_hugetlb_memcg.c

## Purpose

`test_hugetlb_memcg.c` validates memory cgroup accounting for hugetlb pages when the cgroup mount has `memory_hugetlb_accounting`. The complete 234-line file was read.

## Important APIs, Types, and Functions

Key constants are `ADDR`, `FLAGS`, `LENGTH`, and `PROTECTION`. Helpers include `get_hugepage_size()`, `set_file()`, `set_nr_hugepages()`, `check_first()`, `write_data()`, `hugetlb_test_program()`, and `test_hugetlb_memcg()`.

## Control Flow

`main()` checks the mount option, requires 2MB hugepages, finds cgroup v2, then runs one test. The child test sets `nr_hugepages`, mmaps 8MB of hugetlb memory, verifies mmap alone does not charge memory, reads one page and expects about 2MB charged, writes the full range and expects about 8MB charged, unmaps, and expects usage to return to baseline.

## State and Persistence Behavior

It writes `/proc/sys/vm/nr_hugepages`, creates a cgroup with `memory.max=100M` and `memory.swap.max=0`, maps hugetlb pages, faults them, and observes `memory.current`. The hugepage count is not restored by this file.

## Dependencies and Integration Points

It depends on cgroup v2 memory controller, hugetlb support, 2MB hugepages, `/proc/meminfo`, `/proc/sys/vm/nr_hugepages`, `mmap(MAP_HUGETLB)`, and `cgroup_util`.

## Risks and Edge Cases

Systems without the mount option, without 2MB hugepages, or without permission to set `nr_hugepages` skip or fail. Global hugepage pool changes can affect other workloads. The fixed expected 2MB charge is specific to default hugepage size.

## Test Signals

Pass requires no charge for pool setup or mmap, approximate 2MB charge after first fault, approximate 8MB after touching all pages, and usage dropping back after `munmap()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/cgroup/test_hugetlb_memcg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/cgroup/test_kill.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/cgroup/test_kill.c

## Purpose

`test_kill.c` validates the cgroup v2 `cgroup.kill` interface for simple cgroups, nested trees, and forkbomb-like workloads. The complete 299-line file was read.

## Important APIs, Types, and Functions

Important helpers are `cg_kill_wait()`, `child_fn()`, `forkbomb_fn()`, and tests `test_cgkill_simple()`, `test_cgkill_tree()`, and `test_cgkill_forkbomb()`.

## Control Flow

`main()` finds cgroup v2 and runs three table-driven tests. Each test creates one or more cgroups, spawns sleeping child processes through `cg_run_nowait()`, waits for population, writes `1` to `cgroup.kill`, waits for cgroup event notification, then reaps children and verifies `cgroup.events` reaches `populated 0`.

## State and Persistence Behavior

It creates temporary cgroups and many child processes, triggers kernel-side recursive kill, waits on pidfd helper `wait_for_pid()`, and cleans up hierarchy state.

## Dependencies and Integration Points

It depends on cgroup v2 `cgroup.kill`, `cgroup.events`, inotify wait helpers, the pidfd selftest helper header for `wait_for_pid()`, and `cgroup_util`.

## Risks and Edge Cases

The test assumes `cgroup.kill` is available. Forkbomb children can multiply quickly, so event waits and cleanup must work. Inotify events may race with process exit if a watch is not established before killing, which `cg_kill_wait()` avoids.

## Test Signals

Pass signals are successful kill writes, child reap completion, and `cgroup.events` showing `populated 0` for simple, tree, and forkbomb cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/cgroup/test_kill.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/cgroup/test_kmem.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/cgroup/test_kmem.c

## Purpose

`test_kmem.c` validates memory cgroup kernel-memory accounting for slab/dcache, deleted memcgs, `/proc/kpagecgroup`, kernel stacks, dying descendants, and percpu memory. The complete 458-line file was read.

## Important APIs, Types, and Functions

Key constants are `MAX_VMSTAT_ERROR` and `KMEM_DEAD_WAIT_RETRIES`. Helpers include `alloc_dcache()`, `alloc_kmem_smp()`, `cg_run_in_subcgroups()`, `spawn_1000_threads()`, and tests `test_kmem_basic()`, `test_kmem_memcg_deletion()`, `test_kmem_proc_kpagecgroup()`, `test_kmem_kernel_stacks()`, `test_kmem_dead_cgroups()`, and `test_percpu_basic()`.

## Control Flow

`main()` finds cgroup v2, verifies the memory controller, enables it, then runs six tests. Tests allocate negative dentries, force reclaim with `memory.high`, create/destroy many child memcgs under a memory-enabled parent, read all of `/proc/kpagecgroup`, spawn 1000 threads to validate `kernel_stack`, poll `nr_dying_descendants`, and compare parent `memory.current` to stat components.

## State and Persistence Behavior

It creates many memory cgroups, charges kernel slab/percpu/thread stack memory, sets `memory.high`, reads memory stats, and destroys subtrees. State is transient but can rely on asynchronous RCU and rstat cleanup.

## Dependencies and Integration Points

It depends on cgroup v2 memory controller, `memory.stat`, `memory.current`, `memory.high`, `cgroup.stat`, `/proc/kpagecgroup`, pthreads, `get_nprocs()`, and `cgroup_util`.

## Risks and Edge Cases

Accounting is approximate because per-cpu batches and asynchronous freeing create lag. Large thread counts and 1000 cgroups can stress small systems. `/proc/kpagecgroup` may require privileges or kernel config. Fixed waits for RCU/dying cgroups can be too short on busy hosts.

## Test Signals

Expected signals include slab growth above 1MB then reclaim below half, parent current matching anon+file+kernel+sock within `MAX_VMSTAT_ERROR`, full `/proc/kpagecgroup` read to EOF, `kernel_stack` at least 1000 pages, `nr_dying_descendants` eventually zero, and percpu accounting close to `memory.current`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/cgroup/test_kmem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/cgroup/test_memcontrol.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/cgroup/test_memcontrol.c

## Purpose

`test_memcontrol.c` is the main cgroup v2 memory controller selftest. It validates controller propagation, `memory.current`, peak reset semantics, min/low protection, high/max enforcement, synchronous throttling, reclaim, OOM events, swap peak, socket accounting, OOM group behavior, and inotify deletion events. The complete 1835-line file was read.

## Important APIs, Types, and Functions

Important globals are `has_localevents` and `has_recursiveprot`. Helpers include `get_temp_fd()`, `alloc_pagecache()`, `alloc_anon()`, `is_swap_enabled()`, `set_oom_adj_score()`, `alloc_anon_50M_check()`, `alloc_pagecache_50M_check()`, `alloc_pagecache_50M_noexit()`, `alloc_anon_noexit()`, `cg_test_proc_killed()`, `reclaim_until()`, `tcp_server()`, `tcp_client()`, and `read_event()`. Tests cover `subtree_control`, `current_peak`, `min`, `low`, `high`, `high_sync`, `max`, `reclaim`, `oom_events`, `swap_max_peak`, `sock`, three `oom_group_*` cases, and two inotify deletion cases.

## Control Flow

`main()` finds cgroup v2, verifies memory availability, enables memory at the root, reads mount options, and runs the table. Allocation helpers run in child cgroups and deliberately fault anonymous memory, page cache, socket buffers, or OOM workloads. Tests set memory knobs, trigger pressure or reclaim, read controller stats/events, and compare against expected values with tolerance.

## State and Persistence Behavior

The file creates cgroup trees, writes memory limits/protection/swap/OOM group knobs, creates temporary files via `O_TMPFILE`, allocates anonymous and page-cache memory, opens per-FD peak trackers, starts TCP sockets, sets `oom_score_adj`, and installs inotify watches. All kernel state is intended to be removed by cgroup destruction, child exit, and fd close.

## Dependencies and Integration Points

It depends on cgroup v2 memory controller files (`memory.current`, `memory.peak`, `memory.stat`, `memory.events`, `memory.min`, `memory.low`, `memory.high`, `memory.max`, `memory.reclaim`, `memory.swap.*`, `memory.oom.group`), cgroup mount options, IPv6 localhost sockets, inotify, OOM killer behavior, swap availability for swap tests, and `cgroup_util`.

## Risks and Edge Cases

Memory pressure tests are sensitive to available RAM, swap configuration, reclaim timing, rstat flushing, kernel feature availability, and host OOM policy. Peak reset tests depend on writable peak files and per-FD tracking support. Socket accounting relies on asynchronous `sock` stat drop and has polling slack. OOM event propagation differs with `memory_localevents`, and low event expectations differ with `memory_recursiveprot`.

## Test Signals

Strong signals include child cgroup controller visibility, current/peak values near 50M allocations, correct per-FD peak reset behavior, expected min/low protected reclaim values, `high` and `max` event increments, successful `memory.reclaim`, correct OOM and OOM kill counters, swap/memory peak reset behavior, socket memory matching `memory.stat sock`, OOM group killing scope, and inotify `IN_DELETE_SELF`/`IN_IGNORED` events on file and directory deletion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/cgroup/test_memcontrol.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/cgroup/test_pids.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/cgroup/test_pids.c

## Purpose

`test_pids.c` validates cgroup v2 pids controller enforcement and localized pids event accounting. The complete 181-line file was read.

## Important APIs, Types, and Functions

Helpers are `run_success()`, `run_pause()`, `test_pids_max()`, and `test_pids_events()`.

## Control Flow

`main()` finds cgroup v2, verifies the pids controller, enables `+pids`, and runs two tests. `test_pids_max()` sets `pids.max=2`, enters the cgroup, starts one paused child, and verifies the next child creation fails with `EAGAIN`. `test_pids_events()` requires `pids_localevents`, sets a parent limit, runs children in a child cgroup, and verifies the max event increments on the limiting parent rather than the child.

## State and Persistence Behavior

It writes `pids.max`, moves the current process between cgroups, spawns and signals paused children, and reads `pids.events`. It moves back to the root before cleanup.

## Dependencies and Integration Points

It depends on cgroup v2 pids controller files, `/sys/kernel/cgroup/features`, process creation failure semantics, signals, and `cgroup_util`.

## Risks and Edge Cases

The first test places the current process in the limited cgroup, so cleanup must always re-enter root. Event localization requires kernel support for `pids_localevents` and skips otherwise.

## Test Signals

Pass signals are `cg_run_nowait()` failure with `errno == EAGAIN` at the limit and `pids.events max` incrementing exactly on the parent limit cgroup when localized event support is present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/cgroup/test_pids.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/cgroup/test_stress.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/cgroup/test_stress.sh

## Purpose

`test_stress.sh` is a tiny wrapper that runs the core cgroup test under concurrent stressors. The complete 4-line script was read.

## Important APIs, Types, and Functions

It invokes `./with_stress.sh -s subsys -s fork ${OUTPUT:-.}/test_core`.

## Control Flow

The script delegates all behavior to `with_stress.sh`, selecting subtree-control toggling and fork-loop stress while repeatedly running the built `test_core` binary from `OUTPUT` or the current directory.

## State and Persistence Behavior

State changes come from `with_stress.sh` and `test_core`: cgroup subtree-control toggles, forked `/usr/bin/true` processes, and core test cgroup mutations.

## Dependencies and Integration Points

It depends on bash, `with_stress.sh`, a built `test_core` binary, and cgroup v2 support required by the underlying stress harness.

## Risks and Edge Cases

If `OUTPUT` points to the wrong build directory or `test_core` is absent, the wrapper fails. Stress can amplify timing sensitivity in `test_core`.

## Test Signals

The only direct signal is the exit code from `with_stress.sh`; success means `test_core` repeatedly passed while the selected stressors ran.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/cgroup/test_stress.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/cgroup/test_zswap.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/cgroup/test_zswap.c

## Purpose

`test_zswap.c` validates cgroup memory/zswap integration: zswap usage accounting, disabling zswap per cgroup, zswap-in stats, writeback enable/disable behavior, per-memcg shrink isolation, kswapd charging, and incompressible page stats. The complete 772-line file was read.

## Important APIs, Types, and Functions

Helpers include `read_int()`, `set_min_free_kb()`, `read_min_free_kb()`, `get_zswap_stored_pages()`, `get_cg_wb_count()`, `get_zswpout()`, `allocate_and_read_bytes()`, `allocate_bytes()`, `setup_test_group_1M()`, `attempt_writeback()`, `test_zswap_writeback_one()`, `no_kmem_bypass_child()`, `allocate_random_and_wait()`, and `get_zswap_incomp()`. Tests include `test_zswap_usage`, `test_swapin_nozswap`, `test_zswapin`, writeback enabled/disabled, `test_no_kmem_bypass`, `test_no_invasive_cgroup_shrink`, and `test_zswap_incompressible`.

## Control Flow

`main()` finds cgroup v2, requires zswap module presence and memory controller, enables memory, then runs the table. Tests create limited cgroups, allocate more than `memory.max` to force swap/zswap, read `memory.stat` fields, manipulate `memory.zswap.max` and `memory.zswap.writeback`, trigger `memory.reclaim`, temporarily raises `min_free_kbytes` to wake kswapd, and uses `MADV_PAGEOUT` on random data for incompressible tracking.

## State and Persistence Behavior

The file mutates cgroup memory and zswap files, allocates memory in children, writes `/proc/sys/vm/min_free_kbytes` with restoration, reads debugfs zswap global stats, and creates shared memory/pipe synchronization for child tests.

## Dependencies and Integration Points

It depends on cgroup v2 memory/zswap files, zswap kernel support, debugfs `/sys/kernel/debug/zswap/stored_pages`, swap/reclaim behavior, `MADV_PAGEOUT`, sysinfo, sysctl `min_free_kbytes`, and `cgroup_util`.

## Risks and Edge Cases

Many tests require swap/zswap configuration and enough memory pressure without destabilizing the host. `test_no_kmem_bypass` skips systems above about 5GB RAM and temporarily changes a global VM sysctl. Some stats are gauges and can fall when children exit, so synchronization is important. Debugfs may be unavailable.

## Test Signals

Signals include increasing `zswpout`, zero `zswpout` when `memory.zswap.max=0`, sufficient `zswpin`, `zswpwb` changing only when writeback is enabled, control cgroup writeback count staying zero during another memcg's shrink, zswapped bytes matching global stored pages during kswapd pressure, and positive `zswap_incomp` for random pages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/cgroup/test_zswap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/cgroup/wait_inotify.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/cgroup/wait_inotify.c

## Purpose

`wait_inotify.c` is a small helper program that blocks until an inotify modify event occurs on a specified cgroup file. It is used by cpuset partition root state tests. The complete 87-line file was read.

## Important APIs, Types, and Functions

It defines `usage`, global `file` and `verbose`, `fail_message()`, and `main()`.

## Control Flow

`main()` parses optional `-v`, validates exactly one file argument, opens the file to ensure it exists, creates an inotify fd, adds an `IN_MODIFY` watch, then polls up to 10 seconds per iteration until `POLLIN` is observed. Verbose mode reads and prints the number of inotify events before exit.

## State and Persistence Behavior

It does not mutate the watched file. It creates a transient inotify watch and closes the fd before exiting.

## Dependencies and Integration Points

It depends on libc, inotify, poll, and cgroup files. `test_cpuset_prs.sh` shells out to this binary in its invalid-partition inotify test.

## Risks and Edge Cases

`fail_message()` passes caller-controlled `msg` as a format string with `file`; current callers use fixed strings. The option parsing mutates `argv`/`argc` manually after `getopt()`, which works for the simple `-v` use but is unusual. Poll timeout loops forever on repeated timeouts, so a missing event can hang until test harness timeout.

## Test Signals

The helper succeeds by exiting 0 after an `IN_MODIFY` event; verbose mode additionally reports how many event records were read.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/cgroup/wait_inotify.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/cgroup/with_stress.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/cgroup/with_stress.sh

## Purpose

`with_stress.sh` is a bash harness that runs a command repeatedly while background cgroup stressors operate. The complete 101-line script was read.

## Important APIs, Types, and Functions

It defines `stress_fork()`, `stress_subsys()`, and `init_and_check()`, plus arrays `stresses` and `stress_pids`, and options `-c`, `-d`, `-h`, and `-s`.

## Control Flow

The script parses options, finds cgroup2, checks that the chosen controller can be enabled and disabled, starts requested stress functions in the background, repeatedly runs the remaining command until duration expires or the command fails, then terminates and waits for stress processes before returning the command status.

## State and Persistence Behavior

`stress_fork()` repeatedly launches `/usr/bin/true`. `stress_subsys()` repeatedly writes `+controller` and `-controller` to the root `cgroup.subtree_control`. State is intended to be transient, but the last controller state depends on where the loop is killed.

## Dependencies and Integration Points

It depends on bash, cgroup v2, a writable root `cgroup.subtree_control`, `/usr/bin/true`, `date`, `mount`, `awk`, and the command under test.

## Risks and Edge Cases

Killing stress loops may leave the selected controller enabled or disabled. The command is invoked as `$*`, so arguments with spaces are not preserved robustly. If a stressor exits early, the harness does not notice until cleanup. Stress can create false failures in timing-sensitive tests.

## Test Signals

Exit status mirrors the repeatedly executed command. Successful use demonstrates that a cgroup test survives concurrent fork and subtree-control churn for the configured duration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/cgroup/with_stress.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/clone3/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/clone3/Makefile

## Purpose

The clone3 `Makefile` builds clone3 kselftest programs and links libcap for capability-specific tests. The complete 8-line file was read.

## Important APIs, Types, and Functions

It appends `-g -std=gnu99 $(KHDR_INCLUDES)` to `CFLAGS`, appends `-lcap` to `LDLIBS`, defines `TEST_GEN_PROGS := clone3 clone3_clear_sighand clone3_set_tid clone3_cap_checkpoint_restore`, and includes `../lib.mk`.

## Control Flow

Kselftest make infrastructure uses `TEST_GEN_PROGS` to compile and install the four generated binaries with the given flags and libraries.

## State and Persistence Behavior

It creates build outputs for clone3 selftests and does not affect runtime state.

## Dependencies and Integration Points

It depends on kernel header include paths from `KHDR_INCLUDES`, GNU99 C support, libcap, and selftests `lib.mk`.

## Risks and Edge Cases

Missing libcap headers/library breaks the whole directory build even though only one test needs libcap. Header/API drift in local kernel headers can affect clone3 struct and flag availability.

## Test Signals

Successful build of all four `TEST_GEN_PROGS` validates this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/clone3/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/clone3/clone3.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/clone3/clone3.c

## Purpose

`clone3.c` is the general clone3 syscall ABI selftest. It validates basic clone creation, argument size compatibility, excess argument rejection, exit signal validation, PID/time namespace flags, and rejection of legacy signal bits in `flags`. The complete 342-line file was read.

## Important APIs, Types, and Functions

Important types are `enum test_mode`, `filter_function`, `size_function`, and `struct test`. Helpers include `call_clone3()`, `test_clone3()`, `not_root()`, `no_timenamespace()`, and `page_size_plus_8()`.

## Control Flow

`main()` prints the kselftest header, declares a plan, verifies clone3 support, then iterates `tests[]`. Each row may skip through a filter, compute a dynamic size, call `sys_clone3()`, wait for the child when one is created, and compare the result to an expected errno or success.

## State and Persistence Behavior

It creates short-lived child processes and optional PID/time namespaces. There is no file persistence.

## Dependencies and Integration Points

It depends on clone3 syscall support, local `clone3_selftests.h`, kselftest helpers, root for PID/time namespace cases, and `/proc/self/ns/time` for time namespace availability.

## Risks and Edge Cases

Results depend on the running kernel's clone3 feature set and namespace permission policy. Tests with larger-than-struct arguments depend on zeroed vs nonzero excess bytes. Running inside nested PID namespaces can alter some expectations.

## Test Signals

Pass signals are exact expected return codes for each table row and successful wait/reap for child-creating clone3 calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/clone3/clone3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/clone3/clone3_cap_checkpoint_restore.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/clone3/clone3_cap_checkpoint_restore.c

## Purpose

`clone3_cap_checkpoint_restore.c` verifies that `clone3()` `set_tid` requires `CAP_CHECKPOINT_RESTORE` and that this capability works for a non-root process after dropping UID/GID while keeping capabilities. The complete 178-line file was read.

## Important APIs, Types, and Functions

Important helpers are `child_exit()`, `call_clone3_set_tid()`, `test_clone3_set_tid()`, `struct libcap`, and `set_capability()`. The single harness test is `TEST(clone3_cap_checkpoint_restore)`.

## Control Flow

The test verifies clone3 support and root execution, forks once to learn a free PID, sets a capability set containing `CAP_SETUID`, `CAP_SETGID`, and manually-added `CAP_CHECKPOINT_RESTORE`, enables `PR_SET_KEEPCAPS`, drops to UID/GID 65534, verifies `set_tid` fails without effective checkpoint-restore, restores the capability, and verifies the same `set_tid` succeeds.

## State and Persistence Behavior

It changes process capabilities, UID/GID, and keepcaps state inside the test process; it also creates short-lived clone3 children with requested PIDs.

## Dependencies and Integration Points

It depends on libcap, `prctl(PR_SET_KEEPCAPS)`, clone3 `set_tid`, root privileges, kselftest harness, and `clone3_selftests.h`.

## Risks and Edge Cases

The code manually sets capability bit 40 because userspace headers may not expose `CAP_CHECKPOINT_RESTORE`. This is sensitive to libcap internals and capability numbering. PID reuse expectations assume the forked child PID becomes available quickly.

## Test Signals

Pass requires `set_tid` returning `-EPERM` without the effective capability after dropping privileges and returning success after `CAP_CHECKPOINT_RESTORE` is restored.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/clone3/clone3_cap_checkpoint_restore.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/clone3/clone3_clear_sighand.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/clone3/clone3_clear_sighand.c

## Purpose

`clone3_clear_sighand.c` tests `CLONE_CLEAR_SIGHAND` semantics. It verifies mutual exclusion with `CLONE_SIGHAND` and that custom signal handlers are reset to defaults in the child. The complete 124-line file was read.

## Important APIs, Types, and Functions

Helpers include `nop_handler()`, local `wait_for_pid()`, and `test_clone3_clear_sighand()`.

## Control Flow

`main()` sets one planned test, verifies clone3 support, and calls the test. The test first expects `clone3(CLONE_CLEAR_SIGHAND | CLONE_SIGHAND)` not to succeed. It then installs no-op handlers for `SIGUSR1` and `SIGUSR2`, clones with `CLONE_CLEAR_SIGHAND`, and the child verifies both handlers are `SIG_DFL` before exiting successfully.

## State and Persistence Behavior

It modifies the current process signal dispositions for `SIGUSR1` and `SIGUSR2` and creates one short-lived child. It does not restore handlers before exit because it is a standalone test program.

## Dependencies and Integration Points

It depends on clone3 support, signal APIs, `CLONE_CLEAR_SIGHAND`, kselftest, and `clone3_selftests.h`.

## Risks and Edge Cases

The initial invalid clone check only fails if `pid > 0`; a zero child would be unexpected but not separately handled. Signal handler modifications are process-global but isolated to the test binary.

## Test Signals

Pass is reported when the child sees default handlers for both signals after `CLONE_CLEAR_SIGHAND`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/clone3/clone3_clear_sighand.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/clone3/clone3_selftests.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/clone3/clone3_selftests.h

## Purpose

`clone3_selftests.h` provides a local clone3 syscall ABI wrapper and support probe used by clone3 and cgroup tests. The complete 69-line file was read.

## Important APIs, Types, and Functions

It defines `ptr_to_u64()`, fallback `__NR_clone3`, local `struct __clone_args`, `sys_clone3()`, and `test_clone3_supported()`.

## Control Flow

`sys_clone3()` flushes stdio and invokes `syscall(__NR_clone3, args, size)`. `test_clone3_supported()` calls clone3 with an intentionally invalid `exit_signal`; if clone3 is unavailable it skips, if it unexpectedly creates a child it fails, otherwise it prints supported.

## State and Persistence Behavior

The header has no persistent state. The probe can create and reap a child only if the kernel incorrectly accepts an invalid signal, which is treated as failure.

## Dependencies and Integration Points

It depends on Linux scheduler/types headers, syscall numbers, kselftest helpers, and wait APIs. It is included by clone3 tests and by cgroup utility code for `CLONE_INTO_CGROUP`.

## Risks and Edge Cases

The local `struct __clone_args` must match the kernel ABI. Fallback syscall number 435 is architecture-sensitive but used when headers lack `__NR_clone3`. The support probe treats only `ENOSYS` as unsupported; other errors imply support.

## Test Signals

Compile success and `clone3() syscall supported` output are the primary signals; downstream tests validate the wrapper more deeply.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/clone3/clone3_selftests.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/clone3/clone3_set_tid.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/clone3/clone3_set_tid.c

## Purpose

`clone3_set_tid.c` is a detailed clone3 `set_tid` ABI test. It validates invalid set_tid sizes/values, PID reuse, `CLONE_NEWPID`, nested PID namespace mappings, PID leak cleanup on error paths, and `/proc/$pid/status` `NSpid` reporting. The complete 418-line file was read.

## Important APIs, Types, and Functions

Constants and globals include `MAX_PID_NS_LEVEL`, `pipe_1`, and `pipe_2`. Helpers are `child_exit()`, `call_clone3_set_tid()`, and `test_clone3_set_tid()`.

## Control Flow

`main()` verifies clone3, opens pipes, reads `/proc/sys/kernel/pid_max`, runs invalid-size and invalid-value test rows, skips root-only parts when non-root, then as root finds a free PID, reallocates it, tests namespace-specific PID creation, unshares a PID namespace, runs nested child tests, synchronizes with a clone3 child via pipes, reads `NSpid` from `/proc/<pid>/status`, and folds child kselftest counts back into the parent.

## State and Persistence Behavior

It creates and reaps many short-lived processes, unshares PID namespaces, uses pipes for synchronization, and reads procfs. No persistent files are written.

## Dependencies and Integration Points

It depends on clone3 `set_tid`, PID namespaces, root privileges for most positive tests, `/proc/sys/kernel/pid_max`, `/proc/$pid/status`, kselftest, and `clone3_selftests.h`.

## Risks and Edge Cases

The file assumes execution in the host PID namespace for several expected errors. Nested namespace depth can alter the `MAX_PID_NS_LEVEL - 1` comments. PID reuse is inherently timing-sensitive, though the test immediately uses a just-freed PID. Manual kselftest count adjustment is subtle.

## Test Signals

Signals include exact errno matches for invalid inputs, success for PID 1 in new namespaces, expected parent-visible PIDs, leak checks allowing later PID allocation, and `NSpid` containing the requested outer/middle/inner PID tuple.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/clone3/clone3_set_tid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/connector/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/connector/Makefile

## Purpose

The connector `Makefile` builds the process connector filter selftest. The complete 6-line file was read.

## Important APIs, Types, and Functions

It appends `-Wall $(KHDR_INCLUDES)` to `CFLAGS`, defines `TEST_GEN_PROGS = proc_filter`, and includes `../lib.mk`.

## Control Flow

Kselftest make infrastructure compiles `proc_filter.c` into the generated test program.

## State and Persistence Behavior

It only produces build artifacts and has no runtime persistence.

## Dependencies and Integration Points

It depends on kernel headers through `KHDR_INCLUDES` and selftests `lib.mk`.

## Risks and Edge Cases

Warnings are enabled with `-Wall`; header drift in connector/proc connector structs can break the build.

## Test Signals

Successful build of `proc_filter` validates the Makefile.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/connector/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/connector/proc_filter.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/connector/proc_filter.c

## Purpose

`proc_filter.c` is an interactive process connector selftest/listener. It registers with the kernel connector netlink proc event source, optionally requests a filtered event stream, prints received process events, and unregisters on SIGINT. The complete 310-line file was read.

## Important APIs, Types, and Functions

Important globals are `interrupted`, `nl_sock`, `ret_errno`, `tcount`, `evn`, and `filter`. Key functions are `send_message()`, `register_proc_netlink()`, `sigint()`, `handle_packet()`, `handle_events()`, and `main()`.

## Control Flow

`main()` parses optional `-f`, installs a SIGINT handler, builds either legacy `enum proc_cn_mcast_op` input or `struct proc_input` filtering for `PROC_EVENT_NONZERO_EXIT`, registers a `NETLINK_CONNECTOR` socket and epoll fd, loops handling events until interrupted, sends ignore/unregister, closes fds, prints total count, and exits.

## State and Persistence Behavior

It opens a netlink socket bound to `CN_IDX_PROC`, registers kernel listener state, creates an epoll fd, increments `tcount` for events, and unregisters listener state before exit when interrupted normally.

## Dependencies and Integration Points

It depends on Linux connector headers, `NETLINK_CONNECTOR`, `CN_IDX_PROC`, `CN_VAL_PROC`, proc connector events, epoll, signals, and kselftest print helpers.

## Risks and Edge Cases

The program is listener-like and runs until SIGINT, so automated harnesses need to manage lifetime. Error cleanup paths close different fd subsets but can reference `epoll_fd` after partial initialization. Filtered mode depends on `struct proc_input` kernel support. `handle_packet()` assigns to its local `event` pointer and does not copy back through the parameter, which is fine because callers only rely on printing/counting.

## Test Signals

Signals include successful netlink registration, receipt and printing of fork/exec/exit/uid/gid/session/ptrace/comm/coredump events, filtered nonzero-exit events with `-f`, clean unregister, and nonzero `tcount` when events occur.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/connector/proc_filter.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/core/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/core/Makefile

## Purpose

The core `Makefile` builds generic core selftests for `close_range` and `unshare`. The complete 7-line file was read.

## Important APIs, Types, and Functions

It appends `-g $(KHDR_INCLUDES)` to `CFLAGS`, defines `TEST_GEN_PROGS := close_range_test unshare_test`, and includes `../lib.mk`.

## Control Flow

Kselftest make infrastructure compiles the two listed generated programs using kernel headers.

## State and Persistence Behavior

It only produces build artifacts and has no runtime state.

## Dependencies and Integration Points

It depends on `KHDR_INCLUDES`, the selftests top-level make conventions, and source files `close_range_test.c` and `unshare_test.c` in the same directory.

## Risks and Edge Cases

Header mismatches or missing source files break the directory build. Debug info is always enabled through `-g`.

## Test Signals

Successful build of `close_range_test` and `unshare_test` validates the Makefile.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/core/Makefile -->
