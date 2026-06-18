# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_sal_rados.cc

## Purpose

This file implements the Ceph RGW Storage Abstraction Layer (SAL) backend for RADOS. It adapts high-level RGW concepts such as stores, users, buckets, objects, multipart uploads, lifecycle queues, restore queues, notifications, Lua scripts, roles, accounts, groups, OIDC providers, zones, and zonegroups onto RADOS objects, omap keys, xattrs, bucket indexes, cls operations, metadata logs, and service-layer helpers.

The file is intentionally broad: it is the concrete RADOS implementation behind many `rgw::sal` virtual interfaces declared in `rgw_sal_rados.h` and related SAL headers. Most functions are thin forwarding wrappers around `RGWRados`, `RGWBucketCtl`, `RGWUserCtl`, `RGWSI_*` services, and `rgwrados::*` helper namespaces, but several areas contain significant orchestration logic: bucket creation/removal, bucket logging commits, object cloud-tier restore/transition, multipart completion/abort, multipart locking/renewal, restore FIFO management, and Lua watch/notify handling.

## Important APIs, Types, and Functions

- `RadosStore` is the root store implementation. It creates SAL users, buckets, objects, lifecycle/restore managers, notification objects, writers, Lua managers, and roles; exposes cluster/zone/metadata/usage APIs; and bridges account, group, topic, OIDC, role, quota, rate-limit, sync-policy, and raw-object calls to RADOS-backed services.
- `RadosUser` wraps user metadata and attributes. It loads/stores/removes user info through `ctl()->user`, reads and trims usage through `RGWRados`, verifies MFA through `svc()->cls->mfa`, and lists groups by reading group metadata objects.
- `RadosBucket` implements bucket metadata, listing, deletion, ACL, quota, stats, lifecycle cleanup, multipart enumeration/abort, pubsub bucket topics, and bucket logging object naming/write/commit/remove behavior.
- `RadosObject` implements object state loading, attribute reads/modification/removal, RADOS raw object translation, object deletion/copy, Swift versioning helpers, cloud-tier transition and restore, expiry handling, layout dumping, and read/delete operation wrappers.
- `RadosMultipartUpload` owns multipart metadata operations: upload initialization, part listing from omap, completion into a final manifest, abort cleanup, orphaned part cleanup, and writer creation.
- `MPRadosSerializer`, `LCRadosSerializer`, and `RadosRestoreSerializer` use RADOS object locks to serialize multipart, lifecycle, and restore operations. `MPRadosSerializer` also starts an async lock-renewal coroutine.
- `RadosLifecycle` maps lifecycle work-list operations to `cls_rgw_lc_*` object class calls in the lifecycle pool.
- `RadosRestore` maps restore work queues to `neorados::cls::fifo::FIFO` objects in the restore pool.
- `RadosNotification` delegates reserve/commit to `rgw::notify`.
- `RadosAtomicWriter`, `RadosAppendWriter`, and `RadosMultipartWriter` are SAL writer shims around lower-level processor objects.
- `RadosZoneGroup` and `RadosZone` expose zone/placement metadata from `RGWZoneGroup`, `RGWZone`, and zone services.
- `RadosLuaManager` stores Lua scripts in the zone log pool, package allowlist entries in omap, and uses RADOS watch/notify to invalidate script bytecode or reload packages.
- `RadosRole` stores, loads, and deletes IAM role metadata through `rgwrados::role`.
- `newRadosStore()` is the `extern "C"` factory. It creates a `neorados` handle, allocates `RadosStore`, allocates `RGWRados`, wires them together, and returns the SAL store pointer.

Important helpers include `drain_aio()` for collecting async delete completions, `get_owner_buckets_obj()` for selecting `{user}.buckets` versus `{account}.buckets`, `write_mdlog_entry()` for account/group metadata log records, `to_temp_object_name()` for bucket logging shadow object names, and `get_logging_temp_object_pool()` for selecting the correct temporary logging data pool when the target pool is erasure-coded.

## Control Flow

Store-level calls are mostly adapter flow: validate or construct SAL objects, fetch the RADOS handle or zone params, and delegate to `RGWRados`, `ctl()`, `svc()`, or `rgwrados::*`. Examples include user lookup by access key/email/swift ID, account/group/topic/OIDC/role CRUD, raw object deletion, usage logging, metadata listing, and admin REST resource registration.

Bucket creation calls `RGWRados::create_bucket()`, treats `-EEXIST` as a possible race, verifies owner/index layout compatibility, links the bucket to the owner, and then checks whether a concurrent delete removed the entrypoint. On link failure for a newly-created bucket, it attempts to unlink to avoid partial owner state.

Bucket removal first refreshes bucket info, lists all versions, optionally rejects non-empty buckets, deletes children through `rgw_remove_object()`, aborts multiparts for local buckets, removes lifecycle config, removes pubsub topic mappings, syncs owner stats, deletes the bucket instance, removes notification definitions, cleans bucket logging state, and unlinks owner bucket metadata. `remove_bypass_gc()` is a more direct destructive path that walks manifests and deletes tail/head objects with bounded async RADOS operations before removing the bucket.

