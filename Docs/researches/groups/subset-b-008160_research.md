# subset-b-008160 VOS Research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/vos/vos_common.c -->
# sources/object-store/daos/src/vos/vos_common.c

## Purpose
`vos_common.c` provides shared VOS runtime glue: module initialization, TLS setup, standalone self-mode setup, telemetry allocation, transaction begin/end wrappers, timestamp-cache helper behavior, and media-free helpers. It is the layer that binds VOS to DAOS server module registration, PMDK/umem transactions, BIO/NVMe contexts, RAS notifications, object-cache TLS state, and DTX transaction publishing.

## Important APIs, Types, And Functions
- `struct vos_self_mode` stores standalone-mode TLS, BIO xstream context, NVMe initialization state, a mutex, and a reference count.
- `vos_report_layout_incompat()` reports incompatible durable layout versions through RAS.
- `vos_tls_get()` and `vos_xsctxt_get()` hide the distinction between server TLS and standalone self-mode.
- `vos_ts_add_missing()` fills negative timestamp-cache entries for short-circuited dkey/akey paths.
- `vos_bio_addr_free()` frees SCM offsets through `umem_free()` and NVMe extents through `vea_free()`.
- `vos_tx_begin()` and `vos_tx_end()` wrap umem transactions and DTX handle publication, validation, cleanup, and object eviction on abort.
- `vos_tls_init()` / `vos_tls_fini()` allocate and destroy per-xstream VOS object cache, pool/container handle hashes, transaction descriptor, timestamp table, GC pool list, and telemetry nodes.
- `vos_mod_init()` registers pool/container/object/DTX btree classes and initializes ilog, pool settings, PMDK logging, aggregation thresholds, and environment-driven feature switches.
- `vos_self_init_ext()` / `vos_self_fini()` initialize standalone ABT, NVMe, sys DB/SMD, VOS module state, and BIO xstream context.
- `vos_metrics_alloc()` creates aggregation, space, checkpoint, WAL, cache, VEA, and GC telemetry.

## Control Flow
Module startup enters `vos_mod_init()`, attaches the PMDK log, initializes pool settings, registers container, DTX, object, and object-tree btree classes, initializes ilog support, then reads environment variables such as `DAOS_VOS_AGG_THRESH`, `DAOS_DKEY_PUNCH_PROPAGATE`, `DAOS_SKIP_OLD_PARTIAL_DTX`, and `DAOS_VOS_AGG_GAP`. Server mode gets TLS through `dss_module_key`; standalone mode uses `vos_self_init_ext()`, which serializes global setup with `self_mode.self_lock`, initializes ABT and NVMe, opens the system DB, initializes SMD, allocates BIO context, and honors `DAOS_EVTREE_MODE`.

The transaction path starts with `vos_tx_begin()`. Without a DTX handle it directly begins an umem transaction and checks whether a referenced object was evicted during a possible yield. With a DTX handle it marks the handle as the current TLS DTX and records that the local transaction started. `vos_tx_end()` is the matching exit path. It accumulates SCM/NVMe reservations into the DTX handle, waits until the final operation in a multi-modification DTX, calls `vos_dtx_prepared()` for real non-local DTXs, publishes allocations on success, ends the umem transaction, validates the DTX if required, updates active/solo DTX state, and cancels allocations plus DTX state on error.

## State And Persistence Behavior
Most state here is transient TLS or module state, but it coordinates persistent transactions. `vos_tx_publish()` publishes or cancels reserved SCM actions via `vos_publish_scm()` and NVMe block reservations via `vos_publish_blocks()`. `vos_tx_end()` is responsible for ordering durable DTX preparation, allocation publication, and `umem_tx_end()` so metadata and allocation state commit consistently. Local DTX aborts evict every touched object from the object cache to avoid stale pointers after transaction rollback.

