# Group Research: group_1644_qemu_sources_virtualization_qemu_block_qcow2_refcount_c_sources_vir_ee0c5c3939d4

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/block/qcow2-refcount.c -->
# File Research: sources/virtualization/qemu/block/qcow2-refcount.c

Implements qcow2 refcount storage, allocation, freeing, discard queuing, refcount checking/repair, metadata overlap protection, refcount-order conversion, refcount table shrinking, and metadata preallocation detection.

Key entry points:
- `qcow2_refcount_init()` / `qcow2_refcount_close()` load and free the in-memory refcount table and select packed refcount accessor functions for refcount orders 0 through 6.
- `qcow2_get_refcount()` reads one cluster refcount from the refcount table/refblock cache, treating missing table/block entries as zero.
- `qcow2_refcount_area()` creates self-covering refcount metadata at image creation or table growth time.
- `qcow2_alloc_clusters()`, `qcow2_alloc_clusters_at()`, `qcow2_alloc_bytes()`, `qcow2_free_clusters()`, and `qcow2_free_any_cluster()` are the main allocation/free APIs used by qcow2 metadata and data paths.
- `qcow2_update_snapshot_refcount()` walks L1/L2 tables to add/drop snapshot references and refresh `QCOW_OFLAG_COPIED`.
- `qcow2_check_refcounts()` constructs an independent in-memory refcount map, compares it with on-disk refcounts, optionally repairs leaks/corruption, rebuilds refcount structures when necessary, and checks copied flags.
- `qcow2_check_metadata_overlap()` and `qcow2_pre_write_overlap_check()` protect qcow2 metadata from invalid writes.
- `qcow2_change_refcount_order()` rewrites refblocks/reftable for a new refcount entry width.
- `qcow2_shrink_reftable()`, `qcow2_get_last_cluster()`, and `qcow2_detect_metadata_preallocation()` provide cleanup and image-layout helpers.

Core mechanics:
- Refcount entries are packed according to `s->refcount_order`: 1, 2, 4, 8, 16, 32, or 64-bit counts via `get_refcount_ro*()` and `set_refcount_ro*()`.
- `alloc_refcount_block()` allocates refblocks without normal recursive allocation, handles self-describing refblocks, grows the reftable through `qcow2_refcount_area()`, and returns `-EAGAIN` when callers must retry allocation after metadata consumed candidate clusters.
- `update_refcount()` rounds byte ranges to clusters, allocates needed refblocks, checks overflow/underflow, updates `s->free_cluster_index`, invalidates cached tables whose clusters become free, and queues optional passthrough discards.
- Discards are coalesced in `queue_discard()` and submitted by `qcow2_process_discards()` after refcount work succeeds unless discard caching is active.
- Check/repair code counts references from the header, active and snapshot L1/L2 trees, snapshot table, refcount table, refblocks, crypto header, and persistent bitmaps, then compares against on-disk refcounts.
- Rebuild mode allocates replacement refblocks and reftable from an in-memory refcount table, writes them, updates the qcow2 header, and leaves old structures as leaks for a later leak-fix pass.
- Metadata overlap checks cover main header, active/inactive L1 and L2 tables, refcount table, refblocks, snapshot table, and bitmap directory.

Important invariants:
- Refblock offsets must be cluster-aligned and nonzero when installed.
- Refcount arithmetic must not exceed `s->refcount_max` or underflow.
- Refcount metadata updates are ordered against L2-table updates through cache dependency calls.
- Refcount block allocation must avoid endless recursion by using no-ref allocation and self-covering metadata layouts.
- Snapshot refcount updates intentionally special-case the active L1 table; `qcow2_snapshot_goto()` depends on that behavior.
- `QCOW_OFLAG_COPIED` is valid only when the referenced cluster/refblock has refcount 1.

Filesystem/block relevance:
- This is the qcow2 allocator and consistency engine. It decides which host clusters are owned, shared, leaked, discardable, or safe to overwrite, so it is central to qcow2 copy-on-write correctness.

Notable risks:
- Failure during free paths can leak clusters; several comments explicitly choose leaking over risking corruption.
- Corrupt refcount metadata may force full refcount-structure rebuild rather than local repair.
- Overlap checking relies on all metadata regions being known and correctly represented in memory.
<!-- END FILE RESEARCH: sources/virtualization/qemu/block/qcow2-refcount.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/block/qcow2-snapshot.c -->
# File Research: sources/virtualization/qemu/block/qcow2-snapshot.c

Implements qcow2 internal snapshot table parsing, writing, validation/repair, snapshot creation, rollback, deletion, listing, and temporary read-only snapshot loading.

