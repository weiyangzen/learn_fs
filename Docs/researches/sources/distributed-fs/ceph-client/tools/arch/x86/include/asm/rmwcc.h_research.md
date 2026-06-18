# sources/distributed-fs/ceph-client/tools/arch/x86/include/asm/rmwcc.h

## Purpose
Provides macros for read-modify-write instructions that return whether a condition code was set after the operation.

## APIs, Types, and Functions
`__GEN_RMWcc()` emits `asm goto` with a conditional jump to a label and returns `1` or `0`. `GEN_UNARY_RMWcc()` and `GEN_BINARY_RMWcc()` format unary and binary instruction templates.

## Control Flow, State, and Persistence
Generated code executes the supplied instruction on memory, branches on the named condition code, and returns immediately from the surrounding inline function or macro context. The memory clobber preserves ordering around the RMW.

## Dependencies and Integration
Consumed by x86 atomic/bitops-style tool headers that need kernel-like condition-code helpers. It depends on compiler support for `asm goto`.

## Risks and Test Signals
Risks include misuse in a context where `return` is invalid, wrong operand constraints, unsupported compilers, and condition-code naming mistakes. Test signals are compile tests for unary and binary macro users and runtime checks for operations such as add/sub/cmpxchg wrappers that depend on carry/zero/sign flags.
