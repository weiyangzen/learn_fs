# sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/nsfs/pidns.c

## Purpose

`pidns.c` tests `NS_GET_PARENT` for PID and user namespace fds created by a child in new user and PID namespaces.

## Important APIs, Types, and Functions

It defines `NS_GET_USERNS`, `NS_GET_PARENT`, a small aligned clone stack in `struct cr_clone_arg`, and a sleeping `child` function. APIs include `clone(CLONE_NEWUSER|CLONE_NEWPID|SIGCHLD)`, `/proc/<pid>/ns/{pid,user}`, `/proc/self/ns/{pid,user}`, `ioctl`, `fstat`, `stat`, `prctl(PR_SET_PDEATHSIG)`, `kill`, and `wait`.

## Control Flow, State, and Persistence

The parent clones a child that sleeps forever. For both `pid` and `user` namespace paths, it opens the child's namespace fd, calls `NS_GET_PARENT`, stats the returned parent fd, and compares its inode with the caller's corresponding namespace. It then verifies asking for the parent of that parent fails with `EPERM`. State persists only as the child process and namespace fds until killed.

## Dependencies, Integration Points, Risks, and Test Signals

Dependencies are PID/user namespace support and nsfs parent ioctl behavior. It integrates with namespace hierarchy permission checks. Risks include fixed small clone stack, lack of explicit child readiness, and exact `EPERM` expectation for parent-of-parent. Passing signals are parent namespace inode matches for both namespace types and `EPERM` on further parent lookup.
