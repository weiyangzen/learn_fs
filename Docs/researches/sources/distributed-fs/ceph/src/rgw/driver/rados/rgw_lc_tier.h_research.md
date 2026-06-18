# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_lc_tier.h

## Purpose
Declares the lifecycle cloud-tier interface used by RGW lifecycle code to transfer objects to remote cloud storage and retrieve or restore them later. It also defines the context object that bundles local source object state, target endpoint configuration, tier policy, ACL mapping, multipart thresholds, and coroutine yield context.

## Important APIs And Types
`RGWLCCloudTierCtx` is the central API carrier. It includes source fields (`rgw_bucket_dir_entry& o`, `rgw::sal::Driver*`, `RGWBucketInfo&`, source `rgw::sal::Object*`, storage/restore classes, tier type), remote fields (`RGWRESTConn&`, location constraint, target bucket, target storage class), ACL mappings, multipart min/threshold sizes, flags for multipart, target bucket creation, per-bucket target naming, and `optional_yield`.

The header exports `rgw_cloud_tier_transfer_object()`, `rgw_cloud_tier_get_object()`, `rgw_cloud_tier_restore_object()`, `cloud_tier_restore()`, and `is_restore_in_progress()`. It also defines default and lower-bound multipart sizes: `DEFAULT_MULTIPART_SYNC_PART_SIZE` and `MULTIPART_MIN_POSSIBLE_PART_SIZE`.

## Control Flow And Integration
Callers populate `RGWLCCloudTierCtx` from lifecycle policy/tier configuration and call transfer or restore/get functions. The implementation uses `target_by_bucket` to choose between legacy `bucket/object` remote keys and per-bucket object-only keys, and mutates flags such as `is_multipart_upload` and `target_bucket_created` as transfer progresses.

## State And Persistence
The header itself persists no data but exposes fields that drive persisted state: remote object metadata, local multipart status objects, target bucket cache membership, and restore-in-progress handling. References in the context must remain valid for the duration of synchronous/coroutine work because most members are raw pointers or references.

## Dependencies And Risks
The interface is tightly coupled to RADOS RGW internals (`rgw_lc`, `rgw_rados`, `rgw_sal_rados`), REST connection code, zone tier configuration, and coroutine yield support. The raw pointer/reference style makes lifetime ownership external; misuse can lead to stale bucket/object/tier references. Tests should compile both callers and implementation under RADOS-enabled builds and exercise context values for legacy versus per-bucket target naming.
