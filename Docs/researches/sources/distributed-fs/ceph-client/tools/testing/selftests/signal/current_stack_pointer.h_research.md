# sources/distributed-fs/ceph-client/tools/testing/selftests/signal/current_stack_pointer.h

## Purpose
Provides a portable `sp` register variable for reading the current stack pointer in signal tests.

## Important APIs, types, and functions
Declares `register unsigned long sp asm("...")` for alpha, arm, aarch64, csky, m68k, mips, riscv, i386, loongarch64, powerpc, s390x, sh, x86_64, and xtensa.

## Control flow
Preprocessor architecture selection chooses the correct register name or emits a compile-time error.

## State and persistence
No persisted state; `sp` reflects the current execution stack pointer when read.

## Dependencies and integration points
Used by `sas.c` to confirm a signal handler is executing on the alternate signal stack.

## Risks
Unsupported architectures fail compilation until a register mapping is added. Compiler behavior for global register variables is architecture-sensitive.

## Test signals
`sas.c` fails if `sp` is not within the expected altstack address range during `SIGUSR1`.
