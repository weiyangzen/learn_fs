# sources/distributed-fs/ceph-client/arch/x86/include/asm/mmu.h

## Purpose
Defines x86 `mm_context_t`, the architecture-specific per-mm state used for TLB generation, LDT, LAM, VDSO, protection keys, RDPMC permission, and optional global ASID tracking.

## Important APIs, Types, And Functions
Key flags are `MM_CONTEXT_UPROBE_IA32`, `MM_CONTEXT_HAS_VSYSCALL`, `MM_CONTEXT_LOCK_LAM`, `MM_CONTEXT_FORCE_TAGGED_SVA`, and `MM_CONTEXT_NOTRACK`. `mm_context_t` contains `ctx_id`, `tlb_gen`, `next_trim_cpumask`, optional `ldt_usr_sem`/`ldt`, LAM masks, `lock`, `vdso`, `vdso_image`, `perf_rdpmc_allowed`, pkey allocation fields, and broadcast TLB global ASID fields. `INIT_MM_CONTEXT()` initializes `init_mm` context.

## Control Flow
The fields are manipulated by context creation, duplication, exit, and `switch_mm` paths. TLB update paths increment `tlb_gen` after page-table modifications before flushing.

## State And Persistence
State is per-process address-space state. It persists for the lifetime of an `mm_struct` and is inherited or reset during fork/exec according to `mmu_context.h`.

## Dependencies And Integration Points
Depends on locks, atomics, LAM, pkeys, VDSO, uprobe IA32 mode, broadcast TLB flush, and paravirt/Xen behavior. It integrates with the scheduler, TLB flushing, mm teardown, perf RDPMC, and userspace address tagging.

## Risks And Edge Cases
`ctx_id` must not be reused. `tlb_gen` ordering is central to avoiding stale translations. LAM and DMA/SVA compatibility flags must be synchronized. LDT lifetime is security-sensitive.

## Test Signals
TLB shootdown tests, LAM tests, pkey tests, modify_ldt tests, VDSO mapping tests, perf RDPMC policy tests, and fork/exec stress are useful.
