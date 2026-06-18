# Research: sources/distributed-fs/ceph-client/arch/alpha/include/asm/fpu.h

This header defines Alpha floating-point control register access and declares FP register helpers. `rdfpcr` reads the FPCR either from saved thread state or from hardware using EV6 `ftoit/itoft` sequences or older store/load floating instructions. `wrfpcr` writes saved thread state when FP is saved or writes hardware FPCR directly, preserving `$f0`.

`swcr_update_status` merges accrued exception status from hardware FPCR into software control word on EV6. External helpers read/write FP registers in full and single precision. The functions disable preemption while inspecting or changing current thread FP state.

State includes `current_thread_info()->status`, saved FP array slot 31, hardware FPCR, and TS_RESTORE_FP status. Risks are preemption safety, preserving `$f0`, EV6 versus older instruction sequences, and lazy FP restore semantics. Tests include FP signal/context switching, ptrace FP register access, and math exception status behavior.
