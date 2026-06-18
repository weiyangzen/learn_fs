# sources/distributed-fs/ceph-client/tools/arch/x86/include/uapi/asm/unistd_32.h

## Purpose
Provides a small tool-side subset of 32-bit x86 syscall numbers when the including environment has not already defined them.

## APIs, Types, and Functions
Defines guarded `__NR_*` macros for `fork`, `execve`, `getppid`, `getpgid`, `capget`, `gettid`, `futex`, `getcpu`, `perf_event_open`, `setns`, and `seccomp`.

## Control Flow, State, and Persistence
No runtime behavior. Each definition is protected by `#ifndef` so system headers can override or predefine values.

## Dependencies and Integration
Included by `uapi/asm/unistd.h` for `__i386__` builds and by tools that need a limited syscall constant set.

## Risks and Test Signals
Risks include an incomplete syscall set for new tool users and stale numbers if copied incorrectly. Test signals are i386 compile coverage and raw syscall tests for perf, futex, namespace, seccomp, and process-ID operations.
