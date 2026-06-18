# sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/nsfs/owner.c

## Purpose

`owner.c` tests `NS_GET_USERNS`, which returns the owning user namespace for another namespace fd, and verifies permission behavior after entering a different user namespace.

## Important APIs, Types, and Functions

The program defines `NS_GET_USERNS` and a `pr_err` diagnostic macro. It uses `pipe`, `fork`, `unshare(CLONE_NEWUTS|CLONE_NEWUSER)`, `/proc/<pid>/ns/uts`, `/proc/self/ns/user`, `ioctl`, `fstat`, `stat`, `prctl(PR_SET_PDEATHSIG)`, `kill`, and `wait`.

## Control Flow, State, and Persistence

The parent forks a child that creates a new UTS and user namespace, closes pipe ends, and sleeps. The parent treats pipe EOF as readiness, opens the child's UTS namespace fd, calls `NS_GET_USERNS`, and compares the returned namespace inode to `/proc/self/ns/user` or the expected owner. It opens the initial user namespace and then unshares into a new user namespace, where `NS_GET_USERNS` on both the child's namespace and initial user namespace should fail with `EPERM`. State is held in namespace fds and the child process lifetime.

## Dependencies, Integration Points, Risks, and Test Signals

Dependencies are user and UTS namespace support and nsfs owner ioctls. It integrates with namespace ownership and permission checks. Risks include EOF-as-ready synchronization being ambiguous if the child exits early, infinite child sleep requiring cleanup, and exact permission expectations. Passing signals are matching namespace inode numbers before privilege transition and `EPERM` after entering the new user namespace.
