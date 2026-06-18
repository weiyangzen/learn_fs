# sources/distributed-fs/ceph/src/rgw/services/svc_bucket_sync.h

## Purpose

`svc_bucket_sync.h` declares the abstract bucket-sync service interface used by bucket metadata storage to maintain bucket-level sync policy handlers and bucket index sync hints. The file was read as a complete 52-line header.

## Important APIs, Types, and Functions

`RGWSI_Bucket_Sync` derives from `RGWServiceInstance`. It defines `RGWBucketSyncPolicyHandlerRef` as `std::shared_ptr<RGWBucketSyncPolicyHandler>` and declares pure virtual methods `get_policy_handler()`, `handle_bi_update()`, `handle_bi_removal()`, and `get_bucket_sync_hints()`.

## Control Flow

The header has no implementation flow. Concrete services provide policy handler lookup for optional zone/bucket scope, react to bucket-info updates/removals, and return source/destination sync hint buckets.

## State and Persistence Behavior

No state is stored in this interface. Implementations may persist sync hints or policies in system objects or indexes; `svc_bucket_sobj.cc` calls update/removal hooks after bucket instance mutations.

## Dependencies and Integration Points

It includes `driver/rados/rgw_service.h` and forward-declares `RGWBucketSyncPolicyHandler`. It integrates bucket metadata writes with multisite bucket sync policy evaluation and sync hint maintenance.

## Risks and Edge Cases

Bucket metadata writes depend on `handle_bi_update()` success, while removal treats `handle_bi_removal()` failures as nonfatal in the system-object implementation. Optional zone/bucket arguments require implementations to handle global, zone, and bucket-specific policies consistently.

## Test Signals

Signals include mock policy-handler tests, bucket instance update/removal integration tests, hint source/destination tests, and error-path tests for update failure versus removal failure handling.
