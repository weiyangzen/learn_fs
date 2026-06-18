# File Research: sources/block-storage/linux-dm/drivers/md/dm-exception-store.h

## Role
Declares the device-mapper snapshot exception-store API shared by the snapshot target and store implementations.

## Public Types
- `chunk_t` represents snapshot chunk numbers.
- `struct dm_exception` maps an `old_chunk` from the origin to a `new_chunk` in the COW device.
- `struct dm_exception_store_type` is the store implementation vtable.
- `struct dm_exception_store` is the common store instance wrapper with type pointer, owning snapshot, chunk geometry, implementation context, and userspace overflow support flag.

## Store Vtable
Store implementations provide:
- `ctr` and `dtr` lifecycle methods.
- `read_metadata()` to load COW metadata and report exceptions through a callback.
- `prepare_exception()` and `commit_exception()` for allocating and committing new COW chunks.
- `prepare_merge()` and `commit_merge()` for snapshot merge progress.
- `drop_snapshot()` to invalidate metadata.
- `status()` and `usage()` reporting hooks.

## Chunk Helpers
- The high 8 bits of `new_chunk` can encode a count of consecutive following chunks when `chunk_t` is 64-bit.
- `dm_chunk_number()`, `dm_consecutive_chunk_count()`, and increment/decrement helpers manipulate that packed representation.
- `sector_to_chunk()` converts sectors to chunk numbers using the store’s `chunk_shift`.

## Exposed Functions
Declares type register/unregister, chunk-size setup, store create/destroy, global store init/exit, and the two built-in store implementation init/exit pairs.

## Filesystem/Storage Relevance
This header defines the abstraction that lets DM snapshots use different COW metadata formats while presenting the same copy-on-write and merge semantics to upper block/filesystem layers.
