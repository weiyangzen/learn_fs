# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_cr_tools.cc

## Purpose

Implements concrete `_send_request()` specializations for small RGW RADOS coroutine helpers declared in `rgw_cr_tools.h`. These wrappers let coroutine code create users, fetch user and bucket metadata, update bucket lifecycle configuration, and retrieve bucket sync policy handlers through the existing RGW admin, SAL, lifecycle, and bucket-service APIs.

## Important APIs, Types, and Functions

The file specializes `RGWUserCreateCR::Request::_send_request`, `RGWGetUserInfoCR::Request::_send_request`, `RGWGetBucketInfoCR::Request::_send_request`, `RGWBucketLifecycleConfigCR::Request::_send_request`, and `RGWBucketGetSyncPolicyHandlerCR::Request::_send_request`. `RGWUserCreateCR` builds an `RGWUserAdminOpState` from `rgw_user_create_params` and calls `RGWUserAdminOp_User::create()`. The metadata helpers call `store->ctl()->user->get_info_by_uid()`, `store->load_bucket()`, `RGWLC::set_bucket_config()`, and `store->ctl()->bucket->get_sync_policy_handler()`.

## Control Flow and Data Flow

User creation reads the `rgw_user_max_buckets` config default, copies user-facing fields into an admin op state, maps the optional key type string to S3 or Swift constants, applies default bucket/user quota limits when requested, and invokes the admin create operation with `RGWNullFlusher` and `null_yield`. User-info and bucket-info coroutines are direct read-through calls that fill their result objects. Lifecycle setup first obtains `RGWLC` from `store->getRados()`, fails with `-EIO` when lifecycle support is not initialized, and then submits bucket attrs plus an `RGWLifecycleConfiguration`. Sync-policy retrieval forwards optional zone and bucket scope into the bucket service and stores the returned `RGWBucketSyncPolicyHandlerRef`.

## State and Persistence Behavior

This file does not own durable state, but several calls mutate RGW metadata. `RGWUserAdminOp_User::create()` persists user info, keys, caps, suspension/system flags, max-bucket limits, and optional quota records. `RGWLC::set_bucket_config()` persists lifecycle config against bucket metadata and lifecycle infrastructure. The get-info, load-bucket, and sync-policy handler calls only read cluster metadata into coroutine result objects.

## Dependencies and Integration Points

The implementation depends on `RGWStore`/RADOS store access from `rgw_cr_rados.h`, user admin operation state from `rgw_user.h` and `rgw_op.h`, bucket loading through SAL, lifecycle service `RGWLC`, zone/bucket sync services, and Ceph logging/error helpers. Callers are other RGW coroutine flows that need a coroutine object instead of directly invoking admin or service APIs; sync policy use is visible in data sync and bilog trimming code.

## Risks and Edge Cases

`params.key_type` treats only the literal `"swift"` as Swift and defaults every other non-empty value to S3, so invalid strings are not rejected here. The default max-buckets config is read as `int64_t` and stored as `int32_t`, which relies on configured values fitting the narrower type. User creation applies quota defaults only when the corresponding config values are non-negative. In lifecycle setup, negative `set_bucket_config()` results are logged, but the code returns `-ret`; because Ceph APIs conventionally return negative errno values, this can flip an error into a positive value. `params.bucket` is a raw pointer and must remain valid for the coroutine call. These helpers use `null_yield`, so they are not passing an external yield context into the underlying operations.

## Test Signals

Useful coverage includes user creation with generated and supplied keys, Swift key type, invalid key-type strings, explicit and default max-bucket limits, quota defaults enabled/disabled, exclusive create conflicts, user-info miss/hit paths, tenant-qualified bucket loading, lifecycle service missing, lifecycle set failures preserving expected error sign, and sync policy retrieval for zone-scoped, bucket-scoped, and global calls.
