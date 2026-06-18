# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/32/pgtable.h

Purpose: defines the 32-bit Book3S Linux page-table format, permission/cache bits, virtual layout, PTE update primitives, swap encoding, and pgprot helpers for classic hash MMU processors.

Important APIs/types/functions: key macros are `_PAGE_PRESENT`, `_PAGE_HASHPTE`, `_PAGE_READ`, `_PAGE_WRITE`, `_PAGE_EXEC`, `_PAGE_*CACHE*`, `PTE_RPN_MASK`, `_PAGE_CHG_MASK`, `PAGE_KERNEL*`, index sizes, `VMALLOC_START/END`, and swap encoders. Functions include `map_kernel_page()`, `unmap_kernel_page()`, `flush_hash_entry()`, `pte_update()`, `ptep_get_and_clear()`, `ptep_set_wrprotect()`, `__ptep_set_access_flags()`, PTE accessors/modifiers, `pfn_pte()`, `__set_pte_at()`, and pgprot cache transformations.

Control flow: PTE changes call `pte_update()` for atomic hash-safe updates when needed, flush hash entries when clearing accessed or replacing hashed 64-bit PTEs, and select simple stores for UP/per-CPU cases. Access-flag updates set dirty/accessed/RW/exec bits and flush the TLB page.

State and persistence: state is Linux page-table memory plus cached HPTE state signaled by `_PAGE_HASHPTE`. Virtual layout constants define vmalloc/ioremap/fixmap relationships for the boot lifetime.

Dependencies and integration points: depends on generic folded PMD headers, page table checks, scheduler/thread definitions, KASAN, highmem, hash TLB flushing, and MMU feature detection.

Risks: `_PAGE_HASHPTE` preservation is central to avoiding stale hash entries. 64-bit PTE store ordering uses `eieio` between halves. Swap encoding borrows bits and must not collide with present/hash markers. Vmalloc/ioremap layout can clash with early mappings on large RAM systems.

Test signals: hash page fault tests, `mprotect`, fork, swap, THP-disabled page-table walks, KASAN vmalloc configs, highmem configs, and stress that clears accessed/dirty bits while faults occur.
