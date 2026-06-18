<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/mmap_inner_array.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/mmap_inner_array.c

Purpose: Map-in-map mmapable inner-array access test for list/map layout constraints. The file has 58 source lines and 1196 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `none declared in this file`. Local functions/subprograms: `add_to_list_in_inner_array`. Maps: `inner_array, outer_map`. Types: `inner_array_type`. BPF helpers/kfuncs/macros used as calls: `bpf_get_current_pid_tgid, bpf_map_lookup_elem`. Verifier messages asserted here: `none declared in this file`.

Control flow: This file is consumed as a header or object fragment rather than defining a complete attached program section. Control flow is centered on map lookups/updates select per-test storage and branch on NULL results.

State and persistence: Persistent state is held in BPF maps `inner_array, outer_map` and in globals emitted into BPF data sections.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: the main risk is drift between this BPF object and the user-space selftest expectations that load it.

Test signals: compilation and successful linking into companion BPF objects; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/mmap_inner_array.c -->
