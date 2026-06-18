# Group Research: group_1438_openzfs_sources_cow_pools_openzfs_module_zfs_dsl_scan_c_sources_cow_241bc60da389

Scope: `Docs/research_subset_a.md` / `sources/cow-pools/openzfs/module/zfs/*`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/dsl_scan.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/dsl_scan.c

## Role

Implements OpenZFS pool scan machinery: scrub, resilver, error scrub, async destroy block freeing, obsolete-block marking, scan checkpointing, sorted scrub I/O queues, scan progress accounting, and scan state persistence in the MOS pool directory.

## Major Subsystems

- Scan lifecycle:
  - `dsl_scan_init()` loads persisted scan and error-scrub state, handles old scrub layout compatibility, reloads the dataset queue, initializes DDT walks, and restores progress counters.
  - `dsl_scan_setup_check()` and `dsl_scan_setup_sync()` start scrub or resilver state, create the scan queue object, reset stats, initialize DDT traversal, emit events, and persist `dsl_scan_phys_t`.
  - `dsl_scan()` is the public start/resume entry point for scrub, resilver, and error scrub.
  - `dsl_scan_done()` tears down scan queues, removes legacy scrub keys, updates DTLs, rotates error logs, emits finish/cancel events, and marks scan state finished or canceled.
  - `dsl_scan_cancel()` and scrub/error-scrub pause/resume helpers wrap state changes in sync tasks.

- Error scrub:
  - `dsl_errorscrub_setup_sync()` initializes `errorscrub_phys`, cursor state, and event/history records.
  - `dsl_errorscrub_sync()` walks the last error log, reads affected blocks, supports both legacy bookmark names and `SPA_FEATURE_HEAD_ERRLOG`, limits blocks per txg, persists cursor state, and completes when no cursor entries remain.
  - `scrub_filesystem()` maps head error-log entries to live filesystems and relevant snapshots, then issues raw scrub reads for blocks still affected.
  - `read_by_block_level()` resolves a bookmark back to a current block pointer through dnode/dbuf lookup, avoids unloaded encrypted datasets, and issues scan I/O.

- Metadata traversal:
  - `dsl_scan_visit()` drives DDT traversal, MOS/origin traversal, resumed dataset traversal, and queued dataset traversal.
  - `dsl_scan_visitds()` scans one dataset’s root block, traverses its ZIL for live heads, adds next snapshots and clones to the queue, and handles repeated passes when mutation invalidates the current pass.
  - `dsl_scan_visitbp()`, `dsl_scan_recurse()`, and `dsl_scan_visitdnode()` recursively inspect block pointers, dnodes, objset blocks, indirect blocks, spill blocks, user/group/project accounting objects, and feature assertions.
  - Traversal skips holes, redacted blocks, blocks below `scn_cur_min_txg`, DDT-contained blocks already handled by the DDT pass, and physical births above `scn_cur_max_txg`.

- DDT scrub interaction:
  - `dsl_scan_ddt()` walks dedup-table classes up to `scn_ddt_class_max`.
  - `dsl_scan_ddt_entry()` creates synthetic block pointers for DDT entries and scans each physical variant once.
  - The file documents why DDT-scrub-first avoids repeatedly scrubbing deduped blocks but still tolerates class changes during an active scan.

- Sorted scan I/O:
  - `scan_io_t` stores the minimal block-pointer and bookmark data needed to reconstruct scrub/resilver reads.
  - Per-top-vdev `dsl_scan_io_queue_t` tracks queued `scan_io_t` records by address plus range extents by address and weighted size.
  - `dsl_scan_enqueue()` queues non-gang scan I/O into per-vdev sorted queues when sorted scans are active; gang blocks and legacy scans execute immediately.
  - `scan_io_queues_run()` fans out one worker per top-level vdev to issue queued extents.
  - `scan_io_queue_fetch_ext()` chooses LBA order during checkpoints or the best weighted extent during memory clearing.
  - `scan_io_queue_gather()` removes up to 32 queued I/Os from an extent at a time and shrinks/removes the extent.
  - `scan_exec_io()` applies global or per-vdev in-flight byte limits and issues raw scrub/resilver reads.
  - `dsl_scan_scrub_done()` releases ABD buffers, updates in-flight counters, wakes waiters, and increments scan or error-scrub errors.

