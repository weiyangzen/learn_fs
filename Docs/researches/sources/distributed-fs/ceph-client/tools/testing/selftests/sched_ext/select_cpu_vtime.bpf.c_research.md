<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/sched_ext/select_cpu_vtime.bpf.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/sched_ext/select_cpu_vtime.bpf.c

## Purpose

BPF sched_ext scheduler fixture that validates direct-dispatch enqueue flags and vtime ordering from select_cpu.

## Important APIs, Types, and Functions

Uses scx/common.bpf.h, sched_ext struct_ops, select_cpu_vtime_select_cpu, select_cpu_vtime_dispatch, select_cpu_vtime_running, select_cpu_vtime_stopping, select_cpu_vtime_enable, select_cpu_vtime_init, sections license, .struct_ops.link, and BPF helpers/kfuncs visible in the source.

## Control Flow and Integration

BPF implements a tiny vtime scheduler with VTIME_DSQ, vtime_now tracking, task_vtime clamping, vtime insert from select_cpu, dispatch move-to-local, running/stopping virtual time updates, and init DSQ creation. The struct sched_ext_ops instance exposes the callbacks to the kernel when userspace attaches the generated skeleton.

## State and Persistence Behavior

State is held in BPF global variables, BPF maps, task storage, UEI exit records, or rodata parameters depending on the test. It is reset when the skeleton is destroyed and does not persist outside the BPF object.

## Dependencies and Integration Points

Depends on sched_ext kernel support, BPF syscall, BTF/vmlinux.h, libbpf skeleton generation, and the paired userspace testcase in the same directory.

## Risks and Edge Cases

Many failures are intentional verifier or scheduler exits; the paired C test must distinguish expected SCX_EXIT_ERROR or load failure from regressions. Host-wide sched_ext attachment means tests must run serially.

## Test Signals

The paired userspace test loads this skeleton, attaches the struct_ops map or expects load failure, then inspects UEI/counters or child process outcomes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/sched_ext/select_cpu_vtime.bpf.c -->
