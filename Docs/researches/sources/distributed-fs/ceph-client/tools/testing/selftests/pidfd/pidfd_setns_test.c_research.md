# sources/distributed-fs/ceph-client/tools/testing/selftests/pidfd/pidfd_setns_test.c

## Purpose
Exercises `setns()` with pidfds and pidfd-derived namespace file descriptors across user, mount, pid, uts, ipc, net, cgroup, and time namespaces, including invalid flags and exited-task handling.

## Important APIs, Types, and Functions
`ns_info[]` maps namespace names, clone flags, and pidfd namespace ioctls. The `current_nsset` fixture stores parent namespace fds, child namespace fds, pidfd-derived namespace fds, and child pidfds. Helpers include `switch_timens()`, `preserve_ns()`, and `in_same_namespace()`.

## Control Flow
Fixture setup captures the current namespace set, creates one exited child and two paused children in new namespaces where available, opens `/proc/<pid>/ns/*` fds, and derives namespace fds through pidfd ioctls. Tests cover invalid `setns()` flags, `ESRCH` on exited pidfd, incremental pidfd setns, incremental nsfd setns, pidfd-derived nsfd setns, one-shot pidfd setns with combined flags, namespace non-corruption between children, and invalid pidfd descriptors.

## State and Persistence
The test mutates the calling process namespace membership during individual tests and owns paused child processes until teardown. It persists no files, but it keeps many namespace fds open to compare inode/device identity and prevent namespace lifetime loss.

## Dependencies and Integration Points
Depends on clone/unshare/setns namespace support, `/proc/*/ns`, pidfd namespace ioctls from `pidfd.h`, socketpairs for child readiness, and `kselftest_harness.h`. It integrates deeply with pidfs namespace ioctl behavior and generic namespace APIs.

## Risks and Test Signals
Privilege and kernel-feature availability can skip paths through missing namespace files or `EOPNOTSUPP`. Risks include leaking changed namespaces across test cases, child cleanup failures, and false positives for pid namespaces because joining a pid namespace affects only future children; the code handles this by comparing the original pid namespace where appropriate.
