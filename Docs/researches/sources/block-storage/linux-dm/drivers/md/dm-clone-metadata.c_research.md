# File Research: sources/block-storage/linux-dm/drivers/md/dm-clone-metadata.c

## Purpose
Implements persistent metadata for the Device Mapper `clone` target. It tracks which destination regions have been hydrated from the source device using an on-disk bitset plus an in-memory region bitmap and transaction-local dirty maps.

## Main Interfaces
- Open/close: `dm_clone_metadata_open()`, `dm_clone_metadata_close()`.
- Region updates: `dm_clone_set_region_hydrated()`, `dm_clone_cond_set_range()`.
- Commit/rollback: `dm_clone_metadata_pre_commit()`, `dm_clone_metadata_commit()`, `dm_clone_metadata_abort()`.
- Recovery/mode control: `dm_clone_reload_in_core_bitset()`, `dm_clone_metadata_set_read_only()`, `dm_clone_metadata_set_read_write()`.
- Queries: `dm_clone_is_hydration_done()`, `dm_clone_is_region_hydrated()`, `dm_clone_is_range_hydrated()`, `dm_clone_nr_of_hydrated_regions()`, `dm_clone_find_next_unhydrated_region()`.
- Metadata sizing: `dm_clone_get_free_metadata_block_count()`, `dm_clone_get_metadata_dev_size()`.

## Control Flow
Opening metadata creates a block manager, detects whether the superblock is all zeroes, then either formats fresh metadata or validates and opens existing metadata. Formatting creates a transaction manager, space map, empty disk bitset sized to `nr_regions`, and writes the superblock.

Runtime hydration updates set bits in the in-memory `region_map` and current dirty map under `bitmap_lock`. `pre_commit` atomically swaps the active dirty map so new hydration updates land in the next transaction while the old map is committed. `commit` flushes only dirty bitset words to disk, flushes the bitset cache, pre-commits the transaction manager, copies the space-map root, updates the superblock, and commits.

## State And Synchronization
`struct dm_clone_metadata` owns the block device, target geometry, persistent-data managers, disk bitset root, in-memory `region_map`, two dirty-map sets, and read-only/fail state. `bitmap_lock` protects bitmap mutation and dirty-map selection. `lock` serializes open-format/commit/abort/reload and space-map queries. Dirty maps separate fast interrupt-safe region updates from slower blocking metadata I/O.

## Integration Points
Uses Device Mapper persistent-data components: block manager, transaction manager, metadata space map, and disk bitset. The clone target calls these functions to mark kcopyd-completed, overwrite-completed, or discarded regions as hydrated and to enforce destination flush before metadata commit.

## Notable Behaviors
- Metadata version support is currently version 1 only.
- The metadata device is formatted only when the superblock is all zeroes.
- Region and target size must match existing metadata on reopen.
- `dm_clone_set_region_hydrated()` is nonblocking and safe for interrupt context.
- `dm_clone_cond_set_range()` uses spin locks but is documented as unsafe from disabled-interrupt contexts.
- Abort destroys and recreates persistent-data structures from the last committed state; failure enters `fail_io`.

## Risks And Review Focus
- The two-phase dirty-map swap is durability-critical: clone must flush destination data before committing hydrated bits.
- `dm_clone_reload_in_core_bitset()` intentionally bypasses `bitmap_lock` and must only be used after read-only transition.
- Dirty map failure leaves no clean spare dirty map, causing later `pre_commit` validation failure.
- Region range validation must avoid overflow and out-of-bounds bit operations.
