<!-- Source: sources/distributed-fs/ceph-client/fs/nfs/blocklayout/blocklayout.h -->
# sources/distributed-fs/ceph-client/fs/nfs/blocklayout/blocklayout.h

## Purpose
Private header for the NFS pNFS block layout driver. It defines block-volume/device/extent/layout data structures, protocol limits, sector/page constants, rpc_pipefs message structures, and cross-file function declarations.

## Important APIs, Types, And Functions
Defines `struct pnfs_block_volume`, `struct pnfs_block_dev_map`, `struct pnfs_block_dev`, `struct pnfs_block_extent`, `struct pnfs_block_layout`, `struct bl_pipe_msg`, and `struct bl_msg_hdr`. Inline conversions are `BLK_LO2EXT()` and `BLK_LSEG2EXT()`. Declares device functions (`bl_register_dev()`, `bl_alloc_deviceid_node()`, `bl_free_deviceid_node()`), extent tree functions, and rpc_pipefs functions (`bl_resolve_deviceid()`, `bl_init_pipefs()`, `bl_cleanup_pipefs()`).

## Control Flow
No direct runtime flow, but the structures drive `blocklayout.c`, `dev.c`, `extent_tree.c`, and `rpc_pipefs.c`. Device maps provide a `map()` callback that translates logical offsets to block devices/ranges. Extents can live in rb trees or temporary lists through a union node/list member.

## State And Persistence
State represented includes hierarchical block volumes (simple, slice, concat, stripe, SCSI), block device file/device offsets, registration flags, persistent reservation key, extent file/volume offsets and state, layout read/write extent trees, SCSI-layout indicator, and last written byte.

## Dependencies And Integration Points
Includes device mapper, NFS FS, SUNRPC rpc_pipefs, NFSv4 internals, pNFS, and NFS network namespace headers. It is the contract among all blocklayout driver compilation units.

## Risks
Limits such as UUID/designator sizes and max devices protect allocation bounds; protocol changes must update these carefully. Sector units in extents differ from byte units in NFS arguments, so callers must convert consistently. Union use requires an extent to be in only one container at a time.

## Test Signals
Compile all blocklayout objects, decode device trees of each volume type, insert/remove/lookup extents in rw/ro trees, and validate SCSI/block layout registration paths.
