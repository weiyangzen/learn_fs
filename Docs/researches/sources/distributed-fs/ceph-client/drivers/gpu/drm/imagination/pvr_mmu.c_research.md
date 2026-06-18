# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_mmu.c

## Purpose
Implements the PowerVR device MMU page-table manager. It creates and destroys MMU contexts, maps scatter-gather backed GEM memory into GPU virtual addresses, unmaps ranges, tracks host-side mirror page tables, syncs table memory for device consumption, and sends firmware MMU cache/TLB flush commands when mappings change.

## Important APIs, types, and functions
- Public APIs: `pvr_mmu_flush_request_all()`, `pvr_mmu_flush_exec()`, `pvr_mmu_context_create()`, `pvr_mmu_context_destroy()`, `pvr_mmu_get_root_table_dma_addr()`, `pvr_mmu_op_context_create()`, `pvr_mmu_op_context_destroy()`, `pvr_mmu_map()`, and `pvr_mmu_unmap()`.
- Backing memory: `struct pvr_mmu_backing_page` wraps one zeroed host page, CPU mapping, DMA address, raw page pointer, and owning `pvr_device`.
- Raw tables: `struct pvr_page_table_l2_entry_raw`, `pvr_page_table_l1_entry_raw`, `pvr_page_table_l0_entry_raw`, `pvr_page_flags_raw`, and raw L2/L1/L0 table structs encode Rogue MMU entries with compile-time size checks.
- Mirror tables: `struct pvr_page_table_l2`, `pvr_page_table_l1`, and `pvr_page_table_l0` mirror the hardware tree and track children, parents, parent indices, and entry counts.
- Operation state: `struct pvr_mmu_context`, `struct pvr_page_table_ptr`, and `struct pvr_mmu_op_context` cache traversal position, preallocated tables for map operations, freed tables from unmaps, SG mapping parameters, and required sync level.
- Core helpers include table entry set/clear/is-valid helpers, `pvr_page_table_l1_get_or_insert()`, `pvr_page_table_l0_get_or_insert()`, `pvr_mmu_op_context_set_curr_page()`, `pvr_mmu_op_context_next_page()`, `pvr_page_create()`, `pvr_page_destroy()`, and `pvr_mmu_map_sgl()`.

## Control flow
MMU cache flushing is flag driven. Table writes call `pvr_mmu_set_flush_flags()` through sync helpers. `pvr_mmu_flush_exec()` atomically consumes `pvr_dev->mmu_flush_cache_flags`, skips work before firmware boot or when no flags are pending, sends a `ROGUE_FWIF_KCCB_CMD_MMUCACHE` command, waits for completion, and hard-resets the GPU once before retrying. If retry or waited completion fails, it marks the device lost.

Context creation allocates a root L2 table and stores the owning device. Operation context creation optionally preallocates enough L1/L0 tables for a requested mapping range, using the supplied size and offset. Mapping calls set the current GPU page with creation enabled, derive L0 flags from GEM BO flags, walk the DMA SG table from `sgt_offset`, call `pvr_mmu_map_sgl()` for each covered segment, and roll back already-created pages if a later segment fails. Unmapping sets the current page without creation, skips missing intermediate tables, clears existing leaf entries, and queues empty L0/L1 tables for later freeing.

Traversal flushes stale tables before changing cached pointers. `pvr_mmu_op_context_next_page()` increments L0, then L1, then L2 indices and syncs levels that are about to be unloaded. Insertion uses preallocated table lists, issues write memory barriers before linking parent entries, and marks the needed parent sync level. Removal clears raw parent entries, detaches mirror child pointers, moves emptied tables to free lists, and recursively removes empty parents. Operation context destruction performs the remaining page-table sync, immediately waits for a firmware flush for unmaps, frees unused preallocations and unmap-deleted tables, then frees the op context.

## State and persistence
Persistent driver state is the root and child mirror page-tree under each `pvr_mmu_context`, plus DMA-backed raw table pages visible to the GPU. Per-operation state is transient but can mutate persistent mappings by inserting or deleting table entries. `pvr_dev->mmu_flush_cache_flags` coalesces cache/TLB flush requirements across page-table writes until `pvr_mmu_flush_exec()` consumes it. Mapped GPU virtual addresses persist until explicitly unmapped or the owning VM/MMU context is destroyed.

## Dependencies and integration points
The file depends on PowerVR device, firmware, KCCB, GEM flags, Rogue firmware interface, and Rogue MMU register-definition headers. It uses Linux page allocation, `vmap()`, DMA mapping/sync APIs, SG iteration, atomics, barriers, `drm_dev_enter()`, and runtime device-loss handling through `pvr_power_reset()` and `pvr_device_lost()`. VM code obtains the root table DMA address for firmware memory contexts and creates op contexts around VM bind/unbind operations.

## Risks
Flush failure is treated as memory-corruption risk and escalates to reset/device loss, so KCCB wait behavior is critical. Table range preallocation uses `sgt_offset + size` to estimate table counts; boundary conditions around exact table-size multiples deserve scrutiny. Mapping rollback only unmaps pages counted as successfully mapped and must preserve traversal state exactly. The code assumes callers pass page-aligned sizes and device addresses; some validation exists for mapping size/SG offsets, but index helpers do not bounds-check. Non-coherent DMA paths rely on the correct sync level and leaf-to-root sync ordering.

## Test signals
Useful signals are successful VM bind/unbind under sparse and multi-SG objects, `-EEXIST` on double-map attempts, no leaks from failed map preallocation or mid-SG rollback, correct firmware MMU cache commands, reset/device-lost logs on forced KCCB failures, and GPU page-fault behavior after unmap. Boundary tests should cover L0/L1/L2 index rollover, zero-size map/unmap, offsets into SG entries, non-coherent DMA devices, and mappings crossing table boundaries.
