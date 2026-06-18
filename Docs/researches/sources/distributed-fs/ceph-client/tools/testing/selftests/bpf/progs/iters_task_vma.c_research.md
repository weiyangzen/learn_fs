<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/iters_task_vma.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/iters_task_vma.c

Purpose: Task VMA iterator smoke test over the current task's VMAs with a deliberately unlikely branch to keep verifier state live. The file has 44 source lines and 828 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `raw_tp/sys_enter:iter_task_vma_for_each`. Local functions/subprograms: `iter_task_vma_for_each`. Maps: `none declared in this file`. Types: `none declared in this file`. BPF helpers/kfuncs/macros used as calls: `bpf_cmp_unlikely, bpf_for_each, bpf_get_current_task_btf`. Verifier messages asserted here: `none declared in this file`.

Control flow: Entry points are BPF programs in `raw_tp/sys_enter:iter_task_vma_for_each`. Control flow is centered on iterator helpers drive bounded or verifier-modeled loops.

State and persistence: There is no long-lived userspace-visible storage beyond BPF global/data variables and verifier-observed stack state. Open-coded iterator state is stack-resident and must be initialized, advanced, and destroyed in verifier-approved order.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: iterator lifetime and stack-state precision must stay synchronized with verifier semantics.

Test signals: successful attachment/execution of raw_tp/sys_enter:iter_task_vma_for_each; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/iters_task_vma.c -->
