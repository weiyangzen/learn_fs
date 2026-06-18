<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/tlbflush.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/asm/tlbflush.h

**Purpose:** Defines Alpha TLB flush helpers for current mm, pages, ranges, all address spaces, and kernel ranges. EV5/EV6 paths use ASN invalidation where possible.

**Important APIs/types/functions:** `flush_tlb_current`, `flush_tlb_current_page`, `flush_tlb_all`, `flush_tlb_mm`, `flush_tlb_page`, `flush_tlb_range`, and `flush_tlb_kernel_range` plus `__load_new_mm_context` integration.

**Control flow:** For EV5-style builds, flushing the current mm reloads the mm context; flushing a page can call `tbis`. Non-current mm flushes invalidate `mm->context` entries so the next switch allocates a new ASN. Generic or SMP paths may use external implementations.

**State and persistence behavior:** Mutates per-mm context versions, current PCB ASN, and CPU TB contents.

**Dependencies and integration points:** Depends on `mmu_context.h`, PAL TBI calls, scheduler current mm, and generic VM invalidation callers.

**Risks:** Too-narrow flushes leave stale translations; too-broad flushes cost performance. Current-versus-noncurrent mm distinction must be correct under SMP.

**Test signals:** mprotect/COW/unmap tests, kernel vmalloc/ioremap flush tests, migration/compaction, and SMP TLB shootdown workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/tlbflush.h -->
