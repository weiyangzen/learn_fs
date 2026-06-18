<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/kfunc_implicit_args.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/kfunc_implicit_args.c

Purpose: Tests kfuncs with implicit `struct bpf_prog_aux` arguments and verifies that implementation symbols cannot be called directly. The file has 42 source lines and 1115 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `syscall:test_kfunc_implicit_arg, syscall:test_kfunc_implicit_arg_impl_illegal, syscall:test_kfunc_implicit_arg_legacy, syscall:test_kfunc_implicit_arg_legacy_impl`. Local functions/subprograms: `test_kfunc_implicit_arg, test_kfunc_implicit_arg_impl_illegal, test_kfunc_implicit_arg_legacy, test_kfunc_implicit_arg_legacy_impl`. Maps: `none declared in this file`. Types: `none declared in this file`. BPF helpers/kfuncs/macros used as calls: `bpf_kfunc_implicit_arg, bpf_kfunc_implicit_arg_impl, bpf_kfunc_implicit_arg_legacy, bpf_kfunc_implicit_arg_legacy_impl`. Verifier messages asserted here: `cannot find address for kernel function bpf_kfunc_implicit_arg_impl`.

Control flow: Entry points are BPF programs in `syscall:test_kfunc_implicit_arg, syscall:test_kfunc_implicit_arg_impl_illegal, syscall:test_kfunc_implicit_arg_legacy, syscall:test_kfunc_implicit_arg_legacy_impl`. Control flow is centered on test kfunc calls validate argument typing, reference ownership, and module resolution; annotated negative cases assert exact verifier diagnostics.

State and persistence: There is no long-lived userspace-visible storage beyond BPF global/data variables and verifier-observed stack state.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros; extern kfunc/ksym declarations: int bpf_kfunc_implicit_arg(int a) __weak __ksym, int bpf_kfunc_implicit_arg_impl(int a, struct bpf_prog_aux *aux) __weak __ksym, int bpf_kfunc_implicit_arg_legacy(int a, int b) __weak __ksym, int bpf_kfunc_implicit_arg_legacy_impl(int a, int b, struct bpf_prog_aux *aux) __weak __ksym. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: expected verifier strings are intentionally brittle across verifier diagnostic wording changes.

Test signals: libbpf verifier annotations __failure, __retval(11), __retval(5), __retval(7); expected verifier diagnostics such as `cannot find address for kernel function bpf_kfunc_implicit_arg_impl`; successful attachment/execution of syscall:test_kfunc_implicit_arg, syscall:test_kfunc_implicit_arg_impl_illegal, syscall:test_kfunc_implicit_arg_legacy, syscall:test_kfunc_implicit_arg_legacy_impl; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/kfunc_implicit_args.c -->
