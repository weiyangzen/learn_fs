# sources/distributed-fs/ceph-client/tools/include/nolibc/arch.h

## Purpose
Selects the correct nolibc architecture backend for the active compiler target.

## APIs, Types, and Functions
The file has no functions. It conditionally includes `arch-x86.h`, `arch-arm64.h`, `arch-arm.h`, `arch-mips.h`, `arch-riscv.h`, `arch-s390.h`, `arch-loongarch.h`, `arch-powerpc.h`, `arch-sparc.h`, `arch-m68k.h`, or `arch-sh.h`, and emits a preprocessor error for unsupported targets.

## Control Flow, State, and Persistence
All control flow is compile-time preprocessor selection based on architecture macros such as `__x86_64__`, `__aarch64__`, `__arm__`, and similar. No runtime state is created.

## Dependencies and Integration
Depends on compiler predefined architecture macros and the sibling `arch-*.h` headers. It is included by generic nolibc wrappers before any syscall macro is used.

## Risks and Test Signals
Risks are missing aliases for new compiler target spellings, accidentally selecting the wrong ABI variant, and unsupported architectures failing only when this header is reached. Test signals are cross-architecture preprocessing checks and minimal nolibc builds for every listed backend.
