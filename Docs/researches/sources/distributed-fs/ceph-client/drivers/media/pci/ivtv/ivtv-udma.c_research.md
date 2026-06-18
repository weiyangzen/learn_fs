# sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-udma.c

## Purpose
This file implements user-memory DMA support for sending userspace buffers to the decoder/OSD side of the ivtv hardware. It pins user pages, handles highmem bounce pages, builds Linux and hardware scatter-gather lists, starts decoder DMA, and unmaps resources.

## Important APIs, Types, and Functions
Public functions are `ivtv_udma_get_page_info`, `ivtv_udma_fill_sg_list`, `ivtv_udma_fill_sg_array`, `ivtv_udma_alloc`, `ivtv_udma_setup`, `ivtv_udma_unmap`, `ivtv_udma_free`, `ivtv_udma_start`, and `ivtv_udma_prepare`.

## Control Flow
Setup computes page span and offsets for the user buffer, pins pages with `pin_user_pages_unlocked`, fills a software scatterlist, allocates/copies bounce pages for highmem pages, maps the SG list for DMA-to-device, converts it into the CX2341x SG array, marks the last element with the interrupt bit, and syncs the SG array for the device. Prepare either starts DMA immediately under `dma_reg_lock` or marks UDMA pending. IRQ completion or callers later unmap SG mappings and unpin pages.

## State and Persistence Behavior
The file mutates `itv->udma` fields: pinned page array, bounce pages, `page_count`, `SG_length`, SG array, SG DMA handle, and UDMA pending/in-progress flags. Bounce pages and the SG array mapping persist across individual transfers until module/card cleanup.

## Dependencies and Integration Points
It depends on Linux GUP, scatterlist, DMA mapping/sync APIs, highmem mapping, ivtv IRQ DMA arbitration, framebuffer writes, and YUV frame DMA paths.

## Risks
Pinned user pages must be released on every error path. Highmem bounce handling copies data before DMA and assumes write-only device direction. SG array bounds depend on caller-provided maximum page capacity. Starting UDMA shares the decoder DMA engine with normal stream DMA, so flag arbitration must be correct.

## Test Signals
Exercise aligned and unaligned userspace buffers, multi-page and single-page transfers, highmem bounce paths where possible, signal interruption while pending, DMA mapping failures, repeated OSD/YUV transfers, and cleanup with active or failed UDMA setup.
