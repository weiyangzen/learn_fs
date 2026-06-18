# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/64/hash.h

Purpose: supplies common 64-bit Book3S hash-MMU page-table operations used by the top-level page-table dispatcher.

Important APIs/types/functions: provides hash versions of PTE update, set, same/none checks, PMD/PUD bad/same checks, hugepage update and deposit/withdraw interfaces, hash vmemmap/kernel mapping functions, and transparent hugepage support hooks. It also supplies constants derived from hash 4K or 64K headers.

Control flow: inline operations generally preserve hash-specific HPTE flags while updating software PTE bits. Some paths delegate to extern implementations for hugepage, vmemmap, and kernel mapping operations. Compile-time page-size selection chooses 4K or 64K hash behavior.

State and persistence: state is encoded in Linux PTE/PMD/PUD values and HPTE tracking bits. External hash page-table state is managed by hash fault and flush implementations.

Dependencies and integration points: included by `book3s/64/pgtable.h` alongside radix support. It integrates with page faults, TLB/hash flushes, hugepage handling, vmemmap population, and kernel mapping setup.

Risks: hash PTE updates must coordinate with concurrent HPTE invalidation. Mistakes can leak stale hash translations. Hugepage behavior diverges sharply between 4K and 64K hash modes.

Test signals: hash MMU boot, page fault stress, `mprotect`, THP/hugetlb where supported, vmemmap population, kernel ioremap tests, and concurrent unmap/fault stress.
