# sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/kvm.h

## Purpose

`kvm.h` exports a MIPS userspace ABI header.

## Important APIs, Types, And Functions

The file defines constants, structs, enum values, or generic-header selections consumed by libc, tools, ioctls, KVM, perf, ptrace, IPC, memory-management, signal, and build/header-install paths. Includes: `linux/types.h`. Macros/constants: `__LINUX_KVM_MIPS_H`, `KVM_COALESCED_MMIO_PAGE_OFFSET`, `KVM_REG_MIPS_GP`, `KVM_REG_MIPS_CP0`, `KVM_REG_MIPS_KVM`, `KVM_REG_MIPS_FPU`, `KVM_REG_MIPS_R0`, `KVM_REG_MIPS_R1`, `KVM_REG_MIPS_R2`, `KVM_REG_MIPS_R3`, `KVM_REG_MIPS_R4`, `KVM_REG_MIPS_R5`, `KVM_REG_MIPS_R6`, `KVM_REG_MIPS_R7`, `KVM_REG_MIPS_R8`, `KVM_REG_MIPS_R9`, `KVM_REG_MIPS_R10`, `KVM_REG_MIPS_R11`, `KVM_REG_MIPS_R12`, `KVM_REG_MIPS_R13`, `KVM_REG_MIPS_R14`, `KVM_REG_MIPS_R15`, `KVM_REG_MIPS_R16`, `KVM_REG_MIPS_R17`, `KVM_REG_MIPS_R18`, `KVM_REG_MIPS_R19`, `KVM_REG_MIPS_R20`, `KVM_REG_MIPS_R21`, `KVM_REG_MIPS_R22`, `KVM_REG_MIPS_R23`, `KVM_REG_MIPS_R24`, `KVM_REG_MIPS_R25`, `KVM_REG_MIPS_R26`, `KVM_REG_MIPS_R27`, and 23 more. Types/enums/unions: `kvm_regs`, `kvm_fpu`, `kvm_debug_exit_arch`, `kvm_guest_debug_arch`, `kvm_sync_regs`, `kvm_sregs`, `kvm_mips_interrupt`.

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
Static review signal: this source currently has 226 lines and 7690 bytes; major size or symbol-surface changes should trigger a fresh review of this report.
