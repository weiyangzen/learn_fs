# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/cgroup_attach_autodetach.c

## Purpose
This serial test verifies automatic detachment and eventual program release when a cgroup with attached programs is removed without explicit detach.

## APIs, Types, and Functions
It hand-builds a minimal `BPF_PROG_TYPE_CGROUP_SKB` allow program using raw BPF instructions and `bpf_test_load_program`. It uses `setup_cgroup_environment`, `create_and_get_cgroup`, `join_cgroup`, `bpf_prog_attach`, `bpf_prog_query`, `bpf_prog_get_fd_by_id`, and shell `ping`.

## Control Flow
The test loads two allow programs, creates and joins `/cg_autodetach`, attaches both with `BPF_F_ALLOW_MULTI`, queries their IDs, sends loopback traffic, allocates memory to keep the cgroup pinned, closes program and cgroup FDs, leaves/removes the cgroup via cleanup, then polls up to roughly five seconds for `bpf_prog_get_fd_by_id` to fail for each old program ID.

## State, Dependencies, and Integration
State includes cgroup hierarchy, attached BPF programs, program IDs, loopback traffic, and a temporary heap allocation. Cleanup closes any remaining program/cgroup FDs and resets cgroup environment.

## Risks and Test Signals
The signal is disappearance of program IDs after asynchronous auto-detach. Risks are timing sensitivity, ping availability, cgroup cleanup behavior, and delayed RCU/program release on busy kernels.
