# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/64/tlbflush.h

Purpose: provides common Book3S64 TLB flush wrappers that dispatch to hash or radix implementations.

Important APIs/types/functions: includes hash/radix flush headers and defines common `flush_tlb_mm`, `flush_tlb_page`, `flush_tlb_range`, `flush_tlb_kernel_range`, `local_flush_tlb_*`, `tlb_flush`, and page-size-aware helpers.

Control flow: wrappers branch on `radix_enabled()` to select radix invalidation; otherwise they call hash flush routines. Some helpers are no-ops or aliases when the active MMU does not need separate local handling.

State and persistence: affects hardware translation caches and, in hash mode, HPTE state. No private state is stored.

Dependencies and integration points: used by common mmu_gather, page-table update, mprotect, unmap, and kernel mapping code.

Risks: dispatch must match the active MMU mode. Mixing hash and radix flush semantics would leave stale translations or call unsupported operations.

Test signals: hash/radix boot matrices, mmu_gather teardown tests, SMP shootdown, mprotect/unmap stress, and kernel-range flush tests.
