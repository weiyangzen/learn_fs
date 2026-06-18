# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/cgroup_preorder.c

## Purpose
This file validates `BPF_F_PREORDER` execution ordering for cgroup getsockopt programs across parent and child cgroups and within the same cgroup.

## APIs, Types, and Functions
It uses `cgroup_preorder.skel.h`, `bpf_prog_attach_opts`, `bpf_prog_detach2`, `bpf_program__expected_attach_type`, cgroup helpers, and `setsockopt`/`getsockopt` on `IP_TOS`. `run_getsockopt_test` performs the attach and trigger sequence.

## Control Flow
The test creates parent and child cgroups, opens a socket, and runs the helper twice: once with mixed default/preorder flags and once with all attachments preorder. The helper attaches two child programs, triggers getsockopt and checks child-only order, resets BSS, attaches two parent programs, triggers again, and validates the full parent/child execution order for the selected mode.

## State, Dependencies, and Integration
State includes cgroup FDs, socket TOS value, skeleton BSS `idx` and `result`, and four temporary program attachments. Cleanup detaches every program and closes resources.

## Risks and Test Signals
The signal is exact BSS result ordering. Risks include kernel preorder semantics changes, attach-type support, and getsockopt not traversing the expected cgroup hook path.
