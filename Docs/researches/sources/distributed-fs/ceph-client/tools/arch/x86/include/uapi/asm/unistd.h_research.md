# sources/distributed-fs/ceph-client/tools/arch/x86/include/uapi/asm/unistd.h

## Purpose
Selects the correct x86 syscall-number header for user-space builds and defines the x32 syscall bit.

## APIs, Types, and Functions
Exports `__X32_SYSCALL_BIT` as `0x40000000`, then includes `unistd_32.h`, `unistd_x32.h`, or `unistd_64.h` for non-kernel builds depending on `__i386__`, `__ILP32__`, and default x86-64 compilation.

## Control Flow, State, and Persistence
Preprocessor logic determines the syscall ABI at compile time. No runtime behavior or state exists.

## Dependencies and Integration
Consumed by tools that issue raw syscalls or need syscall constants without glibc-specific headers. It integrates architecture-local generated syscall lists with generic user-space builds.

## Risks and Test Signals
Risks include wrong header selection for x32, missing `unistd_x32.h` in include paths, and assumptions that syscall numbers are signed. Test signals are compile checks for i386, x86-64, and x32 and raw syscall smoke tests for constants used by tools.
