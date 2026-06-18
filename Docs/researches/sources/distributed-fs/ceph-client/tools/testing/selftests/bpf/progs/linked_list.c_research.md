<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/linked_list.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/linked_list.c

Purpose: Positive intrusive BPF linked-list tests over map, inner-map, global, nested, and array-backed list heads. The file has 421 source lines and 8340 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `tc:map_list_push_pop, tc:inner_map_list_push_pop, tc:global_list_push_pop, tc:global_list_push_pop_nested, tc:global_list_array_push_pop, tc:map_list_push_pop_multiple, tc:inner_map_list_push_pop_multiple, tc:global_list_push_pop_multiple, tc:map_list_in_list, tc:inner_map_list_in_list, tc:global_list_in_list`. Local functions/subprograms: `list_push_pop, list_push_pop_multiple, list_in_list, test_list_push_pop, test_list_push_pop_multiple, test_list_in_list, map_list_push_pop, inner_map_list_push_pop, global_list_push_pop, global_list_push_pop_nested, global_list_array_push_pop, map_list_push_pop_multiple, inner_map_list_push_pop_multiple, global_list_push_pop_multiple; plus 3 more`. Maps: `none declared in this file`. Types: `head_nested_inner, head_nested`. BPF helpers/kfuncs/macros used as calls: `bpf_list_pop_back, bpf_list_pop_front, bpf_list_push_back, bpf_list_push_front, bpf_map_lookup_elem, bpf_obj_drop, bpf_obj_new, bpf_spin_lock, bpf_spin_unlock`. Verifier messages asserted here: `none declared in this file`.

Control flow: Entry points are BPF programs in `tc:map_list_push_pop, tc:inner_map_list_push_pop, tc:global_list_push_pop, tc:global_list_push_pop_nested, tc:global_list_array_push_pop, tc:map_list_push_pop_multiple, tc:inner_map_list_push_pop_multiple, tc:global_list_push_pop_multiple; plus 3 more`. Control flow is centered on map lookups/updates select per-test storage and branch on NULL results; critical sections protect intrusive container or resource-spin-lock state.

State and persistence: There is no long-lived userspace-visible storage beyond BPF global/data variables and verifier-observed stack state. It also manipulates verifier-tracked kernel object references or kptr ownership, so every acquire/exchange/drop path is part of the state contract.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: reference/kptr ownership mistakes can leak references or allow use-after-drop patterns.

Test signals: successful attachment/execution of tc:map_list_push_pop, tc:inner_map_list_push_pop, tc:global_list_push_pop, tc:global_list_push_pop_nested, tc:global_list_array_push_pop, tc:map_list_push_pop_multiple; plus 5 more; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/linked_list.c -->
