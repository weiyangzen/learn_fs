# sources/distributed-fs/ceph-client/arch/arm/mm/abort-ev7.S

Purpose: provides the ARMv7 early data-abort helper, relying on ARMv7 hardware fault status rather than software instruction decoding.

Important APIs/types/functions: exports `v7_early_abort`. It reads CP15 FSR and FAR into `r1` and `r0`, disables user access, and branches to `do_DataAbort`.

Control flow: the handler is straight-line: capture fault metadata, close user access in the exception context, and tail-call the common data-abort path.

State and persistence: no persistent state. It is an exception entry helper with strict register ABI.

Dependencies and integration points: selected by `CPU_ABRT_EV7` for ARMv7 and ARMv8 AArch32-style configurations. Integrated with ARM fault dispatch and `do_DataAbort`.

Risks: any change to the register ABI would break common fault handling. Unlike older handlers, it does not patch FSR from decoded instructions, so it assumes ARMv7 status bits are sufficient and correct for permission reporting.

Test signals: ARMv7 page fault and permission fault tests, user/kernel access-disable verification, and boot tests across SMP and LPAE-capable configurations.
