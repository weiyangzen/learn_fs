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
