# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/cgroup_mprog_opts.c

## Purpose
This file tests the newer cgroup multi-program attach, detach, query, and link APIs with explicit ordering options and revision checks. It covers normal, preorder, link-based, and invalid option combinations.

## APIs, Types, and Functions
It uses `cgroup_mprog.skel.h`, `bpf_prog_attach_opts`, `bpf_prog_detach_opts`, `bpf_prog_query_opts`, `bpf_link_create`, `bpf_link_update`, `bpf_link_detach`, `id_from_prog_fd`, and cgroup helpers. `assert_mprog_count` wraps `bpf_prog_query` count assertions.

## Control Flow
`test_prog_attach_detach` attaches four programs with `BPF_F_BEFORE`, `BPF_F_AFTER`, `relative_fd`, and `expected_revision`, queries IDs/revision/order, then detaches with revision validation. `test_link_attach_detach` performs analogous operations through BPF links and checks link IDs. Preorder variants verify `BPF_F_PREORDER` combinations. `test_invalid_attach_detach` exercises bad relative FDs, bad revisions, conflicting flags, missing multi/preorder requirements, and invalid detach options. The entry runs these across supported attach types.

## State, Dependencies, and Integration
State is a test cgroup, loaded skeleton programs, program/link IDs, and kernel mprog revision counters. Cleanup paths carefully detach in reverse order and destroy skeletons.

## Risks and Test Signals
Signals are exact program/link ordering, revision values, counts, and expected errno for invalid cases. This is sensitive to kernel mprog API evolution and attach-type support.
