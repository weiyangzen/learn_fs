<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/setjmp_32.S -->
# sources/distributed-fs/ceph-client/arch/x86/um/setjmp_32.S

## Purpose
`setjmp_32.S` implements 32-bit kernel setjmp/longjmp used by UML host-side control transfers.

## Important APIs, types, and functions
Exports `kernel_setjmp` and `kernel_longjmp` with jmp_buf layout matching `archsetjmp_32.h`.

## Control flow
`kernel_setjmp` saves callee-saved registers, post-return ESP, and return address; `kernel_longjmp` restores them and jumps to saved EIP.

## State and persistence behavior
State is per-task saved register/TLS/fault/FP data or host-probed globals where the file defines them; otherwise state is transient local syscall/signal handling data.

## Dependencies and integration points
It depends on UML task/thread structures, generated register offsets, host ptrace/ucontext/syscall APIs, and bitness-specific x86 ABI headers.

## Risks and edge cases
Risks center on ABI drift: wrong register offsets, selector validation, FP/XSTATE sizing, or signal-frame layout can corrupt user state or break ptrace/core dumps.

## Test signals
Signals include UML boot, ptrace selftests, signal delivery/return tests, TLS/arch_prctl tests, syscall-table smoke tests, and core-dump/register inspection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/setjmp_32.S -->
