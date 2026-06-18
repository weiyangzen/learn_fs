<!-- Source: sources/distributed-fs/ceph-client/fs/nfs/blocklayout/blocklayout.c -->
# sources/distributed-fs/ceph-client/fs/nfs/blocklayout/blocklayout.c

## Purpose
Implements the NFSv4.1 pNFS block and SCSI layout driver. It translates pNFS block extents into block-device BIOs, handles parallel BIO completion, decodes/validates layout segments, manages extent returns/commits, enforces alignment for pageio coalescing, and registers layoutdriver types.

## Important APIs, Types, And Functions
Key layoutdriver callbacks are `bl_read_pagelist()`, `bl_write_pagelist()`, `bl_alloc_layout_hdr()`, `sl_alloc_layout_hdr()`, `bl_free_layout_hdr()`, `bl_alloc_lseg()`, `bl_free_lseg()`, `bl_return_range()`, `bl_prepare_layoutcommit()`, `bl_cleanup_layoutcommit()`, `bl_set_layoutdriver()`, and pageio ops. Internal helpers include `do_add_page_to_bio()`, `bl_submit_bio()`, `bl_mark_devices_unavailable()`, `verify_extent()`, `decode_sector_number()`, `bl_find_get_deviceid()`, and `is_aligned_req()`.

## Control Flow
Read/write pagelist paths allocate a `parallel_io`, start a blk plug, walk pages and pNFS extents, map file sectors through extent volume offsets and device maps, build/submit BIOs, and complete through end_io callbacks. Read holes are zero-filled without device IO. BIO errors set `pnfs_error`, mark layout failure, and mark deviceids unavailable. Last BIO completion schedules cleanup work, which calls `pnfs_ld_read_done()` or `pnfs_ld_write_done()`. Write cleanup marks sectors written in the extent tree and extends layoutcommit state. Layout segment allocation decodes XDR extents into a temporary list, validates spec ordering/coverage, resolves and registers deviceids, inserts extents into rb trees, or cleans up on error.

## State And Persistence
Runtime state includes `pnfs_block_layout` extent rb trees, `bl_lwb`, deviceid cache entries, block device maps, BIOs, and NFS pageio headers. Persistent effects are direct block device reads/writes and layoutcommit metadata marking written sectors.

## Dependencies And Integration Points
Integrates with NFS pNFS core, block layer BIO API, device mapper-backed device discovery, rpc_pipefs device resolution, extent_tree helpers, NFS pageio, layoutcommit, and module layout aliases `nfs-layouttype4-3` and `nfs-layouttype4-5`.

## Risks
Risks are high because IO bypasses the MDS. Sector/page alignment, EOF full-page write behavior, device unavailability caching, extent validation, BIO length clipping, and cleanup work scheduling must be exact. Error fallback relies on marking layout failure so NFS can redo through the metadata server.

## Test Signals
Test aligned buffered and direct reads/writes, read holes, EOF writes, device map boundary splits, BIO failure fallback, unavailable device retry timeout, invalid layout extent decoding, layout return range removal, layoutcommit preparation/cleanup, and registration/unregistration of block and SCSI layout types.
