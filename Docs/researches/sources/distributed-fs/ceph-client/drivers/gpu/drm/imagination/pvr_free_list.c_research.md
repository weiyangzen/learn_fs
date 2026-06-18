# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_free_list.c

## Purpose
Implements PowerVR parameter-manager free lists: kernel bookkeeping, firmware-facing freelist structures, host-side growth on firmware requests, reconstruction after HWR, and lifetime management for free lists referenced by HWRT datasets.

## Important APIs, types, and functions
- `pvr_get_free_list_min_pages()` returns the minimum local freelist size, with RogueXE and BRN66011-specific thresholds.
- `pvr_free_list_create()` validates UAPI create arguments, binds the userspace-provided PM/FW protected list BO, allocates a firmware ID, creates the FW freelist object, and seeds it with initial pages.
- `pvr_free_list_process_grow_req()` handles firmware FWCCB grow requests and replies with `ROGUE_FWIF_KCCB_CMD_FREELIST_GROW_UPDATE`.
- `pvr_free_list_process_reconstruct_req()` rebuilds one or more free lists and sends `FREELISTS_RECONSTRUCTION_UPDATE`.
- Internal helpers include `free_list_create_kernel_structure()`, `free_list_fw_init()`, `pvr_free_list_grow()`, `pvr_free_list_insert_node_locked()`, and `calculate_free_list_ready_pages_locked()`.

## Control flow
Creation checks growth invariants, alignment to `ROGUE_BIF_PM_FREELIST_BASE_ADDR_ALIGNSIZE`, nonzero maximum pages, and that the target GPU virtual address maps to a PM/FW protected GEM object with no CPU userspace access. The free list is assigned a global firmware ID via `pvr_dev->free_list_ids`, then a FW object is initialized and `pvr_free_list_grow()` allocates the initial backing pages.

Growing allocates a `pvr_free_list_node`, creates a cached device GEM allocation sized in PM physical pages, walks its DMA pages, writes PFNs into the freelist stack object from the calculated stack offset, and reserves `ready_pages` so firmware can handle OOM quickly before host growth completes. Firmware grow requests first account for previously consumed ready pages, attempt another grow of `grow_pages`, then report new and ready page counts back through KCCB.

Reconstruction looks up each FW freelist ID, rebuilds the freelist stack from the tracked memory-block list, resets firmware counters in the mapped freelist structure, and marks attached HWRT data as HWR while clearing `HWRTDATA_HAS_LAST_GEOM`.

## State and persistence
Persistent state lives in `struct pvr_free_list`: FW ID, current/max/grow/ready pages, the userspace freelist GEM BO, FW object, GPU address, memory block list, and HWRT linkage list. `free_list_ids` maps FW IDs to live objects and `pvr_file->free_list_handles` owns file handles. Page memory persists as `pvr_free_list_node` objects until release. The FW freelist struct stores current stack top, device address, grow state, and page counters.

## Dependencies and integration points
Depends on GEM allocation/mapping, VM lookup of userspace GPU addresses, FW object helpers, xarrays, KCCB/FWCCB messaging, Rogue FWIF layouts, and HWRT datasets. HWRT data is linked to the local freelist so reconstruction can reset render-target state. Release invokes `pvr_fw_structure_cleanup()` and may process pending FWCCB work before retrying cleanup when firmware reports busy.

## Risks
The page-count arithmetic is alignment-sensitive and uses reserved ready pages, so off-by-one or underflow errors can corrupt the freelist stack. Growth updates host state before KCCB response and must stay consistent with firmware consumption. Reconstruction maps HWRT FW objects inside the freelist lock; errors are warning-only. FW cleanup returning `-EBUSY` is retried once after FWCCB processing, so persistent firmware ownership still becomes a warning path.

## Test signals
Exercise create argument validation, PM/FW-protected BO requirements, initial grow, grow request response counts, reconstruction after HWR, HWRT unlink on destroy, and cleanup busy retry. Useful runtime signals are WARNs from malformed IDs, invalid DMA PFN width, FW cleanup failures, KCCB send failures, and successful page-count changes visible in firmware traces.
