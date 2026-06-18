# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/write.c

Main bcachefs data write implementation. It includes extensive inline documentation for the write path, read path, EC, reflink, reconcile, move path, copygc, and scrub, followed by the implementation of COW writes, inline writes, encoded data writes, nocow writes, replica submission, and index updates.

Key entry points:
- `bch2_sum_sector_overwrites()` computes inode-sector and disk-sector deltas for an extent overwrite.
- `bch2_extent_update()` updates extents and inode accounting atomically, including reconcile tagging.
- `bch2_submit_wbio_replicas()` submits one bio per extent pointer/device, cloning bios for additional replicas.
- `bch2_write_point_do_index_updates()` serializes post-IO index updates per write point.
- `bch2_write()` is the closure entry point for foreground writes and move writes.
- `bch2_write_op_error()`, `__bch2_write_op_to_text()`, and `bch2_write_op_to_text()` provide error/status rendering.
- `bch2_fs_io_write_init()` and `bch2_fs_io_write_exit()` manage biosets.

Core behavior:
- COW writes allocate sectors through the foreground allocator, optionally compress/encrypt/checksum/bounce data, append extent keys, submit writes, then update the btree after IO completes.
- Encoded data moves may reuse existing encoded extents when compatible; otherwise compressed data is decompressed, decrypted if needed, rechecksummed, recompressed/re-encrypted, and rewritten.
- Inline writes store small file-tail data directly in `KEY_TYPE_inline_data`.
- Nocow writes try to overwrite existing writable, unencoded, non-EC extents in place; stale pointers, snapshots, incompatible extents, or alignment issues fall back to COW.
- Write errors drop failed pointers from insert keys when possible, allowing degraded writes; total failure returns data write IO error.
- Per-write-point queues track state and defer index updates to `btree_update_wq` or `copygc.wq`.

Important invariants:
- Extent updates always update the inode, even when only `bi_journal_seq` changes, so fsync correctness is preserved.
- Misaligned writes are rejected.
- `nochanges` and failed write refs stop writes before allocation/submission.
- Encryption nonces are derived from extent version state; encrypted data cannot be blindly rechecksummed as unencrypted data.
- Nocow writes require per-bucket nocow locks and valid bucket generations after btree locks are dropped.
- Move writes use `bch2_data_update_index_update()` instead of the foreground default index update path.

Dependencies and interactions:
- Uses allocator/write points/open buckets, btree extent updates, inode/subvolume lookup, checksum/compression/encryption helpers, EC writepoint buffers, nocow locking, data update, async object debug lists, journal-sensitive inode updates, and device latency/accounting.
