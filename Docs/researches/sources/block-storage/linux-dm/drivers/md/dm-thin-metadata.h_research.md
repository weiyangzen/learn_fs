# File Research: sources/block-storage/linux-dm/drivers/md/dm-thin-metadata.h

## Purpose
Declares the public thin-pool metadata API used by the thin provisioning target and related DM code.

## Public Constants and Types
- `THIN_METADATA_BLOCK_SIZE`
- `THIN_METADATA_MAX_SECTORS`
- `THIN_METADATA_MAX_SECTORS_WARNING`
- `THIN_METADATA_NEEDS_CHECK_FLAG`
- `dm_thin_id`
- Opaque:
  - `struct dm_pool_metadata`
  - `struct dm_thin_device`
- `struct dm_thin_lookup_result` with mapped pool block and shared flag.
- `dm_pool_pre_commit_fn`

## API Areas
- Pool metadata open/close:
  - `dm_pool_metadata_open()`
  - `dm_pool_metadata_close()`
- Device lifecycle:
  - `dm_pool_create_thin()`
  - `dm_pool_create_snap()`
  - `dm_pool_delete_thin_device()`
  - `dm_pool_open_thin_device()`
  - `dm_pool_close_thin_device()`
  - `dm_thin_dev_id()`
- Transactions:
  - `dm_pool_commit_metadata()`
  - `dm_pool_abort_metadata()`
  - transaction ID get/set
- Metadata snapshots for userspace:
  - reserve, release, get held root
- Mapping operations:
  - find block
  - find mapped range
  - allocate data block
  - insert/remove block
  - remove range
- Queries:
  - changed/aborted flags
  - highest mapped block
  - mapped counts
  - free block counts
  - data/metadata device size
  - shared-block check
- Space-map refcount helpers:
  - increment/decrement data ranges
- Resize:
  - data and metadata device resize
- Mode and health:
  - read-only/read-write
  - metadata threshold registration
  - needs-check set/query
  - prefetches
  - pre-commit callback registration

## Compatibility Flags
- `THIN_FEATURE_COMPAT_SUPP`
- `THIN_FEATURE_COMPAT_RO_SUPP`
- `THIN_FEATURE_INCOMPAT_SUPP`

All are zero in this version, meaning no optional on-disk feature bits are supported.

## Contract Notes
- Snapshot creation requires a quiesced origin.
- `dm_pool_abort_metadata()` preserves open thin devices but reports whether their uncommitted changes were aborted.
- `dm_thin_find_block()` documents `-EWOULDBLOCK` for nonblocking lookup, `-ENODATA` for absent mappings, and `0` on success.
- Resize documentation describes shrink safety behavior, but the implementation rejects shrinking entirely.
