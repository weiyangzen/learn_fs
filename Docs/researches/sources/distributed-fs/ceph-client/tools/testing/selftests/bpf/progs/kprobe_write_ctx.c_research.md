<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/kprobe_write_ctx.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/kprobe_write_ctx.c

Purpose: Verifier tests around writing kprobe and kprobe.multi context memory, including freplace/fentry combinations. The file has 42 source lines and 607 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `kprobe:kprobe_write_ctx, kprobe.multi:kprobe_multi_write_ctx, ?kprobe:kprobe_dummy, ?freplace:freplace_kprobe, ?fentry/bpf_fentry_test1:BPF_PROG`. Local functions/subprograms: `kprobe_write_ctx, kprobe_multi_write_ctx, kprobe_dummy, freplace_kprobe, BPF_PROG`. Maps: `none declared in this file`. Types: `none declared in this file`. BPF helpers/kfuncs/macros used as calls: `none declared in this file`. Verifier messages asserted here: `none declared in this file`.

Control flow: Entry points are BPF programs in `kprobe:kprobe_write_ctx, kprobe.multi:kprobe_multi_write_ctx, ?kprobe:kprobe_dummy, ?freplace:freplace_kprobe, ?fentry/bpf_fentry_test1:BPF_PROG`. Control flow is centered on the body returns compact success/failure signals to the libbpf selftest harness.

State and persistence: There is no long-lived userspace-visible storage beyond BPF global/data variables and verifier-observed stack state.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros; kprobe/fentry/fexit tracing support and stable test symbols. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: symbol names and attachment capabilities can vary with kernel config and inlining.

Test signals: successful attachment/execution of kprobe:kprobe_write_ctx, kprobe.multi:kprobe_multi_write_ctx, ?kprobe:kprobe_dummy, ?freplace:freplace_kprobe, ?fentry/bpf_fentry_test1:BPF_PROG; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/kprobe_write_ctx.c -->
