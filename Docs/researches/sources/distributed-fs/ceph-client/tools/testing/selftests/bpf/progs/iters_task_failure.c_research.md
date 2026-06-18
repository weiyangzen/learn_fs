<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/iters_task_failure.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/iters_task_failure.c

Purpose: Negative verifier cases for task/css/css-task iterators used without required RCU protection or in disallowed program types. The file has 106 source lines and 2577 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `none declared in this file`. Local functions/subprograms: `bpf_cgroup_release, bpf_rcu_read_lock, bpf_rcu_read_unlock, BPF_PROG, BPF_PROG, BPF_PROG, BPF_PROG, BPF_PROG`. Maps: `none declared in this file`. Types: `cgroup`. BPF helpers/kfuncs/macros used as calls: `bpf_cgroup_from_id, bpf_cgroup_release, bpf_for_each, bpf_get_current_cgroup_id, bpf_rcu_read_lock, bpf_rcu_read_unlock`. Verifier messages asserted here: `kernel func bpf_iter_task_new requires RCU critical section protection, kernel func bpf_iter_css_new requires RCU critical section protection, expected an RCU CS when using bpf_iter_task_next, expected an RCU CS when using bpf_iter_css_next, css_task_iter is only allowed in bpf_lsm, bpf_iter and sleepable progs`.

Control flow: This file is consumed as a header or object fragment rather than defining a complete attached program section. Control flow is centered on iterator helpers drive bounded or verifier-modeled loops; annotated negative cases assert exact verifier diagnostics.

State and persistence: There is no long-lived userspace-visible storage beyond BPF global/data variables and verifier-observed stack state. Open-coded iterator state is stack-resident and must be initialized, advanced, and destroyed in verifier-approved order.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: expected verifier strings are intentionally brittle across verifier diagnostic wording changes; iterator lifetime and stack-state precision must stay synchronized with verifier semantics.

Test signals: libbpf verifier annotations __failure; expected verifier diagnostics such as `kernel func bpf_iter_task_new requires RCU critical section protection, kernel func bpf_iter_css_new requires RCU critical section protection, expected an RCU CS when using bpf_iter_task_next, expected an RCU CS when using bpf_iter_css_next; plus 1 more`; compilation and successful linking into companion BPF objects; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/iters_task_failure.c -->
