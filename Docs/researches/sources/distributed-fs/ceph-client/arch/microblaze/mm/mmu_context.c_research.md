# sources/distributed-fs/ceph-client/arch/microblaze/mm/mmu_context.c

Purpose: manages MicroBlaze MMU address-space context IDs.

Important APIs and state: global `next_mmu_context`, `context_map`, `nr_free_contexts`, and `context_mm[]`; `mmu_context_init()` initializes reserved/free contexts; `steal_context()` reclaims one context.

Control flow: context zero is reserved for kernel. On exhaustion, `steal_context()` selects `next_mmu_context`, flushes that mm's TLB entries, and destroys its context.

State and persistence: persistent allocator state maps context IDs to `mm_struct` owners.

Dependencies and integration: used by `asm/mmu_context.h` helpers and TLB switch paths; `set_context` in assembly writes PID.

Risks and test signals: no LRU, so reclaim is pseudo-random and depends on `next_mmu_context` maintenance outside this file. Test many-process context rollover, TLB flush correctness, and kernel context reservation.
