<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/tlbflush.h -->
# sources/distributed-fs/ceph-client/arch/openrisc/include/asm/tlbflush.h

## Purpose
Declares local and SMP-aware TLB invalidation APIs for OpenRISC.

## Important APIs, Types, And Functions
Local functions include `local_flush_tlb_all()`, `local_flush_tlb_mm()`, `local_flush_tlb_page()`, and `local_flush_tlb_range()`. Non-SMP maps generic names directly to local versions; SMP declares global versions implemented in `smp.c`. `flush_tlb()` flushes `current->mm`, and `flush_tlb_kernel_range()` routes through range flushing.

## Control Flow
Memory-management updates call these hooks after page table changes. SMP builds target remote CPUs through IPI helpers in `kernel/smp.c`.

## State And Persistence
Invalidates hardware DTLB and ITLB entries. No software state is stored here.

## Dependencies And Integration Points
Depends on `mm_struct`, `vm_area_struct`, current task state, and OpenRISC processor definitions. Used by page faults, DMA cache-inhibit changes, fixmap setup, and generic mm.

## Risks
`flush_tlb()` assumes `current->mm` is non-null. Kernel range flushing with `vma == NULL` must be handled by the implementation, especially on SMP.

## Test Signals
TLB invalidation after mprotect, munmap, vmalloc, module loading, DMA uncached mapping, and SMP shootdown tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/tlbflush.h -->
