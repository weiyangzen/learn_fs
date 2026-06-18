# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnge/bnge_rmem.c

## Purpose
This file allocates and frees DMA ring memory and firmware backing-store context memory. It builds page tables for hardware rings, initializes context memory with firmware-requested values, configures backing store through HWRM, and initializes each netdev ring's `bnge_ring_mem_info` before allocation.

## Important APIs, Types, And Functions
Public functions are `bnge_alloc_ring`, `bnge_free_ring`, `bnge_alloc_ctx_mem`, `bnge_free_ctx_mem`, and `bnge_init_ring_struct`. Important internal helpers are `bnge_init_ctx_mem`, `bnge_alloc_ctx_one_lvl`, `bnge_alloc_ctx_pg_tbls`, `bnge_free_ctx_pg_tbls`, `bnge_setup_ctxm_pg_tbls`, and `bnge_backing_store_cfg`.

## Control Flow
Ring allocation optionally allocates a page-table DMA block, allocates each DMA page, writes valid/last PTE bits, optionally initializes context pages, and optionally allocates software virtual memory. Context allocation first queries qcaps, computes L2 plus optional RoCE QP/SRQ/CQ/TIM/TQM entries, allocates one- or two-level page tables, and sends backing-store config for all valid context types. Free paths walk the same nested page-table structures and release DMA/vmalloc/kzalloc memory.

## State And Persistence
`bnge_ring_mem_info` records page arrays, DMA arrays, page table, depth, flags, vmem pointer, and optional context type. `bd->ctx` holds `bnge_ctx_mem_info`, each valid `bnge_ctx_mem_type`, and allocated `bnge_ctx_pg_info` arrays. `BNGE_CTX_FLAG_INITED` marks that backing store was configured.

## Dependencies And Integration Points
It depends on HWRM backing-store qcaps/cfg wrappers, `bnge_netdev.h` ring page counts and descriptor sizes, `bnge_resc.h` sizing helper, Linux coherent DMA, vmalloc, and kdump/RoCE state.

## Risks
Partial allocation paths can leave nested context page tables requiring complete cleanup. Multi-level page-table construction uses fixed `MAX_CTX_PAGES` limits and must preserve firmware depth/page-size expectations. RoCE-enabled paths allocate much larger two-level contexts and are skipped in kdump.

## Test Signals
Open/close with normal L2, RoCE enabled, kdump kernel behavior, large firmware context requirements, and injected DMA allocation failures. Validate HWRM backing-store config success and no DMA leaks across repeated probe/remove.
