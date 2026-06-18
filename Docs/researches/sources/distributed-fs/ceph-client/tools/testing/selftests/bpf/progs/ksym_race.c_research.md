<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/ksym_race.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/ksym_race.c

Purpose: Per-CPU ksym access race reproducer using a test-module percpu symbol and `bpf_this_cpu_ptr`. The file has 14 source lines and 283 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `tc:ksym_fail`. Local functions/subprograms: `ksym_fail`. Maps: `none declared in this file`. Types: `none declared in this file`. BPF helpers/kfuncs/macros used as calls: `bpf_this_cpu_ptr`. Verifier messages asserted here: `none declared in this file`.

Control flow: Entry points are BPF programs in `tc:ksym_fail`. Control flow is centered on the body returns compact success/failure signals to the libbpf selftest harness.

State and persistence: There is no long-lived userspace-visible storage beyond BPF global/data variables and verifier-observed stack state.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros; extern kfunc/ksym declarations: int bpf_testmod_ksym_percpu __ksym. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: the main risk is drift between this BPF object and the user-space selftest expectations that load it.

Test signals: successful attachment/execution of tc:ksym_fail; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/ksym_race.c -->
