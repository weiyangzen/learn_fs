# sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-udma.h

## Purpose
This header declares ivtv user-DMA helpers and inline DMA sync operations for the shared UDMA SG array.

## Important APIs, Types, and Functions
It declares page-info, SG-list, SG-array, setup, unmap, free, alloc, prepare, and start functions. Inline helpers `ivtv_udma_sync_for_device` and `ivtv_udma_sync_for_cpu` synchronize `itv->udma.SGarray` through `itv->udma.SG_handle`.

## Control Flow
There is no standalone flow. Callers allocate the shared SG array, set up a transfer, prepare/start it through the IRQ-arbitrated DMA engine, then unmap after completion.

## State and Persistence Behavior
The header stores no state. The declared implementation mutates pinned pages, SG mappings, DMA handles, and UDMA flags in `struct ivtv`.

## Dependencies and Integration Points
It depends on `struct ivtv`, `struct ivtv_user_dma`, `struct ivtv_dma_page_info`, V4L2/user buffers, DMA APIs, and decoder DMA registers.

## Risks
The sync helpers assume `SG_handle` is valid. Callers must serialize with `itv->udma.lock` and respect UDMA setup/unmap pairing.

## Test Signals
Build coverage, framebuffer DMA writes, YUV frame DMA, pending DMA interruption, and cleanup after mapping errors validate the interface.