Telemetry nodes and handle hashes are in DRAM. The aggregation gap and start epoch are process-global. Standalone self-mode maintains a reference count so repeated users share initialization and the final release drains GC with `gc_wait()` before tearing down BIO, DB, TLS, NVMe, and ABT.

## Dependencies And Integration Points
This file integrates with `vos_internal.h`, `pmdk_log.h`, umem transactions, BIO/NVMe, VEA, DAOS telemetry, RAS, sys DB/SMD, DAOS server module registration, timestamp cache, object cache, DTX, GC, ilog, object tree, and pool/container handle hash helpers. It is called by most VOS mutation paths through `vos_tx_begin()` / `vos_tx_end()` and by module lifecycle code through `vos_srv_module`.

## Risks And Edge Cases
- `vos_tx_publish()` documents a rollback gap for failed NVMe publish after some reservations have already been released from DRAM, which can temporarily leak space until allocator state is reconciled or restart occurs.
- Transaction begin/end may yield; object eviction checks are required to avoid committing through stale cached object pointers.
- `vos_tx_end()` has multiple race paths around `dae_preparing`, delayed abort, solo DTX post handling, validation, and `-DER_INPROGRESS` client retry.
- Standalone initialization is global and reference-counted; partial failure must call `vos_self_fini_locked()` without double-freeing state.
- Environment switches affect aggregation and DTX compatibility semantics, so tests need explicit coverage of default and overridden values.

## Test Signals
Useful tests include transaction success and abort with SCM/NVMe reservations, object eviction during transaction begin, delayed abort while preparing, standalone init/fini reference counting, sys DB init with and without metadata NVMe, telemetry allocation failure tolerance, aggregation-gap bounds parsing, and timestamp missing-entry population for negative lookups.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/vos/vos_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/vos/vos_container.c -->
# sources/object-store/daos/src/vos/vos_container.c

## Purpose
`vos_container.c` implements the VOS container API and container UUID iteration. It owns creation, open/close, destruction, query, stable-epoch tracking, persisted container properties, and the volatile open-handle cache for `struct vos_container`.

## Important APIs, Types, And Functions
- `struct cont_df_args` passes a persistent `vos_cont_df` pointer and pool into container btree callbacks.
- `vct_ops` defines the persistent container-table btree class: hash key generation, record allocation/free/fetch/update.
- `vos_cont_create()` inserts a new `vos_cont_df` record in the pool container tree.
- `vos_cont_open()` builds the in-memory container handle, opens the object btree, initializes GC, volatile DTX active/committed btrees, DTX LRU array, VEA hints, and reindexes active DTX state.
- `vos_cont_close()` decrements the open count, evicts object-cache entries at last close, and drops the uhash reference.
- `vos_cont_destroy()` removes the persistent container record after ensuring no open handle exists, flushing WAL metadata, and deleting from the pool container btree inside an umem transaction.
- `vos_cont_iter_ops` exposes `VOS_ITER_COUUID` iteration over container UUIDs.
- `vos_cont_get_local_stable_epoch()`, `vos_cont_get_global_stable_epoch()`, `vos_cont_set_global_stable_epoch()`, `vos_cont_set_mod_bound()`, and `vos_cont_save_props()` manage stable epoch and container-extension metadata.

## Control Flow
Creation looks up the UUID, begins an umem transaction, and `dbtree_update()` invokes `cont_df_rec_alloc()`. Allocation persists `vos_cont_df`, its extension, GC bins, and the object table root. Open first checks the in-memory handle hash by container UUID plus pool UUID; an existing handle only increments `vc_open_count`. A cold open fetches the durable `vos_cont_df`, allocates `struct vos_container`, opens GC and object btree state, allocates DTX volatile structures, loads VEA hints, sets `vc_mod_epoch_bound`, reindexes active DTX blobs, then inserts the handle into the uhash and pool container list.

