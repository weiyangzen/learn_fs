<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_bucket_sync_sobj.h -->
# sources/distributed-fs/ceph/src/rgw/services/svc_bucket_sync_sobj.h

Purpose: Declares the concrete system-object backed implementation of the RGW bucket sync service.

Important APIs, types, and functions: `RGWSI_Bucket_Sync_SObj` derives from `RGWSI_Bucket_Sync`. It stores a chained cache of bucket sync policy handlers and a hint index manager. The public API exposes `init()`, `get_policy_handler()`, `handle_bi_update()`, `handle_bi_removal()`, and `get_bucket_sync_hints()`. The private `optional_zone_bucket` key supports caching temporary policy handlers during recursive hint resolution.

Control flow: Callers initialize dependencies, service startup creates the cache, bucket metadata changes enter through `handle_bi_update()`/`handle_bi_removal()`, and sync workers/admin paths can ask for policy handlers or related bucket hints. Private helpers resolve policy hints and recursively load hinted bucket handlers while avoiding repeated loads through a temporary map.

State and persistence: The header declares in-memory cache ownership and service pointers only; persistent state is in the implementation's sysobj hint indexes and bucket metadata objects.

Dependencies and integration points: Depends on RGW service infrastructure, bucket sync base interface, zone/sysobj/cache/bucket services, and sync policy handler types from RGW bucket sync. It is part of the RGW service graph created by `RGWServices_Def`.

Risks and test signals: The contract assumes `init()` is called before `do_start()` and before any policy/hint operation. Tests should exercise the virtual base interface through this implementation and verify null optional zone/bucket cases as well as bucket-instance normalization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_bucket_sync_sobj.h -->
