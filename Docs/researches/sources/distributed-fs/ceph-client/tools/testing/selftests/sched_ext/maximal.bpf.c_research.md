<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/sched_ext/maximal.bpf.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/sched_ext/maximal.bpf.c

## Purpose

BPF sched_ext scheduler fixture that load/attach smoke test for a scheduler defining every sched_ext callback.

## Important APIs, Types, and Functions

Uses scx/common.bpf.h, sched_ext struct_ops, maximal_select_cpu, maximal_enqueue, maximal_dequeue, maximal_dispatch, maximal_runnable, maximal_running, maximal_stopping, maximal_quiescent, maximal_yield, maximal_core_sched_before, maximal_set_weight, maximal_set_cpumask, maximal_update_idle, maximal_cpu_online, maximal_cpu_offline, maximal_init_task, maximal_enable, maximal_exit_task, maximal_disable, maximal_cgroup_init, maximal_cgroup_exit, maximal_cgroup_prep_move, maximal_cgroup_move, maximal_cgroup_cancel_move, maximal_cgroup_set_weight, maximal_cgroup_set_bandwidth, maximal_init, maximal_exit, sections license, tp_btf/sched_switch, .struct_ops.link, and BPF helpers/kfuncs visible in the source.

## Control Flow and Integration

BPF defines select, enqueue, dequeue, dispatch, runnable/running/stopping/quiescent, yield, core scheduling, weight/cpumask, idle, hotplug, task, cgroup, init, exit, plus a sched_switch tracing program. The struct sched_ext_ops instance exposes the callbacks to the kernel when userspace attaches the generated skeleton.

## State and Persistence Behavior

State is held in BPF global variables, BPF maps, task storage, UEI exit records, or rodata parameters depending on the test. It is reset when the skeleton is destroyed and does not persist outside the BPF object.

## Dependencies and Integration Points

Depends on sched_ext kernel support, BPF syscall, BTF/vmlinux.h, libbpf skeleton generation, and the paired userspace testcase in the same directory.

## Risks and Edge Cases

Many failures are intentional verifier or scheduler exits; the paired C test must distinguish expected SCX_EXIT_ERROR or load failure from regressions. Host-wide sched_ext attachment means tests must run serially.

## Test Signals

The paired userspace test loads this skeleton, attaches the struct_ops map or expects load failure, then inspects UEI/counters or child process outcomes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/sched_ext/maximal.bpf.c -->
