<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/kmem_cache_iter.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/kmem_cache_iter.c

Purpose: Iterator and open-coded iterator programs for kmem_cache discovery, name matching, and map-based result collection. The file has 109 source lines and 2315 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `iter/kmem_cache:slab_info_collector, raw_tp/bpf_test_finish:BPF_PROG, syscall:open_coded_iter`. Local functions/subprograms: `slab_info_collector, BPF_PROG, open_coded_iter`. Maps: `slab_hash, slab_result`. Types: `kmem_cache_result`. BPF helpers/kfuncs/macros used as calls: `bpf_for_each, bpf_get_current_task, bpf_get_kmem_cache, bpf_map_lookup_elem, bpf_map_update_elem, bpf_probe_read_kernel_str, bpf_strncmp`. Verifier messages asserted here: `none declared in this file`.

Control flow: Entry points are BPF programs in `iter/kmem_cache:slab_info_collector, raw_tp/bpf_test_finish:BPF_PROG, syscall:open_coded_iter`. Control flow is centered on iterator helpers drive bounded or verifier-modeled loops; map lookups/updates select per-test storage and branch on NULL results.

State and persistence: Persistent state is held in BPF maps `slab_hash, slab_result` and in globals emitted into BPF data sections. Open-coded iterator state is stack-resident and must be initialized, advanced, and destroyed in verifier-approved order.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros; extern kfunc/ksym declarations: struct kmem_cache *bpf_get_kmem_cache(u64 addr) __ksym. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: iterator lifetime and stack-state precision must stay synchronized with verifier semantics.

Test signals: successful attachment/execution of iter/kmem_cache:slab_info_collector, raw_tp/bpf_test_finish:BPF_PROG, syscall:open_coded_iter; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/kmem_cache_iter.c -->