Destroy first invalidates dedup state, rejects open containers, flushes the WAL header, starts a transaction, rechecks for a concurrent reopen, and deletes the container-tree record. The btree free callback does not directly free the full subtree; it evicts timestamp state and enqueues the container for GC with `GC_CONT`. `vos_cont_destroy()` then waits for GC.

## State And Persistence Behavior
Persistent state lives in `vos_cont_df`, `vos_cont_ext_df`, the object tree root, container GC bins, DTX active/committed blob heads and tails, and stable/container property fields in the extension. In-memory state includes open count, uhash link, object btree handle, DTX LRU array and volatile btrees, DTX ordering lists, VEA hint contexts, GC link, DTX counters, local stable epoch, and mod-epoch boundary.

Local stable epoch is calculated from active DTX ordering lists and `vos_agg_gap`, never moving backwards. It also advances `vc_mod_epoch_bound`, which rejects old modifications after a stable epoch has been reported. Global stable epoch is persisted in the container extension, can only move forward, and cannot exceed the local stable epoch.

## Dependencies And Integration Points
The file depends on DAOS dbtree, uhash, umem, VEA hints, GC, DTX, object cache, WAL flush, dedup invalidation, timestamp eviction, checksum/container property structures, and iterator framework. It is the integration point between pool handles and object/DTX/GC subsystems.

## Risks And Edge Cases
- Open error handling calls `cont_free_internal()` for partially initialized handles; the function must tolerate invalid DTX handles and unloaded hints.
- Destroy has a race window around WAL flush and transaction begin, so it explicitly rechecks for container reopen before deleting persistent state.
- Stable-epoch calculations trade precision for O(1)/O(N) DTX list handling, especially for unsorted or reindexed DTX entries.
- Older pool versions or containers without extensions cannot support global stable epoch or saved properties.
- `cont_df_rec_free()` enqueues GC rather than synchronously freeing container contents, so GC correctness is required for durable deletion.

## Test Signals
Tests should cover create duplicate, open cached and cold paths, partial open failure cleanup, close last handle object-cache eviction, destroy busy and race-reopen paths, container UUID iteration anchors, local stable epoch with sorted/unsorted/reindex DTX entries, monotonic global stable epoch enforcement, and property save idempotence for checksum/chunksize fields.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/vos/vos_container.c -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/vos/vos_csum_recalc.c -->
# sources/object-store/daos/src/vos/vos_csum_recalc.c

## Purpose
`vos_csum_recalc.c` verifies input checksums and computes output checksums during VOS aggregation. Aggregation can coalesce several input physical segments into one logical output extent; this file validates the source data before writing the merged checksum metadata.

## Important APIs, Types, And Functions
- `calc_csum_params()` computes the checksum count and starting record index for an input segment, including prefix/suffix records needed by merge-window alignment.
- `csum_agg_verify()` compares freshly calculated input checksums against the checksum array carried by the physical extent, offsetting into the original checksum array when the segment is a subrange.
- `vos_csum_recalc_fn()` is the public worker function called by aggregation. It initializes source and destination scatter/gather lists, runs DAOS checksum calculation for each input segment, verifies each input, clears the shared output checksum buffer, and calculates the checksum for the aggregate output extent.

## Control Flow
The caller passes `struct csum_recalc_args` with a BIO sglist, target evtree entry, and per-segment `struct csum_recalc` metadata. `vos_csum_recalc_fn()` allocates a one-iov source SGL and a destination SGL sized to the segment count, creates a `daos_csummer` using the entry checksum type and chunk size, and loops through each input BIO iov. For each segment it checks logical/physical lengths, points the source SGL at the raw buffer and the destination SGL at the requested buffer, computes verification checksum parameters, zeros the checksum buffer, calls `daos_csummer_calc_one()`, and compares against the original physical checksum. Any mismatch returns `-DER_CSUM` and leaves output checksum data zeroed. If all inputs validate, it zeros `ent_in->ei_csum` and calculates output checksums across the destination SGL.

