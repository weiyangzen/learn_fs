# sources/distributed-fs/ceph-client/arch/powerpc/mm/book3s64/hash_hugepage.c

Purpose: Provides transparent huge page hash insertion for Book3S hash MMU, mapping a PMD-sized THP or devmap PMD with HPTEs whose actual page size is 16M while the base page size may be 4K or 64K.

Important APIs and functions: The sole exported implementation is `__hash_page_thp()`. It uses `get_hpte_slot_array()` to find the deposited PTE fragment used as per-subpage HPTE metadata, `hpte_valid()`, `hpte_hash_index()`, `mark_hpte_slot_valid()`, `flush_hash_hugepage()`, `htab_convert_pte_flags()`, and `mmu_hash_ops` update/insert/remove callbacks.

Control flow: The function atomically locks the PMD with `pmd_xchg()` and updates accessed/dirty state. It rejects non-THP PMDs by checking `H_PAGE_THP_HUGE`. It computes the base-page index within the huge PMD from the fault address and selected `psize`. For 4K base size, it invalidates older 64K HPTEs if the PMD was hashed without combo mode, then clears the slot array. If the target slot is valid it computes the global slot and tries `hpte_updatepp()`. On misses it inserts into primary then secondary hash groups, removing an entry and retrying when both are full. Finally it marks the slot valid, sets `H_PAGE_COMBO` for 4K base mappings, orders slot metadata with `smp_wmb()`, and clears `H_PAGE_BUSY`.

State and persistence: HPTE state is tracked by PMD bits plus the deposited PTE fragment slot array. The PMD busy bit serializes writers and protects slot-array updates. There is no persistent storage beyond in-memory page tables and hardware hash table entries.

Dependencies and integration: Invoked by `hash_page_mm()` when `find_linux_pte()` reports a huge PMD that is a THP. It integrates with `hash_pgtable.c` deposit/withdraw logic and native/pseries hash backends.

Risks: Slot-array lifetime is critical; withdraw/split paths must not race with hashing. The 4K fallback conversion path must clear old 64K metadata or future faults may update the wrong HPTE. Insert retry loops depend on backend eviction making progress.

Test signals: THP fault, split, collapse, mprotect, and devmap PMD tests on hash MMU are relevant. Useful stress signals include `stress_hpt`, concurrent THP collapse/split with page faults, and mixed 4K/64K slice page sizes.
