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