## State And Persistence Behavior
This file does not persist state directly. It mutates the checksum buffers in `evt_entry_in` and `csum_recalc_args`, sets `args->cra_rc`, and uses caller-owned BIO buffers. It intentionally shares the input/output checksum buffer range and clears it before output generation to avoid leaving stale checksum values after verification.

## Dependencies And Integration Points
It depends on DAOS checksum library (`daos_csummer_*`, `csum_chunk_count()`), evtree extent helpers, BIO iov accessors, aggregation data structures from `vos_internal.h`, and DAOS fail injection (`DAOS_VOS_AGG_MW_THRESH`). It is invoked from `vos_aggregate.c` as part of merge-window aggregation.

## Risks And Edge Cases
- Offset math must match checksum chunk boundaries when the output segment covers a subrange of an input physical extent.
- Prefix and suffix lengths must be multiples of record size; assertions catch invalid callers.
- Failure injection can force checksum mismatch when `cr_phy_off` is nonzero.
- The function uses one shared checksum buffer for repeated verification and final output; missing clears would corrupt results.
- Any checksum mismatch aborts output checksum calculation and should propagate to aggregation metrics and error handling.

## Test Signals
Test full-extent verification, subrange verification with nonzero physical offset, merge windows with prefix/suffix records, multi-segment output checksum generation, checksum mismatch returning `-DER_CSUM`, failure-injection mismatch, and allocation failures in source or destination SGL initialization.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/vos/vos_csum_recalc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/vos/vos_dtx.c -->
# sources/object-store/daos/src/vos/vos_dtx.c

## Purpose
`vos_dtx.c` implements VOS distributed transaction tracking. It manages active DTX allocation, durable prepare blobs, committed DTX blobs, availability checks for reads/updates/purge/migration, commit/abort transitions, membership refresh, reindex after container open, aggregation of old committed records, cleanup, local transactions, and DTX telemetry/statistics.

## Important APIs, Types, And Functions
- Active DTX entries use `struct vos_dtx_act_ent` in a volatile LRU array plus durable `struct vos_dtx_act_ent_df` records inside `DTX_ACT_BLOB_SIZE` blobs.
- Committed entries use volatile `struct vos_dtx_cmt_ent` btree records plus durable `struct vos_dtx_cmt_ent_df` records inside `DTX_CMT_BLOB_SIZE` blobs.
- `vos_dtx_table_register()` registers active and committed DTX dbtree classes.
- `vos_dtx_attach()`, `vos_dtx_register_record()`, `vos_dtx_prepared()`, and `vos_dtx_cleanup()` connect RPC/operation DTX handles to VOS mutations.
- `vos_dtx_check_availability()` maps DTX state to availability for fetch, update, punch, discard, purge, migration, and transactional reads.
- `vos_dtx_commit()` / `vos_dtx_commit_internal()` / `vos_dtx_post_handle()` commit one or more DTXs and update both durable committed blobs and volatile indexes.
- `vos_dtx_abort()` / `vos_dtx_abort_internal()` release records as aborted and remove active entries.
- `vos_dtx_check()`, `vos_dtx_load_mbs()`, `vos_dtx_refresh_mbs()`, `vos_dtx_set_flags()`, `vos_dtx_mark_committable()`, and `vos_dtx_mark_sync()` support DTX refresh/resync and corruption/orphan handling.
- `vos_dtx_act_reindex()` and `vos_dtx_cmt_reindex()` rebuild volatile indexes from durable blobs.
- `vos_dtx_aggregate()` compacts old committed blobs; `vos_dtx_cache_reset()` rebuilds volatile DTX caches; `vos_dtx_get_cmt_stat()` scans committed blobs for count and time statistics.

