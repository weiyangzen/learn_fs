# sources/distributed-fs/ceph-client/fs/nfs/blocklayout/dev.c

## Purpose
This file decodes pNFS block layout deviceid payloads into a `pnfs_block_dev` tree that can map logical file extents onto Linux block devices. It supports simple, slice, concat, stripe, and SCSI volume encodings, opens the referenced block devices, validates SCSI persistent-reservation capability, and releases device resources through the deviceid node lifecycle.

## Important APIs, types, and functions
The public entry points are `bl_alloc_deviceid_node()`, `bl_free_deviceid_node()`, and `bl_register_dev()`. `bl_alloc_deviceid_node()` decodes a `struct pnfs_device`, allocates `struct pnfs_block_volume` records, parses the top-level volume into a `struct pnfs_block_dev`, initializes the embedded `nfs4_deviceid_node`, and marks it unavailable if parsing failed. `bl_free_deviceid_node()` tears down nested device trees and frees the node with RCU. `bl_register_dev()` recursively registers SCSI PR keys for leaf devices, rolling back already-registered children on failure.

Internal mapping functions implement layout geometry: `bl_map_simple()` maps directly to one block device, `bl_map_concat()` finds the child range containing an offset, and `bl_map_stripe()` selects a child by stripe chunk and adjusts both file and disk offsets. Parser functions mirror the volume types: `nfs4_block_decode_volume()`, `bl_parse_simple()`, `bl_parse_scsi()`, `bl_parse_slice()`, `bl_parse_concat()`, and `bl_parse_stripe()`.

## Control flow
Device setup begins in `bl_alloc_deviceid_node()`: allocate an XDR scratch folio, read volume count, decode each volume, allocate the top device, and parse the final volume as the top-level mapping. Simple legacy volumes resolve a kernel `dev_t` through `bl_resolve_deviceid()` in `rpc_pipefs.c`; SCSI volumes validate code-set/designator combinations, open known `/dev/disk/by-id/` naming schemes, and require `pr_ops`. Composite volumes recursively parse referenced child indices and install the appropriate `map` callback.

## State and persistence behavior
Device state is in memory and tied to NFS deviceid cache lifetime. Leaf devices hold `struct file *bdev_file` references and SCSI leaves store a PR key plus registration flag. Composite devices own child arrays. No durable state is written by this file; externally visible persistence comes from opened block-device references and SCSI persistent reservations.

## Dependencies and integration points
The file depends on `blocklayout.h` types, Linux block APIs (`bdev_file_open_by_dev`, `bdev_file_open_by_path`, `bdev_nr_bytes`), XDR decode helpers, pNFS deviceid cache APIs, SCSI PR operations, and blocklayout tracepoints. It integrates with `rpc_pipefs.c` for legacy simple-volume device resolution and with extent/data-path code through the `pnfs_block_dev_map` callbacks.

## Risks and test signals
Key risks are malformed XDR, bad child indices, zero/unsupported devices, missing persistent-reservation operations, PR registration rollback, and stripe math overflow or divide-by-zero if a server supplies invalid counts or chunk sizes. Useful test signals include mount attempts using simple, SCSI, concat, slice, and stripe devices; unavailable deviceid marking on decode/open failures; PR register/unregister traces; and I/O path checks that mapped offsets land on expected block devices.
