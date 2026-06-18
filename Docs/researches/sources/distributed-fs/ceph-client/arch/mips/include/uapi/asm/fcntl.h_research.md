# sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/fcntl.h

## Purpose

`fcntl.h` exports a MIPS userspace ABI header.

## Important APIs, Types, And Functions

The file defines constants, structs, enum values, or generic-header selections consumed by libc, tools, ioctls, KVM, perf, ptrace, IPC, memory-management, signal, and build/header-install paths. Includes: `asm/sgidefs.h`, `asm-generic/fcntl.h`. Macros/constants: `_UAPI_ASM_FCNTL_H`, `O_APPEND`, `O_DSYNC`, `O_NONBLOCK`, `O_CREAT`, `O_TRUNC`, `O_EXCL`, `O_NOCTTY`, `FASYNC`, `O_LARGEFILE`, `__O_SYNC`, `O_SYNC`, `O_DIRECT`, `F_GETLK`, `F_SETLK`, `F_SETLKW`, `F_SETOWN`, `F_GETOWN`, `F_GETLK64`, `F_SETLK64`, `F_SETLKW64`, `__ARCH_FLOCK_EXTRA_SYSID`, `__ARCH_FLOCK_PAD`. Types/enums/unions: `flock64`.

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
Static review signal: this source currently has 61 lines and 2028 bytes; major size or symbol-surface changes should trigger a fresh review of this report.
