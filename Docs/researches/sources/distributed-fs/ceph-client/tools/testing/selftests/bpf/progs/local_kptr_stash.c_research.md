<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/local_kptr_stash.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/local_kptr_stash.c

Purpose: Positive local kptr stash tests for rb-tree nodes, local roots, refcounted nodes, and map-stored kptr exchange. The file has 286 source lines and 5686 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `tc:stash_rb_nodes, tc:stash_plain, tc:stash_local_with_root, tc:unstash_rb_node, tc:stash_test_ref_kfunc, tc:refcount_acquire_without_unstash, tc:stash_refcounted_node`. Local functions/subprograms: `less, create_and_stash, stash_rb_nodes, stash_plain, stash_local_with_root, unstash_rb_node, stash_test_ref_kfunc, refcount_acquire_without_unstash, stash_refcounted_node`. Maps: `refcounted_node_stash, some_nodes`. Types: `plain_local, node_data, refcounted_node, stash, plain_local, local_with_root, map_value, node_data, refcounted_node`. BPF helpers/kfuncs/macros used as calls: `bpf_kfunc_call_test_release, bpf_kptr_xchg, bpf_map_lookup_elem, bpf_obj_drop, bpf_obj_new, bpf_rbtree_add, bpf_refcount_acquire, bpf_spin_lock, bpf_spin_unlock`. Verifier messages asserted here: `none declared in this file`.

Control flow: Entry points are BPF programs in `tc:stash_rb_nodes, tc:stash_plain, tc:stash_local_with_root, tc:unstash_rb_node, tc:stash_test_ref_kfunc, tc:refcount_acquire_without_unstash, tc:stash_refcounted_node`. Control flow is centered on map lookups/updates select per-test storage and branch on NULL results; test kfunc calls validate argument typing, reference ownership, and module resolution; critical sections protect intrusive container or resource-spin-lock state.

State and persistence: Persistent state is held in BPF maps `refcounted_node_stash, some_nodes` and in globals emitted into BPF data sections. It also manipulates verifier-tracked kernel object references or kptr ownership, so every acquire/exchange/drop path is part of the state contract.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: reference/kptr ownership mistakes can leak references or allow use-after-drop patterns.

Test signals: successful attachment/execution of tc:stash_rb_nodes, tc:stash_plain, tc:stash_local_with_root, tc:unstash_rb_node, tc:stash_test_ref_kfunc, tc:refcount_acquire_without_unstash; plus 1 more; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/local_kptr_stash.c -->
