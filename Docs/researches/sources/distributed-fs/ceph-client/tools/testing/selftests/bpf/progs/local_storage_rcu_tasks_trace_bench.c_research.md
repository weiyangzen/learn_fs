<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/local_storage_rcu_tasks_trace_bench.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/local_storage_rcu_tasks_trace_bench.c

Purpose: RCU Tasks Trace benchmark probes that create/delete task local storage and timestamp grace-period phases. The file has 68 source lines and 1424 bytes, so it is a small-to-medium BPF selftest artifact rather than production Ceph client runtime code.

Important APIs, types, and functions: BPF sections: `fentry/rcu_tasks_trace_pregp_step:pregp_step, fentry/rcu_tasks_trace_postgp:postgp`. Local functions/subprograms: `get_local, pregp_step, postgp`. Maps: `task_storage`. Types: `none declared in this file`. BPF helpers/kfuncs/macros used as calls: `bpf_get_current_task_btf, bpf_ktime_get_ns, bpf_task_storage_delete, bpf_task_storage_get`. Verifier messages asserted here: `none declared in this file`.

Control flow: Entry points are BPF programs in `fentry/rcu_tasks_trace_pregp_step:pregp_step, fentry/rcu_tasks_trace_postgp:postgp`. Control flow is centered on the body returns compact success/failure signals to the libbpf selftest harness.

State and persistence: Persistent state is held in BPF maps `task_storage` and in globals emitted into BPF data sections. Local-storage helper calls persist values on kernel objects such as tasks, sockets, inodes, or cgroups until explicit delete or object teardown.

Dependencies and integration points: Depends on Linux BPF selftests infrastructure; `vmlinux.h`/BTF type information; `bpf_helpers.h`/`bpf_tracing.h` macros; BPF local storage map helpers. It integrates with `tools/testing/selftests/bpf` user-space tests through section names, global variables, maps, expected verifier annotations, and generated BPF skeletons.

Risks: symbol names and attachment capabilities can vary with kernel config and inlining.

Test signals: successful attachment/execution of fentry/rcu_tasks_trace_pregp_step:pregp_step, fentry/rcu_tasks_trace_postgp:postgp; skeleton/selftest assertions over maps, return values, counters, or perf output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/local_storage_rcu_tasks_trace_bench.c -->
