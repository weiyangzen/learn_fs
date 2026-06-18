<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/map_percpu_stats.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/map_percpu_stats.c

Purpose: BPF map iterator program that emits per-map element-count statistics with `bpf_map_sum_elem_count`. The file has 25 source lines and 528 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `iter/bpf_map:dump_bpf_map`. Local functions/subprograms: `dump_bpf_map`. Maps: `none declared in this file`. Types: `none declared in this file`. BPF helpers/kfuncs/macros used as calls: `bpf_map_sum_elem_count`. Verifier messages asserted here: `none declared in this file`.

Control flow: Entry points are BPF programs in `iter/bpf_map:dump_bpf_map`. Control flow is centered on the body returns compact success/failure signals to the libbpf selftest harness.

State and persistence: There is no long-lived userspace-visible storage beyond BPF global/data variables and verifier-observed stack state.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: the main risk is drift between this BPF object and the user-space selftest expectations that load it.

Test signals: successful attachment/execution of iter/bpf_map:dump_bpf_map; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/map_percpu_stats.c -->
