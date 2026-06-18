# sources/distributed-fs/ceph-client/arch/arm/mm/abort-ev4t.S

Purpose: implements early data-abort decoding for ARMv4T CPUs, adding Thumb instruction support to the ARMv4 abort model.

Important APIs/types/functions: exports `v4t_early_abort` and includes `abort-macro.S` for `do_thumb_abort`. It reads FSR/FAR from CP15, invokes Thumb-specific decode when `PSR_T_BIT` is set, otherwise reads the ARM instruction and infers write status from bit 20.

Control flow: after obtaining FSR and FAR, `do_thumb_abort` handles Thumb faults directly by decoding a 16-bit instruction and branching to `do_DataAbort`. If the aborted context is ARM state, execution falls through to ARM instruction fetch, FSR cleanup, write-bit adjustment, and the common abort handler.

State and persistence: no persistent state. Register outputs are FAR in `r0`, FSR in `r1`, and preserved context registers as required by the abort vector ABI.

Dependencies and integration points: selected by `CPU_ABRT_EV4T`, used by ARM920/922/925/1020-class configurations, and integrated with common `do_DataAbort`.

Risks: safe classification depends on correctly reading user Thumb/ARM instruction memory during abort handling. Thumb `LDRSB` needs special handling because its opcode bit convention differs from normal load/store write-bit semantics.

Test signals: test ARM and Thumb user-mode load/store aborts, especially `LDRSB`, write faults, and executable/non-executable mapping mismatches that could cause nested instruction reads.
