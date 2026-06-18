## sources/distributed-fs/ceph-client/arch/arm64/include/asm/gpr-num.h

Purpose: names AArch64 general-purpose register numbers for assembly and decoding code.

Important APIs/types/functions: defines constants for x0-x30 plus frame pointer, link register, stack pointer/zero register aliases as used by low-level code.

Control flow: constants only.

State and persistence: no state.

Dependencies and integration: used by instruction generation, ptrace/register access, assembly macros, and BPF/tracing helpers.

Risks: wrong numbering breaks generated instructions and register decoding. Test signals are instruction encoder tests, ptrace register tests, and BPF/ftrace register mapping tests.
