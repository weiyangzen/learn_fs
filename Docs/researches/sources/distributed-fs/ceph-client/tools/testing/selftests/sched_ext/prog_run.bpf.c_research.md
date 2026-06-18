<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/sched_ext/prog_run.bpf.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/sched_ext/prog_run.bpf.c

## Purpose

BPF sched_ext scheduler fixture that verifies a syscall BPF program can call into an attached scheduler and trigger sched_ext unregister exit.

## Important APIs, Types, and Functions

Uses scx/common.bpf.h, sched_ext struct_ops, prog_run_exit, sections license, syscall, .struct_ops.link, and BPF helpers/kfuncs visible in the source.

## Control Flow and Integration

syscall program calls scx_bpf_exit_bstr() with exit code 0xdeadbeef; scheduler exit records UEI. The struct sched_ext_ops instance exposes the callbacks to the kernel when userspace attaches the generated skeleton.

## State and Persistence Behavior

State is held in BPF global variables, BPF maps, task storage, UEI exit records, or rodata parameters depending on the test. It is reset when the skeleton is destroyed and does not persist outside the BPF object.

## Dependencies and Integration Points

Depends on sched_ext kernel support, BPF syscall, BTF/vmlinux.h, libbpf skeleton generation, and the paired userspace testcase in the same directory.

## Risks and Edge Cases

Many failures are intentional verifier or scheduler exits; the paired C test must distinguish expected SCX_EXIT_ERROR or load failure from regressions. Host-wide sched_ext attachment means tests must run serially.

## Test Signals

The paired userspace test loads this skeleton, attaches the struct_ops map or expects load failure, then inspects UEI/counters or child process outcomes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/sched_ext/prog_run.bpf.c -->
