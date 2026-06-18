<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/iters_css_task.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/iters_css_task.c

Purpose: LSM and cgroup iterator programs that combine current-task cgroup acquisition with css-task iteration and cgroup iterator output. The file has 103 source lines and 2182 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `lsm/file_mprotect:BPF_PROG, ?iter/cgroup:cgroup_id_printer`. Local functions/subprograms: `bpf_cgroup_release, BPF_PROG, cgroup_id, cgroup_id_printer, BPF_PROG`. Maps: `none declared in this file`. Types: `cgroup, cgroup`. BPF helpers/kfuncs/macros used as calls: `bpf_cgroup_acquire, bpf_cgroup_from_id, bpf_cgroup_release, bpf_for_each, bpf_get_current_cgroup_id, bpf_get_current_task_btf`. Verifier messages asserted here: `none declared in this file`.

Control flow: Entry points are BPF programs in `lsm/file_mprotect:BPF_PROG, ?iter/cgroup:cgroup_id_printer`. Control flow is centered on iterator helpers drive bounded or verifier-modeled loops.

State and persistence: There is no long-lived userspace-visible storage beyond BPF global/data variables and verifier-observed stack state. Open-coded iterator state is stack-resident and must be initialized, advanced, and destroyed in verifier-approved order.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: iterator lifetime and stack-state precision must stay synchronized with verifier semantics.

Test signals: successful attachment/execution of lsm/file_mprotect:BPF_PROG, ?iter/cgroup:cgroup_id_printer; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/iters_css_task.c -->
