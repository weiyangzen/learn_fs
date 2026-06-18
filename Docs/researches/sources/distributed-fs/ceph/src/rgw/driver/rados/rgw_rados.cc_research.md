# Research: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_rados.cc

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-006973`: lines 1-7990, `Docs/researches/chunks/subset-b-006973_research.md`
- `subset-b-006974`: lines 7991-12065, `Docs/researches/chunks/subset-b-006974_research.md`

## Chunk Research

### subset-b-006973: lines 1-7990

# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_rados.cc lines 1-7990

## Scope

This chunk covers the first 7,990 lines of the Ceph RGW RADOS backend implementation. It includes common helpers, object version tracking, per-request object-state caching, multisite notifier/sync worker setup, RADOS pool and service initialization, log and usage APIs, bucket creation/listing/deletion helpers, object locator repair, Swift versioning copy/restore, object metadata write transactions, local and remote copy paths, cloud-tier transition/restore, garbage-collection chain management, bucket index checking, encrypted multipart resync, object deletion, object-state loading, atomic write tests, metadata attribute updates, multipart part-state selection, and the beginning of `RGWRados::Object::Read::prepare()`.

The chunk ends inside `RGWRados::Object::Read::prepare()` after the call to `get_part_obj_state()` for requested multipart parts. The rest of read preparation, range setup, filters, iteration, and later object/bucket APIs are outside this chunk and must be merged with the next chunk for complete read-path conclusions.

## Purpose

`rgw_rados.cc` is the main bridge between RGW's object-store abstraction and Ceph RADOS. This section owns the low-level object lifecycle around bucket indexes, head/tail object layout, object xattrs, manifests, versioning, multisite logs, and background processors.

At runtime it maps logical RGW bucket/object identities to raw RADOS objects, prepares conditional RADOS operations with CLS version checks, keeps bucket index entries consistent with object head writes/deletes, maintains object state and manifest caches for a request, and drives copy/transition/restore flows that may span local RADOS pools, remote zones, or cloud tiers. It also initializes the RGW background machinery for GC, lifecycle, restore, object expiration, resharding, bucket logging, notifications, sync, and sync-log trimming.

## Important APIs, Types, and Functions

Early helpers include `read_attr()` overloads for extracting xattrs, `decode_restore_index_fields()` for translating restore-status attrs into bucket-index fields, and `rgw_obj_select::get_raw_obj()` for resolving either a raw object or a logical object through placement.

`RGWObjVersionTracker` wraps CLS version operations for both librados and neorados. `prepare_op_for_read()`, `prepare_read()`, `prepare_write()`, and `prepare_op_for_write()` attach compare/read/set/inc version operations; `apply_write()` updates the local version tracker after a successful write, especially for incremented versions.

`RGWObjectCtx` stores per-object `RGWObjStateManifest` entries behind a shared mutex. `get_state()` lazily creates cache entries, while `set_compressed()`, `set_atomic()`, `set_prefetch_data()`, and `invalidate()` preserve selected state flags across invalidation.

Background worker classes include `RGWRadosThread`, `RGWMetaNotifier`, `RGWDataNotifier`, `RGWMetaSyncProcessorThread`, `RGWDataSyncProcessorThread`, and `RGWSyncLogTrimThread`. They run periodic or long-lived loops for mdlog/datalog notification, metadata sync, data sync, meta/data/bucket log trimming, and wakeup routing through `wakeup_meta_sync_shards()` and `wakeup_data_sync_shards()`.

`RGWIndexCompletionManager` manages asynchronous bucket-index completion callbacks. It creates `complete_op_data` records, distributes them across shard locks, removes them on completion, and retries completions that hit `-ERR_BUSY_RESHARDING` by reopening the current bucket shard and replaying `cls_rgw_bucket_complete_op()` under `guard_reshard()`.

Initialization APIs include `init_rados()`, `init_svc()`, `init_begin()`, `init_complete()`, `finalize()`, `register_to_service_map()`, `update_service_map()`, and pool open helpers such as `open_root_pool_ctx()`, `open_gc_pool_ctx()`, `open_restore_pool_neo_ctx()`, and `open_pool_ctx()`. `init_complete()` wires together the sync module, pool contexts, index completion manager, GC, object expirer, metadata/data sync threads, trim threads, notifiers, bucket/topic caches, lifecycle, restore, quota, tombstone cache, resharding, bucket logging, notifications, and v1 topic migration.

Log and usage functions include `log_list_init()`, `log_list_next()`, `log_remove()`, `log_show_init()`, `log_show_next()`, `usage_log_hash()`, `log_usage()`, `read_usage()`, `trim_usage()`, and `clear_usage()`. Usage entries are sharded into `usage.N` objects and manipulated through RGW CLS usage-log helpers.

Bucket APIs include `Bucket::update_bucket_id()`, `Bucket::List::list_objects_ordered()`, `Bucket::List::list_objects_unordered()`, `create_pool()`, `create_bucket_id()`, `create_bucket()`, `BucketShard::init()` overloads, `on_last_entry_in_listing()`, `check_bucket_empty()`, `store_delete_bucket_info_flag()`, `delete_bucket()`, `set_bucket_owner()`, `set_buckets_enabled()`, and `bucket_suspended()`.

Object placement and repair functions include `obj_to_raw()`, `get_obj_head_ioctx()`, `get_obj_head_ref()` overloads, `get_raw_obj_ref()`, `get_system_obj_ref()`, `fix_head_obj_locator()`, `move_rados_obj()`, and `fix_tail_obj_locator()`. These resolve data pools, object ids, locators, and repair old misplaced head/tail objects.

Object write and metadata update paths are centered on `RGWRados::Object::Write::_do_write_meta()` and `write_meta()`. They prepare bucket-index transactions, apply preconditions, prepare atomic xattr tags, write head data/xattrs/manifests, record restore and storage-class fields, complete bucket index entries, update OLH state for versioned objects, schedule object-expirer hints, and update quota cache. `set_attr()` and `set_attrs()` provide a metadata-only path that still updates object xattrs, bucket index metadata, restore category/state, replication trace, expiration hints, and cached state.

Copy and remote-transfer types include `RGWRadosPutObj`, `set_copy_attrs()`, `rewrite_obj()`, `reindex_obj()`, `obj_time_weight`, `RGWGetExtraDataCB`, `stat_remote_obj()`, `RGWFetchObjFilter_Default::filter()`, `fetch_remote_obj()`, `copy_obj_to_remote_dest()`, `copy_obj()`, and `copy_obj_data()`. These paths preserve or rewrite attributes, stream remote objects through processors, verify ETags, choose placement/storage class, handle encryption/compression attrs, and decide between zero-copy manifest/refcount reuse and full data rewrite.

Cloud-tier and restore helpers include `fixup_manifest_to_parts_len()`, `transition_obj()`, and `restore_obj_from_cloud()`. They preserve encrypted multipart part lengths, copy objects into transition placement, fetch archived/cloud-tiered bytes back, set restore status/type/time/expiry attrs, update storage class/category, and complete via `AtomicObjectProcessor`.

Deletion and GC APIs include `Object::complete_atomic_modification()`, `update_gc_chain()`, `send_chain_to_gc()`, `delete_objs_inline()`, `defer_gc()`, `remove_rgw_head_obj()`, `cls_obj_check_prefix_exist()`, `cls_obj_check_mtime()`, `Object::Delete::delete_obj()`, `delete_obj()`, `delete_raw_obj()`, and `delete_obj_index()`. They coordinate head object removal, OLH/delete-marker handling, bucket-index delete transactions, tail-object refcount/GC submission, tombstone cache insertion, and quota decrements.

State/read preparation includes `generate_fake_tag()`, `is_olh()`, `has_olh_tag()`, `get_olh_target_state()`, `get_obj_state_impl()`, `get_obj_state()` overloads, `Object::get_manifest()`, `Object::Read::get_attr()`, `Object::Stat::{stat_async,wait,finish}()`, `append_atomic_test()` overloads, `Object::get_state()`, `Object::invalidate_state()`, `Object::get_current_version_state()`, `Object::check_preconditions()`, `Object::prepare_atomic_modification()`, `get_part_obj_state()`, and the opening of `Object::Read::prepare()`.

## Control Flow

Initialization starts with `init_begin()`: it sets the context, connects librados, initializes service layers, initializes control interfaces, and generates the host id. `init_complete()` then opens all required pools, creates the index completion manager, starts optional background services, determines whether sync should run, starts meta/data sync threads for configured source zones, configures log trimming, initializes caches, starts lifecycle/restore/quota/reshard/bucket logging/notification services, and optionally starts topic migration on a meta-master zone.

Shutdown reverses this order in `finalize()`. It marks sync threads down, stops the async processor before joining sync workers, stops notifiers, sync tracer, restore/lifecycle/GC/object-expirer processors, quota, services, caches, reshard wait/thread, notifications, bucket logging, and finally deletes the index completion manager. Several workers have independent `stop_process()` hooks so coroutine managers and sync managers can break out of blocking runs.

Bucket listing has two variants. Ordered listing repeatedly calls `cls_bucket_list_ordered()` with marker/prefix/delimiter state, handles namespace enforcement, end markers, visibility/version filtering, delimiter common-prefix filtering both for newer CLS-side filtering and older client-side fallback, and stops once enough results are gathered or progress stalls. Unordered listing calls `cls_bucket_list_unordered()`, reads ahead to compensate for filtering, and applies namespace, version, prefix, end-marker, and access filters without global sort guarantees.

Bucket creation loops up to `MAX_CREATE_RETRIES`. Each attempt generates or uses a bucket id, fills ownership/placement/versioning/object-lock/quota/layout fields, initializes the index when placement is known, and writes linked bucket info exclusively. On `-EEXIST`, it rereads existing bucket info, cleans up the newly initialized index/instance if it raced with a different bucket instance, and returns the existing info.

Object metadata writes first load object state and possibly the current version for preconditions. `_do_write_meta()` checks ETag/size/time preconditions, prepares atomic xattr tags, sets object-retention defaults, writes data/manifest/xattrs/mtime/source-zone/storage-class/restore fields, prepares the bucket index if needed, issues the RADOS write, cleans previous tail objects through GC, completes the bucket-index entry, updates OLH for versioned operations, records expiration hints, invalidates cached state, and updates quota. On non-timeout errors it cancels the pending index operation; on timeout it intentionally leaves the pending entry for later listing recovery.

Remote fetch/copy streams the source through `RGWRESTConn::get_obj()`. `RGWRadosPutObj` receives optional JSON metadata prelude, decodes attrs, handles encrypted/compressed object edge cases, optionally inserts compression and ETag-verifier filters, performs fallback ACL permission checks for old peers, and sends data into an `AtomicObjectProcessor`. `fetch_remote_obj()` retries endpoint internal errors, validates transferred size, decodes ACL owner, optionally overrides owner, applies replication attrs, removes or preserves expiration/tags as appropriate, verifies computed ETag, then retries `processor.complete()` on copy-if-newer races until the destination is demonstrably current or `MAX_COMPLETE_RETRY` is reached.

Local copy chooses between full data copy and manifest/refcount reuse. It prepares a source read, sanitizes attrs for destination semantics, removes stale replication/encryption/storage-class attrs, follows OLH, compares source/destination placement and pools, and forces full copy when manifests are absent, placement differs, pools differ, the source has no tail, the head chunk is too large, or a data processor requires rewriting. In zero-copy mode it increments tail refcounts asynchronously, optionally copies the first chunk into the new head, writes a cloned manifest through `write_meta()`, and rolls back successful refcount increments on failure.

Cloud transition reads the existing object and rewrites it into a target placement while preserving encryption multipart metadata and original mtime. Cloud restore first reads current attrs/mtime, validates restore storage class, fetches data from cloud or S3 Glacier tier helpers, handles in-progress Glacier restores, stamps restore status/time/type/expiry/cloud-tier attrs, suppresses sync for temporary restores, forces sync logging for permanent restores, and completes the restored object through `AtomicObjectProcessor`.

Deletion splits on versioning. For versioned buckets, deleting a current object creates a delete marker through `set_olh()`, while deleting an explicit instance unlinks that instance after bucket-index and conditional checks. It then writes datalog entries when data logging is enabled. For unversioned buckets, it loads state, validates unmodified/time/expiration/size/ETag conditions, prepares a bucket-index delete transaction, removes RGW head attrs/object through CLS, completes or cancels the index transaction according to the RADOS result, inserts a tombstone cache entry on successful or already-missing head deletion, completes atomic tail cleanup, invalidates state on races, and updates quota.

Object state loading starts from the request `RGWObjectCtx` cache. `get_obj_state_impl()` stats the raw head object unless `assume_noent` is set, fills existence/mtime/attrs/version/epoch, trims legacy NUL-terminated ETags, decodes compression and manifest data, patches manifests to the current head placement, creates fake tags for old manifest objects without id tags, accounts for AEAD plaintext sizes, decodes pg version/source zone, recognizes OLH attrs, and optionally follows OLH to the target object. Missing objects can inherit mtime/zone/pg information from the tombstone cache.

`set_attrs()` is a metadata-only write but still follows the same consistency pattern: append an atomic compare when possible, write/removes xattrs, add expiration hints, remove replication trace so peers can resync metadata changes, prepare a bucket-index add operation with a new tag, preserve mtime unless explicitly overridden, complete/cancel the index transaction, derive owner/etag/content-type/storage-class from new or existing attrs, compute CloudTiered category/restore fields for the index, and update cached attrs/tag/mtime.

Multipart part preparation is split between `get_part_obj_state()` and the start of `Object::Read::prepare()`. The read path first loads the whole-object state and manifest, records part count from the manifest, copies crypt and ETag attrs when a part is requested, and then redirects state/manifest to the requested part head. `get_part_obj_state()` validates multipart structure, locates the requested part, optionally prefetches the part head, loads that head without OLH following, reuses the part's own manifest if present, or synthesizes a per-part manifest by copying stripes until the next part.

## State and Persistence Behavior

Object identity is persisted in RADOS as head objects, xattrs, optional manifests, bucket-index entries, datalog/bilog entries, and per-object CLS version information. `RGWObjVersionTracker` keeps read/write versions aligned with CLS operations, while `RGWObjectCtx` caches decoded state for request-local consistency and invalidates after mutating operations.

Bucket info is persisted through bucket entrypoint and instance metadata objects. Bucket indexes are RADOS objects manipulated through `svc.bi`, `svc.bi_rados`, and `cls_rgw_*` operations. Object writes/deletes use pending bucket-index operations followed by completion/cancel; timeouts intentionally preserve pending entries so listing repair can reconcile disk state later.

Multisite persistence flows through mdlog, datalog, bilog flags, bucket log layouts, sync traces, and zone trace sets. `add_datalog_entry()` is fatal in regular object-index completion paths, while some cleanup/delete-bucket paths log datalog failures as warnings because the bucket metadata change already succeeded.

Object attrs carry major semantic state: ACL, ETag, content type, manifest, id/tail tags, pg version, source zone, storage class, compression info, encryption info, object-lock retention/legal hold, restore status/type/time/expiry, cloud-tier config, delete-at, replication status/trace/timestamp, append part number, OLH info/version/id tag, and AEAD original/decrypted size hints.

Manifests describe the head/tail layout and are used for multipart objects, large object stripes, zero-copy copy/refcounting, GC chain construction, part reads, compression/encryption accounting, and old-object repair. Tail object lifetime is reference-counted with `cls_refcount_get/put()` or sent to GC through `RGWGC::send_split_chain()`.

The tombstone cache stores recent delete mtime/zone/pg state for missing objects so later sync/conflict logic can compare against deleted objects. It is only allocated when zones are syncing from this zone.

Restore and transition state is duplicated into both object attrs and bucket-index fields. `decode_restore_index_fields()` extracts restore status and expiry, and write/update/reindex paths propagate those fields into index entries so listings can report restore state without reading each head object.

Background state includes thread pointers and locks for meta/data sync workers, `bucket_trim`, `sync_log_trimmer`, notifier objects, lifecycle/restore/GC/reshard processors, caches, async processor, coroutine registry, and D3N data cache. `finalize()` must stop these in dependency order to avoid callbacks into destroyed services.

## Dependencies and Integration Points

This code integrates deeply with librados and neorados (`IoCtx`, `ObjectReadOperation`, `ObjectWriteOperation`, `AioCompletion`, async operate, pool alignment queries, service daemon map), and with RGW CLS classes (`cls_rgw_*`, `cls_refcount_*`, `cls_version_*`) for bucket index, object checks, usage logs, versioning, and tail refcounts.

RGW service dependencies include `svc.zone`, `svc.zone_utils`, `svc.sync_modules`, `svc.async_processor`, `svc.datalog_rados`, `svc.mdlog`, `svc.bi`, `svc.bi_rados`, `svc.cache`, `svc.site`, and control layers such as `ctl.bucket` and `ctl.user`.

Multisite and remote-copy integration uses `RGWRESTConn`, `RGWHTTPManager`, `RGWCoroutinesManager`, `RGWPostRESTResourceCR`, `RGWDataPostNotifyCR`, `RGWStatRemoteBucketCR`, `RGWMetaSyncStatusManager`, `RGWDataSyncStatusManager`, sync counters, sync trace, mdlog/datalog trim coroutines, zone/zonegroup connection maps, and bucket sync policy handlers.

The write/copy data plane uses `rgw::putobj::AtomicObjectProcessor`, `DataProcessorFilter`, optional `rgw::sal::DataProcessorFactory`, `RGWPutObj_Compress`, compressor plugins, ETag verifier filters, `rgw::Aio` throttles, and `RGWGetObj_Filter`/read iteration.

Lifecycle and maintenance integration includes `RGWGC`, `RGWLC`, `rgw::restore::Restore`, `RGWObjectExpirer`, `RGWReshard`, `RGWReshardWait`, bucket logging, notification manager, quota handler, and topic migration.

Security and metadata integration includes ACL owner decoding, `RGWUserPermHandler` fallback source-bucket permission checks, object-lock retention/legal-hold attrs, encryption/decryption helpers, compression helpers, cloud-tier helpers, and owner override through user control lookup.

Operational integration includes debug logging, LTTng tracepoints for write prepare/operate/complete, perf counters for data sync, service map registration/status updates, and formatter/flusher output for encrypted multipart resync progress.

## Risks and Edge Cases

Bucket-index correctness depends on prepare/operate/complete/cancel ordering. The code deliberately leaves pending index entries on `-ETIMEDOUT`; tests and operators must expect later listing repair rather than immediate cleanup. Conversely, canceling after non-timeout write failures must not erase real successful writes.

Reshard races are handled in asynchronous completion by retrying `-ERR_BUSY_RESHARDING` against the current bucket shard. Failures during retry are logged but not recoverable in that thread, so index consistency depends on guard logic and later repair paths.

Object-state cache invalidation is subtle. `RGWObjectCtx::invalidate()` preserves atomic, prefetch, and compressed flags, but stale attr/state data must be cleared after writes/deletes. Mutators that update cached attrs in place, such as `set_attrs()`, must keep `obj_tag`, `attrset`, and `mtime` coherent.

Versioning and OLH flows have many special cases: null version ids, explicit marker version ids, delete markers, suspended versioning, pure OLH objects, current-version preconditions, follow-OLH loops returning `-EAGAIN`, and skip-OLH updates during multi-object delete. Incorrect instance clearing can delete or index the wrong version.

Copy behavior can silently switch between zero-copy and data-copy. Placement changes, pool changes, missing manifests, no-tail manifests, oversized heads, and data processors force data rewrite; otherwise tail refcounts are reused. Rollback only attempts to drop refs for successful async increments, so partial cleanup failures can leave extra refs.

Encryption/compression metadata is high risk. Remote replication avoids ETag verification for encrypted objects, preserves encrypted+compressed compression info, constructs `RGW_ATTR_CRYPT_PARTS` from manifests when needed, drops stale key attrs on copy, and rewrites/removes multipart boundary attrs depending on zero-copy versus data-copy paths. Wrong attr preservation can break decryption, range reads, ETag validation, or quota/listing sizes.

Restore/cloud-tier state appears in object attrs, object category, storage class, delete-at hints, and bucket-index restore fields. Temporary restores suppress sync and retain CloudTiered category/storage-class semantics; permanent restores force logging and make the object regular. Partial metadata updates must fall back to existing attrs or listings will report incorrect restore state.

Bucket deletion in multisite mode does not immediately remove bucket instance info; it marks `BUCKET_DELETED`, advances log layout generation, and writes datalog entries for old shards. Remote emptiness checks are conservative when sync policies are directional, filtered, or zones opt out; failures to list remote buckets are logged but do not always block deletion.

Preconditions compare a mixture of object state, bucket-index dirent metadata, CLS mtime checks, and HTTP ETags with quote stripping. Some paths compare low-precision timestamps unless requested otherwise. Races may be converted into success for unconditional writes but into precondition failures for conditional requests.

`restore_obj_from_cloud()` declares `RGWFetchObjFilter *filter;` and then checks `if (!filter)` before assignment in this chunk. That is suspicious because the pointer is uninitialized locally; if compiled as-is, behavior depends on subsequent optimizer/static-analysis handling and should be reviewed with surrounding code and warnings.

The chunk boundary cuts `Object::Read::prepare()` before the fallback handling for invalid part 1 and the rest of read setup. Any analysis of part reads, ranges, decrypt/decompress filters, or read iteration remains incomplete until the next chunk is merged.

## Test Signals

Initialization tests should cover missing/created pools, raw versus normal service init, sync disabled because the zone need not sync, meta-master notifier startup, data-sync source-zone thread creation, sync-log trimming enabled/disabled, notification and bucket-logging init failures, D3N cache enablement, and clean `finalize()` with each optional subsystem enabled.

Bucket listing tests should exercise ordered and unordered listing with versions, namespaces, empty namespace enforcement, prefixes, delimiters, common prefixes, end markers, access filters, old CLS delimiter fallback, marker forward-progress failure, and very small or negative `max` values.

Bucket creation/deletion tests should cover concurrent create/delete races, object-lock default flags, index initialization cleanup on conflict, bucket index missing during reindex, empty checks across local bucket index entries, multisite remote non-empty detection under directional/filter policies, `BUCKET_DELETED` flag persistence, and datalog generation for deleted layouts.

Object write tests should validate atomic create/overwrite behavior, `If-Match`/`If-None-Match`, size and last-modified preconditions, object-lock default retention, manifest writes, compressed and AEAD accounted sizes, source-zone attrs, restore status/expiry index fields, timeout pending-index behavior, cancellation on RADOS errors, OLH update for versioned writes, delete-at expirer hints, and quota deltas.

Copy tests should include local same-pool zero-copy, different pool/placement data-copy, copy-to-self, first-head-chunk copy, refcount rollback on partial failure, destination remote zonegroup copy, source remote zone/zonegroup fetch, owner override, fallback ACL checks for old peers, ETag verification success/failure, encrypted source, compressed source, encrypted+compressed source, tag preservation/removal, and replication trace/status/timestamp updates.

Swift versioning tests should cover archive-bucket owner mismatch, archive bucket missing, destination S3 versioning interaction, copying out previous versions, restoring the latest archive entry, deleting archive copies after restore, and races returning `-ECANCELED` or `-ENOENT`.

Cloud transition/restore tests should cover invalid restore storage class, S3 Glacier in-progress response, temporary restore expiry/delete-at hints, permanent restore logging, restore attrs and bucket-index fields, storage-class reporting for temporary restored copies, cloud-tier config attrs, preserving transition mtime, and truncated cloud fetch detection.

Delete tests should cover unversioned object delete, forced index cleanup when the head is missing, object expiration-time precondition, unmodified-since checks with high/low precision, versioned delete marker creation, explicit instance unlink, explicit marker version id, suspended null version, multi-object delete with skipped OLH updates, tombstone cache insertion, GC chain submission/fallback inline deletion, and quota decrement.

Object-state tests should load objects with no attrs, legacy NUL ETags, invalid compression attrs, manifests with missing tags requiring fake tag generation, pure OLH objects, null-version OLH heads, tombstone-cache hits, AEAD original/decrypted size attrs, invalid manifest decode, pg/source-zone decode failures, and prefetch-data reads.

Attribute update tests should verify metadata-only mtime preservation, explicit set-mtime override for resync, replication trace removal, restore-category fallback from existing attrs, storage class fallback, ACL/ETag/content-type fallback, delete-at hint addition, null-version existence checks, index cancel on write failure, and cached attr mutation after success.

Multipart part-read tests for this chunk should cover invalid/missing manifests, non-multipart manifests, missing requested part, part iterator pointing at a tail object, part head with its own manifest, synthesized per-part manifest across stripes, part count off-by-one for single-part multipart objects, prefetch transfer from multipart head to part head, and crypt/ETag attr copying into part reads.

Operational signals include debug logs for bucket-index transaction instrumentation (`rgw_bucket_index_transaction_instrumentation`), tracepoints around write prepare/operate/complete, service-map metadata/status updates, formatter output from encrypted multipart resync, datalog/mdlog notify logs, sync wakeup logs by shard/source zone, and errors that leave pending index entries for later bucket listing repair.

## Cross-Chunk Notes

The next chunk must continue from `RGWRados::Object::Read::prepare()` line 7,990. It should complete the read-preparation analysis and connect the read/iterate paths back to the state, manifest, part, compression, encryption, and precondition behavior documented here.

### subset-b-006974: lines 7991-12065

# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_rados.cc lines 7991-12065

## Scope

This chunk covers the middle/tail of `rgw_rados.cc` from the end of `RGWRados::Object::Read::prepare()` through read iteration, bucket-index update transactions, versioned object logical-head (OLH) maintenance, raw object and bucket-index listing helpers, usage log operations, dynamic resharding decisions, quota checks, and asynchronous object deletion helpers. It ends with JSON/test instance helpers for object expiration hints and OLH metadata types.

The code is the RADOS-backed implementation layer under RGW's SAL. It translates object, bucket-index, lifecycle, garbage-collection, usage-log, quota, and resharding operations into librados object operations and CLS RGW calls while preserving object versioning invariants, multipart manifests, bucket-index consistency, multisite bilog/datalog propagation, and cache/read flow control.

## Purpose

The chunk provides several core RGW data-path and metadata-path services:

- Read objects and object ranges from head/tail RADOS objects, including multipart part reads, object manifests, prefetched head data, async read throttling, and D3N data-cache population.
- Maintain bucket index entries through prepare/complete/cancel transaction phases and guard those operations against dynamic bucket resharding.
- Implement OLH bookkeeping for versioned buckets, where a null instance object points to the current object version or delete marker and pending OLH operations are reconciled through bucket-index logs.
- List bucket index entries in ordered and unordered modes across one or many shards, repairing stale index state by comparing entries to disk state.
- Provide raw object stat/list operations, usage-log CLS wrappers, bucket instance metadata getters/setters, bucket statistics readers, GC/LC/expiration wrappers, dynamic reshard scheduling, quota checks, and async delete primitives.

## Important APIs, Types, and Functions

`RGWRados::Object::Read::prepare()` finishes read setup. The covered tail handles `partNumber` requests by redirecting `astate`/`manifest` to a multipart part object, copying only safe encryption attributes, restoring the multipart object's ETag, setting target object/attrs/mtime/size/epoch outputs, and enforcing conditional headers via time weights and ETag comparison.

`RGWRados::Object::Read::range_to_ofs()` normalizes HTTP-style ranges. Negative offsets mean suffix ranges, negative ends mean end-of-object, and out-of-range starts return `-ERANGE`.

`RGWRados::Bucket::UpdateIndex::{guard_reshard,prepare,complete,complete_del,cancel}` implement the bucket-index transaction wrapper used by object mutations. `prepare()` creates or reuses an operation tag and calls `cls_obj_prepare_op()`. `complete()` builds a `rgw_bucket_dir_entry` with size, accounted size, mtime, ETag, content type, storage class, owner, append/restore metadata, and calls `cls_obj_complete_add()`. `complete_del()` and `cancel()` complete delete/cancel phases. Each may add datalog entries when zone configuration requires data logging.

`RGWRados::Object::Read::{read,iterate}` and `RGWRados::iterate_obj()` resolve logical object offsets through `RGWObjManifest`, split reads on manifest stripes and configured max request sizes, use atomic tests on head reads, serve prefetched head data when available, and submit librados reads either synchronously (`read()`) or through the async throttle path (`iterate()`).

`get_obj_data::flush()` merges async read completions in logical offset order, delivers contiguous buffers to `RGWGetDataCB`, and optionally writes eligible buffers to `d3n_data_cache` unless bypassed or too large.

`RGWRados::obj_operate()` overloads are small head-object helpers for `ObjectWriteOperation` and `ObjectReadOperation`.

`RGWRados::olh_*`, `bucket_index_*_olh*`, `apply_olh_log()`, `update_olh()`, `set_olh()`, `unlink_obj_instance()`, `follow_olh()`, and `clear_olh()` implement versioned-object logical-head state. Important persisted attributes are `RGW_ATTR_OLH_ID_TAG`, `RGW_ATTR_OLH_VER`, `RGW_ATTR_OLH_INFO`, `RGW_ATTR_ID_TAG`, and `RGW_ATTR_OLH_PENDING_PREFIX*`.

`RGWRados::guard_reshard()`, `check_reshard_logrecord_status()`, `recover_reshard_logrecord()`, and `block_while_resharding()` retry bucket-index operations across resharding and recover failed/incomplete reshard markers when a lock can be taken.

`RGWRados::raw_obj_stat()`, `pool_iterate_*()`, `list_raw_objects_*()`, and `append_async()` are low-level raw RADOS object helpers for stat/read-first-chunk, pool scans with cursors, prefix-filtered raw object listing, and async append.

`RGWRados::{get_bucket_stats,get_bucket_stats_async,cls_bucket_head_async}` read bucket-index shard headers and aggregate `RGWStorageStats`, bucket/master versions, markers, and sync-stopped state. `RGWGetBucketStatsContext` is the async callback aggregator.

`RGWRados::{get_bucket_instance_info,get_bucket_info,try_refresh_bucket_info,put_bucket_instance_info,put_linked_bucket_info}` bridge to `RGWBucketCtl` for bucket instance and entrypoint metadata.

`RGWRados::{bi_get_instance,bi_get_olh,bi_get,bi_put,bi_list,bi_remove}` expose direct bucket-index entry access through CLS RGW BI operations.

`RGWRados::{gc_operate,gc_aio_operate,list_gc_objs,process_gc,process_lc,process_expired_objects}` delegate to RGW garbage collection, lifecycle, and object expiration processors.

`RGWRados::{cls_obj_prepare_op,cls_obj_complete_op,cls_obj_complete_add,cls_obj_complete_del,cls_obj_complete_cancel}` build the underlying bucket-index CLS operations, add reshard guards, pass bilog flags/zones trace, and use `index_completion_manager` for async completion tracking.

`RGWRados::{cls_bucket_list_ordered,cls_bucket_list_unordered}` implement multi-shard bucket listing. Ordered listing fans out CLS list calls, merges shard results lexicographically, handles duplicate names, and stops when a truncated shard is exhausted. Unordered listing walks shard by shard from a computed marker shard and supports the `RGWBIAdvanceAndRetryError` marker-advance protocol.

`RGWRados::{cls_obj_usage_log_add,cls_obj_usage_log_read,cls_obj_usage_log_trim,cls_obj_usage_log_clear}` are usage-log pool wrappers around CLS usage-log calls. Trim repeats until CLS reports `-ENODATA`.

`RGWRados::remove_objs_from_index()` directly removes OMAP keys from bucket index shard objects without CLS, used by admin repair/unlink paths.

`RGWRados::check_disk_state()` compares a bucket-index entry to the object's actual head state, reconstructs metadata from xattrs and manifest data, removes multipart part index entries, and encodes CLS suggestions to update or remove stale index entries.

`RGWRados::{calculate_preferred_shards,check_bucket_shards,add_bucket_to_reshard,get_target_shard_id}` calculate and enqueue dynamic bucket resharding decisions.

`RGWRados::{delete_tail_obj_aio,delete_obj_aio}` queue asynchronous tail/head object deletion. Tail deletion uses `cls_refcount_put()`, while head deletion can prepare/delete the bucket index for consistency.

`objexp_hint_entry`, `RGWOLHInfo`, and `RGWOLHPendingInfo` provide formatter dumps and generated test instances for encoding/test infrastructure.

## Control Flow

Object read setup enters with object state and manifest loaded by the source object. For part reads, the code obtains part state from `get_part_obj_state()` in the previous lines, treats `partNumber=1` on non-multipart objects as a whole-object read, copies cryptographic attrs except object-level multipart encryption attrs, and then remaps `state.obj`, `state.head_obj`, current pool, and ioctx to the selected object. Conditional request handling happens after state selection so ETag and mtime checks apply to the effective read target.

`Read::read()` performs a single bounded read. It clamps `end` to object size, resolves the requested logical offset to either the head object or a manifest tail stripe, caps length by pool max chunk size, adds an atomic state test when reading from the head, drains prefetched head data first, opens or reuses the proper pool ioctx, sets the object locator, and issues a RADOS read. If part of the range was satisfied from prefetched data, it appends the later RADOS buffer before returning the total bytes.

`Read::iterate()` streams larger ranges. `iterate_obj()` walks manifest stripes or the head object in `rgw_get_obj_max_req_size` chunks and calls `_get_obj_iterate_cb()`. The callback applies head-object atomic checks and prefetch handling, submits async librados reads through an `rgw::Aio` throttle, and calls `get_obj_data::flush()` so out-of-order completions are buffered until contiguous data can be delivered to the client callback. On error, `iterate()` cancels the data path and drains completions without sending data.

Bucket-index updates use a two-phase prepare/complete model. Mutation code calls `UpdateIndex::prepare()` unless the operation is blind. That records an operation tag in the bucket index. Later, success calls `complete()`/`complete_del()` and failure calls `cancel()`. All three write CLS bucket-index operations against a `BucketShard`; reshard races return `-ERR_BUSY_RESHARDING` or `-ENOENT`, which `guard_reshard()` handles by blocking for reshard completion, refreshing shard state, and retrying up to a fixed bound.

Reshard blocking reads the bucket resharding marker with `get_reshard_status()`. If the bucket index object disappeared or reports no active reshard, bucket info and shard generation are refreshed. If resharding persists, the code attempts recovery by taking `RGWBucketReshardLock`; success means no active resharder owns the lock, so it refreshes bucket metadata and clears reshard flags. Otherwise it waits through `reshard_wait`. Repeated busy status returns `-ERR_BUSY_RESHARDING`.

OLH updates start by turning the null instance into an OLH object if needed. `olh_init_modification_impl()` creates/asserts the OLH object, installs object and OLH tags, creates an `RGWOLHPendingInfo` xattr whose name begins with a time-sortable prefix, and writes it with tag guards. `set_olh()` then links a target version/delete marker in the bucket index. `unlink_obj_instance()` similarly records an unlink in the bucket index. Both paths retry `-ECANCELED`, cancel pending xattrs on failure, may repair tag mismatches from BI state, and finally call `update_olh()` unless explicitly skipped.

`update_olh()` loops over `bucket_index_read_olh_log()` pages and applies them with `apply_olh_log()`. `apply_olh_log()` interprets link, unlink, remove-instance, and stale records by epoch, removes pending xattrs, selects the correct target or delete marker, deletes obsolete object instances, updates `RGW_ATTR_OLH_INFO` and `RGW_ATTR_OLH_VER`, then either clears the OLH object or trims the OLH log. `follow_olh()` removes timed-out pending entries, forces an update when live pending entries exist, decodes `RGW_ATTR_OLH_INFO`, returns `-ENOENT` for delete markers, and otherwise returns the target instance.

Bucket listing opens all relevant bucket-index shard objects. Ordered listing issues list operations to all selected shards, wraps each shard result in a `ShardTracker`, merges the smallest next key from a multimap, repairs entries with pending/nonexistent/forced-check state via `check_disk_state()`, records suggested index updates per shard, and sets truncation/last-entry markers according to shard exhaustion. Unordered listing computes a starting shard from the marker and bucket hash, lists one shard at a time, handles marker-only retry responses, applies the same disk-state repair, and advances across shards until enough entries are returned.

`check_disk_state()` resolves the listed key to an object, fetches current state without following OLH, suggests removal if the object no longer exists, otherwise reconstructs index metadata from object size/accounted size, mtime, ETag, content type, storage class, ACL owner, append state, pool id, epoch, and object tag. For multipart manifests, it deletes stale multipart part index entries. It then encodes a CLS suggestion update to be submitted asynchronously by listing callers.

Dynamic resharding flow begins after stats indicate object counts. `check_bucket_shards()` exits if disabled or layout is not reshardable, calls `calculate_preferred_shards()` with stricter per-shard thresholds for versioned buckets, rejects reductions unless configured, and enqueues a `cls_rgw_reshard_entry` through `RGWReshard::add()`.

## State and Persistence Behavior

Object read state is held in `RGWObjState`, `RGWObjManifest`, per-read `state.obj/head_obj/cur_pool/cur_ioctx/io_ctxs`, and optional output fields in read params. Reads do not mutate persistent object data, but head reads include atomic tests against object state to avoid racing with concurrent modifications. Prefetched head data and D3N data-cache writes are in-memory/cache side effects.

Bucket-index mutation state is persisted in bucket index shard objects through CLS RGW operations. Operation tags (`optag`) link prepare and complete/cancel phases. `rgw_bucket_dir_entry` metadata becomes the persistent listing/stat source. Datalog and bilog emission depend on zone logging state, `log_op`, bilog flags, and zones trace.

OLH state is persisted partly on the null-instance object and partly in bucket index logs. The OLH object stores ID tags, version counters, current target/delete marker info, and pending operation xattrs. Bucket index OLH operations store link/unlink/remove records and are later trimmed. The code protects these writes with xattr comparisons on OLH tags and versions to prevent concurrent writers from clobbering each other.

Pending OLH entries use encoded `RGWOLHPendingInfo.time` and sorted xattr names. `check_pending_olh_entries()` removes only timed-out leading entries, relying on time-ordered names to stop at the first non-expired entry. `remove_olh_pending_entries()` trims at most 1000 xattrs per RADOS operation under an OLH tag guard.

Bucket metadata persistence is delegated to `RGWBucketCtl`: bucket instance info, bucket entrypoint info, object version trackers, attrs, mtimes, and linked entrypoint creation are stored there. `try_refresh_bucket_info()` uses the read version as a refresh guard.

Bucket listing repair is advisory. `check_disk_state()` encodes update/remove suggestions into a bufferlist, and list callers submit `cls_rgw_suggest_changes()` asynchronously without waiting for success. This means listing can return corrected results while persistent index cleanup may lag.

Raw object listing state is represented by `RGWPoolIterCtx` and librados object cursors. Cursor strings come from `NObjectIterator::get_cursor()` and can be reused by callers to resume pool scans.

Dynamic reshard decisions persist as reshard queue entries rather than changing layouts inline. The code caps desired shard count by `get_max_bucket_shards()` and records tenant, bucket name/id, old/new shard counts, timestamp, and dynamic initiator.

Async deletes persist via queued librados AIO operations. `delete_obj_aio()` may also prepare and remove bucket-index state before/around the head object removal when `keep_index_consistent` is true, but completion waiting is left to the caller through the returned completion handles.

## Dependencies and Integration Points

The chunk depends on librados `IoCtx`, `ObjectReadOperation`, `ObjectWriteOperation`, `AioCompletion`, `NObjectIterator`, object cursors, and object versions. Most persistent metadata operations go through CLS RGW helpers such as `cls_rgw_bucket_prepare_op`, `cls_rgw_bucket_complete_op`, `cls_rgw_bucket_link_olh`, `cls_rgw_bucket_unlink_instance`, `cls_rgw_get_olh_log`, `cls_rgw_trim_olh_log`, `cls_rgw_clear_olh`, `cls_rgw_bi_get/list/put`, `cls_rgw_usage_log_*`, `cls_rgw_guard_bucket_resharding`, and `cls_rgw_suggest_changes`.

RGW service dependencies include `svc.zone` for zone identity, logging decisions, and zone params; `svc.bi_rados` for bucket-index opening, shard hashing, list calls, and header reads; `svc.datalog_rados` for datalog updates; `ctl.bucket` for bucket metadata; `quota_handler`; `gc`; `obj_expirer`; `reshard_wait`; `index_completion_manager`; and optional `d3n_data_cache`.

Object model dependencies include `rgw_obj`, `rgw_raw_obj`, `rgw_bucket`, `RGWBucketInfo`, `RGWObjectCtx`, `RGWObjState`, `RGWObjStateManifest`, `RGWObjManifest`, `RGWOLHInfo`, `RGWOLHPendingInfo`, `rgw_bucket_dir_entry`, `rgw_bucket_olh_entry`, `rgw_cls_list_ret`, `rgw_cls_bi_entry`, `rgw_usage_log_info`, and `RGWStorageStats`.

Multisite integration is present through bilog flags, `rgw_zone_set` zones trace, data logging decisions, and comments around OLH repair for cross-zone attribute overwrite bugs. Listing and bucket-index mutation paths insert the local zone and bucket key into zones trace before CLS operations that may be logged.

Configuration controls behavior throughout the chunk: read chunk/window sizes, max chunk size, D3N cache request limits, dynamic resharding limits and reduction allowance, OLH pending timeout, reshard progress judge interval/jitter, and debug injection flags for OLH cancellation, set-OLH errors, and BI unlink latency.

## Risks and Edge Cases

Part reads deliberately skip object-level encryption attrs while copying the source object's ETag. Incorrect attr filtering could produce invalid content lengths, wrong decryption context, or client-visible ETag mismatches for multipart part reads.

Read paths rely on manifest offset math and max chunk caps. A bad manifest, incorrect `obj_find()`/`obj_find_part()` position, or unchecked zero-length/end handling can return the wrong stripe or loop incorrectly. Async iteration must preserve ordering through `get_obj_data::flush()` despite out-of-order completions.

D3N cache writes happen while flushing read completions and are gated by a coarse lock plus request size checks. Cache key choice uses the completed raw object oid, so callers should verify that striped/multipart reads do not unintentionally cache ambiguous data.

Bucket-index transaction correctness depends on pairing prepare tags with later complete/cancel. Failures after data writes but before index complete can leave pending index entries that listing later repairs through `check_disk_state()`. Blind operations skip this protection.

Reshard handling has multiple retry limits and recovery branches. Returning `-ENOENT` from a bucket shard operation is treated as probable resharding, but persistent missing shard objects or unrelated corruption can follow the same path. Lock-based recovery clears reshard flags only after refreshing bucket info, but a wrong lock/error interpretation could prematurely clear active reshard state.

OLH handling is concurrency-sensitive. It uses xattr compare guards, pending xattrs, index logs, retries, and repair logic to handle racing writers and multisite inconsistencies. Bugs can expose the wrong current version, fail to remove a delete marker, leak pending attrs, or delete a valid version during `apply_olh_log()` removal processing.

`apply_olh_log()` chooses among same-epoch links by instance ordering and unlink-before-link state. This is subtle for multisite replay and concurrent version operations; test coverage should include epoch collisions, remote-zone relinks, delete markers, and skipped OLH object updates.

Listing repair is best-effort and asynchronous. A client can receive corrected entries while the underlying bucket index remains stale if the suggested update is lost. Ordered listing also stops early when a truncated shard is exhausted, so callers must tolerate fewer than requested entries with truncation.

Unordered listing has explicit protection against `RGWBIAdvanceAndRetryError` without marker progress. This guards infinite loops, but returning `-EIO` from a malformed CLS response can surface as a user-visible list failure.

`parse_index_hash_source()` assumes incomplete multipart raw names contain at least two periods. Malformed multipart markers return `-EINVAL`; shard selection for unordered listing then fails.

`remove_objs_from_index()` bypasses CLS invariants and removes OMAP keys directly. It is appropriate for admin repair paths but risks removing live entries if the input key list or shard hash calculation is wrong.

`check_disk_state()` repairs based on current object state without following OLH. In versioned buckets or races with concurrent mutation, suggested updates/removals must not overwrite newer correct index state. The code uses index version/pool/epoch and CLS suggestions, but race behavior remains a key test area.

Dynamic reshard calculations reduce max objects per shard for versioned buckets and may enqueue reductions only when configured. Bad stats or object count estimates can over-reshard, under-reshard, or enqueue repeated no-op reshard requests.

Async delete functions push completion handles to callers, so resource cleanup and completion waiting are external. Error paths release newly created completions, but callers must release/wait handles they receive.

## Test Signals

Read tests should cover suffix ranges, empty objects, out-of-range offsets, object size clamping, prefetched head data, manifest tail stripes, pool changes between stripes, multipart part reads, part one on non-multipart objects, encryption attr filtering, ETag conditionals, and async iterate ordering under out-of-order completions.

Bucket-index transaction tests should cover prepare/complete/cancel for add/delete, generated versus supplied write tags, datalog emission, bilog flags/zones trace, blind mode, missing bucket shard, `-ENOENT` retry, busy reshard blocking, and incomplete prepare cleanup visible through listing.

Reshard tests should cover active reshard wait, reshard marker disappearance, successful refresh of new bucket info/shard generation, lock acquisition failure updating judge time, lock acquisition success clearing stale flags, retry exhaustion, and `InLogrecord` progress recovery.

OLH tests should cover initializing a nonexistent OLH, converting a regular null version to OLH, concurrent `-ECANCELED` retries, pending xattr timeout/removal, link/unlink log application, delete markers, same-epoch collisions, stale ops, multisite tag repair from BI, skipped OLH object update paths, and failure injection knobs.

Listing tests should cover ordered multi-shard merge, duplicate names across shards, delimiter/prefix filtering, force-check filters, truncated shard early stop, last-entry marker setting, unordered start marker shard calculation, multipart marker shard calculation, marker advance-and-retry progress, and asynchronous suggestion generation.

Disk-state repair tests should cover nonexistent objects, stale existing index entries, ACL owner decode failure, appendable detection, storage-class/content-type/ETag propagation, multipart manifest part index deletion, pool-id lookup failure, object tag propagation, and suggested remove/update buffers.

Bucket stats tests should cover single-shard and multi-shard headers, bucket/master version manager strings, max marker aggregation, syncstopped propagation, async callback aggregation, error return before and after some AIO submissions, and callback suppression with `unset_cb()`.

Raw object and BI tests should cover pool cursor parsing errors, iterator exceptions, prefix filtering, `-ENOENT` list behavior, BI get decode errors, multipart `bi_put()` hash source override, BI list `reshardlog` mode, and `bi_remove()` idempotence on missing objects.

Usage-log tests should cover add/read/truncate/clear, read truncation markers, trim repeating until `-ENODATA`, and raw usage-log pool reference failures.

Dynamic reshard tests should cover disabled resharding, unreshardable layouts, versioned threshold adjustment, min/max shard caps, no-reduction policy, allowed reduction, exact same shard count rejection, and queue entry contents.

Async deletion tests should cover tail refcount puts, head object removes, index-consistent delete prepare failure, AIO submit failure completion release, successful handle collection, and index deletion failure after AIO submission.
