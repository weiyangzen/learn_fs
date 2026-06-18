
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/kernel_flag.c

## Purpose

`kernel_flag.c` tests kernel-origin tracking for `bpf()` invocations by using an LSM program to allow normal skeleton loading while blocking light-skeleton kernel-based calls.

## Important APIs, Types, and Functions

The test uses `test_kernel_flag.skel.h`, `kfunc_call_test.skel.h`, and `kfunc_call_test.lskel.h`. It sets `monitored_tid` to `sys_gettid()`, attaches the LSM skeleton, then attempts normal and light skeleton open/load.

## Control Flow and Data Flow

After the LSM program attaches, a normal libbpf skeleton load is expected to pass the gatekeeper. A light skeleton load is expected to fail because it uses kernel-origin BPF invocations that the LSM program blocks. The monitored TID is reset before cleanup.

## State, Dependencies, Integration Points, Risks, and Test Signals

State is LSM BSS `monitored_tid` and attached LSM link. Dependencies are BPF LSM support, kfunc test skeletons, and light skeleton generation. Integration is kernel flag propagation through BPF syscall paths. Risks include LSM availability and assumptions about libbpf vs lskel call paths. Test signals are successful LSM attach, successful normal skeleton load, and failed lskel open/load.
