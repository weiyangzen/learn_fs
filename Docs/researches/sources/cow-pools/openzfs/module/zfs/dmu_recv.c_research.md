# File Research: sources/cow-pools/openzfs/module/zfs/dmu_recv.c

## Purpose
Implements ZFS receive for send streams: begin/resume validation, temporary dataset/clone setup, stream record parsing, checksumming, raw/encrypted receive handling, corrective receive healing, writer-thread application of records, cleanup, and final snapshot/clone-swap commit.

## Main Responsibilities
- Validates stream header type, feature flags, pool feature support, encryption/raw constraints, origins, clone/full/incremental semantics, and redaction compatibility.
- Creates or reuses an inconsistent receive dataset or `%recv` temporary clone.
- Supports resumable receives by saving object/offset/byte resume state in dataset ZAP fields.
- Reads stream payloads and next headers, maintains Fletcher checksum, handles byteswapped streams.
- Processes `DRR_OBJECT`, `DRR_FREEOBJECTS`, `DRR_WRITE`, `DRR_WRITE_EMBEDDED`, `DRR_FREE`, `DRR_SPILL`, `DRR_OBJECT_RANGE`, `DRR_REDACT`, and `DRR_END`.
- Applies writes through a background writer thread fed by a bounded queue, with indirect prefetch from the reader side.
- Handles raw receive crypt parameters, raw bonus/dnode block metadata, and raw key material.
- Implements corrective receive mode that rewrites corrupted blocks in place when checksum repair is possible.
- Finalizes successful receive by snapshotting, clone-swapping, clearing inconsistent state, updating GUID/creation time, cleaning resume fields, and creating zvol minors.

## Key Data And State
- Tunables:
  - `zfs_recv_queue_length`
  - `zfs_recv_queue_ff`
  - `zfs_recv_write_batch_size`
  - `zfs_recv_best_effort_corrective`
- `dmu_recv_tag`: dataset ownership tag for active receives.
- `recv_clone_name = "%recv"`: temporary clone name for receiving into existing datasets.
- `receive_record_arg`: queued stream record, payload/ABD, bytes-read position, and EOS marker.
- `receive_writer_arg`: writer-thread state including objset, raw/heal/resumable flags, write batch, object range encryption parameters, max object seen, and synchronization fields.
- `dmu_recv_begin_arg`: sync-task input bundling origin, cookie, credentials, and crypto params.
- `or_need_sync_t`: tracks whether raw object-range/freeobjects processing needs a txg sync before reallocation.

