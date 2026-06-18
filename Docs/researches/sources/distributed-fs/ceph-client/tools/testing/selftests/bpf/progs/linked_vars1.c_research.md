<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/linked_vars1.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/linked_vars1.c

Purpose: Cross-object global variable and weak kconfig/ksym resolution test. The file has 55 source lines and 1382 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `raw_tp/sys_enter:BPF_PROG`. Local functions/subprograms: `BPF_PROG`. Maps: `none declared in this file`. Types: `none declared in this file`. BPF helpers/kfuncs/macros used as calls: `none declared in this file`. Verifier messages asserted here: `none declared in this file`.

Control flow: Entry points are BPF programs in `raw_tp/sys_enter:BPF_PROG`. Control flow is centered on the body returns compact success/failure signals to the libbpf selftest harness.

State and persistence: There is no long-lived userspace-visible storage beyond BPF global/data variables and verifier-observed stack state.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros; extern kfunc/ksym declarations: int LINUX_KERNEL_VERSION __kconfig, bool CONFIG_BPF_SYSCALL __kconfig __weak, const void bpf_link_fops __ksym __weak, int input_bss2, int input_data2, const int input_rodata2. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: the main risk is drift between this BPF object and the user-space selftest expectations that load it.

Test signals: successful attachment/execution of raw_tp/sys_enter:BPF_PROG; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/linked_vars1.c -->
