<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/loop2.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/loop2.c

Purpose: While-true loop verifier test with an explicit internal break bound. The file has 25 source lines and 395 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `raw_tracepoint/consume_skb:while_true`. Local functions/subprograms: `while_true`. Maps: `none declared in this file`. Types: `none declared in this file`. BPF helpers/kfuncs/macros used as calls: `none declared in this file`. Verifier messages asserted here: `none declared in this file`.

Control flow: Entry points are BPF programs in `raw_tracepoint/consume_skb:while_true`. Control flow is centered on the body returns compact success/failure signals to the libbpf selftest harness.

State and persistence: There is no long-lived userspace-visible storage beyond BPF global/data variables and verifier-observed stack state.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: the main risk is drift between this BPF object and the user-space selftest expectations that load it.

Test signals: successful attachment/execution of raw_tracepoint/consume_skb:while_true; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/loop2.c -->
