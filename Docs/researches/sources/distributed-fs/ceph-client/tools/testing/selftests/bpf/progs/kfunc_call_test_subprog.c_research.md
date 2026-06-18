<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/kfunc_call_test_subprog.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/kfunc_call_test_subprog.c

Purpose: Subprogram kfunc-call test that mixes socket context conversion, per-CPU ksym lookup, and test kfunc calls. The file has 38 source lines and 758 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `tc:kfunc_call_test1`. Local functions/subprograms: `kfunc_call_test1`. Maps: `none declared in this file`. Types: `none declared in this file`. BPF helpers/kfuncs/macros used as calls: `bpf_get_smp_processor_id, bpf_kfunc_call_test1, bpf_kfunc_call_test3, bpf_per_cpu_ptr, bpf_sk_fullsock`. Verifier messages asserted here: `none declared in this file`.

Control flow: Entry points are BPF programs in `tc:kfunc_call_test1`. Control flow is centered on test kfunc calls validate argument typing, reference ownership, and module resolution.

State and persistence: There is no long-lived userspace-visible storage beyond BPF global/data variables and verifier-observed stack state.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros; extern kfunc/ksym declarations: const int bpf_prog_active __ksym. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: the main risk is drift between this BPF object and the user-space selftest expectations that load it.

Test signals: successful attachment/execution of tc:kfunc_call_test1; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/kfunc_call_test_subprog.c -->
