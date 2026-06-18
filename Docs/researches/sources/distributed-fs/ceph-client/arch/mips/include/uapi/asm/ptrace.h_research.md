# sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/ptrace.h

## Purpose

`ptrace.h` exports a MIPS userspace ABI header.

## Important APIs, Types, And Functions

The file defines constants, structs, enum values, or generic-header selections consumed by libc, tools, ioctls, KVM, perf, ptrace, IPC, memory-management, signal, and build/header-install paths. Includes: `linux/types.h`. Macros/constants: `_UAPI_ASM_PTRACE_H`, `FPR_BASE`, `PC`, `CAUSE`, `BADVADDR`, `MMHI`, `MMLO`, `FPC_CSR`, `FPC_EIR`, `DSP_BASE`, `DSP_CONTROL`, `ACX`, `PTRACE_GETREGS`, `PTRACE_SETREGS`, `PTRACE_GETFPREGS`, `PTRACE_SETFPREGS`, `PTRACE_OLDSETOPTIONS`, `PTRACE_GET_THREAD_AREA`, `PTRACE_SET_THREAD_AREA`, `PTRACE_PEEKTEXT_3264`, `PTRACE_PEEKDATA_3264`, `PTRACE_POKETEXT_3264`, `PTRACE_POKEDATA_3264`, `PTRACE_GET_THREAD_AREA_3264`, `PTRACE_GET_WATCH_REGS`, `PTRACE_SET_WATCH_REGS`. Types/enums/unions: `defines`, `user_pt_regs`, `pt_regs`, `pt_watch_style`, `mips32_watch_regs`, `mips64_watch_regs`, `pt_watch_regs`.

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
Static review signal: this source currently has 110 lines and 2802 bytes; major size or symbol-surface changes should trigger a fresh review of this report.
