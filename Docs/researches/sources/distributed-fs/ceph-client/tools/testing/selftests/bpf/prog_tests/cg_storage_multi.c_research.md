# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/cg_storage_multi.c

## Purpose
This serial cgroup test validates cgroup local storage semantics when multiple programs and attach types are involved. It distinguishes egress-only, isolated per-attach-type storage, and shared cgroup storage behavior across parent and child cgroups.

## APIs, Types, and Functions
It uses cgroup and network helpers, `struct cgroup_value` from `progs/cg_storage_multi.h`, skeletons `cg_storage_multi_egress_only`, `cg_storage_multi_isolated`, and `cg_storage_multi_shared`, `bpf_program__attach_cgroup`, and map lookup helpers. Local helpers `assert_storage`, `assert_storage_noexist`, and `connect_send` drive assertions and traffic.

## Control Flow
The serial entry creates parent and child cgroups, then runs three subtests. `test_egress_only` attaches parent then child egress programs and checks packet counters keyed by cgroup ID and attach type. `test_isolated` attaches two egress and one ingress program at parent and child, verifying separate ingress and egress storage keys. `test_shared` repeats the topology but expects combined ingress/egress counters under a shared cgroup ID key.

## State, Dependencies, and Integration
State spans cgroup hierarchy, UDP sockets, kernel BPF maps, links, and skeleton BSS invocation counters. Cgroups and links are closed/destroyed after each path. It depends on cgroup v2 helpers, networking, and local storage map semantics.

## Risks and Test Signals
Signals are exact invocation counts and map values after traffic. Risks include cgroup setup failures, socket traffic not triggering expected hooks, or key schema changes between isolated and shared storage maps.
