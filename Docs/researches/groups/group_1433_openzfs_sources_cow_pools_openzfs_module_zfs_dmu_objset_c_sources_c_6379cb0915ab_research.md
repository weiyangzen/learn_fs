# Group Research: group_1433_openzfs_sources_cow_pools_openzfs_module_zfs_dmu_objset_c_sources_c_6379cb0915ab

Scope: `Docs/research_subset_a.md`, source tree `sources/cow-pools/openzfs`.  
Files read completely: `dmu_objset.c` 3112 lines, `dmu_recv.c` 3904 lines, `dmu_redact.c` 1200 lines.

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/dmu_objset.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/dmu_objset.c

## Purpose
Implements OpenZFS DMU objset lifecycle and synchronization: opening/holding/owning objsets, creating filesystems/objsets, syncing dirty dnodes and special dnodes, eviction, user/group/project accounting, dataset enumeration, snapshot/child listing, and objset stats/helpers.

## Main Responsibilities
- Initializes global `os_lock` for safe interaction with `dnode_move()` and objset teardown.
- Opens `objset_t` from a root block or hole, reads/writes `objset_phys_t`, registers dataset property callbacks, and opens special dnodes.
- Provides hold/own/release/disown APIs around `dsl_dataset_t` and `dsl_pool_t`.
- Creates objsets and datasets through DSL sync tasks, including encrypted dataset creation edge cases.
- Syncs dirty dnodes in parallel, writes the objset root block, updates ZIL state, and runs sync-done accounting cleanup.
- Maintains user/group/project byte and object accounting through per-sync-task AVL caches.
- Runs background user-space and id/project quota upgrades.
- Enumerates datasets/snapshots/children through DSL/ZAP traversal, optionally parallelized.
- Exports objset metadata helpers and kernel symbols.

## Key Data And State
- `krwlock_t os_lock`: teardown barrier for object relocation safety.
- `dmu_find_threads`: optional tunable for parallel dataset discovery.
- `dmu_rescan_dnode_threshold`: threshold for enabling meta-dnode backfill after enough dnodes are freed.
- `upgrade_tag`: long-hold tag for background objset upgrades.
- `file_cbs[DMU_OST_NUMTYPES]`: per-objset-type callback table for extracting file owner/generation info.
- `userquota_node_t`, `userquota_cache_t`, `userquota_updates_arg_t`: batching structures for syncing quota deltas.
- `dmu_objset_find_ctx_t`: recursive dataset traversal context.

## Important Functions
- `dmu_objset_open_impl()`: allocates and initializes `objset_t`, reads the root BP through ARC, expands old objset phys buffers as needed, registers property callbacks, initializes lists/locks/per-cpu object allocators, opens meta/user/group/project dnodes, and allocates ZIL.
- `dmu_objset_from_ds()`: lazily opens and attaches an objset to a dataset under `ds_opening_lock`.
- `dmu_objset_hold_flags()`, `dmu_objset_own()`, `dmu_objset_own_obj()`: public entry points for holding or owning datasets and obtaining objsets, including decryption/MAC handling for encrypted objsets.
- `dmu_objset_create_impl_dnstats()` and `dmu_objset_create_impl()`: initialize a new objset’s meta-dnode, type, feature-accounting flags, and dirty the dataset.
- `dmu_objset_create_check()` / `dmu_objset_create_sync()`: DSL sync-task pair for dataset creation, parent validation, crypto validation, filesystem limits, and encrypted creation sync forcing.
- `dmu_objset_sync()`: core sync path. Releases the objset phys ARC buffer, creates the root block write, syncs special dnodes, builds `os_synced_dnodes`, dispatches dirty dnode sync tasks, then schedules meta-dnode/ZIL finalization.
- `sync_dnodes_task()` / `sync_meta_dnode_task()`: parallel dirty-dnode sync workers and final root/ZIL completion stage.
- `dmu_objset_sync_done()`: dispatches either quota update tasks or simple dnode release tasks after syncing.
- `dmu_objset_userquota_get_ids()`: extracts old/new user, group, and project IDs from bonus or spill buffers for accounting.
- `dmu_objset_space_upgrade()`: walks objects and dirties bonus buffers to backfill accounting state.
- `dmu_objset_find_dp()` / `dmu_objset_find_impl()` / `dmu_objset_find()`: recursive dataset/snapshot traversal with hidden dataset filtering.
- `dmu_objset_evict()` / `dmu_objset_evict_done()`: unregisters properties, tears down SA/ZIL/dbufs/dnodes, waits through `os_lock`, destroys locks/lists, deregisters from SPA eviction tracking, and frees `objset_t`.

