# sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/reg.h

## Purpose

`reg.h` exports a MIPS userspace ABI header.

## Important APIs, Types, And Functions

The file defines constants, structs, enum values, or generic-header selections consumed by libc, tools, ioctls, KVM, perf, ptrace, IPC, memory-management, signal, and build/header-install paths. Macros/constants: `__UAPI_ASM_MIPS_REG_H`, `MIPS32_EF_R0`, `MIPS32_EF_R1`, `MIPS32_EF_R2`, `MIPS32_EF_R3`, `MIPS32_EF_R4`, `MIPS32_EF_R5`, `MIPS32_EF_R6`, `MIPS32_EF_R7`, `MIPS32_EF_R8`, `MIPS32_EF_R9`, `MIPS32_EF_R10`, `MIPS32_EF_R11`, `MIPS32_EF_R12`, `MIPS32_EF_R13`, `MIPS32_EF_R14`, `MIPS32_EF_R15`, `MIPS32_EF_R16`, `MIPS32_EF_R17`, `MIPS32_EF_R18`, `MIPS32_EF_R19`, `MIPS32_EF_R20`, `MIPS32_EF_R21`, `MIPS32_EF_R22`, `MIPS32_EF_R23`, `MIPS32_EF_R24`, `MIPS32_EF_R25`, `MIPS32_EF_R26`, `MIPS32_EF_R27`, `MIPS32_EF_R28`, `MIPS32_EF_R29`, `MIPS32_EF_R30`, `MIPS32_EF_R31`, `MIPS32_EF_LO`, and 86 more.

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
Static review signal: this source currently has 208 lines and 5426 bytes; major size or symbol-surface changes should trigger a fresh review of this report.
