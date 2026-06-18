# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/cgroup_mprog_ordering.c

## Purpose
This test validates multi-program ordering for cgroup getsockopt hooks when `BPF_F_BEFORE` is used with and without an explicit relative FD.

## APIs, Types, and Functions
It reuses `cgroup_preorder.skel.h`, cgroup helpers, `bpf_prog_attach_opts`, `bpf_prog_detach2`, `bpf_program__expected_attach_type`, and a TCP socket `getsockopt` trigger. `run_getsockopt_test` implements one ordering check.

## Control Flow
The entry joins `/parent`, creates a socket, and invokes `run_getsockopt_test` twice. Each run attaches `parent`, then attaches `parent_2` with `BPF_F_ALLOW_MULTI | BPF_F_BEFORE`, optionally setting `relative_fd` to the first program. A `getsockopt(IP_TOS)` call triggers both programs, and the skeleton BSS `result` array must record the expected order `4, 3`.

## State, Dependencies, and Integration
State is one cgroup FD, socket FD, skeleton BSS result array, and temporary program attachments. Cleanup detaches both programs and destroys the skeleton.

## Risks and Test Signals
The signal is BSS ordering after getsockopt. Risks include unsupported mprog ordering flags, attach-type mismatch, and socket option behavior differences.
