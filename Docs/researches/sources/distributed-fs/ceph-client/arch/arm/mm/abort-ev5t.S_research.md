# sources/distributed-fs/ceph-client/arch/arm/mm/abort-ev5t.S

Purpose: implements early data-abort decoding for ARMv5T CPUs, including Thumb handling and the ARM `LDRD` read-instruction exception to normal write-bit decoding.

Important APIs/types/functions: exports `v5t_early_abort` and uses macros `do_thumb_abort` and `teq_ldrd` from `abort-macro.S`. It reads FSR/FAR, handles Thumb, reads ARM instruction, disables user access, clears FSR bit 11, checks for `LDRD`, and otherwise derives write status from bit 20.

Control flow: Thumb-mode faults are resolved by the macro path. ARM-mode faults are decoded locally; if `teq_ldrd` matches, the handler does not mark the fault as a write. Other instructions use the load bit to set the write indicator before tail-branching to `do_DataAbort`.

State and persistence: no persistent state; it prepares `r0`/`r1` for the common abort path.

Dependencies and integration points: selected by `CPU_ABRT_EV5T` for XScale, XSC3, Mohawk, Feroceon, and related ARMv5-style CPUs. Relies on CP15 fault registers and the common data-abort path.

Risks: misclassifying `LDRD` as a write would incorrectly signal faults on read-only mappings. Instruction fetch from the faulting PC remains fragile if user mappings are inconsistent.

Test signals: trigger read/write aborts for ARM, Thumb, and `LDRD` instructions; verify `si_code`/fault permissions match read vs write; and run on ARMv5T hardware or emulator configurations selecting this object.
