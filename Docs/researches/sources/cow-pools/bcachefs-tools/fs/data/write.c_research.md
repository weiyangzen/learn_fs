# File Research: sources/cow-pools/bcachefs-tools/fs/data/write.c

## Role

Implements the bcachefs data write path. It covers normal COW writes, encoded writes for move/update operations, compression, encryption, checksumming, inline data, nocow overwrites, replica submission, write-point queueing, btree index updates, and filesystem write-path initialization.

The top of the file also contains extensive bcachefs documentation for data write/read paths, encoded extents, encryption, erasure coding, reflink, move, reconcile, copygc, and scrub.

## Write Path Overview

`bch2_write()` is the closure entry point. It validates alignment and write permissions, obtains a filesystem write reference for normal writes, increments the write IO clock, optionally writes small tail data as inline data, then enters `__bch2_write()`.

Normal COW writes allocate new storage, transform data if needed, submit writes to replicas, then update the extent btree atomically. Move/data-update writes reuse the same IO pipeline but call `bch2_data_update_index_update()` instead of the default logical extent insert path.

## Extent and Inode Updates

`bch2_sum_sector_overwrites()` computes inode-sector and disk-sector deltas for a new extent over existing keys and determines whether usage is increasing.

`bch2_extent_update()` is the shared logical extent update helper. It traverses and trims the new extent, adjusts disk reservation, updates inode size/sectors through `bch2_extent_update_i_size_sectors()`, marks reconcile needs, inserts the extent, commits, updates caller totals, and advances the iterator.

`bch2_write_index_default()` inserts normal user writes into `BTREE_ID_extents`, resolving the subvolume snapshot and repeatedly calling `bch2_extent_update()` for keylist entries.

## Replica Submission and Completion

`bch2_submit_wbio_replicas()` clones a write bio for each extent pointer, obtains IO references for non-nocow writes or consumes caller-held refs for nocow writes, sets device/sector fields, records IO accounting, and submits each bio. Invalid or unavailable devices complete with an error.

`bch2_write_endio()` records device completion/error status, tracks failed devices, unlocks nocow buckets, records nocow devices needing flush, drops IO refs, frees bounce buffers, releases clone bios, and decrements the parent closure.

`bch2_write_drop_io_error_ptrs()` removes failed pointers from inserted keys after degraded writes; if no dirty pointers remain it returns a data-write error.

## Write Point Queueing

Write ops are associated with allocator write points. `bch2_write_queue()` attaches an op to a write point. `bch2_write_index()` queues the op for btree index update after IO completion. `bch2_write_point_do_index_updates()` drains a write point's completed operations, performs index updates, and either continues allocation/writing or finishes the op.

`__wp_update_state()` and `wp_update_state()` maintain write-point state and timing for stopped, waiting-for-IO, waiting-for-work, and runnable states.

## Encoding Pipeline

`bch2_write_extent()` prepares one writable extent segment:

- Reuses encoded data directly when it already satisfies geometry, checksum/encryption class, compression state, and write-point free space.
- Otherwise decompresses compressed encoded data when needed.
- Rechecks/recomputes checksums with `bch2_write_rechecksum()`.
- Decrypts when compression or checksum conversion requires plaintext.
- Allocates bounce bios when compression, encryption, checksum stability, EC buffering, or debug corruption injection require owned pages.
- Compresses, encrypts, checksums, and appends extent keys through `init_append_extent()`.
- Splits bios when the source remains only partially consumed.

`bch2_write_prep_encoded_data()` handles the special move/update case where the input bio already represents an encoded extent and may be rewritten whole, trimmed, decompressed, decrypted, or rechecksummed.

## Normal COW Allocation Loop

`__bch2_write()` repeatedly requests sectors from the foreground allocator with target, EC, replica, watermark, and flag constraints. It handles allocator blocking differently for sync and async callers, writes all possible data into the current write point, marks internal move writes `REQ_FUA`, submits replicas, and then either synchronously waits/indexes or queues async completion.

Allocator errors on normal writes are logged with detailed write-op text.

## Nocow Path

`bch2_nocow_write()` attempts in-place writes when the operation is not a move, the file/options request nocow, and existing extents are writable:

- Resolves the current snapshot and inode size.
- Requires direct non-encoded extents with enough durable replicas.
- Avoids splitting bios at unaligned extent ends.
- Takes IO refs before dropping btree locks.
- Locks nocow buckets and verifies bucket generations to avoid stale pointers.
- Splits bios by extent boundaries and submits writes directly to existing pointers.
- Converts unwritten extents after IO if needed.
- Falls back to normal COW if requirements are not met.

`bch2_nocow_write_convert_unwritten()` clears unwritten flags in successfully written extents and updates inode size/reconcile state. `bch2_nocow_write_done()` performs final nocow error/convert handling.

## Inline Data

`bch2_write_data_inline()` stores small writes as `KEY_TYPE_inline_data` when inline data is enabled and the data length is at most `min(block_size / 2, 1024)`. It copies data from the bio into the key, pads to 8-byte value alignment, inserts through the index path, and finishes the write without device IO.

## Error Handling and Diagnostics

`bch2_write_op_error()` logs file-position-aware write errors. `__bch2_write_index()` handles IO errors, degraded writes, index-update errors, open bucket cleanup, and final error propagation.

`__bch2_write_op_to_text()` and `bch2_write_op_to_text()` print position, age, flags, watermark, replicas, devices already held, inode options, open buckets, closure refs, error, and data-update state for move writes.

## Initialization

`bch2_fs_io_write_init()` initializes the write bioset and replica clone bioset. `bch2_fs_io_write_exit()` releases them.