## Important Functions
- `byteswap_record()`: byteswaps replay record headers by record type.
- `compatible_redact_snaps()` / `redact_check()`: validates redacted incremental receive safety against origin redaction snapshots.
- `recv_check_large_blocks()`: rejects incrementals missing large-block support when the base has large-block feature active.
- `recv_begin_check_feature_flags_impl()`: verifies stream features are supported by the pool and enabled feature set.
- `recv_begin_check_existing_impl()`: validates receive into an existing dataset, including `%recv` absence, resume state absence, snapshot conflicts, zvol-child rule, healing constraints, raw/encryption compatibility, origin/fromguid matching, force behavior, redaction, and large blocks.
- `dmu_recv_begin_check()` / `dmu_recv_begin_sync()`: standard begin sync-task pair; creates `%recv` or new dataset, marks it inconsistent, records resume state, activates stream features, and prepares raw/redacted metadata.
- `dmu_recv_resume_begin_check()` / `dmu_recv_resume_begin_sync()`: resume sync-task pair; validates inconsistent dataset state, resume GUID/object/offset fields, ownership, redaction snapshot consistency, and reowns the target.
- `dmu_recv_begin()`: public setup entry point; parses `DRR_BEGIN`, reads begin payload nvlist, creates crypto params, and runs begin sync task.
- `receive_read()` / `receive_cksum()` / `receive_read_payload_and_next_header()`: stream I/O and checksum pipeline.
- `receive_read_record()`: loads each record payload and issues prefetches for write-like records.
- `receive_process_record()`: dispatches parsed records to object/free/write/spill/range/redact handlers.
- `receive_object()` and `receive_handle_existing_object()`: allocate/reclaim/free object state, handle dnode slots, blocksize changes, raw structure constraints, crypt params, bonus byteswap, checksums/compression, maxblkid, and resume state.
- `flush_write_batch_impl()`: batches adjacent writes for one object into a single transaction, using lightweight writes when possible and falling back for large-block transitions.
- `receive_process_write_record()`: validates order, healing behavior, batching, max object tracking, and write queue ownership.
- `receive_spill()`, `receive_write_embedded()`, `receive_free()`, `receive_freeobjects()`, `receive_object_range()`, `receive_redact()`: per-record mutation handlers.
- `do_corrective_recv()`: rewrites corrupted blocks in place, handling decompression, recompression, encryption, checksum verification, and follow-up reread/error-log update.
- `receive_writer_thread()`: drains the queue, applies records, flushes write batches, handles EOS and error cleanup, and signals completion.
- `dmu_recv_stream()`: main streaming loop; handles raw key payload, resume check, queue/thread setup, reading/prefetching, queueing, EOS flush, clone full-send tail object freeing, and error cleanup.
- `dmu_recv_end_check()` / `dmu_recv_end_sync()`: final sync-task pair; validates final clone swap/snapshot/destroy operations, commits raw keys, destroys replaced snapshots when forced, clears inconsistent state, removes resume metadata, and disowns the dataset.
- `dmu_recv_end()`: public finalizer that runs end sync task or cleanup and creates zvol minors on success.
- `dmu_objset_is_receiving()`: tests whether an objset’s dataset is owned by `dmu_recv_tag`.

## Control Flow Notes
- `dmu_recv_begin()` must be followed by `dmu_recv_stream()` on success; `dmu_recv_stream()` must be followed by `dmu_recv_end()` on success.
- The reader thread does stream I/O, checksum validation, and prefetch; the writer thread mutates the DMU.
- Resume state is saved at the last successfully received object/write offset so resumed streams can verify exact restart location.
- Non-healing receive batches writes until a non-write record, object change, or batch-size boundary.
- Raw receive defers some objset/key initialization until stream processing because raw send carries key and dnode-crypt metadata in the stream.
- Redact records are currently applied as frees until more efficient redaction-range handling exists.
- Existing-dataset receive normally writes into `%recv`, then finalizes by clone swapping with the real head.

## Error Handling And Invariants
- Rejects unsupported stream features, compound streams, invalid objset types, raw-without-encryption, raw-with-embedded, raw without spill flag, large-block mismatches, invalid redaction ancestry, and many malformed record fields.
- Ensures writes are processed in nondecreasing `(object, offset)` order for resumability.
- For raw receives, object range records must align to full dnode blocks and carry crypt params used when writing meta-dnode blocks.
- Healing mode only processes `DRR_WRITE` records and avoids unnecessary rewrites unless existing block read fails with `ECKSUM`.
- On stream/read/writer errors, `dmu_recv_cleanup_ds()` either preserves resumable state or destroys the inconsistent dataset/head.
- Finalization checks clone swap, snapshot creation, forced snapshot destruction, raw key checks, and head destruction before committing changes.

## Dependencies
Depends on DMU/DSL/ZIO/ARC/ZAP/ZVOL/encryption infrastructure: `dmu_objset`, `dnode`, `dbuf`, `arc`, `zio`, `dsl_dataset`, `dsl_dir`, `dsl_pool`, `dsl_bookmark`, `dsl_crypto`, `zap`, `zvol`, `bqueue`, `objlist`, and send stream record definitions.

## Research Notes
This file is the receive-side state machine. The highest-risk areas are ordering/resume correctness, raw encrypted metadata preservation, `%recv` clone swap finalization, redacted-origin compatibility, and memory ownership across queued records and ABD payloads.
