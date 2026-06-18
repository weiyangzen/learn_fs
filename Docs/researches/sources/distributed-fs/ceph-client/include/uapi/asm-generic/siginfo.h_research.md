# sources/distributed-fs/ceph-client/include/uapi/asm-generic/siginfo.h

## Purpose
Defines the generic Linux UAPI `siginfo_t`, `sigval_t`, signal-specific `si_code` constants, and `sigevent_t` layout used by user space, libc, ptrace, seccomp, POSIX timers, and signal delivery paths. The file is ABI rather than executable logic.

## Important APIs, Types, And Functions
Key exports are `sigval_t`, `union __sifields`, `siginfo_t`, field aliases such as `si_pid`, `si_addr`, `si_syscall`, `si_perf_data`, and constants for `SI_*`, `ILL_*`, `FPE_*`, `SEGV_*`, `BUS_*`, `TRAP_*`, `CLD_*`, `POLL_*`, `SYS_*`, and `SIGEV_*`. `sigevent_t` carries notification mode, signal number, payload value, optional thread function, and thread id.

## Control Flow
There is no runtime control flow. Compile-time conditionals select architecture-specific field order, band/clock types, attributes, padding, and IA64-specific `SEGV` naming. `SI_FROMUSER()` and `SI_FROMKERNEL()` classify origin from `si_code`.

## State, Persistence, And Dependencies
Instances are transient kernel/user ABI payloads copied during signal delivery and timer setup. It depends on `<linux/compiler.h>` and `<linux/types.h>` for `__user`, kernel integer, pid, uid, timer, and clock types.

## Integration Points
Integrated by `asm/siginfo.h`, `signal.h`, syscall implementations for `rt_sigqueueinfo`, `waitid`, POSIX timers, seccomp, perf signal traps, ptrace, and libc signal headers.

## Risks
The 128-byte `siginfo_t` size and 32-bit alignment warning are hard ABI constraints. Adding 64-bit-aligned fields, changing union order, or changing constants breaks user space. Architecture overrides must preserve historical layouts.

## Test Signals
Useful checks include `sizeof(siginfo_t) == 128`, architecture ABI layout tests, signal delivery tests for every `si_code` class, seccomp `SIGSYS`, perf `TRAP_PERF`, POSIX timer `sigevent`, and 32/64-bit compat signal frame tests.
