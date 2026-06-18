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
