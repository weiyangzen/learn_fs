# `sources/distributed-fs/ceph-client/drivers/md/dm-exception-store.h`

## Purpose

`dm-exception-store.h` defines the snapshot exception-store interface shared by `dm-snap`, common registry code, and concrete persistent/transient store implementations. It describes snapshot chunk identifiers, exception records, store operations, and helper functions for packed consecutive chunk counts.

## Important APIs, Types, and Functions

`chunk_t` aliases `sector_t` for snapshot chunk numbers. `struct dm_exception` maps `old_chunk` to `new_chunk`; on 64-bit chunk values, the top 8 bits of `new_chunk` encode a count of following contiguous chunks. `struct dm_exception_store_type` is the implementation vtable: constructor/destructor, metadata loading, exception preparation/commit, merge preparation/commit, snapshot drop, status, usage, and registry list node. `struct dm_exception_store` holds the chosen type, parent snapshot, chunk geometry, type-specific context, and an overflow-support flag.

Inline helpers include `dm_chunk_number()`, `dm_consecutive_chunk_count()`, increment/decrement helpers for the packed count, `get_dev_size()`, and `sector_to_chunk()`. Public functions register/unregister store types, set chunk size, create/destroy stores, and initialize/exit built-in store modules.

## Control Flow

The snapshot target includes this header to create a store, load metadata through `read_metadata()`, allocate and commit exceptions while copying chunks, and coordinate merge operations. Store implementations include this header to provide a `dm_exception_store_type` and to call registration helpers during module init.

## State and Persistence Behavior

The header defines the contract for persistent state but does not implement it. Persistent behavior is implementation-specific: persistent stores record metadata on the COW device, while transient stores keep it in memory. The packed consecutive-count bits are part of the in-memory/public exception representation and must be handled carefully by all users.

## Dependencies and Integration Points

The header depends on block-device, hash-list, list, and device-mapper definitions. It forward-declares `struct dm_snapshot` and exposes `dm_snap_origin()` and `dm_snap_cow()` so common code can validate chunk sizes against both devices. Built-in implementations are declared as `dm_persistent_snapshot_init/exit()` and `dm_transient_snapshot_init/exit()`.

## Risks and Edge Cases

The packed high bits in `new_chunk` reduce available chunk-number bits to 56 when used; code must call `dm_chunk_number()` before treating it as a raw chunk. Increment and decrement helpers use `BUG_ON()` for overflow/underflow detection. Store vtable callbacks have asynchronous and failure-sensitive semantics, especially `commit_exception()` and merge operations, so implementation tests need to verify callback completion and metadata validity.

## Test Signals

Tests should validate packed consecutive chunk handling, sector-to-chunk conversion, store type registration lifecycle, create/destroy API behavior, merge callback semantics, overflow support reporting, and usage/status output across persistent and transient implementations.
