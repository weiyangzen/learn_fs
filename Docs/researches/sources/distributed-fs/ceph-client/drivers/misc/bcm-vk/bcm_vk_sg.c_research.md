# sources/distributed-fs/ceph-client/drivers/misc/bcm-vk/bcm_vk_sg.c

## Purpose
`bcm_vk_sg.c` converts user-space buffers described in VK messages into DMA-mapped scatter-gather lists that firmware can consume, and frees those mappings when a request completes or is drained.

## Important APIs, Types, and Functions
The public APIs are `bcm_vk_sg_alloc()` and `bcm_vk_sg_free()`. Internal helpers `bcm_vk_dma_alloc()` and `bcm_vk_dma_free()` pin user pages, allocate a coherent SGL buffer, map pages with `dma_map_page()`, coalesce physically contiguous mappings up to `BCM_VK_MAX_SGL_CHUNK` (16 MiB), write firmware `_vk_data` entries, and unmap/free resources.

## Control Flow
For each non-empty `_vk_data`, allocation reads the packed user pointer, calculates page span and first-page offset, allocates a page-pointer array, pins pages with write access for device-to-host transfers, allocates coherent memory for the firmware SGL, maps pages, compresses contiguous DMA ranges, and replaces the original user pointer and size with the DMA address and SGL byte size. Public allocation rolls back already completed planes on failure. Free walks all populated DMA descriptors, unmaps each SGL range, frees coherent memory, puts pinned pages, frees the page array, and clears `sglist`.

## State and Persistence
State lives in caller-owned `struct bcm_vk_dma` arrays. Each descriptor owns pinned pages, a coherent SGL buffer, DMA handle, length, mapping direction, and page count. There is no persistent module state.

## Dependencies and Integration Points
The file depends on Linux DMA mapping, GUP, page, vmalloc/slab helpers, unaligned accessors, VK UAPI `_vk_data` layout, and `bcm_vk_msg.c` transfer-buffer handling. Firmware sees the generated little-endian SGL header and entries through the DMA address stored back into `_vk_data`.

## Risks and Edge Cases
Failure paths inside `bcm_vk_dma_alloc()` can leak pinned pages or mappings if coherent allocation or a later page mapping fails before `dma->sglist` is established for outer cleanup. `get_user_pages_fast()` pinning semantics require careful direction handling and dirty-page expectations for `DMA_FROM_DEVICE`. The SGL allocation assumes one entry per page is enough before coalescing. Zero size/address pairs are treated as no-op planes, while half-empty pairs are errors.

## Test Signals
Exercise aligned and unaligned buffers, multi-page buffers, physically contiguous coalescing, four-plane transfers, zero planes, invalid half-empty descriptors, GUP failure, DMA mapping failure fault injection, and free-after-partial-allocation paths with page-pin leak detection.
