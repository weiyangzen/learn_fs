# sources/distributed-fs/ceph-client/tools/arch/arm64/include/uapi/asm/unistd.h

## Purpose
Selects arm64 syscall table options for generic unistd generation in tools.

## Important APIs, Types, and Functions
Defines `__ARCH_WANT_RENAMEAT`, `__ARCH_WANT_NEW_STAT`, `__ARCH_WANT_SET_GET_RLIMIT`, `__ARCH_WANT_TIME32_SYSCALLS`, and `__ARCH_WANT_MEMFD_SECRET`, then includes `asm-generic/unistd.h`.

## Control Flow, State, and Persistence
The include-time flow is generic syscall macro expansion. No persistent state exists.

## Dependencies and Integration Points
Used by syscall table generation and tools that need arm64 syscall numbers matching kernel UAPI.

## Risks and Test Signals
Risk is stale architecture wants changing generated syscall numbers or availability macros. Test signals are syscall-number diff checks and perf trace/syscall-table generation on arm64.
