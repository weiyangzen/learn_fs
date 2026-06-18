<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/kprobe_multi_session.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/kprobe_multi_session.c

Purpose: Kprobe session tests that distinguish entry/return phases and verify function IP matching across wildcard and symbol attaches. The file has 89 source lines and 1986 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `fentry/bpf_modify_return_test:BPF_PROG, kprobe.session/bpf_fentry_test*:test_kprobe, kprobe.session/bpf_fentry_test1:test_kprobe_syms`. Local functions/subprograms: `session_check, BPF_PROG, test_kprobe, test_kprobe_syms`. Maps: `none declared in this file`. Types: `none declared in this file`. BPF helpers/kfuncs/macros used as calls: `bpf_get_current_pid_tgid, bpf_get_func_ip, bpf_program__attach_kprobe_multi_opts`. Verifier messages asserted here: `none declared in this file`.

Control flow: Entry points are BPF programs in `fentry/bpf_modify_return_test:BPF_PROG, kprobe.session/bpf_fentry_test*:test_kprobe, kprobe.session/bpf_fentry_test1:test_kprobe_syms`. Control flow is centered on the body returns compact success/failure signals to the libbpf selftest harness.

State and persistence: There is no long-lived userspace-visible storage beyond BPF global/data variables and verifier-observed stack state.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros; extern kfunc/ksym declarations: const void bpf_fentry_test1 __ksym, const void bpf_fentry_test2 __ksym, const void bpf_fentry_test3 __ksym, const void bpf_fentry_test4 __ksym, const void bpf_fentry_test5 __ksym, const void bpf_fentry_test6 __ksym; plus 2 more; kprobe/fentry/fexit tracing support and stable test symbols. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: symbol names and attachment capabilities can vary with kernel config and inlining.

Test signals: successful attachment/execution of fentry/bpf_modify_return_test:BPF_PROG, kprobe.session/bpf_fentry_test*:test_kprobe, kprobe.session/bpf_fentry_test1:test_kprobe_syms; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/kprobe_multi_session.c -->
