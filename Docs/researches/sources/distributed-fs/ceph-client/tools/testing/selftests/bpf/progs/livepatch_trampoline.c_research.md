<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/livepatch_trampoline.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/livepatch_trampoline.c

Purpose: Fentry/fexit trampoline attachment smoke test for a function that can be affected by livepatch-style trampolines. The file has 31 source lines and 537 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `fentry/cmdline_proc_show:BPF_PROG, fexit/cmdline_proc_show:BPF_PROG`. Local functions/subprograms: `BPF_PROG, BPF_PROG`. Maps: `none declared in this file`. Types: `none declared in this file`. BPF helpers/kfuncs/macros used as calls: `bpf_get_current_pid_tgid`. Verifier messages asserted here: `none declared in this file`.

Control flow: Entry points are BPF programs in `fentry/cmdline_proc_show:BPF_PROG, fexit/cmdline_proc_show:BPF_PROG`. Control flow is centered on the body returns compact success/failure signals to the libbpf selftest harness.

State and persistence: There is no long-lived userspace-visible storage beyond BPF global/data variables and verifier-observed stack state.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros; kprobe/fentry/fexit tracing support and stable test symbols. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: symbol names and attachment capabilities can vary with kernel config and inlining.

Test signals: successful attachment/execution of fentry/cmdline_proc_show:BPF_PROG, fexit/cmdline_proc_show:BPF_PROG; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/livepatch_trampoline.c -->
