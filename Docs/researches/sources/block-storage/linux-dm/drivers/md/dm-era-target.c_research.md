# File Research: sources/block-storage/linux-dm/drivers/md/dm-era-target.c

## Role
Implements the `era` target, a persistent changed-block tracker. It records which fixed-size data blocks were written during each era, supports checkpointing to advance eras, and exposes metadata snapshots for userspace inspection.

## Persistent Metadata
- The superblock lives at block 0 and includes checksum, magic, version, metadata space-map root, data block size, metadata block size, block count, current era, current writeset, writeset tree root, era array root, and metadata snapshot block.
- Uses dm persistent-data components: block manager, transaction manager, space map, disk bitset, btree, and array.
- A writeset is a disk bitset plus an in-core bitset cache of blocks written in the current era.
- The writeset tree maps era number to archived writeset metadata.
- The era array maps data block number to the most recent era known after archived writesets are digested.

## Metadata Lifecycle
- `metadata_open()` creates persistent-data objects, formatting an all-zero metadata device when allowed or opening an existing superblock.
- `metadata_resize()` reallocates the two in-core writesets and resizes the era array when the target size changes.
- `metadata_era_rollover()` archives the current writeset if present, creates a fresh disk bitset in the alternate writeset slot, atomically swaps the current writeset pointer with RCU, and increments the era.
- `metadata_commit()` flushes the current bitset, pre-commits the transaction manager, saves the space-map root, rewrites the superblock, and commits.
- `metadata_take_snap()` rolls over, commits, shadows the superblock, and increments roots so userspace can inspect a stable metadata snapshot.
- `metadata_drop_snap()` deletes the snapshot’s cloned writeset tree and era array and drops the cloned superblock reference.

## Digest Process
- Archived writesets are digested incrementally by `struct digest`.
- `metadata_digest_lookup_writeset()` finds the lowest-era archived writeset.
- `metadata_digest_transcribe_writeset()` scans up to 100 bits per step and writes matching blocks’ era values into the era array.
- `metadata_digest_remove_writeset()` removes the archived writeset after transcription.
- The incremental coroutine avoids long metadata stalls in the worker thread.

## IO Path
- Constructor syntax is `<metadata dev> <data dev> <data block size (sectors)>`.
- Block size must be positive and a multiple of `MIN_BLOCK_SIZE` sectors.
- `dm_set_target_max_io_len()` limits bios to one era block.
- `era_map()` remaps all bios to the origin device. Non-flush writes whose block is not yet marked in the current writeset are deferred to the worker; other bios pass through.
- The worker marks deferred writes in the on-disk current writeset, commits if any new bit was set, updates the in-core bitset only after successful commit, and submits or errors the queued bios.

## Worker and RPC Model
- A single ordered workqueue serializes digest work, deferred write marking, and RPC metadata operations.
- Messages are implemented as RPCs to the worker: `checkpoint`, `take_metadata_snap`, and `drop_metadata_snap`.
- `postsuspend` archives the current era and then stops/flushed the worker.
- `preresume` resizes metadata if needed, starts the worker, and performs an era rollover.

## Status and Limits
- Info status reports metadata block size, used/total metadata blocks, current era, and held metadata snapshot block or `-`.
- Table status reports metadata device, origin device, and sectors per block.
- IO hints set optimal IO size to the era block size when existing stacked limits are incompatible.

## Important Invariants
- Current writeset pointer changes are synchronized with RCU so IO paths see either the old or new writeset safely.
- The in-core bitset is updated only after the corresponding on-disk bit and metadata commit succeed.
- A metadata snapshot must be unique; taking a second snapshot before dropping the first is rejected.
- `valid_nr_blocks()` keeps bit counts within both dm-bitset and `test_bit()` practical limits.

## Filesystem/Storage Relevance
`dm-era` is a block-level dirty-region history engine. It can support backup, replication, or userspace tracking tools that need to know which blocks changed between checkpoints without depending on filesystem internals.

## Notable Risks
- Several error paths are marked `FIXME: fail mode`; metadata write failures can currently stop progress or error deferred bios rather than entering a polished recovery mode.
- Digestion of old eras is asynchronous, so users of metadata snapshots must understand the difference between archived writesets and transcribed era-array state.
