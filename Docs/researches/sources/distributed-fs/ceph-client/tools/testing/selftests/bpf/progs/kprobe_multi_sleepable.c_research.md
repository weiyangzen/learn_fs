<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/kprobe_multi_sleepable.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/kprobe_multi_sleepable.c

Purpose: Sleepable kprobe.multi test proving sleepable helpers are accepted only on sleepable attachments. The file has 26 source lines and 422 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `kprobe.multi:handle_kprobe_multi_sleepable, fentry/bpf_fentry_test1:BPF_PROG`. Local functions/subprograms: `handle_kprobe_multi_sleepable, BPF_PROG`. Maps: `none declared in this file`. Types: `none declared in this file`. BPF helpers/kfuncs/macros used as calls: `bpf_copy_from_user`. Verifier messages asserted here: `none declared in this file`.

Control flow: Entry points are BPF programs in `kprobe.multi:handle_kprobe_multi_sleepable, fentry/bpf_fentry_test1:BPF_PROG`. Control flow is centered on helper-mediated memory reads avoid direct unsafe kernel/user access.

State and persistence: There is no long-lived userspace-visible storage beyond BPF global/data variables and verifier-observed stack state.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros; kprobe/fentry/fexit tracing support and stable test symbols. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: memory access tests are sensitive to BTF type layout and helper sleepability rules; symbol names and attachment capabilities can vary with kernel config and inlining.

Test signals: successful attachment/execution of kprobe.multi:handle_kprobe_multi_sleepable, fentry/bpf_fentry_test1:BPF_PROG; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/kprobe_multi_sleepable.c -->
