# sources/distributed-fs/glusterfs/xlators/cluster/dht/src/dht-inode-write.c

## Purpose

`dht-inode-write.c` implements write-side and mutating inode FOPs for DHT: `writev`, `truncate`, `ftruncate`, `fallocate`, `discard`, `zerofill`, `setattr`, and `fsetattr`. It forwards regular-file operations to the cached child and preserves enough call state to retry on a migration target. For directories and other non-regular files, it fans metadata changes across layout children or routes directory MDS changes first.

## Important APIs, Types, and Functions

Each write-like operation has a callback and a second-wind helper: `dht_writev_cbk`/`dht_writev2`, `dht_truncate_cbk`/`dht_truncate2`, `dht_fallocate_cbk`/`dht_fallocate2`, `dht_discard_cbk`/`dht_discard2`, `dht_zerofill_cbk`/`dht_zerofill2`, and `dht_file_setattr_cbk`/`dht_setattr2`. Public entry points cache arguments into `local->rebalance`: iovec copies, iobrefs, offsets, sizes, flags, valid masks, and target attrs. Directory/non-file setattr aggregation uses `dht_setattr_cbk`, `dht_mds_setattr_cbk`, and `dht_non_mds_setattr_cbk`.

## Control Flow

Regular-file mutating FOPs initialize local state, wind to `local->cached_subvol`, then the callback checks for remote-fd errors, hard failures, migration phase2, and migration phase1. Phase2 or missing-file symptoms call `dht_rebalance_complete_check`; phase1 calls `dht_rebalance_in_progress_check` unless existing migration info plus fd context already identify an opened destination. The retry helpers set `call_cnt = 2` and re-wind the same operation to the destination child using the saved arguments. On second callbacks, source and destination pre/post attrs may be merged so upper layers see consistent metadata.

## State and Persistence Behavior

The file mutates child file data and metadata through child FOPs but does not itself write DHT layout xattrs. It stores transient retry data in `dht_local_t` and updates inode time cache after successful multi-child `setattr`. `writev` duplicates iovecs and refs the iobref so a retry remains valid after the original call stack advances. Phase1 writes add `GF_PROTECT_FROM_EXTERNAL_WRITES` to `xattr_req` before retrying to protect migration against concurrent external writes. Directory setattr first writes the MDS subvolume when present and then propagates to non-MDS children.

## Dependencies and Integration Points

The file depends on migration helpers, fd reopening, inode ctx migration info, DHT phase mode macros, `dht_set_local_rebalance`, and `dht_iatt_merge`. It integrates with layout/MDS metadata for directory setattr, with child storage translators for actual writes, and with upper translators that rely on correct pre/post attributes and stripped migration phase bits.

## Risks and Test Signals

Key risks are non-idempotent retry behavior for mutating operations, stale or missing duplicated write buffers, incorrect attr merging between source and destination, failure to protect phase1 external writes, and directory setattr partially applying when MDS or non-MDS children fail. Tests should cover each write FOP during phase1 and phase2 migration, fd not opened on destination, writev buffer lifetime across retry, truncation by path and fd, fallocate/discard/zerofill retry paths, regular-file setattr after complete migration, directory setattr with MDS down, non-regular multi-child setattr aggregation, and confirmation that `DHT_STRIP_PHASE1_FLAGS` runs before unwinding attrs.
