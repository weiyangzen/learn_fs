# sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/perf_regs.h

## Purpose

`perf_regs.h` exports a MIPS userspace ABI header.

## Important APIs, Types, And Functions

The file defines constants, structs, enum values, or generic-header selections consumed by libc, tools, ioctls, KVM, perf, ptrace, IPC, memory-management, signal, and build/header-install paths. Macros/constants: `_ASM_MIPS_PERF_REGS_H`. Types/enums/unions: `perf_event_mips_regs`.

## Control Flow

There is no in-kernel control flow in the header itself; runtime behavior is the kernel/user ABI that interprets these numbers or structure layouts.

## State And Persistence

State crosses the kernel boundary through syscalls, ioctls, signal frames, ptrace register views, KVM register IDs, IPC objects, or headers-install outputs; the definitions are ABI-persistent.

## Dependencies And Integration Points

It integrates with `headers_install`, libc/toolchain consumers, syscall implementations, compat ABI handling, tracing/perf tools, KVM userspace, and architecture signal/ptrace code.

## Risks

Risks are ABI breakage, endian/layout drift, wrong ioctl or errno numbers, and incompatibility with old MIPS userlands.

## Test Signals

Test signals are `make headers_install`, UAPI compile tests, LTP ABI/syscall tests, strace/perf/KVM userspace tests, and big/little endian 32/64-bit builds.
Static review signal: this source currently has 41 lines and 864 bytes; major size or symbol-surface changes should trigger a fresh review of this report.
