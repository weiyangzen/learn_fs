# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/cgroup_getset_retval.c

## Purpose
This test validates cgroup getsockopt/setsockopt hooks that read and set syscall return values. It checks retval propagation, override ordering, legacy reject compatibility, synchronization between context retval and helper-visible retval, and which hook sections are exposed.

## APIs, Types, and Functions
It uses skeletons `cgroup_getset_retval_setsockopt`, `cgroup_getset_retval_getsockopt`, and `cgroup_getset_retval_hooks`, plus `bpf_program__attach_cgroup`, `setsockopt`, `getsockopt`, `start_server`, and `bpf_object__find_program_by_name`. The generated `exposed_hooks` table comes from `cgroup_getset_retval_hooks.h`.

## Control Flow
The entry joins a cgroup and starts a UDP server socket. Setsockopt subtests attach combinations of programs that set errno, read retval, default to zero, or perform legacy EPERM-style rejection; then they call `setsockopt` and assert errno, invocation count, assertion flags, and BSS retval. Getsockopt subtests perform analogous checks for kernel errors, BPF override, and clearing retval. `test_exposed_hooks` iterates hook names, enables one at a time, and checks load return against expected errors.

## State, Dependencies, and Integration
State is cgroup membership, socket FD, BPF links, and skeleton BSS counters. Each subtest destroys links and skeletons. The test integrates with cgroup socket option hooks and newer retval helper semantics.

## Risks and Test Signals
Signals are syscall return/errno, BSS `invocations`, `assertion_error`, `retval_value`, and `ctx_retval_value`. Risks include kernel version support for retval hooks, exact errno semantics, and generated hook table drift.