Bucket listing builds an `RGWRados::Bucket::List` operation, copies SAL list parameters into low-level list params, calls `list_objects()`, and propagates the returned marker back into both results and params for pagination.

Bucket logging has two data paths. `write_logging_object()` appends records to a temporary shadow object, optionally with asynchronous completion. `commit_logging_object()` either queues an async commit target entry or reads the temp object, handles erasure-coded temp-pool copying, builds a manifest for the final log object, writes object metadata with owner/etag/attrs, updates the "last committed" xattr on the object-name holder, and returns the committed object name to the caller.

Object reads are wrapped by `RadosObject::RadosReadOp`: `prepare()` maps SAL conditional/read parameters onto `RGWRados::Object::Read`, updates the SAL object instance, size, mtime, attrs, and parts count, then `read()`, `iterate()`, and `get_attr()` forward to the parent operation. Deletes are similarly wrapped by `RadosDeleteOp`, which copies SAL delete params to `RGWRados::Object::Delete` and returns delete marker/version results.

Cloud tier restore and transition build an `S3RESTConn` from tier config, derive a target bucket name using zonegroup, storage class, bucket tenant/name, and owner, construct `RGWLCCloudTierCtx`, and call cloud-tier transfer/restore helpers. On restore failure, the code attempts to reset the head object to a cloud-tiered state. Temporary restored object expiry rewrites the head metadata back to cloud-tiered state and sends restore-expired notifications; non-temporary expiry performs a regular delete.

Multipart completion lists uploaded parts in chunks, validates part count/order/etag/minimum size, appends each part manifest into a final manifest, updates compression and AEAD encryption metadata, records old part index keys for removal, cleans past part history, calculates the multipart etag, applies retention/legal-hold attrs, and writes final object metadata with `completeMultipart` and tail modification enabled. Abort repeatedly reads the metadata object's version tracker, lists and cleans parts, sends GC chains or deletes inline, then deletes the metadata object with version checking, retrying on `-ECANCELED`.

Multipart locking uses a RADOS cls lock on the object. `try_lock()` asserts object existence, takes an exclusive lock, starts a coroutine that renews the lock at half the duration, and optionally injects test delays/errors from config. `unlock()` cancels renewal and performs the unlock operation. Loss of renewal clears the serializer's locked state and logs that a racing request may corrupt the upload if it completes.

Lifecycle operations are direct `cls_rgw_lc_*` object-class calls against the lifecycle pool, with explicit encode/decode from cls structs to SAL `LCEntry`/`LCHead`. Restore operations initialize FIFO objects, push encoded restore entries, list FIFO entries into `RestoreEntry` objects, and trim by marker using blocked neorados FIFO calls.

Lua script access reads/writes encoded script strings from the zone log pool. If a background Lua processor exists, reads prefer cached bytecode and register watches on scripts. Script updates and package reloads use RADOS notify, decode ack payloads, and treat notify timeouts as `-EAGAIN`. Watcher errors attempt to unwatch and re-watch.

## State and Persistence Behavior

Persistent bucket state lives in bucket entrypoints, bucket instance metadata, bucket indexes, owner bucket-list objects, lifecycle config attrs, pubsub notification attrs/objects, topic bucket-mapping omap entries, bucket logging name objects, temporary logging shadow objects, and final log objects. Version trackers are used on entrypoints, user metadata, bucket topics, multipart metadata, account/group metadata, and roles to guard conditional updates.

Persistent object state lives in RADOS head objects, manifests, tail objects, attrs such as ACL, etag, compression, checksums, restore status/type/time/expiry, delete-at, storage class, transition/internal mtime, cloud-tier storage class, encryption original size, and multipart part numbers. Object mutations often set atomic state before writing attrs or metadata so racing writes fail instead of silently overwriting.

Multipart state is stored as metadata objects in `RGW_OBJ_NS_MULTIPART`, with upload information in the head data and part records in omap. Part data manifests may have current and historical prefixes; abort and complete paths clean both and remove index entries. GC chains are submitted to RGW garbage collection when available and are deleted inline when GC is disabled.

Bucket logging persists temporary appends in shadow objects named from bucket id and target object name. The code stores `RGW_ATTR_COMMITTED_LOGGING_OBJ` and `RGW_ATTR_LOGGING_EC_POOL` xattrs on the logging name object to remember the last committed target and whether temp writes must avoid an erasure-coded data pool.

Account, group, topic, OIDC provider, role, and some bucket metadata updates also write metadata-log entries through `RGWSI_MDLog` or `rgwrados::*` helpers so multisite metadata sync can observe changes.

Lifecycle queues persist in RADOS lifecycle pool objects through cls rgw lifecycle methods. Restore queues persist in restore pool FIFO objects using neorados. Lua packages persist as omap keys under `lua_package_allowlist`, while scripts persist as encoded system objects in the log pool and use watch maps (`script_watches`, `reverse_script_watches`) for in-memory handle tracking.

## Dependencies and Integration Points

