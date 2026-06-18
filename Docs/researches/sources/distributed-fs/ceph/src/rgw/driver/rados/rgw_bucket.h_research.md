# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_bucket.h

## Purpose
`rgw_bucket.h` declares the RADOS RGW bucket control/admin interface. It describes bucket metadata objects, user bucket lists, admin operation state, admin operation entry points, and `RGWBucketCtl`, the service-facing controller that reads/writes bucket entrypoint and instance metadata and keeps owner bucket directories and sync policy queries consistent.

## Important APIs, Types, and Functions
`RGWBucketCompleteInfo` packages `RGWBucketInfo` with raw metadata attrs for full bucket-instance metadata sync. `RGWBucketEntryMetadataObject` and `RGWBucketInstanceMetadataObject` adapt bucket entrypoint and instance state to `RGWMetadataObject`. `RGWUserBuckets` is an encodable map of bucket name to `RGWBucketEnt` with `owns()`, `add()`, `remove()`, and `count()`.

`RGWBucketAdminOpState` is the mutable parameter block for admin operations. It stores user/account identity, display name, bucket/object names, markers, flags for stats/index/delete/sync/dump behavior, concurrency and age thresholds, bucket pointer, quota, and rate-limit info. `RGWBucket` is the instance wrapper used by admin code, with methods for initialization, bucket index checks, ownership changes, quota updates, object removal, policy lookup, and sync toggling. `RGWBucketAdminOp` exposes static command-level APIs over a `rgw::sal::Driver`.

`RGWBucketCtl` declares entrypoint and instance `GetParams`, `PutParams`, and `RemoveParams`, plus operations for reading/storing/removing entrypoints and instances, resolving bucket info through entrypoint if needed, setting attrs, linking/unlinking buckets to owners, reading stats, syncing owner stats, and obtaining bucket sync policy handlers.

## Control Flow
Callers configure `RGWBucketAdminOpState`, then invoke `RGWBucketAdminOp` statics. Those statics construct `RGWBucket`, call `init()`, and delegate to instance methods or SAL calls. Lower-level services use `RGWBucketCtl` directly: callers pass a `rgw_bucket`, optional version/mtime/attrs/cache parameters, and the controller converts that into service metadata keys with `RGWSI_Bucket::get_entrypoint_meta_key()` or `get_bi_meta_key()`.

The controller separates three concepts: entrypoint metadata for name-to-instance resolution, bucket instance metadata for the authoritative bucket record, and owner bucket directory membership. This split is visible in APIs such as `read_bucket_info()`, where a bucket without `bucket_id` first reads the entrypoint before loading the instance.

## State and Persistence Behavior
The header makes object-version tracking explicit. Entrypoint and instance get/put/remove params can carry `RGWObjVersionTracker`, `mtime`, attrs, cache refresh versions, and exclusivity flags. Instance `PutParams::orig_info` distinguishes three states: original not fetched, original absent/new bucket, or original info available. That matters to overwrite hooks, metadata sync, and index/log side effects in the implementation.

`RGWBucketAdminOpState` owns an optional cloned SAL bucket once initialized, so subsequent operations can mutate or inspect a stable bucket object. `RGWBucketCtl::link_bucket()` and `unlink_bucket()` take a librados handle and an `rgw_owner` variant, making owner-directory persistence work for both users and accounts. `bucket_exports_data()` and `bucket_imports_data()` surface sync-policy persistence through `RGWBucketSyncPolicyHandler`.

## Dependencies and Integration Points
The declarations depend on RGW common bucket types, SAL driver/user/bucket/object abstractions, metadata handlers, formatter support, librados forward declarations, zone/bucket/user services, bucket sync services, and bucket index services. Factory functions create normal and archive metadata handlers for metadata sync. Global helpers `rgw_remove_object()`, `rgw_object_get_attr()`, `check_bad_owner_bucket_mapping()`, and `rgw_find_bucket_by_id()` are used by admin and repair code outside this translation unit.

## Risks
The API exposes many optional pointer parameters, so null handling and lifetime of out-params are important. `RGWBucketAdminOpState` mixes user, account, bucket, object, and operation flags; invalid combinations must be rejected by implementation. `RGWBucketCtl` methods are compiled under RADOS guards in the implementation, so callers must account for non-RADOS stores where some admin operations are unsupported. Version tracker propagation is subtle: passing the wrong tracker can cause stale-write failures or missed optimistic concurrency checks.

## Test Signals
Compile-time coverage should verify all declared admin methods match command dispatch and SAL/RADOS implementations. Behavioral tests should cover entrypoint-only bucket lookup, direct instance lookup, object version conflict paths, exclusive creates, owner link/unlink for users and accounts, legacy bucket conversion through `set_bucket_instance_attrs()`, sync policy imports/exports queries, and metadata-handler factories in normal and archive zones.
