<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/local_storage_bench.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/local_storage_bench.c

Purpose: Benchmark helper programs for map-in-map local-storage lookup loops and randomized task-storage access. The file has 105 source lines and 2324 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `none declared in this file`. Local functions/subprograms: `do_lookup, loop, get_local`. Maps: `array_of_local_storage_maps, array_of_hash_maps`. Types: `loop_ctx`. BPF helpers/kfuncs/macros used as calls: `bpf_get_current_task_btf, bpf_get_prandom_u32, bpf_loop, bpf_map_lookup_elem, bpf_task_storage_get`. Verifier messages asserted here: `none declared in this file`.

Control flow: This file is consumed as a header or object fragment rather than defining a complete attached program section. Control flow is centered on map lookups/updates select per-test storage and branch on NULL results.

State and persistence: Persistent state is held in BPF maps `array_of_local_storage_maps, array_of_hash_maps` and in globals emitted into BPF data sections. Local-storage helper calls persist values on kernel objects such as tasks, sockets, inodes, or cgroups until explicit delete or object teardown.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros; BPF local storage map helpers. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: the main risk is drift between this BPF object and the user-space selftest expectations that load it.

Test signals: compilation and successful linking into companion BPF objects; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/local_storage_bench.c -->
