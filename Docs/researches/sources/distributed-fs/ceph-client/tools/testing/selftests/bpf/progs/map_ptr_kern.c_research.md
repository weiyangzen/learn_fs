<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/map_ptr_kern.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/map_ptr_kern.c

Purpose: Kernel `struct bpf_map` pointer introspection test covering many map implementations and their type-specific fields. The file has 721 source lines and 17590 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `cgroup_skb/egress:cg_skb`. Local functions/subprograms: `check_bpf_map_fields, check_bpf_map_ptr, check, check_default, check_hash, check_array, check_prog_array, check_perf_event_array, check_percpu_hash, check_percpu_array, check_stack_trace, check_cgroup_array, check_lru_hash, check_lru_percpu_hash; plus 17 more`. Maps: `m_hash, m_array, m_prog_array, m_perf_event_array, m_percpu_hash, m_percpu_array, m_stack_trace, m_cgroup_array, m_lru_hash, m_lru_percpu_hash, m_lpm_trie, inner_map; plus 15 more`. Types: `bpf_map_type, bpf_map, bpf_htab, bpf_array, bpf_stack_map, lpm_trie, lpm_key, inner_map, bpf_dtab, bpf_stab; plus 9 more`. BPF helpers/kfuncs/macros used as calls: `bpf_map_lookup_elem, bpf_map_sum_elem_count, bpf_map_update_elem, bpf_ringbuf_discard, bpf_ringbuf_reserve`. Verifier messages asserted here: `none declared in this file`.

Control flow: Entry points are BPF programs in `cgroup_skb/egress:cg_skb`. Control flow is centered on map lookups/updates select per-test storage and branch on NULL results.

State and persistence: Persistent state is held in BPF maps `m_hash, m_array, m_prog_array, m_perf_event_array, m_percpu_hash, m_percpu_array, m_stack_trace, m_cgroup_array, m_lru_hash, m_lru_percpu_hash; plus 17 more` and in globals emitted into BPF data sections.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: the main risk is drift between this BPF object and the user-space selftest expectations that load it.

Test signals: successful attachment/execution of cgroup_skb/egress:cg_skb; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/map_ptr_kern.c -->
