# sources/distributed-fs/ceph-client/arch/mips/include/asm/mmu_context.h

Purpose: MIPS MMU context management for process address spaces, ASID/MMID handling, TLB-miss handler PGD setup, and context switch hooks.

Important APIs/types/functions: `htw_set_pwbase()`, `TLBMISS_HANDLER_SETUP_PGD`, `TLBMISS_HANDLER_RESTORE`, and `TLBMISS_HANDLER_SETUP` configure TLB miss state and hardware page walker base. `MMID_KERNEL_WIRED` reserves MMID 0 for wired kernel entries. Helpers include `asid_version_mask()`, `asid_first_version()`, `cpu_context()`, `set_cpu_context()`, `asid_cache()`, `cpu_asid()`, and declarations for `get_new_mmu_context()`, `check_mmu_context()`, and `check_switch_mmu_context()`. Implements `init_new_context()`, `switch_mm()`, `destroy_context()`, and `drop_mmu_context()`.

Control flow, state, and persistence: `init_new_context()` clears ASID/MMID state and initializes delay-slot emulation tracking. `switch_mm()` disables IRQs, stops HTW, checks/assigns context, updates mm CPU masks, restarts HTW, and restores IRQs. `drop_mmu_context()` either invalidates MMID via GINVT, allocates a new ASID for active mms, or clears inactive per-CPU context.

Dependencies and integration: Depends on cache/TLB flush, HTW, GINVT, hazards, SMP, branch-delay emulation, and generic MM hooks. Integrated with scheduler context switches, TLB miss handlers, KVM entry setup, and process lifecycle.

Risks and test signals: ASID/MMID rollover, HTW stop/start, and GINVT wired-entry reservation are correctness-critical. Test fork/exec/exit stress, ASID rollover, SMP TLB shootdowns, MMID CPUs, hardware page walker paths, KVM entry setup, and delay-slot emulation cleanup.
