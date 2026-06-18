<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/kernel/dma.c -->
# sources/distributed-fs/ceph-client/arch/openrisc/kernel/dma.c

## Purpose
Implements OpenRISC DMA cache-coherency helpers for uncached kernel mappings and explicit cache maintenance.

## Important APIs, Types, And Functions
`arch_dma_set_uncached()` walks kernel page tables, sets `_PAGE_CI`, flushes TLB entries, and writes back D-cache lines. `arch_dma_clear_uncached()` clears `_PAGE_CI`. `arch_sync_dma_for_device()` flushes for `DMA_TO_DEVICE` and invalidates for `DMA_FROM_DEVICE`.

## Control Flow
The set/clear paths lock `init_mm`, use `walk_kernel_page_table_range()`, and call PTE callbacks. Sync paths switch on DMA direction.

## State And Persistence
Mutates kernel PTE cache-inhibit bits until cleared. Cache lines and TLB entries are transient hardware state.

## Dependencies And Integration Points
Depends on Linux DMA map ops, page table walkers, OpenRISC cacheflush and TLB APIs, and `_PAGE_CI`.

## Risks
Missing TLB flush leaves stale cacheable translations. `DMA_BIDIRECTIONAL` intentionally does no automatic maintenance, requiring caller-managed sync. Range alignment and page-table walk errors are important.

## Test Signals
DMA mapping tests with non-coherent devices, cache-inhibit PTE inspection, and data integrity for device read/write buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/kernel/dma.c -->
