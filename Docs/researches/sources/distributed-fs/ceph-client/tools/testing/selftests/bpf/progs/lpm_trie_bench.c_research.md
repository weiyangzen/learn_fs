<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/lpm_trie_bench.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/lpm_trie_bench.c

Purpose: LPM trie benchmark program measuring lookup/insert/update/delete loop costs and deferred map-free timing. The file has 231 source lines and 4565 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `fentry/bpf_map_free_deferred:BPF_PROG, fexit/bpf_map_free_deferred:BPF_PROG, xdp:BPF_PROG`. Local functions/subprograms: `BPF_PROG, BPF_PROG, generate_key, noop, baseline, lookup, insert, update, delete, BPF_PROG`. Maps: `trie_map`. Types: `none declared in this file`. BPF helpers/kfuncs/macros used as calls: `bpf_get_prandom_u32, bpf_ktime_get_ns, bpf_loop, bpf_map_delete_elem, bpf_map_lookup_elem, bpf_map_update_elem, bpf_printk, bpf_strncmp`. Verifier messages asserted here: `none declared in this file`.

Control flow: Entry points are BPF programs in `fentry/bpf_map_free_deferred:BPF_PROG, fexit/bpf_map_free_deferred:BPF_PROG, xdp:BPF_PROG`. Control flow is centered on map lookups/updates select per-test storage and branch on NULL results.

State and persistence: Persistent state is held in BPF maps `trie_map` and in globals emitted into BPF data sections.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros; LPM trie map implementation. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: symbol names and attachment capabilities can vary with kernel config and inlining.

Test signals: successful attachment/execution of fentry/bpf_map_free_deferred:BPF_PROG, fexit/bpf_map_free_deferred:BPF_PROG, xdp:BPF_PROG; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/lpm_trie_bench.c -->
