# sources/distributed-fs/ceph-client/arch/arm/mm/abort-ev4.S

Purpose: implements the early data-abort entry helper for ARMv4-style CPUs using CP15 fault status/address registers and ARM instruction decoding to infer whether the abort came from a write.

Important APIs/types/functions: exports `v4_early_abort`. It reads FSR via `mrc p15, 0, r1, c5, c0, 0`, FAR via `mrc p15, 0, r0, c6, c0, 0`, reads the faulting ARM instruction at `r4`, disables user access with `uaccess_disable ip`, adjusts FSR write bits, and branches to `do_DataAbort`.

Control flow: the vector caller passes `pt_regs` in `r2`, fault PC in `r4`, and PSR in `r5`. The handler fetches fault metadata, reads the aborted instruction, clears FSR bits 10 and 11, tests instruction bit 20, sets the write indicator when needed, then tail-branches into the common data-abort handler.

State and persistence: no persistent state. It transiently updates `r0` and `r1` with FAR/FSR for `do_DataAbort` and must preserve the register contract documented in the comment.

Dependencies and integration points: selected by `CPU_ABRT_EV4` and linked through the ARM exception vector path. It depends on CP15 MMU registers, `asm/assembler.h`, and common fault handling in `do_DataAbort`.

Risks: it reads the aborted instruction from user space while handling an abort, so mismatched I-TLB/D-TLB state can produce nested aborts. The write/read inference is ARM-instruction-specific and lacks Thumb handling; it is only suitable for the CPU models selecting it.

Test signals: boot on FA526/StrongARM-style configurations, trigger read and write data aborts, verify fault status write classification, and test user instruction fetch fault nesting behavior under invalid mappings.
