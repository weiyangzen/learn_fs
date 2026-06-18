# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnge/bnge_rmem.h

## Purpose
This header defines the ring-memory and context-memory data structures used to allocate hardware-visible DMA rings and firmware backing-store pages for `bnge`.

## Important APIs, Types, And Functions
Important types are `struct bnge_ring_mem_info`, `struct bnge_ctx_pg_info`, `struct bnge_ctx_mem_type`, `struct bnge_ctx_mem_info`, and `struct bnge_ring_struct`. It defines PTE flags, hardware-supported page-size selection, context type aliases, backing-store constants, TQM limits, context initialization fields, and public APIs `bnge_alloc_ring`, `bnge_free_ring`, `bnge_alloc_ctx_mem`, `bnge_free_ctx_mem`, and `bnge_init_ring_struct`.

## Control Flow
The header underpins two flows. Descriptor rings fill `bnge_ring_mem_info` with page arrays and optional software vmem, then call `bnge_alloc_ring`. Firmware backing-store flow fills `bnge_ctx_mem_type` from qcaps, allocates `bnge_ctx_pg_info` page tables, and passes those to HWRM backing-store config.

## State And Persistence
Ring memory state tracks DMA page arrays, page-table DMA address, allocation depth, flags, and optional software memory. Context memory state tracks valid context types, entry sizes, instance bitmaps, initialization patterns, max/min entries, split entries, and allocated page-info arrays. `bnge_ring_struct` adds firmware ring ID, group/map index, handle, and queue ID.

## Dependencies And Integration Points
It relies on HSI backing-store type constants and is consumed by `bnge_rmem.c`, `bnge_netdev.c`, `bnge_hwrm_lib.c`, and `bnge_resc.c`. Page-size macros must remain compatible with RX descriptor length limits.

## Risks
Compile-time page-size selection changes ring geometry and maximum descriptor counts. Context type ranges (`BNGE_CTX_MAX`, `BNGE_CTX_L2_MAX`, `BNGE_CTX_V2_MAX`) must stay aligned with firmware HSI. `BNGE_SET_CTX_PAGE_ATTR` maps only supported page sizes and is reused by HWRM backing-store configuration.

## Test Signals
Build across page-size configurations, ring allocation with one and multiple pages, context qcaps/config on L2-only and RoCE-capable devices, and repeated allocation/free with fault injection.
