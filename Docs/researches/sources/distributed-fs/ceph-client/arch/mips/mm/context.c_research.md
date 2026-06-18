# sources/distributed-fs/ceph-client/arch/mips/mm/context.c

Purpose: manages MIPS ASID/MMID allocation and context switching for address spaces.

Important APIs/functions: `get_new_mmu_context()` and `check_mmu_context()` handle classic per-CPU ASIDs. `check_switch_mmu_context()` handles both ASID and MMID CPUs, writes EntryHi or MemoryMapID, invalidates TLBs on generation rollover, and sets up the TLB miss handler PGD. `mmid_init()` initializes the MMID allocator.

Control flow: ASID mode increments per-CPU ASID and flushes on wrap. MMID mode uses a global version, bitmap allocator, reserved per-CPU MMIDs, rollover flush mask, and a fast path using relaxed cmpxchg before taking `cpu_mmid_lock`.

State and persistence: global `mmid_version`, `num_mmids`, `mmid_map`, per-CPU `reserved_mmids`, and `tlb_flush_pending` persist for runtime context management. Per-mm CPU contexts are updated.

Dependencies and integration: called on context switch by MIPS MMU code and TLB refill setup. Depends on CPU ASID masks, ginvt support, SMP sibling masks, and `TLBMISS_HANDLER_SETUP_PGD`.

Risks and test signals: memory ordering and rollover are subtle. A duplicated `if (cpu_has_vtag_icache)` appears in the flush-pending path and is harmless but noisy. Test ASID wrap, MMID exhaustion, SMP sibling shared FTLB invalidation, CPU hotplug assumptions, and DEBUG_VM warnings.
