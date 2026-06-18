<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/dma.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/dma.h

## Purpose
Provides legacy DMA constants and declarations for Xtensa, mainly for generic driver compatibility.

## Important APIs, Types, And Functions
Defines `MAX_DMA_CHANNELS`, `MAX_DMA_ADDRESS`, and declares `request_dma` and `free_dma`.

## Control Flow
No inline runtime flow; platform or generic code supplies channel allocation behavior.

## State And Persistence
No owned state. DMA channel state is managed by implementations elsewhere.

## Dependencies And Integration Points
Depends on `asm/io.h`, page/memory layout, and legacy drivers that still probe ISA/PC-style DMA APIs.

## Risks And Edge Cases
`MAX_DMA_ADDRESS` is platform-sensitive and assumes DMA can target the statically mapped kernel segment. Incorrect value causes bad bounce-buffer decisions or inaccessible DMA memory.

## Test Signals
Build legacy DMA users, run DMA-capable platform tests, and verify `MAX_DMA_ADDRESS` against board memory maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/dma.h -->