- Prefetch:
  - `dsl_scan_prefetch_thread()` drains a bookmark-ordered prefetch queue under global scan in-flight limits.
  - `dsl_scan_prefetch()` queues metadata and indirect blocks likely to be needed by traversal.
  - `dsl_scan_prefetch_cb()` recursively schedules children from prefetched indirect, dnode, and objset blocks.
  - Prefetch is disabled for redacted blocks, holes, old births, and level-0 non-metadata data.

- Dataset mutation handling:
  - `dsl_scan_ds_destroyed()` updates active and cached bookmarks and removes/replaces dataset queue entries when datasets or snapshots are destroyed.
  - `dsl_scan_ds_snapshotted()` moves active scan references from a head to the newly created previous snapshot.
  - `dsl_scan_ds_clone_swapped()` swaps bookmarks and queue entries when clone promotion swaps dataset identities.
  - These paths use `SYNC_CACHED` persistence when the current on-disk scan state may not match in-core queue progress.

- Async destroy/free work:
  - `dsl_process_async_destroys()` frees blocks from `dp_free_bpobj`, async-destroy bptrees, and obsolete bpobjs before scrub/resilver work.
  - `dsl_scan_free_block_cb()` issues sync frees, updates the free dir accounting, waits periodically for async frees, and enforces per-txg limits.
  - Finished async destroy deactivates `SPA_FEATURE_ASYNC_DESTROY`, removes pool directory state, and handles leaked free-dir space when configured.

- Resilver integration:
  - `dsl_scan_need_resilver()` checks DTL coverage, gang/indirect special cases, and deferred-resilver state.
  - `dsl_scan_restart_resilver()` records restart txg.
  - `dsl_scan_assess_vdev()` requests or defers resilver when vdev DTL ranges require it.
  - `dsl_scan_sync()` restarts scans when needed for deferred resilver policy or explicit restart state.

## Main Sync Scheduler

`dsl_scan_sync()` is the primary syncing-context entry point. It only runs in sync pass 1, defers after import, processes async destroys first, handles scan restart conditions, applies test/debug suspension, optionally enables sorted scanning, decides whether to gather metadata or issue queued I/O, runs prefetch during traversal, waits for scan I/O roots, marks scan-complete txg, and persists state with `dsl_scan_sync_state()`.

For sorted scans, metadata traversal and queued I/O issuing are intentionally mutually exclusive. The scan gathers I/O until memory pressure or checkpointing triggers clearing, then issues sorted per-vdev extents until below the soft memory limit or until queues are empty.

## State and Synchronization

- Persistent state is stored in MOS ZAP entries `DMU_POOL_SCAN` and `DMU_POOL_ERRORSCRUB`.
- `scn_phys_cached` exists so dataset mutation can rewrite a safe cached scan state while sorted queues still contain unissued work.
- `scn_queues_pending` counts non-empty per-vdev scan queues.
- `spa_scrub_lock` protects global prefetch/scrub in-flight counters and prefetch queue coordination.
- Each top-level vdev has `vdev_scan_io_queue_lock` for its scan queue and per-vdev in-flight limits.
- `dp_config_rwlock` is entered while traversing pool/dataset topology.

## Tunables

The file defines module parameters for scan vdev in-flight limits, minimum per-txg times, suspend/progress controls, scrub I/O/prefetch disable switches, async free limits, scan memory limits, legacy scan mode, checkpoint interval, extent gap, fill weighting, resilver deferral policy, and error blocks per txg.

## Research Notes

This file is the core scrub/resilver engine. Its main complexity comes from making long-running traversal resumable while concurrently supporting copy-on-write dataset mutations, DDT dedup semantics, vdev DTL healing, async destroy cleanup, and physically sorted I/O issuance without persisting unsafe progress while queued reads remain outstanding.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/dsl_scan.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/dsl_synctask.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/dsl_synctask.c

