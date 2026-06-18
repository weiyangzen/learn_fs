<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/rmwcc.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/rmwcc.h

Purpose: defines macros that perform x86 read-modify-write instructions and return a condition-code result, supporting lock-free and lock fast paths. Important macros include `GEN_UNARY_RMWcc()`, `GEN_BINARY_RMWcc()`, and lower-level `__GEN_RMWcc` forms built around `asm goto`.

Control flow: callers supply an instruction template, memory operand, condition code, and operands; the macro emits inline assembly that branches to labels based on the CPU flags and returns a boolean-like value. State is the target memory operand only.

Dependencies include compiler support for asm goto, x86 condition-code constraints, and users such as qspinlock pending-bit logic. Risks include compiler instrumentation interactions, label use inside statement expressions, operand constraint mistakes, and memory-order assumptions. Test signals include qspinlock builds, objtool/compiler matrix coverage, and lock stress on GCC/Clang variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/rmwcc.h -->