## Control Flow
The normal mutation path attaches a DTX handle through `vos_dtx_attach()`. If needed, `vos_dtx_alloc()` allocates an LRU slot, initializes DTX identity, epoch, flags, membership shape, sorted/unsorted ordering links, and inserts the active entry into the volatile active btree. Record modifications call `vos_dtx_register_record()`, which stores ilog/SVT/EVT offsets in inline or heap-backed arrays and marks the DTX active. On transaction end, `vos_dtx_prepared()` persists the active entry to the current active blob, extending the blob list if needed, writes membership and record arrays, sets `dae_preparing`, and later marks it prepared.

Commit first pins metadata buckets for evictable pools, starts an umem transaction with return-on-failure behavior, appends committed entries to committed blobs, calls `dtx_rec_release()` to mark ilog/SVT/EVT records committed, and commits the umem transaction. `vos_dtx_post_handle()` then updates telemetry, removes active btree/LRU entries, or marks entries committed/aborted if removal fails. Abort follows the same pin-and-transaction pattern but releases records with aborted state and posts removal as abort.

Availability checks first honor already committed/aborted DTX ids embedded in data records. For active DTXs, the function distinguishes purge/discard/default/update/punch/migration intents, owner visibility, corrupted/orphan flags, partial committed records, solo in-commit entries, membership refresh lists, and prepared-vs-initial states. Non-leader prepared entries can trigger server/client retry through `dtx_inprogress()`.

## State And Persistence Behavior
Durable DTX state is append-oriented. Active DTX blobs are linked from `vos_cont_df::cd_dtx_active_head/tail`; committed DTX blobs are linked from `cd_dtx_committed_head/tail`. Active blob entries contain identity, epoch, LID, flags, membership, dkey hash, and record offsets. Record offsets are tagged with DTX record type flags. Committing or aborting records updates ilog entries or `ir_dtx`/`dc_dtx` fields in SVT/EVT records and then invalidates active durable entries or frees whole blobs when empty. Committed blobs retain compact DTX reply-reconstruction history until aggregation removes old entries.

Volatile state includes active and committed btrees, DTX LRU array, active/sorted/unsorted/reindex lists, DTX handle backpointers, counts, telemetry gauges, and CoS/removal flags. Reindex on open reconstructs volatile active entries and committed index entries from durable blobs, including special handling for invalid, corrupted, orphan, partial committed, and old partial DTX records.

## Dependencies And Integration Points
The file is tightly integrated with umem transactions, DAOS btree, LRU array, ilog, single-value and evtree record descriptors, object cache eviction, bucket pinning/cache for evictable pools, container stable-epoch logic, telemetry, DTX membership structures, fail injection, and VOS aggregation. `vos_common.c` calls into `vos_dtx_prepared()`, validation, cleanup, and post handling from transaction end; iterators and upper layers call status and membership APIs for DTX refresh/resync.

## Risks And Edge Cases
- DTX state spans durable blobs and volatile indexes; partial failures can leave entries marked committed/aborted in memory until restart.
- The committed table may need to reuse old committed blobs under `-DER_NOSPACE`, trading reply-reconstruction history for forward progress.
- Solo DTX committing state is deliberately not treated as fully committed because subsequent fetch may not see data yet.
- Active DTX LID reuse requires epoch validation through the LRU array key and handle validation flags.
- Availability behavior is intent-specific; mistakes can expose uncommitted data, hide committed data, or block aggregation.
- Reindex must tolerate old partial DTX records, invalid durable entries, and non-strict historical epoch ordering.

## Test Signals
High-value tests include prepare/commit/abort for ilog/SVT/EVT records, multi-DTX commit with committed blob extension, committed blob reuse under no-space injection, solo DTX visibility, DTX availability for every intent, membership refresh and leader/non-leader behavior, corruption/orphan flags, invalid-record discard, cache reset and active/committed reindex after reopen, committed aggregation thresholds, evictable-pool bucket pinning, and local transaction object-cache eviction.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/vos/vos_dtx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/vos/vos_dtx_iter.c -->
# sources/object-store/daos/src/vos/vos_dtx_iter.c

