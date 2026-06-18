<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/os-Linux/Makefile -->
# sources/distributed-fs/ceph-client/arch/x86/um/os-Linux/Makefile

## Purpose
`os-Linux/Makefile` builds host-OS-facing x86 UML support.

## Important APIs, types, and functions
Objects are `registers.o`, `mcontext.o`, and 32-bit `tls.o`; `USER_OBJS` marks them for user-mode compilation rules.

## Control flow
Kbuild compiles these with UML user object rules so host libc/ucontext/ptrace APIs can be used.

## State and persistence behavior
State is per-task saved register/TLS/fault/FP data or host-probed globals where the file defines them; otherwise state is transient local syscall/signal handling data.

## Dependencies and integration points
It depends on UML task/thread structures, generated register offsets, host ptrace/ucontext/syscall APIs, and bitness-specific x86 ABI headers.

## Risks and edge cases
Risks center on ABI drift: wrong register offsets, selector validation, FP/XSTATE sizing, or signal-frame layout can corrupt user state or break ptrace/core dumps.

## Test signals
Signals include UML boot, ptrace selftests, signal delivery/return tests, TLS/arch_prctl tests, syscall-table smoke tests, and core-dump/register inspection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/os-Linux/Makefile -->
