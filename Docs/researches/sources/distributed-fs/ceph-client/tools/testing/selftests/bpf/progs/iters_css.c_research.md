<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/iters_css.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/iters_css.c

Purpose: Sleepable BPF iterator program that walks cgroup subsystems under RCU and validates css/cgroup iterator lifetime handling. The file has 76 source lines and 1921 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `none declared in this file`. Local functions/subprograms: `bpf_cgroup_release, bpf_rcu_read_lock, bpf_rcu_read_unlock, iter_css_for_each`. Maps: `none declared in this file`. Types: `cgroup`. BPF helpers/kfuncs/macros used as calls: `bpf_cgroup_from_id, bpf_cgroup_release, bpf_for_each, bpf_get_current_task_btf, bpf_rcu_read_lock, bpf_rcu_read_unlock`. Verifier messages asserted here: `none declared in this file`.

Control flow: This file is consumed as a header or object fragment rather than defining a complete attached program section. Control flow is centered on iterator helpers drive bounded or verifier-modeled loops.

State and persistence: There is no long-lived userspace-visible storage beyond BPF global/data variables and verifier-observed stack state. Open-coded iterator state is stack-resident and must be initialized, advanced, and destroyed in verifier-approved order.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: iterator lifetime and stack-state precision must stay synchronized with verifier semantics.

Test signals: compilation and successful linking into companion BPF objects; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/iters_css.c -->
