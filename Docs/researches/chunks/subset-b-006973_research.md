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
