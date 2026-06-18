<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/mmu_context.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/mmu_context.h

## Purpose
Implements Xtensa MMU context and ASID management for process address-space switches.

## Important APIs, Types, And Functions
Key definitions include per-CPU `asid_cache`, `NO_CONTEXT`, `ASID_USER_FIRST`, `ASID_MASK`, `ASID_INSERT`, `init_mmu`, `init_kio`, `set_rasid_register`, `get_rasid_register`, `get_new_mmu_context`, `get_mmu_context`, `activate_context`, `init_new_context`, `switch_mm`, and `destroy_context`.

## Control Flow
New contexts initialize all per-CPU ASIDs to invalid. On switch, if the process migrated CPUs the icache is invalidated; if migrated or switching to a different `mm`, `activate_context` ensures a current ASID, writes the RASID register with reserved/kernel/user slots, and invalidates the page directory. ASID wrap flushes the local TLB and starts a new generation.

## State And Persistence
State is per-mm ASID arrays, last CPU field, per-CPU ASID cache, RASID hardware register, TLB entries, and page-directory cache state.

## Dependencies And Integration Points
Depends on MMU hardware with TLBs, cacheflush, TLB flush, page tables, percpu, scheduler, and generic MM hooks.

## Risks And Edge Cases
ASID generation wrap must flush stale TLBs. Migration requires icache invalidation for possible VIPT/instruction coherency issues. `invalidate_page_directory` must match hardware page-table cache behavior.

## Test Signals
Run fork/exec/mmap stress, SMP migration, TLB shootdown tests, icache coherency tests, and ASID wrap stress with many processes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/mmu_context.h -->
