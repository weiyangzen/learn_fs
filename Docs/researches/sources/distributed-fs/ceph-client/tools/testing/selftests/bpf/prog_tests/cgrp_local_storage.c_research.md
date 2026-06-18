# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/cgrp_local_storage.c

## Purpose
Exercises cgroup local storage behavior across cgroup v2 and v1 net_cls hierarchies, including tracepoint BTF access, cgroup-attached socket programs, recursion safety, verifier rejection, sleepable iterators, and RCU-lock requirements.

## Important APIs, types, and functions
Uses skeletons `cgrp_ls_tp_btf`, `cgrp_ls_recursion`, `cgrp_ls_attach_cgroup`, `cgrp_ls_negative`, and `cgrp_ls_sleepable`. `CGROUP_MODE_SET()` writes global mode into each skeleton BSS. `test_tp_btf()` mutates a cgroup local storage map and validates tracepoint counters. `test_attach_cgroup()` attaches cgroup and tracing programs, opens a TCP connection, and checks socket cookie map values. Sleepable tests use `bpf_program__set_autoload()`, `bpf_program__attach_iter()`, `bpf_iter_create()`, and RCU-specific load expectations.

## Control flow and state
`test_cgrp_local_storage()` runs `cgrp2_local_storage()` then `cgrp1_local_storage()`. The v2 path joins `/cgrp_local_storage`; the v1 path sets up classid and obtains hierarchy ID. Runtime state includes global `is_cgroup1`/`target_hid`, skeleton BSS counters/IDs, cgroup storage maps, socket cookie map entries, sockets, iterator links, and cgroup/classid FDs.

## Dependencies and integration points
Depends on cgroup v1/v2 helpers, network helpers, syscall tracepoints, BPF iterators, cgroup local storage map semantics, and generated verifier-negative programs. It is integrated as a single selftest that fans out through subtests.

## Risks and test signals
Risks include cgroup v1 availability, RCU semantic differences, and iterator support. Signals include successful map update/lookup/delete, exactly three enter/exit counts in the tracepoint case, expected cookie value derived from client port, no recursion deadlock, rejected negative skeleton, and correct cgroup ID from sleepable paths.
