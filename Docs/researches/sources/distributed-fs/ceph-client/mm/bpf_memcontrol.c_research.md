# sources/distributed-fs/ceph-client/mm/bpf_memcontrol.c

## Purpose
`bpf_memcontrol.c` registers BPF kfuncs that let BPF programs acquire memory cgroups and read selected memory controller statistics and events.

## Important APIs, types, and functions
Kfuncs are `bpf_get_root_mem_cgroup`, `bpf_get_mem_cgroup`, `bpf_put_mem_cgroup`, `bpf_mem_cgroup_vm_events`, `bpf_mem_cgroup_usage`, `bpf_mem_cgroup_memory_events`, `bpf_mem_cgroup_page_state`, and `bpf_mem_cgroup_flush_stats`. The `BTF_KFUNCS_START` block annotates acquire/release/null/RCU/sleepable semantics, and `bpf_memcontrol_init` registers the set for `BPF_PROG_TYPE_UNSPEC`.

## Control flow
At late init, the file registers a BTF kfunc ID set. BPF callers can acquire the root memcg, translate an arbitrary css to the memory-controller css if needed under RCU, release acquired references, read validated vm events or stat counters, read memory usage and memory events, or flush memcg stats in sleepable contexts.

## State and persistence
The file stores no private mutable state. It operates on memcg/css references and counters maintained by the memory controller. Acquired memcg references persist until a matching `bpf_put_mem_cgroup`.

## Dependencies and integration points
It depends on memcontrol, cgroup css lifetime rules, BPF kfunc registration, BTF ID metadata, RCU, and page counter/stat helpers. The Makefile builds it only for `CONFIG_BPF_SYSCALL` plus `CONFIG_MEMCG`.

## Risks and test signals
Risks include reference leaks in BPF programs, invalid enum reads, css translation races, exposing sleepable flushing to non-sleepable program contexts, and behavior when memcg is disabled. Test signals include verifier checks for acquire/release pairing, RCU requirements, root and non-root cgroup lookups, invalid counter indexes, disabled-memcg boots, and BPF selftests for kfunc availability.
