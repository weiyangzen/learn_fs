<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/local_kptr_stash_fail.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/local_kptr_stash_fail.c

Purpose: Negative local kptr stash cases for type mismatch and non-zero-offset release. The file has 86 source lines and 1843 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `tc:stash_rb_nodes, tc:drop_rb_node_off`. Local functions/subprograms: `stash_rb_nodes, drop_rb_node_off`. Maps: `some_nodes`. Types: `node_data, map_value, node_data2, node_data`. BPF helpers/kfuncs/macros used as calls: `bpf_kptr_xchg, bpf_map_lookup_elem, bpf_obj_drop, bpf_obj_new`. Verifier messages asserted here: `invalid kptr access, R2 type=ptr_node_data2 expected=ptr_node_data, R1 must have zero offset when passed to release func`.

Control flow: Entry points are BPF programs in `tc:stash_rb_nodes, tc:drop_rb_node_off`. Control flow is centered on map lookups/updates select per-test storage and branch on NULL results; annotated negative cases assert exact verifier diagnostics.

State and persistence: Persistent state is held in BPF maps `some_nodes` and in globals emitted into BPF data sections. It also manipulates verifier-tracked kernel object references or kptr ownership, so every acquire/exchange/drop path is part of the state contract.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: expected verifier strings are intentionally brittle across verifier diagnostic wording changes; reference/kptr ownership mistakes can leak references or allow use-after-drop patterns.

Test signals: libbpf verifier annotations __failure; expected verifier diagnostics such as `invalid kptr access, R2 type=ptr_node_data2 expected=ptr_node_data, R1 must have zero offset when passed to release func`; successful attachment/execution of tc:stash_rb_nodes, tc:drop_rb_node_off; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/local_kptr_stash_fail.c -->
