# File Research: sources/block-storage/kvdo/vdo/vio-write.c

## Purpose
Implements most of the VDO write path, including allocation, early acknowledgment, dedupe, compression, recovery journal entries, slab reference updates, block map updates, discard continuation, and cleanup.

## Main Write Flow
- `launch_write_data_vio()` rejects read-only writes, acquires a flush generation lock, and locates the block map slot.
- `continue_write_with_block_map_slot()` handles unmapped trim shortcuts, data allocation, zero/discard mapping, and acknowledgment timing.
- `allocate_block()` allocates a physical block and sets `new_mapped`.
- `acknowledge_write_callback()` acknowledges user writes once safe under flush-generation rules.
- `prepare_for_dedupe()` hashes data and routes to the correct hash zone.
- `lock_hash_in_zone()` acquires or joins hash-lock state.
- Writes may then deduplicate, compress/pack, or write a newly allocated block.

## Dedupe And Compression
- `hash_data_vio()` computes MurmurHash3 over the 4 KiB block.
- `launch_deduplicate_data_vio()` maps the LBN to a verified duplicate PBN.
- `launch_compress_data_vio()` checks compression eligibility and sends compression work to the CPU queue.
- `pack_compressed_data()` attempts to pack compressed data on the packer thread.
- `continue_write_after_compression()` either proceeds with compressed mapping journal work or falls back to normal write.

## Journal And Refcount Ordering
- `journal_increment()` and `journal_decrement()` add recovery journal entries for mapping changes.
- `update_reference_count()` writes slab journal entries after validating physical data block ranges.
- Dedupe/compression path:
  - journal increment for new mapping
  - increment refcount
  - read old block mapping
  - journal unmapping
  - decrement old mapping if nonzero
  - update block map
- Normal write path:
  - write data
  - journal new mapping
  - increment new block if nonzero
  - read old mapping
  - journal unmapping
  - decrement old mapping if nonzero
  - update block map

## Cleanup
- Cleanup stages release allocation/PBN locks, verify recovery-journal lock state, release hash lock, release logical and flush-generation locks, then return or relaunch the VIO.
- Multi-block discards reuse the same `data_vio` for following logical blocks until the discard range is exhausted.
- Hash locks are notified on success and error so dependent VIOs can continue or update hash-lock state.

## Error Behavior
- `abort_on_error()` optionally enters read-only mode and routes errors through hash-lock cleanup when needed.
- `VDO_NO_SPACE` during allocation is not immediately fatal; the path attempts dedupe/compression before returning no space.
- Fatal write-path metadata errors generally enter read-only mode.