## Role

Provides the DSL sync-task framework for running caller-supplied checks and mutations in txg syncing context with the correct pool configuration locking and space checks.

## Key Functions

- `dsl_sync_task_common()` opens the target pool, creates a transaction, runs the check callback once in open context under config read locking, queues the task into either normal or early sync-task txg lists, waits for sync completion, and retries after `EAGAIN` once the deferred txg window has synced.
- `dsl_sync_task()` queues a normal blocking sync task.
- `dsl_early_sync_task()` queues a blocking early sync task that executes before dirty dataset data is written in `dsl_pool_sync()`.
- `dsl_sync_task_sig()` supports an interruptible wait and invokes a signal callback once if interrupted while still ensuring the txg sync completes.
- `dsl_sync_task_nowait()` and `dsl_early_sync_task_nowait()` allocate nowait task records and enqueue fire-and-forget sync callbacks.
- `dsl_sync_task_sync()` is called in syncing context, checks requested pool space reservations, takes `dp_config_rwlock` as writer, reruns the check callback, invokes the sync callback on success, and frees nowait tasks.

## Space and Locking Semantics

- `blocks_modified` is converted to an estimated MOS space cost using `DST_AVG_BLKSHIFT`.
- Space checks use `dsl_pool_unreserved_space()` and root-dir used bytes, with MOS writes multiplied by 3 for dittoed metadata.
- Open-context checks run with config read locking; sync-context checks and mutations run with config write locking.
- Early tasks are explicitly warned not to dirty metaslabs because they run before normal dirty-data syncing.

## Research Notes

This file is the small but central bridge between ioctl/open-context control paths and txg-synchronous metadata mutation. Its contract lets callers validate cheaply before queueing, then validate again under syncing-context invariants immediately before mutation.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/dsl_synctask.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/dsl_userhold.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/dsl_userhold.c

## Role

Implements user holds and releases for ZFS snapshots, including persistent holds, temporary holds tied to an onexit minor, hold listing, error-list reporting, and deferred snapshot destruction when the last hold is released.

## Hold Path

- `dsl_dataset_user_hold_check_one()` validates hold tag length, temporary tag length limits, and per-snapshot tag uniqueness.
- `dsl_dataset_user_hold_check()` requires userrefs support, detects duplicate snapshot/tag pairs, validates snapshot names and tags, records successful holds in `dduha_chkholds`, and records `ENOENT` in the caller error list without failing the whole batch.
- `dsl_dataset_user_hold_sync_one_impl()` creates the userrefs ZAP on first hold, increments `ds_userrefs`, stores the tag timestamp, records temporary holds in pool-level hold state, and logs history.
- `dsl_onexit_hold_cleanup()` registers cleanup callbacks for temporary holds.
- `dsl_dataset_user_hold()` wraps the batch in a sync task and returns success when at least the valid existing snapshots were held according to the lzc_hold semantics.

## Temporary Hold Cleanup

- `dsl_dataset_user_release_onexit()` reopens the pool by name, verifies the spa load guid still matches, and releases temporary holds when the owning process exits.
- Temporary hold cleanup groups tags by dataset object string so they can be released even after normal name-based lookup would be inconvenient.

## Release Path

- `dsl_dataset_user_release_impl()` handles normal name-based release and temporary object-id release.
- Kernel builds unmount snapshots before release because releasing holds may allow deferred destruction.
- `dsl_dataset_user_release_check_one()` verifies the target is a snapshot, checks each requested hold tag in the userrefs ZAP, records missing tags in the error list, and marks deferred-destroy snapshots for destruction if the released holds are the final references.
- `dsl_dataset_user_release_sync_one()` removes temporary pool holds, removes userrefs ZAP entries, decrements `ds_userrefs`, and logs history.
- `dsl_dataset_user_release_sync()` releases all checked holds and calls `dsl_destroy_snapshot_sync_impl()` for snapshots that became destroyable.
- `dsl_dataset_user_release()` releases persistent holds.
- `dsl_dataset_user_release_tmp()` releases temporary holds by dataset object id.