## Control Flow Notes
- Opening a normal dataset requires the pool config lock because property registration may query DSL properties.
- Snapshots do not register mutable checksum/compression/copies/dedup/logbias/sync-style properties.
- Encrypted objsets read the root block raw/authenticated and later untransform during ownership when decrypting.
- Objset sync writes the root block only after special dnodes and dirty dnodes are coordinated; final `zio_nowait()` is deferred until `sync_meta_dnode_task()`.
- User-accounting updates are intentionally skipped for encrypted receives and pool claiming.
- Parallel `dmu_objset_find_dp()` uses child task dispatch while each worker takes a priority pool config read lock to avoid deadlock behind pending writers.

## Error Handling And Invariants
- Creation rejects snapshot names, overlong names, excessive nesting, existing targets, invalid crypto, wrong parent type, and filesystem/snapshot limit violations.
- Objset ownership rejects wrong objset type, writable snapshot ownership, and incompatible encryption versions.
- ARC checksum errors from root block reads are normalized to `EIO`.
- Eviction asserts no dirty txg state and that all dnodes are gone before final destruction.
- User quota ZAP increments are protected by `os_userused_lock` because `zap_increment()` is not atomic.
- Dataset traversal stores only the first error under a shared mutex.

## Dependencies
Heavy coupling with DMU/DSL/SPA internals: `dsl_dataset`, `dsl_dir`, `dsl_pool`, `dnode`, `dbuf`, `arc`, `zio`, `zil`, `zap`, `zfeature`, `zvol`, `sa`, and encryption/key mapping code.

## Research Notes
This file is the central objset management layer. For changes touching receive, send, quota accounting, encryption, or dataset lifecycle, this file defines the object lifetime and sync constraints that those higher-level features depend on.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/dmu_objset.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/dmu_recv.c -->
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
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/dmu_recv.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/dmu_redact.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/dmu_redact.c

## Purpose
Implements redaction bookmark/list generation for redacted ZFS sends. It traverses redaction snapshots, computes block ranges modified in all relevant snapshots, converts those ranges into concrete redaction-list entries for the target snapshot, and supports resumable redaction list creation.

## Main Responsibilities
- Traverses datasets at the target snapshot creation txg to identify blocks or object ranges modified by redaction snapshots.
- Emits sorted/coalesced `redact_record` ranges per traversal thread.
- Merges per-snapshot record streams to compute the intersection of ranges that must be redacted.
- Walks target objects and writes redaction-list entries in MOS syncing context.
- Creates or resumes a redaction bookmark with a redaction list.
- Validates redaction snapshots are before the target and are not themselves redacted datasets.
- Handles deleted objects and holes, including meta-dnode holes that cover whole object ranges.

## Key Data And State
- Tunables/constants:
  - `redact_sync_bufsize`
  - `redaction_list_update_interval_ns`
  - `zfs_redact_queue_length`
  - `zfs_redact_queue_ff`
- `redact_record`: logical candidate range with object/block bounds, block sizing, and EOS marker.
- `redact_thread_arg`: traversal thread state, queue, dataset/objset, resume bookmark, cancellation/error fields, deleted object list, and txg.
- `redact_node`: AVL wrapper around one current record per traversal thread, with start/end AVL nodes.
- `merge_data`: pending redaction blocks, coalescing state, per-txg block lists, furthest progress, redaction list pointer, and latest synctask txg.
- `redact_block_list_node`: list wrapper for `redact_block_phys_t`.
- Kernel-only `objnode` and `zfs_get_deleteq()`: sort ZFS delete queue object IDs into an `objlist_t`.

