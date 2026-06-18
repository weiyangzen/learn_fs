<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/missed_tp_recursion.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/missed_tp_recursion.c

Purpose: Tracepoint recursion test that combines fentry, kprobe, and tracepoint printk hooks. The file has 42 source lines and 673 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `fentry/bpf_modify_return_test:BPF_PROG, kprobe/bpf_fentry_test1:test1, tp/bpf_trace/bpf_trace_printk:test2, tp/bpf_trace/bpf_trace_printk:test3, tp/bpf_trace/bpf_trace_printk:test4`. Local functions/subprograms: `BPF_PROG, test1, test2, test3, test4`. Maps: `none declared in this file`. Types: `none declared in this file`. BPF helpers/kfuncs/macros used as calls: `bpf_printk`. Verifier messages asserted here: `none declared in this file`.

Control flow: Entry points are BPF programs in `fentry/bpf_modify_return_test:BPF_PROG, kprobe/bpf_fentry_test1:test1, tp/bpf_trace/bpf_trace_printk:test2, tp/bpf_trace/bpf_trace_printk:test3, tp/bpf_trace/bpf_trace_printk:test4`. Control flow is centered on the body returns compact success/failure signals to the libbpf selftest harness.

State and persistence: There is no long-lived userspace-visible storage beyond BPF global/data variables and verifier-observed stack state.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros; kprobe/fentry/fexit tracing support and stable test symbols. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: symbol names and attachment capabilities can vary with kernel config and inlining.

Test signals: successful attachment/execution of fentry/bpf_modify_return_test:BPF_PROG, kprobe/bpf_fentry_test1:test1, tp/bpf_trace/bpf_trace_printk:test2, tp/bpf_trace/bpf_trace_printk:test3, tp/bpf_trace/bpf_trace_printk:test4; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/missed_tp_recursion.c -->
