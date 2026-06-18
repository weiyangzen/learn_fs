<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/mm/dma-noncoherent.c -->
# sources/distributed-fs/ceph-client/arch/riscv/mm/dma-noncoherent.c

## Purpose
`dma-noncoherent.c` provides RISC-V cache maintenance hooks for noncoherent DMA devices.

## Important APIs, Types, And Functions
It exports `dma_cache_alignment`, `arch_sync_dma_for_device()`, `arch_sync_dma_for_cpu()`, `arch_dma_prep_coherent()`, `arch_setup_dma_ops()`, `riscv_noncoherent_supported()`, and `riscv_set_dma_cache_alignment()`. Internal helpers perform writeback, invalidate, and writeback+invalidate through nonstandard ops or `ALT_CMO_OP`.

## Control Flow
DMA sync for device chooses clean/invalidate/flush based on direction and whether CPU post-flush is expected. Sync for CPU invalidates FROM_DEVICE/BIDIRECTIONAL buffers. Setup warns when noncoherent devices lack supported operations or block alignment exceeds `ARCH_DMA_MINALIGN`, then records `dev->dma_coherent`.

## State And Persistence
Runtime state is `noncoherent_supported` and exported `dma_cache_alignment`. Device DMA coherency is stored in each `struct device`.

## Dependencies And Integration Points
It depends on CBO block sizes, nonstandard cache callback registration, DMA mapping core, and device-tree/ACPI coherency decisions.

## Risks
Wrong maintenance direction corrupts DMA data. Unsupported noncoherent devices are tainted but may still malfunction. Cache block size larger than DMA alignment risks partial-line sharing.

## Test Signals
DMA mapping tests on coherent and noncoherent devices, streaming DMA to/from devices, SWIOTLB bounce tests, and nonstandard cache-op platforms are relevant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/mm/dma-noncoherent.c -->