## Purpose
`vos_dtx_iter.c` implements the `VOS_ITER_DTX` iterator over active DTX entries. It exposes prepared, unresolved DTXs to upper-layer resync and cleanup logic while filtering entries that are committed, aborted, currently preparing, or attached to a live DTX handle.

## Important APIs, Types, And Functions
- `struct vos_dtx_iter` embeds `struct vos_iterator`, stores a dbtree iterator handle, referenced container, current active entry for linear mode, and a mode flag.
- `dtx_iter_prep()` validates iterator type, resolves the container handle, takes a container reference, and prepares a dbtree iterator over `vc_dtx_active_hdl`.
- `dtx_iter_probe()` starts either linear list iteration from `vc_dtx_act_list` for a zero anchor or dbtree iteration for a nonzero anchor.
- `dtx_iter_next()` advances through the selected backend and skips non-returnable DTX entries.
- `dtx_iter_fetch()` fills `vos_iter_entry_t` with DTX id, oid, epoch, version, flags, start time, dkey hash, and membership data.
- `dtx_iter_process()` rejects delete through iteration.

## Control Flow
The iterator has two paths. With a zero anchor, it walks `vc_dtx_act_list` directly and records the current `vos_dtx_act_ent`; this is a linear in-memory scan. With a nonzero anchor, it probes the active DTX btree with `BTR_PROBE_GE` and fetches by anchor. Both `probe` and `next` skip entries that are already commit/abort states, still `dae_preparing`, or currently attached to a live `dae_dth`. Fetch asserts the returned entry is prepared/unattached/uncommitted/unaborted, marks `dae_need_validation` to protect against later races with RPC handling, and returns inline or out-of-line membership data depending on `DAE_MBS_DSIZE()`.

## State And Persistence Behavior
This file does not modify durable DTX blobs. Its visible mutation is `dae_need_validation = 1`, which forces later DTX handlers to revalidate before becoming committable or committed. It holds a container reference for iterator lifetime and closes the dbtree iterator during finish.

## Dependencies And Integration Points
The iterator depends on VOS iterator framework, active DTX btree, active DTX list, container reference management, DTX layout macros, and umem pointer conversion for out-of-line membership data. It is intended for DTX resync and cleanup consumers that enumerate prepared DTXs.

## Risks And Edge Cases
- Linear list and btree iteration must apply identical skip rules.
- Returning membership pointers points directly into active DTX memory or umem-mapped membership storage, so iterator lifetime and container lifetime matter.
- The iterator intentionally forbids deletion; cleanup must use DTX-specific APIs to preserve commit/abort semantics.
- Marking `dae_need_validation` is a race mitigation but also changes later DTX-handle behavior.

## Test Signals
Test zero-anchor list iteration, anchored btree iteration, skip behavior for commit/abort/preparing/attached entries, fetch of inline and out-of-line memberships, validation flag setting, finish reference release, and delete rejection with `-DER_NO_PERM`.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/vos/vos_dtx_iter.c -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/vos/vos_gc.c -->
# sources/object-store/daos/src/vos/vos_gc.c

## Purpose
`vos_gc.c` implements VOS garbage collection for asynchronously freeing containers, objects, dkeys, akeys, single values, and recx extents after higher-level delete/punch/destroy operations enqueue durable GC items. It supports both traditional pool/container GC bins and bucket-aware GC for evictable metadata pools.

