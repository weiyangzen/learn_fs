## sources/distributed-fs/ceph-client/arch/s390/mm/gmap_helpers.c

Purpose: provides exported helper routines for KVM guest mapping code to discard swapped userspace backing pages, mark PTEs as unused, and disable COW sharing for a process that backs guest memory.

Important APIs, types, and functions: exported functions are `gmap_helper_zap_one_page()`, `gmap_helper_discard()`, `gmap_helper_try_set_pte_unused()`, and `gmap_helper_disable_cow_sharing()`. Internal helpers include `ptep_zap_softleaf_entry()`, `find_zeropage_pte_entry()`, `find_zeropage_ops`, and `__gmap_helper_unshare_zeropages()`.

Control flow: `gmap_helper_zap_one_page()` requires the mmap lock, skips missing/hugetlb VMAs, obtains a locked PTE, and clears swap entries while adjusting mm counters and swap references. `gmap_helper_discard()` walks intersecting VMAs and zaps non-hugetlb ranges. `gmap_helper_try_set_pte_unused()` walks page-table levels locklessly enough to find a regular PTE, uses `spin_trylock()` on the PTE lock to avoid inversion with KVM mmu_lock, validates the PMD, and atomically sets `_PAGE_UNUSED`. `gmap_helper_disable_cow_sharing()` requires write mmap lock, flips `mm->context.allow_cow_sharing`, unshares mapped zeropages through page walking and `FAULT_FLAG_UNSHARE`, disables KSM, and rolls back the flag on error.

State and persistence: mutates PTEs, swap counters, swap references, VMA mappings through zap operations, and `mm->context.allow_cow_sharing`. It can disable KSM for the process but notes user space can re-enable it.

Dependencies and integration points: depends on Linux pagewalk, swap/softleaf helpers, KSM, hugetlb checks, mmap locking, and s390 `_PAGE_UNUSED`. It is exported GPL for KVM gmap users that need memory discard semantics and private/nonshared backing.

Risks: `gmap_helper_try_set_pte_unused()` intentionally skips optimization on lock contention; callers must tolerate normal swapping. COW-sharing disable does not address fork-shared anonymous pages, only KSM and zeropages. Zeropage unshare loops must handle races where faulting does not immediately replace the zeropage. Incorrect lock context can deadlock or violate assertions.

Test signals: KVM guest memory tests should verify swapped pages are discarded, hugetlb VMAs are skipped, unused-page optimization does not deadlock under mmu_notifier contention, KSM is disabled, zeropages are replaced with anonymous pages, and errors restore `allow_cow_sharing`.
