# sources/distributed-fs/ceph/src/rgw/rgw_quota.h

## Purpose

Declares the public quota handler interface used by RGW write paths to check quota and adjust cached stats, plus helpers that apply configured default quotas.

## Important APIs, Types, and Functions

`RGWQuotaHandler::check_quota()` validates a prospective object/count delta for a bucket owner, bucket, and `RGWQuota`. `update_stats()` applies object and byte deltas after data changes. `generate_handler()` and `free_handler()` allocate the concrete implementation. `rgw_apply_default_bucket_quota()`, `rgw_apply_default_user_quota()`, and `rgw_apply_default_account_quota()` populate `RGWQuotaInfo` from config defaults.

## Control Flow and Data Flow

Callers construct a handler for a SAL driver, call `check_quota()` before accepting writes, and call `update_stats()` after mutations so the in-memory quota caches track recent changes. Default quota helpers are used when creating or loading quota policy state that should inherit cluster configuration.

## State and Persistence Behavior

The interface itself owns no state, but the implementation created by `generate_handler()` owns caches and optional sync threads. Default helper changes apply to the passed `RGWQuotaInfo` object only; persistence depends on callers saving that info.

## Dependencies and Integration Points

Depends on quota types, user types, `optional_yield`, config forwarding, and SAL driver forward declarations. It is used by object operations, account/user admin paths, and storage driver initialization.

## Risks and Edge Cases

The API expects negative errno returns but exposes raw pointers and manual `free_handler()`. Callers must pair check/update correctly; missing updates make cached quota less accurate, while updates before failed writes overcount. Default helpers enable quotas only when configured max values are non-negative.

## Test Signals

Test handler allocation/destruction with quota threads enabled and disabled, pre-write quota rejection, post-write stats deltas, default helper behavior for only size, only object count, both, and neither configured, and error propagation from the implementation.
