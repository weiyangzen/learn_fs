# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/cgroup_skb_direct_packet_access.c

## Purpose
This compact test verifies that a cgroup skb program can be run through `BPF_PROG_TEST_RUN` and directly access packet data boundaries.

## APIs, Types, and Functions
It uses `cgroup_skb_direct_packet_access.skel.h`, `bpf_prog_test_run_opts`, `bpf_program__fd`, and a 64-byte zeroed test skb buffer.

## Control Flow
The test opens and loads the skeleton, runs the `direct_packet_access` program with packet data via test-run opts, asserts the syscall succeeds, expects retval `1`, and checks that the BPF program wrote a nonzero `data_end` value into BSS.

## State, Dependencies, and Integration
State is limited to the input buffer and skeleton BSS. It does not attach to a real cgroup; it integrates with the kernel test-run path for cgroup skb programs.

## Risks and Test Signals
Signals are test-run success, return value, and BSS `data_end`. Risks include verifier/test-run changes for direct packet access and program type restrictions.
