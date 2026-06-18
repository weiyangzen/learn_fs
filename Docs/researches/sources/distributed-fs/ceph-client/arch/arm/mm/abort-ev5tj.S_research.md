# sources/distributed-fs/ceph-client/arch/arm/mm/abort-ev5tj.S

Purpose: implements ARMv5TEJ/Jazelle-capable early data-abort decoding, preserving the ARMv5T behavior while avoiding instruction decode for Java state.

Important APIs/types/functions: exports `v5tj_early_abort`, uses `do_thumb_abort` and `teq_ldrd`, tests `PSR_J_BIT`, reads CP15 FSR/FAR, clears FSR bits 10 and 11, and branches to `do_DataAbort`.

Control flow: after FSR/FAR capture, Java state bypasses instruction decoding and goes straight to common data-abort handling. Non-Java Thumb state is handled by `do_thumb_abort`; ARM state reads the instruction, disables user access, special-cases `LDRD`, then derives the write indicator from bit 20.

State and persistence: no persistent state; all work is in exception registers.

Dependencies and integration points: selected by `CPU_ABRT_EV5TJ`, notably ARM926T-style configurations. It depends on the PSR Java and Thumb bits being accurate in the saved context.

Risks: Java/Jazelle state cannot be decoded like ARM/Thumb, so permission classification relies on hardware-provided status. As with other early abort handlers, user instruction reads during exception handling can fault again.

Test signals: exercise ARM926T data aborts from ARM, Thumb, and if applicable Jazelle state; verify `LDRD` read faults are not treated as writes; and boot-test configurations selecting `CPU_ABRT_EV5TJ`.
