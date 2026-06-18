<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/tlb.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/asm/tlb.h

**Purpose:** Adapts generic TLB-gather freeing to Alpha page-table descriptor removal.

**Important APIs/types/functions:** `__pte_free_tlb` and `__pmd_free_tlb` mapped to `tlb_remove_ptdesc` with page or virtual ptdesc conversion.

**Control flow:** MM teardown queues freed page-table pages through generic TLB gather so actual freeing occurs after required TLB invalidation.

**State and persistence behavior:** No local state; operates on generic MMU gather batches.

**Dependencies and integration points:** Depends on `asm-generic/tlb.h`, ptdesc helpers, and Alpha page-table allocation.

**Risks:** Wrong ptdesc conversion can free incorrect page-table memory or race with active walkers.

**Test signals:** mmap/munmap teardown, exit, memory pressure, page-table debug, and TLB gather tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/tlb.h -->