The file depends on core Ceph/RGW infrastructure: `RGWRados`, librados/neorados, `RGWObjectCtx`, `RGWObjManifest`, bucket index and bilog services, system object services, metadata log services, zone and zonegroup services, quota/config-key services, cls rgw client operations, lifecycle object classes, FIFO classes, RADOS lock classes, RGW REST/admin managers, pubsub/notification helpers, cloud-tier lifecycle helpers, crypt/checksum helpers, and Lua package support.

It integrates upward with SAL interfaces consumed by RGW REST/auth/data paths. It integrates sideways with specialized helpers under `rgwrados::{account,buckets,group,groups,oidc,role,roles,topic,topics,users}`. It integrates downward with raw RADOS object operations, omap operations, xattrs, aio completion callbacks, object-class operations, RADOS watch/notify, and RADOS service-map registration.

Multisite integration appears in metadata-log writes, bilog sync-completion checks, topic metadata, zone/period lookups, zone unique ids/transaction ids, sync policy handlers, data sync managers, owner stats objects, and code paths that deliberately avoid syncing local-only bucket logging EC-pool state.

## Risks and Edge Cases

- Bucket create/delete races are explicitly handled, but the path spans bucket instance metadata, entrypoints, owner links, and stats. Partial failure can leave inconsistent owner links or stale entrypoints if cleanup also fails.
- Bucket removal is large and best-effort in some cleanup steps. Notification cleanup, lifecycle config removal, bucket logging cleanup, and stats sync failures may be logged without aborting all deletion work.
- `remove_bypass_gc()` directly deletes manifests and head objects with async operations. Incorrect concurrency limits, manifest interpretation, or `keep_index_consistent` choices can leave orphaned tails or stale index entries.
- Multipart completion is sensitive to part ordering, sorted versus unsorted omap compatibility, compression metadata consistency, AEAD plaintext-size accounting, and cleanup of historical part prefixes. Mistakes can produce corrupt manifests, invalid etags, or undeletable part remnants.
- Multipart abort retries metadata deletion on cls-version mismatch, but the cleanup chain is rebuilt across attempts. Races with part upload/complete paths need lock coverage and version checks to remain correct.
- Lock renewal failure in `MPRadosSerializer` clears locked state but cannot undo a request already continuing after lock loss. Tests should exercise injected renewal errors and delays because the log message warns of possible overwrite/corruption.
- Cloud-tier restore failure attempts to reset the object to cloud-tiered metadata. Any failure in that recovery path can leave restore attrs, manifest state, or bucket index state ambiguous.
- Temporary restore expiry rewrites manifests and attrs manually. Decode exceptions are partly swallowed, and object versions with `"null"` instance handling are subtle.
- Bucket logging commit has several cross-pool cases, especially erasure-coded target pools. The temp object name must match manifest generation or commit returns `-EINVAL`; async commit queuing has different durability semantics than immediate commit.
- Lua watch/notify maps are in-memory and must stay consistent with RADOS watch handles. Watcher error handlers restart watches, but repeated failures or missing pools are mostly logged and surfaced as errors only on some paths.
- Many functions return raw negative errno values, while some translate to S3/RGW errors such as `-ERR_BUCKET_EXISTS`, `-ERR_NO_SUCH_UPLOAD`, `-ERR_INVALID_PART`, and `-ERR_TOO_SMALL`. Callers must know which layer's error contract they are receiving.
- Several operations call `maybe_warn_about_blocking()` and use blocked completions even in async-capable flows. This is acceptable in existing RGW patterns but is a scalability signal for restore/lifecycle FIFO paths.

## Test Signals

Useful test coverage should include bucket create races with concurrent delete/recreate, owner link failures, incompatible index layouts on existing buckets, account-owned versus user-owned bucket stats/usage paths, and bucket deletion with notifications, lifecycle attrs, multiparts, logging configuration, and owner stats failures.

Multipart tests should cover sorted v2 omap listing, fallback to unsorted listing, invalid/missing parts, small non-final parts, etag mismatch, compressed and mixed-compression parts, AEAD encrypted multipart metadata, abort retries on `-ECANCELED`, GC-disabled inline cleanup, historical part prefix cleanup, and lock renewal injection via `rgw_mp_lock_inject_renewal_error` and `rgw_mp_lock_inject_delay`.

Object tests should cover read conditional propagation, attr modification with `FLAG_LOG_OP`, versioned null-instance expiry, restore temporary expiry notification, cloud-tier transition/restore rollback, object copy with attrs and delete-at, Swift versioning restore/copy, torrent fallback from omap, and layout dumping for multi-stripe manifests.

Bucket logging tests should cover appending with sync and async completions, commit of empty and non-empty temp objects, erasure-coded target-pool temp relocation, xattr recording of last committed object, async commit list insertion, object-name races (`-EEXIST`, `-ECANCELED`), and deletion of temp objects.

Metadata integration tests should exercise account/group/topic/OIDC/role CRUD plus metadata-log emission, topic bucket mapping add/remove/list loops, persistent topic add/remove, Lua script put/get/delete/watch invalidation, Lua package allowlist add/remove/list/reload notify timeout handling, lifecycle cls entry/head operations, restore FIFO initialize/push/list/trim, and zone/zonegroup placement lookups.
