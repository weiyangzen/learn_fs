# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/cgroup_v1v2.c

## Purpose
Verifies that a cgroup connect4 BPF policy can block TCP connects both in a pure cgroup v2 environment and when cgroup v1 `net_cls` classid is also active.

## Important APIs, types, and functions
Uses `connect4_dropper.skel.h`, `cgroup_helpers.h`, and `network_helpers.h`. `run_test()` loads the skeleton, sets target server port in BSS, attaches `connect_v4_dropper` to the supplied cgroup, optionally joins classid, and expects `connect_to_fd_opts()` to fail with `EPERM`. `test_cgroup_v1v2()` first verifies baseline connectivity without BPF, then runs cgroup-v2-only and cgroup-v1v2 subcases.

## Control flow and state
State consists of server/client sockets, a cgroup FD, optional classid hierarchy, and BPF BSS `port`. The same server is reused for both policy subcases after baseline connectivity is checked. Cleanup destroys skeletons and classid environment.

## Dependencies and integration points
Requires cgroup helper support, cgroup v1 classid setup, IPv4 TCP sockets, and a generated cgroup connect program. It integrates as a selftest entry point `test_cgroup_v1v2()`.

## Risks and test signals
Main risks are environmental: classid mount/setup failure and port byte-order confusion. Passing signal is an `EPERM` connect failure only after BPF is attached, with baseline connect succeeding beforehand.
