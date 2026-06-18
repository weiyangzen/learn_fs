<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/kfunc_module_order.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/kfunc_module_order.c

Purpose: Classifier programs that call kfuncs from differently ordered test modules to validate module kfunc resolution. The file has 31 source lines and 618 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `classifier:call_kfunc_xy, classifier:call_kfunc_yx`. Local functions/subprograms: `call_kfunc_xy, call_kfunc_yx`. Maps: `none declared in this file`. Types: `none declared in this file`. BPF helpers/kfuncs/macros used as calls: `bpf_test_modorder_retx, bpf_test_modorder_rety`. Verifier messages asserted here: `none declared in this file`.

Control flow: Entry points are BPF programs in `classifier:call_kfunc_xy, classifier:call_kfunc_yx`. Control flow is centered on the body returns compact success/failure signals to the libbpf selftest harness.

State and persistence: There is no long-lived userspace-visible storage beyond BPF global/data variables and verifier-observed stack state.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros; extern kfunc/ksym declarations: int bpf_test_modorder_retx(void) __ksym, int bpf_test_modorder_rety(void) __ksym. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: the main risk is drift between this BPF object and the user-space selftest expectations that load it.

Test signals: successful attachment/execution of classifier:call_kfunc_xy, classifier:call_kfunc_yx; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/kfunc_module_order.c -->