## Listing

`dsl_dataset_get_holds()` opens the pool and dataset, walks the dataset userrefs ZAP if present, and returns hold tag names mapped to stored timestamps.

## Error Handling

Missing snapshots or missing hold tags are recorded in caller-provided error nvlists where the API contract permits partial success. Non-`ENOENT` validation errors abort the batch before sync-side mutation.

## Research Notes

The file’s core invariant is that hold creation and release are staged through sync-task check lists. Sync functions operate only on previously validated entries, which keeps batch semantics atomic for non-missing-object errors while still reporting per-entry `ENOENT` details.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/dsl_userhold.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/edonr_zfs.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/edonr_zfs.c

## Role

Adapts the Edon-R 512-bit hash implementation to the OpenZFS ABD-backed `zio_checksum` interface and provides salted checksum template setup/free functions.

## Key Functions

- `edonr_incremental()` feeds ABD chunks into `EdonRUpdate()` in bits.
- `abd_checksum_edonr_native()` copies a prepared Edon-R state template, iterates the ABD payload into it, finalizes the digest, and copies the first checksum words into `zio_cksum_t`.
- `abd_checksum_edonr_byteswap()` calls the native checksum path and is intended to publish byteswapped words for opposite-endian checksum handling.
- `abd_checksum_edonr_tmpl_init()` expands the ZFS checksum salt into one full Edon-R block by hashing the salt and then hashing that digest, initializes an Edon-R state, and feeds the expanded salt block as the MAC key/template.
- `abd_checksum_edonr_tmpl_free()` zeroes and frees the template state.

## Research Notes

The salt expansion relies on `EDONR_BLOCK_SIZE == 2 * digest_size` and uses a static assertion for that invariant. One notable implementation detail is that the byteswap function computes a temporary native checksum; the assignment lines should be checked carefully by maintainers because the visible code byteswaps from `zcp->zc_word` rather than from the temporary checksum variable.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/edonr_zfs.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/fm.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/fm.c

## Role

Provides Fault Management Architecture support used by ZFS: FMA nvlist allocation helpers, ereport and FMRI constructors, ENA helpers, kernel zevent queueing, event stream cursor operations, and FMA-related kstats.

## Kernel Zevent Queue

- `zfs_zevent_alloc()` and `zfs_zevent_free()` allocate/free posted event records and run the provided cleanup callback.
- `zfs_zevent_insert()` inserts newest events at the head and drains the oldest event when `zfs_zevent_len_max` is exceeded.
- `zfs_zevent_post()` stamps time and monotonically increasing EID fields into an ereport, checks native nvlist size against `ERPT_DATA_SZ`, queues the event, wakes waiters, or calls the cleanup callback on failure.
- `zfs_zevent_next()` returns the next event for a per-open stream cursor, duplicates the nvlist, reports per-stream dropped counts, and includes rate-limited drops.
- `zfs_zevent_wait()` waits interruptibly for new events or shutdown.
- `zfs_zevent_seek()` positions a stream cursor by EID, start, or end.
- `zfs_zevent_init()` and `zfs_zevent_destroy()` manage per-open zevent state.
- `zfs_zevent_drain_all()` clears all queued events during shutdown.

## FMA Nvlist Helpers

- `fm_nva_xcreate()` and `fm_nva_xdestroy()` create/destroy fixed-buffer nv allocators.
- `fm_nvlist_create()` creates an FMA nvlist with either caller-supplied allocation operations or default ZFS memory allocation wrappers.
- `fm_nvlist_destroy()` frees the nvlist and optionally its allocator handle.
- `fm_payload_set()` and `i_fm_payload_set()` add typed varargs payload members across scalar, array, string, nvlist, and boolean types while tracking failures.

## Ereport and FMRI Construction

- `fm_ereport_set()` builds an `ereport.*` class event with ENA, detector, and payload fields.
- `fm_fmri_hc_set()` creates hierarchical component FMRIs from name/id varargs.
- `fm_fmri_hc_create()` extends an existing hc-list from a base board FMRI with additional hc pairs.
- `fm_fmri_dev_set()`, `fm_fmri_cpu_set()`, `fm_fmri_mem_set()`, and `fm_fmri_zfs_set()` construct dev, cpu, mem, and zfs scheme FMRIs with version validation and optional authority/device fields.