Key entry points:
- `qcow2_read_snapshots()` loads the snapshot table through `qcow2_do_read_snapshots()` in strict mode.
- `qcow2_write_snapshots()` writes a complete replacement snapshot table, updates the qcow2 header pointer/count only after flushing the new table, then frees the old table.
- `qcow2_check_read_snapshot_table()` re-reads snapshot metadata during check mode, optionally truncates excessive snapshot counts/table entries, and records repairable corruption.
- `qcow2_check_fix_snapshot_table()` rewrites the snapshot table when check mode found fixable snapshot-entry corruption.
- `qcow2_snapshot_create()` copies the active L1 table into a new snapshot L1 table, increments referenced-cluster refcounts, appends the snapshot record, writes the table, and discards obsolete VM-state clusters from the active image.
- `qcow2_snapshot_goto()` validates and loads a snapshot L1 table into the active L1 table, resizing the virtual disk if needed and carefully ordering refcount increments before overwriting the current L1 table.
- `qcow2_snapshot_delete()` removes one snapshot record, rewrites the table, then drops the deleted snapshot’s L1/data references.
- `qcow2_snapshot_list()` exports `QEMUSnapshotInfo` records.
- `qcow2_snapshot_load_tmp()` switches a read-only image to a snapshot L1 table without mutating on-disk state.

Core mechanics:
- Snapshot entries include fixed `QCowSnapshotHeader`, known `QCowSnapshotExtraData`, unknown extra data preservation, ID string, and name string, each 8-byte aligned in the table.
- Repair mode can reduce overlarge snapshot counts/tables and truncate excessive extra metadata; it intentionally leaks discarded clusters for `qcow2_check_refcounts()` to recover.
- v3 images require snapshot extra data covering large VM-state size and disk size; incomplete entries are reported and may be rewritten.
- Snapshot lookup supports exact ID/name matching, ID-only, name-only, and ID-or-name rollback lookup.
- All mutating snapshot operations reject images with external data files via `has_data_file(bs)`.

Important invariants:
- Header snapshot pointer/count are updated only after the replacement table and its refcounts are stable.
- New snapshot creation increments data/L2 references before publishing the new snapshot record.
- Snapshot rollback increments the target snapshot references before overwriting the active L1 table, then decrements old active references after the on-disk active L1 has changed.
- Deletion removes the snapshot from the table before freeing its clusters; later failures are tolerated as leaks rather than resurrecting stale table entries.
- Snapshot L1 tables are validated with `qcow2_validate_table()` before use.

Filesystem/block relevance:
- This file implements qcow2’s user-visible internal snapshot lifecycle. It coordinates snapshot metadata with the refcount engine so copy-on-write sharing remains consistent across active and inactive L1/L2 trees.

Notable risks:
- Snapshot repair deliberately trades corruption avoidance for possible leaks, relying on later refcount checking.
- Failure after deleting a snapshot from the table but before freeing its clusters can leak the deleted snapshot’s storage.
- Rollback has delicate ordering because in-memory and on-disk active L1 tables briefly refer to different generations.
<!-- END FILE RESEARCH: sources/virtualization/qemu/block/qcow2-snapshot.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/block/qcow2-threads.c -->
# File Research: sources/virtualization/qemu/block/qcow2-threads.c

Provides threaded helper execution for qcow2 compression, decompression, encryption, and decryption so CPU-heavy data transforms run through QEMU’s thread pool while callers remain coroutine-based.

Key entry points:
- `qcow2_co_process()` limits concurrent qcow2 worker tasks with `s->nb_threads`, waits on `s->thread_task_queue` when `QCOW2_MAX_THREADS` is reached, submits work via `thread_pool_submit_co()`, then wakes the next waiter.
- `qcow2_co_compress()` selects zlib or zstd compression based on `s->compression_type`.
- `qcow2_co_decompress()` selects zlib or zstd decompression based on `s->compression_type`.
- `qcow2_co_encrypt()` and `qcow2_co_decrypt()` run `qcrypto_block_encrypt()` / `qcrypto_block_decrypt()` in the same worker framework.

Compression behavior:
- zlib uses raw deflate/inflate with a negative window size and expects decompression to fill the destination cluster exactly.
- zlib decompression accepts `Z_BUF_ERROR` only when the output buffer is full, because qcow2 compressed sizes are sector-granular rather than exact.
- zstd support is conditional on `CONFIG_ZSTD`.
- zstd compression uses the streaming API but intentionally performs one end call; a nonzero result is treated as destination-too-small or I/O error.
- zstd decompression loops until the output buffer is full, rejects no-progress iterations, and treats unfinished frames after a full output as corruption/error.

Crypto behavior:
- `qcow2_co_encdec()` chooses the crypto IV offset from host offset or guest offset according to `s->crypt_physical_offset`.
- Encryption/decryption require `s->crypto` and assert guest offset, host offset, and length alignment to the crypto sector size.
- Zero-length crypto operations return success without worker submission.

Important invariants:
- Worker concurrency accounting is protected by `s->lock`.
- Compression wrappers pass stack-allocated argument structs only because `thread_pool_submit_co()` waits for completion before returning.
- Compression/decompression return negative errno-style values; successful decompression returns 0, successful compression returns compressed byte count.
- Unsupported compression enum values abort, so callers must validate image compression type earlier.

Filesystem/block relevance:
- This is qcow2’s CPU transform offload layer for compressed clusters and encrypted payloads. It does not manage allocation, but it directly affects how cluster data is encoded before writes and decoded after reads.

Notable risks:
- The thread cap serializes excess CPU work; queue behavior depends on proper wakeup after every completed worker task.
- zstd decompression intentionally guards against infinite loops when the library consumes or produces no data.
- Alignment assertions mean invalid crypto call sites fail hard in debug/assert-enabled builds.
<!-- END FILE RESEARCH: sources/virtualization/qemu/block/qcow2-threads.c -->