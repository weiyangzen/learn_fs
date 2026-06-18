# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/cgroup_storage.c

## Purpose
This file tests classic cgroup local storage behavior for packet filtering and an out-of-bounds verifier/runtime guard path.

## APIs, Types, and Functions
It uses `cgroup_storage.skel.h`, cgroup helpers, network namespace helpers, `bpf_program__attach_cgroup`, map get-next-key/lookup/update APIs, and shell `ping`. `setup_network` creates a dedicated namespace with loopback up; `cleanup_network` removes it.

## Control Flow
`test_cgroup_storage` creates and joins a cgroup, enters a netns, loads and attaches the BPF program, and sends pings that should alternate success/failure based on a packet counter stored in cgroup storage. It reads the storage key/value, increments the counter from user space, verifies the alternating behavior continues, and asserts there is only one storage key. `test_cgroup_storage_oob` loads the same skeleton, attaches a program intended to trigger an out-of-bounds local-storage access path, and drives it through a socket operation.

## State, Dependencies, and Integration
State includes cgroup membership, netns, BPF link, cgroup storage map entries, and shell ping traffic. Cleanup destroys the skeleton, namespace, cgroup FD, and cgroup environment.

## Risks and Test Signals
Signals are ping success/failure sequence, map lookup/update correctness, single-key enumeration, and expected handling of OOB access. Risks include ping/netns setup failures, packet timing, and local storage map semantics changes.
