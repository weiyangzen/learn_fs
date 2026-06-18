<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nohash/pgtable.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nohash/pgtable.h

## Purpose
This header is the common nohash page-table operation layer shared by 32-bit and 64-bit backends. It defines kernel protections, generic PTE mutation, access-bit helpers, and permission predicates.

## Important APIs, Types, And Functions
It selects the 32-bit or 64-bit pgtable header, defines `_PAGE_CHG_MASK`, `PAGE_KERNEL*`, and helpers including `pte_update()`, `ptep_test_and_clear_young()`, `ptep_set_wrprotect()`, `ptep_get_and_clear()`, `pte_clear()`, `__ptep_set_access_flags()`, `pte_mkwrite_novma()`, `pte_mkdirty()`, `pte_mkyoung()`, `pte_wrprotect()`, `pte_mkexec()`, `pte_write()`, `pte_dirty()`, `pte_special()`, `pte_none()`, `pte_present()`, `pte_hw_valid()`, `pte_young()`, `pte_read()`, `pte_access_permitted()`, and `pte_user_accessible_page()`.

## Control Flow
Existing valid PTE modifications flow through `pte_update()`, which may update multiple entries for huge mappings, mark 44x executable I-cache flush state, and assert PTE locking for non-huge updates. Access-flag changes flush the corresponding TLB page.

## State And Persistence Behavior
PTE state persists in page tables. `icache_44x_need_flush` is set when executable user mappings change on 44x. Page-table check hooks observe clear operations.

## Dependencies And Integration Points
It depends on the selected backend, `linux/page_table_check.h`, nohash TLB flushing, and generic MM expectations for arch PTE operations.

## Risks And Edge Cases
Huge mapping updates advance PFNs across page-directory-sized chunks. Lock assertions differ for huge and normal mappings. Permission helpers must respect backend-specific `_PAGE_READ` semantics, especially Book3E BAP bits.

## Test Signals
Run mprotect, COW, page aging, reclaim, hugepage, 44x executable mapping, page-table-check, and TLB shootdown tests across nohash backends.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nohash/pgtable.h -->
