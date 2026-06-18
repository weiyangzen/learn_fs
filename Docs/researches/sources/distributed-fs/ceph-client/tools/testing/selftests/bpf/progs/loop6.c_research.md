<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/loop6.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/loop6.c

Purpose: Kprobe program that reads virtqueue scatter-gather arguments with bounded loops and kernel memory reads. The file has 96 source lines and 2110 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `kprobe/virtqueue_add_sgs:BPF_KPROBE`. Local functions/subprograms: `BPF_KPROBE`. Maps: `none declared in this file`. Types: `none declared in this file`. BPF helpers/kfuncs/macros used as calls: `bpf_probe_read_kernel`. Verifier messages asserted here: `none declared in this file`.

Control flow: Entry points are BPF programs in `kprobe/virtqueue_add_sgs:BPF_KPROBE`. Control flow is centered on helper-mediated memory reads avoid direct unsafe kernel/user access.

State and persistence: There is no long-lived userspace-visible storage beyond BPF global/data variables and verifier-observed stack state.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: memory access tests are sensitive to BTF type layout and helper sleepability rules.

Test signals: successful attachment/execution of kprobe/virtqueue_add_sgs:BPF_KPROBE; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/loop6.c -->
