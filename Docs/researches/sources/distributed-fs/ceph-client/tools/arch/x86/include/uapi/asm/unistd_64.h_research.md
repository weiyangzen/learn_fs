# sources/distributed-fs/ceph-client/tools/arch/x86/include/uapi/asm/unistd_64.h

## Purpose
Provides a small tool-side subset of 64-bit x86 syscall numbers when not already supplied by system headers.

## APIs, Types, and Functions
Defines guarded `__NR_*` macros for `fork`, `execve`, `getppid`, `getpgid`, `capget`, `gettid`, `futex`, `perf_event_open`, `setns`, `getcpu`, and `seccomp`.

## Control Flow, State, and Persistence
No runtime behavior. Guarded preprocessor definitions avoid redefining constants already present in libc or kernel UAPI headers.

## Dependencies and Integration
Included by `uapi/asm/unistd.h` for LP64 x86-64 builds. Supports tools that need raw syscall constants during standalone builds.

## Risks and Test Signals
Risks are incomplete coverage and accidental mismatch with the kernel syscall table. Test signals are x86-64 compile coverage and smoke tests for raw syscalls used by perf-like tooling.