## Important APIs, Types, And Functions
- `struct vos_gc` describes each GC level with name, type, default drain credits, drain callback, and optional free callback.
- `gc_table[]` defines the hierarchy: akey, dkey, object, container.
- `gc_add_item()` appends a durable `vos_gc_item` to the appropriate GC bin and registers the pool/container for later reclaim.
- `gc_drain_btr()`, `gc_drain_evt()`, `gc_drain_key()`, `gc_drain_obj()`, and `gc_drain_cont()` flatten child trees before the parent item is freed.
- `gc_bin_find_bag()`, `gc_bin_add_item()`, `gc_bin_free_bag()`, `bin_get_item()`, and `gc_free_item()` implement persistent ring-style GC bags.
- `gc_reclaim_pool()` is the classic reclaim loop; `gc_reclaim_pool_p2()` is the bucket-aware path for evictable pools.
- `gc_open_pool()`, `gc_open_cont()`, `gc_init_pool()`, `gc_init_cont()`, and close/check helpers initialize and recover GC state.
- `vos_gc_pool()`, `vos_gc_pool_tight()`, `gc_wait()`, `vos_gc_pool_idle()`, `gc_reserve_space()`, `vos_flush_pool()`, and `vos_gc_metrics_init()` are public/runtime integration APIs.

## Control Flow
Deletion paths call `gc_add_item()` inside an existing umem transaction. It chooses the correct bin from pool or container state, optionally using bucket trees for evictable pools, appends the item to a GC bag, registers the pool in TLS GC lists, and links the container on `vp_gc_cont` if needed.

Classic reclaim starts in `gc_reclaim_pool()`: take a container from the fair queue, start one umem transaction, walk from akey upward to container, drain subtrees within credits, free empty items, update stats, and either deregister an empty pool or move it to the tail for later. Container drain destroys DTX tables first, moves leftover container GC bags to pool bins if needed, and drains the object tree.

Evictable-pool reclaim uses `gc_reclaim_pool_p2()`: pin one metadata bucket, start/commit transactions around bucket changes, flatten containers by moving bucket bins to pool bucket trees, pick non-empty bins by bucket, reclaim bins, delete empty bucket-tree records, unpin, update stats, and call `umem_heap_gc()`. This minimizes cache eviction and keeps GC locality aligned with metadata buckets.

## State And Persistence Behavior
GC bins and bags are durable fields in pool/container df structures and extension bucket trees. A bag stores queued `vos_gc_item` records with item offsets and bucket ids. Freeing a GC item is transactional: the bag head is advanced or bag freed/reset, then the real object/key/container/value memory is freed, and stats are updated. Pool registration (`vp_gc_link`, `vp_opened`) and container GC links are volatile but reconstructed on open by checking durable bins and bucket trees.

Pool initialization creates one empty bag for each pool-level GC type. Container initialization starts bins empty because container bins are only needed after object/key deletion. Bucket GC trees are created in pool/container extensions when available. Destroyed containers are not synchronously freed; their `vos_cont_df` is eventually freed by `gc_free_cont()` after DTX tables, object tree, child bags, and extension state are drained.

## Dependencies And Integration Points
GC integrates with dbtree and evtree drain APIs, umem transactions and cache pinning, VEA flushing, VOS DTX table destruction, container/pool reference management, object/key persistent formats, checker validation for GC bucket trees and pool extension padding, telemetry, standalone GC wait, and pool eviction mode.

## Risks And Edge Cases
- GC must not run with an active DTX handle; `vos_gc_yield()` asserts this.
- Container drain destroys DTX tables before yielding, preventing dangling DTX records during subtree drain.
- Persistent bag manipulation uses transactional pointer updates and `UMEM_XADD_NO_SNAPSHOT`; ordering must avoid losing queued items.
- Bucket-aware GC must unpin buckets and close/commit transactions when switching buckets.
- `gc_bags_move()` can transfer container bags to pool bins, and callers must restart at the akey level to avoid missing moved work.
- If GC cannot allocate space, `vp_gc_nospc` forces very small credit slices on later attempts.

## Test Signals
Tests should cover enqueue and drain for every GC type, ring bag wraparound and last-bag reset, container destroy GC including DTX table destruction and extension free, moving container bags to pool bins, classic and evictable-pool reclaim, bucket-tree add/delete and pin switching, pool registration/deregistration reference counts, no-space retry behavior, `vos_gc_pool()` yield modes, metrics counters, checker validation of GC bucket trees, and VEA flush when no GC work remains.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/vos/vos_gc.c -->
