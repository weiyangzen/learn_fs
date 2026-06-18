# sources/distributed-fs/ceph-client/arch/s390/kernel/Makefile

## Purpose
Defines the Kbuild object selection and per-file compiler instrumentation policy for the s390 kernel directory. It wires core boot, entry, interrupt, diagnostic, tracing, crash, crypto, topology, kexec, and VDSO support into the architecture build.

## Important APIs, Types, And Functions
This file exports no C API. Important build variables are `obj-y`, `obj-$(CONFIG_*)`, `CFLAGS_REMOVE_*`, sanitizer/profiling toggles, `always-$(KBUILD_BUILTIN)`, and `CFLAGS_*` overrides.

## Control Flow
At build time, Kbuild evaluates s390 configuration symbols and appends the corresponding objects. Core objects such as `head.o`, `entry.o`, `debug.o`, `diag/`, `fpu.o`, and `abs_lowcore.o` are always linked. Optional objects are added for audit, early printk, kprobes, ftrace, crash dump, kexec, cert store, perf, BPF, and tracepoints.

## State And Persistence
No runtime state. It persists build policy: early code is excluded from ftrace, gcov, kcov, and UBSAN where instrumentation would be unsafe; stack tracing paths disable sibling-call optimization.

## Dependencies And Integration Points
Integrates s390 architecture code with Kconfig, Kbuild instrumentation, VDSO, perf, BPF, tracing, and the `diag/` subdirectory.

## Risks And Edge Cases
Wrong object selection can cause missing entry points or duplicate instrumentation in fragile boot paths. Ftrace or sanitizer instrumentation on early/entry code can break boot. Tail-call optimization on stack walkers can corrupt backtraces.

## Test Signals
Signals are broad s390 defconfig and randconfig builds, boot tests with tracing and sanitizers toggled, link map checks for `vmlinux.lds`, and feature-specific builds for kexec, crash dump, BPF, perf, and cert store.
