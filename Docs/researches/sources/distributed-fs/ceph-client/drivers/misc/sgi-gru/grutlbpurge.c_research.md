# sources/distributed-fs/ceph-client/drivers/misc/sgi-gru/grutlbpurge.c

Purpose: integrates GRU TLB invalidation with Linux MMU notifier callbacks and provides low-level TGH-based flush helpers. It keeps GRU translations coherent with process address-space changes.

Important APIs/functions: exported helpers are `gru_flush_tlb_range()`, `gru_flush_all_tlb()`, `gru_register_mmu_notifier()`, `gru_drop_mmu_notifier()`, and `gru_tgh_flush_init()`. Internal helpers select and lock local or remote TGH handles, allocate/free notifier state, and implement `invalidate_range_start`/`invalidate_range_end`.

Control flow: when a range invalidation begins, the notifier increments `ms_range_active`, flushes GRU TLB entries for every GRU recorded in the address-space ASID map, and then completion of the invalidation decrements the range count and wakes waiters. For each GRU, active contexts receive a TGH invalidate command using the context bitmap; inactive contexts have their ASID cleared so a future load receives a fresh ASID. Full-chiplet flushes use a TGH invalidate over all ASIDs/contexts.

State and persistence: per-mm `gru_mm_struct` tracks `ms_asidmap` and `ms_asids[]` under `ms_asid_lock`, plus active invalidation count and wait queue. `gru_state` stores TGH selection parameters initialized by `gru_tgh_flush_init()`.

Dependencies and integration: depends on Linux MMU notifier APIs, UV topology, GRU TGH handle operations, and ASID state loaded in `grumain.c`. TLB preload/dropin paths outside this item observe `ms_range_active` and wait queues.

Risks: stale translations are the primary correctness risk. The code currently notes huge pages as TODO and uses `PAGE_SHIFT`. TGH selection uses private handles for local CPUs and locked shared handles for off-blade flushes; contention or bad topology setup can harm latency. Clearing ASIDs for inactive contexts trades correctness for future TLB-miss cost.

Test signals: exercise mmap/unmap/mprotect/fork/exit while GRU contexts are active, verify `flush_tlb*` stats, check ASID clearing on inactive contexts, and stress remote/off-blade invalidations and range-active waiters.
