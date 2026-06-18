<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/kprobe_multi_empty.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/kprobe_multi_empty.c

Purpose: Empty-pattern kprobe.multi object used by user-space tests to validate attach rejection/edge behavior. The file has 13 source lines and 238 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `kprobe.multi/:test_kprobe_empty`. Local functions/subprograms: `test_kprobe_empty`. Maps: `none declared in this file`. Types: `none declared in this file`. BPF helpers/kfuncs/macros used as calls: `none declared in this file`. Verifier messages asserted here: `none declared in this file`.

Control flow: Entry points are BPF programs in `kprobe.multi/:test_kprobe_empty`. Control flow is centered on the body returns compact success/failure signals to the libbpf selftest harness.

State and persistence: There is no long-lived userspace-visible storage beyond BPF global/data variables and verifier-observed stack state.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros; kprobe/fentry/fexit tracing support and stable test symbols. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: symbol names and attachment capabilities can vary with kernel config and inlining.

Test signals: successful attachment/execution of kprobe.multi/:test_kprobe_empty; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/kprobe_multi_empty.c -->
