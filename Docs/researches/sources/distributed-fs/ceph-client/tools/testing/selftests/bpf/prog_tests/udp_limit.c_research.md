# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/udp_limit.c

## Purpose
Tests cgroup socket create/release BPF programs that enforce a single UDP socket per cgroup.

## APIs, Types, and Functions
Entry point is `test_udp_limit()`. It uses `test__join_cgroup()`, `bpf_program__attach_cgroup()`, and normal `socket()`/`close()`.

## Control Flow, State, and Persistence
The test joins/creates `/udp_limit`, loads the skeleton, attaches socket-create and socket-release programs to the cgroup, opens one UDP socket successfully, asserts the second UDP socket fails, closes the first, opens another successfully, and checks BSS `invocations == 4` and `in_use == 1`. Fds and skeleton are cleaned up on exit.

## Dependencies and Integration
Depends on cgroup BPF support, cgroup test helpers, `udp_limit.skel.h`, and UDP socket creation.

## Risks and Test Signals
Risks include cgroup setup permission issues and unexpected socket-create side effects from the test environment. Signals are first socket success, second socket failure, reopen success after release, and exact BSS counters.
