<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s32/hash_low.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s32/hash_low.S

## Purpose
This assembly file implements low-level 32-bit Book3S hash MMU operations: handling hash misses, inserting HPTEs, and flushing hash table entries.

## Important APIs, types, and functions
It defines `_GLOBAL(hash_page)`, `_GLOBAL(add_hash_page)`, `_GLOBAL(create_hpte)`, and `_GLOBAL(flush_hash_pages)`, exporting `flush_hash_pages`. It uses patch sites `patch__hash_page_*` and `patch__flush_hash_*`, `_PAGE_HASHPTE`, `_PAGE_ACCESSED`, `_PAGE_DIRTY`, PTE flags, VSID hashing, `mmu_hash_lock`, `tlbie`, and `TLBSYNC`.

## Control flow
`hash_page` runs on ISI/DSI hash misses, locates the Linux PTE, verifies requested permissions (including KUAP restrictions), atomically sets accessed/dirty/has-HPTE bits, computes the segment VSID, inserts an HPTE, releases the SMP hash lock, and returns through `fast_hash_page_return`. `add_hash_page` preloads an HPTE for a PTE by disabling interrupts/data translation, taking the hash lock, setting `_PAGE_HASHPTE`, and calling `create_hpte`. `create_hpte` converts Linux PTE flags to PPC HPTE words, searches primary and secondary PTEGs for matching or empty slots, and evicts a rotating primary slot if full. `flush_hash_pages` clears `_PAGE_HASHPTE`, invalidates matching primary/secondary HPTEs, executes `tlbie`, and handles ranges.

## State and persistence behavior
It mutates Linux PTE flags, the hardware hash table, TLB state, `next_slot`, and `mmu_hash_lock`. It temporarily disables interrupts and data relocation in selected paths.

## Dependencies and integration points
Called from exception handlers, `book3s32/mmu.c` hash preloading, and `book3s32/tlb.c` flush wrappers. It depends on early/runtime hash table patching by `MMU_init_hw_patch`.

## Risks and edge cases
Risks include SMP races between PTE and HPTE updates, stale TLB entries, 64-bit PTE upper-word dependencies, KUAP permission filtering, hash table full eviction, and correctness while data relocation is disabled.

## Test signals
Signals include successful page fault resolution, correct permission faults, stable SMP operation, TLB flush correctness, and absence of hash-table corruption under memory pressure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s32/hash_low.S -->