## Important Functions
- `record_merge_enqueue()`: coalesces adjacent logical redaction records before queueing; flushes pending record on EOS.
- `zfs_get_deleteq()`: kernel path that reads ZFS unlinked set from the master node ZAP, sorts object IDs with AVL, and builds an ordered objlist.
- `redact_cb()`: `traverse_dataset_resume()` callback. Produces candidate records for deleted objects, regular level-0 blocks, dnode holes, and meta-dnode holes.
- `redact_traverse_thread()`: builds deleted-object list, traverses the redaction dataset logically with metadata prefetch, emits EOS, and records errors.
- `redact_range_compare()`, `redact_node_compare_start()`, `redact_node_compare_end()`, `redact_record_before()`: comparison helpers for logical block ranges and AVL ordering.
- `update_avl_trees()`: advances one traversal thread’s current record in both start/end AVL trees.
- `perform_thread_merge()`: k-way range intersection algorithm over traversal queues; emits ranges covered by every redaction snapshot. With zero redaction snapshots, emits a record covering all objects except object 0.
- `redact_merge_thread()`: wraps `perform_thread_merge()` and appends EOS to the merged queue.
- `hold_next_object()`: finds the next non-metadata object in the target objset and holds its dnode.
- `update_redaction_list()`: coalesces physical redaction blocks, splits counts over `REDACT_BLOCK_MAX_COUNT`, and periodically commits pending entries.
- `commit_rl_updates()` / `redaction_list_update_sync()`: schedules and performs MOS redaction-list writes in syncing context, updating list length and progress fields.
- `perform_redaction()`: consumes merged logical ranges, maps them to existing target objects and block IDs, appends `redact_block_phys_t` entries, flushes final coalesced block, commits final progress as `UINT64_MAX`, and waits for sync.
- `redact_snaps_contains()`: GUID membership helper.
- `dmu_redact_snap()`: public entry point; holds target snapshot and redaction snapshots, creates/resumes redaction bookmark/list, starts traversal and merge threads, runs redaction-list materialization, then releases all holds.

## Control Flow Notes
- One traversal thread is created per redaction snapshot. Each produces sorted ranges because dataset traversal is ordered.
- A separate merge thread maintains two AVL trees: one sorted by range start and one by range end. The intersection `[latest start, earliest end]` is redacted when non-empty.
- `perform_redaction()` runs in open context but writes the redaction list through per-txg lists plus sync tasks because the list object lives in the MOS.
- Resume support uses `rlp_last_object` and `rlp_last_blkid` from the existing redaction list/bookmark to restart traversal and validate completion.
- The zero-redaction-snapshot case deliberately redacts all objects except object 0.

## Error Handling And Invariants
- Redaction target must be a snapshot with an objset and must not already have redacted dataset feature active.
- Redaction snapshots must be before the target and not redacted datasets.
- Resume validates bookmark has a redaction object, snapshot GUID set matches the requested redaction snapshots, and previous progress is not already complete.
- Cancellation propagates through `cancel` flags; workers drain queues to EOS on merge errors.
- `redact_cb()` ignores indirect non-hole blocks and only emits useful level-0/hole/deleted-object ranges.
- MOS redaction-list updates assert queued blocks do not pass the recorded furthest visited position.

## Dependencies
Depends on traversal, DMU object iteration, redaction list/bookmark DSL support, bqueues, AVL/list utilities, and, in kernel builds, ZFS unlink queue inspection: `dmu_traverse`, `dmu_objset`, `dmu_tx`, `dsl_dataset`, `dsl_bookmark`, `dmu_redact`, `objlist`, `bqueue`, `zap`, and ZFS znode/VFS headers.

## Research Notes
This file is the redaction-list construction engine. Its key correctness property is preserving ordered logical ranges from traversals, intersecting them accurately across all redaction snapshots, and only then translating them into concrete block entries in the target snapshot while maintaining resumable progress.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/dmu_redact.c -->