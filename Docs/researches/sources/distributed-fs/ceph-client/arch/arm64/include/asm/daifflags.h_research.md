## sources/distributed-fs/ceph-client/arch/arm64/include/asm/daifflags.h

Purpose: controls DAIF exception mask flags for debug, SError, IRQ, and FIQ handling.

Important APIs/types/functions: exports DAIF flag constants and helpers such as `local_daif_mask`, `local_daif_restore`, `local_daif_inherit`, `local_daif_save`, `local_daif_flags`, and `system_has_prio_mask_debugging`-aware assertions.

Control flow: helpers read/write DAIF with barriers, preserve expected mask ordering, and coordinate with pseudo-NMI/priority masking paths.

State and persistence: changes processor PSTATE DAIF bits; no memory persistence.

Dependencies and integration: used by exception entry/exit, IRQ flags, idle, debug monitors, SError handling, and tracing.

Risks: restoring wrong DAIF bits can re-enable exceptions too early or mask NMIs indefinitely. Test signals are IRQ/NMI stress, lockdep IRQ state checks, debug exception tests, and SError injection.
