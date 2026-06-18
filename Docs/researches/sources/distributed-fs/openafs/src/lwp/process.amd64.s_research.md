# sources/distributed-fs/openafs/src/lwp/process.amd64.s

Purpose: x86_64 assembly implementation of the LWP low-level context-switch primitives `savecontext` and `returnto`.

Important APIs/types/functions: exports `savecontext(int (*f)(), struct savearea *area1, char *newsp)` and `returnto(struct savearea *area2)`. The save area stores `topstack` at offset 0. It references global `PRE_Block` through GOT-relative addressing and uses `_C_LABEL`/`ENTRY` from `lwp_elf.h`.

Control flow: `savecontext` builds a normal frame, stores arguments in stack slots, sets `PRE_Block = 1`, pushes general registers, records the current stack pointer in the save area, optionally switches `%rsp` to `newsp`, and jumps to the supplied function. `returnto` restores `%rsp` from the target save area, pops registers in reverse order, clears `PRE_Block`, repairs the frame, and returns into the restored context.

State and persistence: only CPU register/stack state and `PRE_Block` are modified. No disk or heap state is touched.

Dependencies/integration: used by LWP scheduler on amd64 targets that select assembly switching instead of `process.c`/ucontext. It depends on exact AMD64 calling convention and frame layout.

Risks and test signals: stack alignment, callee-saved register coverage, and GOT use are critical. Any ABI drift can corrupt scheduler state. Compile/link tests verify labels; runtime LWP switching tests (`test`, `rw`, select tests) are the behavioral signal.
