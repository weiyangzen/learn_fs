# sources/distributed-fs/ceph-client/samples/bpf/syscall_nrs.c

Purpose: kbuild helper source for generating syscall number definitions for BPF samples.

Important APIs/types/functions: includes `<uapi/linux/unistd.h>` and `<linux/kbuild.h>`, defines `SYSNR(_NR) DEFINE(SYS##_NR, _NR)`, and `syscall_defines` emits selected syscall constants such as `__NR_write`.

Control flow: compiled to assembly and processed by kbuild `filechk` to produce `syscall_nrs.h`.

State and persistence: generated header persists in the build object directory.

Dependencies and integration: used by the BPF Makefile for samples needing architecture-specific syscall numbers.

Risks: generated output depends on target architecture UAPI headers. Missing syscall macros break generation.

Test signals: `samples/bpf/syscall_nrs.h` is generated and included by dependent BPF samples.
