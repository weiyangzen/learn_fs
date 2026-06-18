# sources/distributed-fs/ceph-client/arch/arm/mm/abort-nommu.S

Purpose: implements the data-abort entry helper for CPUs without a CP15 MMU fault status/address interface.

Important APIs/types/functions: exports `nommu_early_abort`. It clears `r0` and `r1` to represent absent FAR/FSR and branches to `do_DataAbort`.

Control flow: the exception vector enters the helper with `pt_regs`, PC, and PSR already available. Since no MMU fault registers exist, it supplies zero metadata and delegates all handling to the common data-abort path.

State and persistence: no persistent state.

Dependencies and integration points: selected by `CPU_ABRT_NOMMU` for no-MMU CPU models such as ARM9TDMI, ARM940T/946E, and ARMv7-M paths. Integrated with generic data abort dispatch.

Risks: downstream handlers must tolerate missing address/status data. Diagnostics and signal details are necessarily less specific than MMU-backed abort handling.

Test signals: no-MMU boot tests that trigger data aborts, verify no CP15 MMU accesses are emitted, and confirm common fault handling handles zero FAR/FSR without dereferencing invalid metadata.
