# sources/distributed-fs/ceph-client/arch/parisc/math-emu/sfcmp.c

Purpose: implements `sgl_fcmp`, single-precision floating-point comparison for PA-RISC condition predicates.

Important APIs and types: inputs are two single-precision pointers, a condition selector `cond`, and a mutable status pointer. Condition helper macros such as `Exception(cond)`, `Unordered(cond)`, `Equal(cond)`, `Lessthan(cond)`, and `Greaterthan(cond)` determine the C-bit result.

Control flow: the routine copies both operands, checks for NaNs under infinity-exponent encodings, raises invalid for signaling NaNs or quiet NaNs when the condition requests an exception, and sets unordered status when appropriate. Non-NaN infinities fall through to ordinary comparisons. It then compares sign bits, treats `+0` and `-0` as equal, and uses unsigned word ordering for same-sign positives or reversed ordering for negatives.

State and persistence: result state is the FP status C-bit through `Set_status_cbit`; no destination register is written.

Dependencies and integration: called by `fpudispatch.c` compare decode for major opcodes `0x0c` and `0x0e`. `fpudispatch.c` may post-process the returned local status into compare queues or compare arrays by FPU generation.

Risks: NaN condition semantics are easy to invert, especially exception-requesting predicates. The signed comparison relies on IEEE bit ordering and special zero handling.

Test signals: compare zeros with opposite signs, positive and negative finite ordering, infinities, quiet NaN ordered/unordered predicates, signaling NaNs with invalid trap enabled and disabled, and PA2.0 compare-array update paths.
