<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/linked_funcs1.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/linked_funcs1.c

Purpose: One half of a linked-object test where subprograms and kfunc-like helpers reference functions defined in another object. The file has 98 source lines and 2581 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `?raw_tp/sys_enter:BPF_PROG`. Local functions/subprograms: `set_output_val1, set_output_ctx1, BPF_PROG, kfunc_gen1`. Maps: `none declared in this file`. Types: `none declared in this file`. BPF helpers/kfuncs/macros used as calls: `bpf_cast_to_kern_ctx, bpf_core_type_size, bpf_get_current_pid_tgid`. Verifier messages asserted here: `none declared in this file`.

Control flow: Entry points are BPF programs in `?raw_tp/sys_enter:BPF_PROG`. Control flow is centered on the body returns compact success/failure signals to the libbpf selftest harness.

State and persistence: There is no long-lived userspace-visible storage beyond BPF global/data variables and verifier-observed stack state.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros; extern kfunc/ksym declarations: int set_output_val2(int x). It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: the main risk is drift between this BPF object and the user-space selftest expectations that load it.

Test signals: successful attachment/execution of ?raw_tp/sys_enter:BPF_PROG; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/linked_funcs1.c -->
