<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/map_in_map_btf.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/map_in_map_btf.c

Purpose: Map-in-map BTF test that pushes allocated list nodes into an inner array map protected by spin lock. The file has 74 source lines and 1453 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `none declared in this file`. Local functions/subprograms: `add_to_list_in_inner_array`. Maps: `inner_array, outer_array`. Types: `node_data, map_value, inner_array_type`. BPF helpers/kfuncs/macros used as calls: `bpf_get_current_pid_tgid, bpf_list_push_back, bpf_map_lookup_elem, bpf_obj_new, bpf_spin_lock, bpf_spin_unlock`. Verifier messages asserted here: `none declared in this file`.

Control flow: This file is consumed as a header or object fragment rather than defining a complete attached program section. Control flow is centered on map lookups/updates select per-test storage and branch on NULL results; critical sections protect intrusive container or resource-spin-lock state.

State and persistence: Persistent state is held in BPF maps `inner_array, outer_array` and in globals emitted into BPF data sections. It also manipulates verifier-tracked kernel object references or kptr ownership, so every acquire/exchange/drop path is part of the state contract.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: reference/kptr ownership mistakes can leak references or allow use-after-drop patterns.

Test signals: compilation and successful linking into companion BPF objects; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/map_in_map_btf.c -->
