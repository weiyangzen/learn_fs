<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_res_cursor.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_res_cursor.h

Purpose: provides inline cursor utilities for walking TTM resources, scatter-gather tables, and `drm_pagemap_addr` arrays as contiguous DMA/resource segments.

Important APIs and control flow: `xe_res_first()` initializes from a TTM resource and handles VRAM/stolen gpu-buddy blocks or falls back to TT-style offsets. `xe_res_first_sg()` and `xe_res_first_dma()` initialize from SG and DMA page-map sources. `xe_res_next()` advances by bytes, moving across buddy blocks, SG elements, or coalesced DMA elements. `xe_res_dma()` returns the current DMA/resource address and `xe_res_is_vram()` identifies same-device VRAM segments.

State and dependencies: `struct xe_res_cursor` tracks segment start, size, remaining bytes, backing node, memory type, SG pointer, DMA page-map pointer, buddy allocator, and coalesced DMA metadata. It depends on TTM managers, Xe VRAM manager resources, DRM pagemap metadata, and interconnect protocol flags.

Risks and test signals: off-by-one and alignment bugs here affect BO copies and migrations. Tests should cover multi-block VRAM resources, TT fallback, SG advancement, DMA coalescing only when contiguous and same protocol, zero remaining behavior, and `xe_res_is_vram()` for VRAM versus system memory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_res_cursor.h -->
