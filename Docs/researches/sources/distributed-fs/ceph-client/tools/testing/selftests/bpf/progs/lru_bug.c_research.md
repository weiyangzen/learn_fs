<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/lru_bug.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/lru_bug.c

Purpose: LRU hash map regression program that updates/deletes across fentry hooks while tracking current task identity. The file has 50 source lines and 1007 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `fentry/bpf_ktime_get_ns:printk, fentry/do_nanosleep:nanosleep`. Local functions/subprograms: `printk, nanosleep`. Maps: `lru_map`. Types: `map_value`. BPF helpers/kfuncs/macros used as calls: `bpf_get_current_task_btf, bpf_ktime_get_ns, bpf_map_delete_elem, bpf_map_lookup_elem, bpf_map_update_elem`. Verifier messages asserted here: `none declared in this file`.

Control flow: Entry points are BPF programs in `fentry/bpf_ktime_get_ns:printk, fentry/do_nanosleep:nanosleep`. Control flow is centered on map lookups/updates select per-test storage and branch on NULL results.

State and persistence: Persistent state is held in BPF maps `lru_map` and in globals emitted into BPF data sections.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: symbol names and attachment capabilities can vary with kernel config and inlining.

Test signals: successful attachment/execution of fentry/bpf_ktime_get_ns:printk, fentry/do_nanosleep:nanosleep; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/lru_bug.c -->
