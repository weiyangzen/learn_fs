# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/cgroup_attach_multi.c

## Purpose
This serial test validates legacy multi/override cgroup program attach semantics, effective program ordering through cgroup hierarchy, replacement behavior, detach behavior, and query edge cases.

## APIs, Types, and Functions
It uses raw BPF instruction construction in `prog_load_cnt`, creating an array map plus cgroup storage and percpu cgroup storage maps. It calls `bpf_test_load_program`, `bpf_prog_attach`, `bpf_prog_attach_opts`, `bpf_prog_detach2`, `bpf_prog_query`, `bpf_map_lookup_elem`, `bpf_map_update_elem`, and cgroup helper functions. `PING_CMD` triggers egress hooks.

## Control Flow
The test loads several programs that add distinct values to a shared map, sets up nested cgroups, attaches programs with combinations of `BPF_F_ALLOW_MULTI`, `BPF_F_ALLOW_OVERRIDE`, and no flags, sends traffic, and verifies the accumulated value corresponds to the effective program set. It checks duplicate attach rejection, effective query counts and ENOSPC behavior, bottom-program detach, replace failure modes, valid replace including self-replace, and subsequent detach effects.

## State, Dependencies, and Integration
State includes nested cgroups, multiple loaded program FDs, shared array map, local storage maps, and loopback traffic. Cleanup closes programs, map FD, cgroup FDs, and cgroup environment.

## Risks and Test Signals
Signals are map counter sums, query counts, attach flags, program IDs, and expected errno values. The test is sensitive to cgroup hook ordering, legacy attach semantics, ping availability, and exact errno behavior.
