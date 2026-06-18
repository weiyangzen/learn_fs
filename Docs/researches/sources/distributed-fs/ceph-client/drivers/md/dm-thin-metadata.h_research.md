# sources/distributed-fs/ceph-client/drivers/md/dm-thin-metadata.h

## Purpose
This header defines the public metadata contract between the thin target frontend and the thin metadata engine. It exposes opaque pool/device handles, thin device identifiers, metadata limits, superblock flags, feature masks, transaction APIs, mapping APIs, free-space/stat APIs, resize APIs, read-only toggles, threshold callbacks, and the pre-commit callback hook.

## Important APIs, Types, And Functions
- `THIN_METADATA_BLOCK_SIZE`, `THIN_METADATA_MAX_SECTORS`, and `THIN_METADATA_MAX_SECTORS_WARNING` bind thin metadata sizing to persistent-data space-map metadata limits.
- `THIN_METADATA_NEEDS_CHECK_FLAG` marks metadata requiring userspace repair.
- `dm_thin_id` is a `uint64_t`; `dm-thin.c` narrows accepted ids to 24 bits.
- `struct dm_pool_metadata` and `struct dm_thin_device` are opaque outside the implementation.
- `struct dm_thin_lookup_result` returns a physical pool block and a `shared` hint.
- Creation/deletion APIs are `dm_pool_create_thin()`, `dm_pool_create_snap()`, and `dm_pool_delete_thin_device()`.
- Transaction APIs are `dm_pool_commit_metadata()`, `dm_pool_abort_metadata()`, transaction id get/set, and metadata snapshot reserve/release/get.
- Per-device APIs include open/close, lookup, mapped range lookup, insert, remove range, mapped-count, highest mapped block, and changed/aborted-change queries.
- Pool APIs include data allocation, free counts, device sizes, shared-block query, data refcount range inc/dec, data/metadata resize, read-only/read-write, metadata threshold registration, prefetch issue, and pre-commit callback registration.

## Control Flow And Contracts
The header documents the central operational sequencing: callers create/open pool metadata, create or open thin devices, perform lookup/allocation/insert/remove operations, then commit all metadata changes as one transaction. Snapshot creation requires a quiesced origin. `dm_pool_abort_metadata()` rolls back uncommitted changes while leaving thin devices open and reports per-device aborted changes through `dm_thin_aborted_changes()`.

`dm_thin_find_block()` documents `-ENODATA` for absent mapping and `-EWOULDBLOCK` when non-blocking lookup cannot issue I/O. The frontend uses this in `thin_bio_map()` to fast-path already cached mappings and defer misses or blocking cases to the worker.

## State And Persistence Behavior
The header’s API is stateful: all mapping, free-space, transaction-id, resize, held-root, and needs-check behavior ultimately persists in `dm-thin-metadata.c`. The read-only/read-write toggles act on the block manager, not just on callers. The pre-commit callback is explicitly part of metadata commit ordering and is used by the thin-pool target to flush data before publishing metadata roots.

## Dependencies And Integration Points
It includes persistent-data block-manager, space-map, and metadata-space-map headers because callers need `dm_block_t`, `dm_sm_threshold_fn`, and metadata size constants. `dm-thin.c` is the main in-tree consumer in this subset. Userspace integration is indirect through target messages and status output implemented in `dm-thin.c`.

## Risks
- The comment for `dm_pool_open_thin_device()` says opening the same device more than once returns `-EBUSY`, while the implementation increments open count for an already open non-create device; consumers must rely on implementation behavior or verify current upstream semantics.
- `dm_pool_resize_data_dev()` comment mentions `-ENOSPC` for too-small resize, while implementation reports shrink as `-EINVAL`; tests should lock down expected behavior.
- The shared bit is only a hint based on metadata timestamps and may over-report sharing.
- Callers must respect quiescing requirements for snapshots; the metadata layer does not enforce application-level consistency.

## Test Signals
Header-level contract tests should validate documented error codes against implementation, non-blocking lookup behavior, abort/change flags, metadata snapshot lifecycle, read-only/write-mode transitions, threshold callback registration, and commit pre-callback ordering.
