# sources/distributed-fs/ceph-client/drivers/md/dm-cache-metadata.c

## Purpose
`dm-cache-metadata.c` manages the persistent metadata format for the DM cache target. It formats or opens the metadata device, validates and commits the superblock, stores cache-block to origin-block mappings, dirty bits, discard bits, policy hints, feature flags, and statistics, and provides transaction/abort/read-only control around persistent-data objects.

## Important APIs, Types, and Functions
Key structures are on-disk `struct cache_disk_superblock` and in-memory `struct dm_cache_metadata`. Public APIs include `dm_cache_metadata_open()`, `dm_cache_metadata_close()`, `dm_cache_resize()`, `dm_cache_discard_bitset_resize()`, `dm_cache_load_discards()`, `dm_cache_set_discard()`, `dm_cache_insert_mapping()`, `dm_cache_remove_mapping()`, `dm_cache_load_mappings()`, `dm_cache_set_dirty_bits()`, `dm_cache_metadata_get_stats()`, `dm_cache_metadata_set_stats()`, `dm_cache_commit()`, `dm_cache_get_free_metadata_block_count()`, `dm_cache_get_metadata_dev_size()`, `dm_cache_write_hints()`, `dm_cache_metadata_set_read_only()`, `dm_cache_metadata_set_read_write()`, `dm_cache_metadata_set_needs_check()`, `dm_cache_metadata_needs_check()`, `dm_cache_metadata_abort()`, and `dm_cache_metadata_clean_when_opened()`.

## Control Flow
Open goes through a refcounted global table keyed by metadata bdev, creates a block manager, detects all-zero unformatted superblocks, formats if allowed, or validates and opens existing metadata. Formatting creates a transaction manager, mapping array, optional separate dirty bitset for metadata version 2, discard bitset, and initial superblock. Normal mutation takes `root_lock`, updates dm-array or dm-bitset roots, marks `changed`, and leaves persistence to `dm_cache_commit()`. Commit flushes dirty/discard roots, pre-commits the transaction manager, copies the space-map root, writes the superblock fields and clean-shutdown flag, commits, then begins a new transaction by rereading the superblock.

## State and Persistence
Persistent state lives in a checksummed superblock at block 0 plus persistent-data roots for mapping, hints, discard bits, and, for version 2, a separate dirty bitset. Version 1 stores dirty state in low mapping flags; version 2 separates dirty bits. `CLEAN_SHUTDOWN` controls whether loaded mappings and discards are trusted as clean or conservatively treated dirty/undiscarded after a crash. `NEEDS_CHECK` persists a tools-required repair flag. Runtime state includes open refcount, policy identity, stats, roots, block counts, cursors, and `fail_io`, which restricts operations after an abort rollback failure.

## Dependencies and Integration Points
The file integrates with persistent-data components: block manager, transaction manager, metadata space map, dm-array, and dm-bitset. It depends on cache policy identity and hint APIs from `dm-cache-policy-internal.h`, typed block wrappers, and block-device read-only state. The DM cache target uses it to load mappings into the selected policy, persist dirty bits and hints during suspend/commit, and recover metadata after crashes.

## Risks and Edge Cases
Changing the data block size on reopen is rejected. Unsupported incompat or read-write incompatible feature flags prevent opening. Cache shrink first verifies removed blocks are unmapped or clean; dirty blocks make shrink fail. If the previous shutdown was unclean, mappings load as dirty and discard bits load as false to avoid data loss. `dm_cache_metadata_abort()` intentionally creates a new block manager outside `root_lock` to avoid an ABBA deadlock with shrinker teardown; failure sets `fail_io`, after which only close is safe. Policy hints are trusted only when the policy name, major version, hint size, and clean-open state match.

## Test Signals
Important signals include format and reopen across metadata versions 1 and 2, checksum/magic/version rejection, clean versus unclean shutdown mapping load semantics, shrink rejection with dirty blocks, discard bitset resize/load behavior, policy hint preservation and invalidation after policy changes, needs-check persistence, read-only mode rejecting writes, abort success and fail-io behavior, and transaction commits preserving stats and roots across reload.
