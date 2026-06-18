<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/linked_maps2.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/linked_maps2.c

Purpose: Companion map-linking object that supplies/uses maps across linked BPF objects. The file has 77 source lines and 1735 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `raw_tp/sys_enter:BPF_PROG, raw_tp/sys_exit:BPF_PROG`. Local functions/subprograms: `BPF_PROG, BPF_PROG`. Maps: `map1, map2`. Types: `none declared in this file`. BPF helpers/kfuncs/macros used as calls: `bpf_map_lookup_elem, bpf_map_update_elem`. Verifier messages asserted here: `none declared in this file`.

Control flow: Entry points are BPF programs in `raw_tp/sys_enter:BPF_PROG, raw_tp/sys_exit:BPF_PROG`. Control flow is centered on map lookups/updates select per-test storage and branch on NULL results.

State and persistence: Persistent state is held in BPF maps `map1, map2` and in globals emitted into BPF data sections.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros; extern kfunc/ksym declarations: struct {
	__uint(max_entries, 16). It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: the main risk is drift between this BPF object and the user-space selftest expectations that load it.

Test signals: successful attachment/execution of raw_tp/sys_enter:BPF_PROG, raw_tp/sys_exit:BPF_PROG; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/linked_maps2.c -->
