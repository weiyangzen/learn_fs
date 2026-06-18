<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/missed_kprobe_recursion.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/missed_kprobe_recursion.c

Purpose: Recursion/missed-probe test across kprobe.multi, kprobe.session, and regular kprobe attachments. The file has 55 source lines and 906 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `fentry/bpf_modify_return_test:BPF_PROG, kprobe.multi/bpf_fentry_test1:test1, kprobe/bpf_kfunc_common_test:test2, kprobe/bpf_kfunc_common_test:test3, kprobe/bpf_kfunc_common_test:test4, kprobe.multi/bpf_kfunc_common_test:test5, kprobe.session/bpf_kfunc_common_test:test6`. Local functions/subprograms: `BPF_PROG, test1, test2, test3, test4, test5, test6`. Maps: `none declared in this file`. Types: `none declared in this file`. BPF helpers/kfuncs/macros used as calls: `bpf_kfunc_common_test`. Verifier messages asserted here: `none declared in this file`.

Control flow: Entry points are BPF programs in `fentry/bpf_modify_return_test:BPF_PROG, kprobe.multi/bpf_fentry_test1:test1, kprobe/bpf_kfunc_common_test:test2, kprobe/bpf_kfunc_common_test:test3, kprobe/bpf_kfunc_common_test:test4, kprobe.multi/bpf_kfunc_common_test:test5, kprobe.session/bpf_kfunc_common_test:test6`. Control flow is centered on test kfunc calls validate argument typing, reference ownership, and module resolution.

State and persistence: There is no long-lived userspace-visible storage beyond BPF global/data variables and verifier-observed stack state.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros; kprobe/fentry/fexit tracing support and stable test symbols. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: symbol names and attachment capabilities can vary with kernel config and inlining.

Test signals: successful attachment/execution of fentry/bpf_modify_return_test:BPF_PROG, kprobe.multi/bpf_fentry_test1:test1, kprobe/bpf_kfunc_common_test:test2, kprobe/bpf_kfunc_common_test:test3, kprobe/bpf_kfunc_common_test:test4, kprobe.multi/bpf_kfunc_common_test:test5; plus 1 more; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/missed_kprobe_recursion.c -->
