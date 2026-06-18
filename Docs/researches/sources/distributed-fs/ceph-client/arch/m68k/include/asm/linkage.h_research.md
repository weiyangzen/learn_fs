<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/linkage.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/linkage.h

## Purpose
`linkage.h` provides m68k assembly alignment and syscall/linkage protection macros.

## Important APIs, Types, and Functions
It sets `__ALIGN` and `__ALIGN_STR` to `.align 4`. `asmlinkage_protect(n, ret, args...)` expands to arity-specific empty inline assembly constraints that keep stack-passed syscall arguments live until function exit.

## Control Flow, State, and Persistence
There is no runtime state. The macros alter compiler optimization behavior by adding artificial uses of return values and arguments.

## Dependencies and Integration Points
Architecture syscall wrappers and low-level assembly/C boundaries use these definitions through generic linkage headers.

## Risks
The arity-specific macros only cover up to six arguments. Removing or weakening the constraints can let GCC reuse caller-owned stack argument slots or tail-call in ways that break syscall ABI assumptions.

## Test Signals
Compile syscall-heavy code with optimization and inspect that argument stack slots are not clobbered prematurely. Runtime syscall ABI tests are the practical signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/linkage.h -->