## ENA Helpers

- `fm_ena_generate_cpu()` creates format 1 or 2 ENAs from timestamp and CPU id.
- `fm_ena_generate()` disables preemption while reading CPU id.
- `fm_ena_increment()`, `fm_ena_generation_get()`, `fm_ena_format_get()`, `fm_ena_id_get()`, and `fm_ena_time_get()` manipulate and decode ENA fields.

## Kstats and Lifecycle

- `erpt_kstat_data` tracks dropped ereports, set failures, FMRI failures, payload failures, and duplicate ereports.
- `fm_init()` creates the `zfs/fm` kstat, initializes zevent locks/lists/cv, and initializes ZFS ereport support.
- `fm_fini()` tears down ereport support, drains queued events, broadcasts shutdown, waits for blocked waiters, destroys synchronization primitives, and deletes kstats.
- `fm_erpt_dropped_increment()` records rate-limited event drops.

## Research Notes

This file is both protocol-construction utility code and the kernel event transport behind ZFS event consumers. It is careful about bounded event queue length, cursor invalidation on drain, and failure counters for observability.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/fm.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/gzip.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/gzip.c

## Role

Implements the ZFS gzip compression and decompression backend, using kernel zlib wrappers in kernel builds, userspace zlib otherwise, and optional QAT hardware acceleration.

## Key Functions

- `zfs_gzip_compress_buf()` compresses a source buffer into a destination buffer at the requested gzip level.
  - Asserts destination length is no larger than source length.
  - Tries QAT compression when the buffer size qualifies.
  - Treats QAT incompressible status or software compression failure as uncompressed output when destination size equals source size.
  - Returns the compressed size or source length for incompressible/fallback-copy cases.
- `zfs_gzip_decompress_buf()` decompresses into an expected output size.
  - Tries QAT decompression when suitable.
  - Falls back to software decompression.
  - Requires the decompressed byte count to exactly match `d_len`.
- `ZFS_COMPRESS_WRAP_DECL(zfs_gzip_compress)` and `ZFS_DECOMPRESS_WRAP_DECL(zfs_gzip_decompress)` expose the level-specific compressor/decompressor wrapper set expected by the ZFS compression table.

## Build Differences

Kernel builds use `z_compress_level()` and `z_uncompress()` from `zmod`; userspace builds use zlib `compress2()` and `uncompress()`.

## Research Notes

The backend relies on the wider ZFS compression wrapper macros for the public entry points. The local logic is focused on accelerator fallback and strict decompressed-size validation.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/gzip.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/hkdf.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/hkdf.c

## Role

Implements HKDF-SHA512 for ZFS encryption key derivation using the kernel crypto API’s SHA-512 HMAC mechanism.

## Key Functions

- `hkdf_sha512_extract()` performs HKDF extract:
  - Configures `SUN_CKM_SHA512_HMAC`.
  - Uses the salt as the HMAC key.
  - MACs the input key material.
  - Writes a `SHA512_DIGEST_LENGTH` pseudorandom key to the output buffer.
- `hkdf_sha512_expand()` performs HKDF expand:
  - Uses the extract key as the HMAC key.
  - Iteratively computes `T(i) = HMAC(PRK, T(i-1) || info || i)`.
  - Copies full digest blocks and a final partial block into the caller output.
  - Rejects expansion requiring more than 255 digest blocks.
- `hkdf_sha512()` is the exported composition helper that extracts into a stack buffer and then expands into the requested output key.

## Error Handling

Crypto API failures are mapped to `EIO`. Overlong HKDF expansion is rejected with `EINVAL`.

## Research Notes

The code follows the standard HKDF extract/expand split. The comment notes that ZFS encryption uses this to derive new encryption keys and that the `info` parameter is referred to as salt elsewhere in the surrounding code.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/hkdf.c -->