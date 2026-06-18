# sources/distributed-fs/ceph/src/rgw/rgw_rest_ratelimit.cc

## Purpose

`rgw_rest_ratelimit.cc` implements administrative REST operations for reading and updating RGW rate-limit configuration at three scopes: bucket-specific attrs, user-specific attrs, and global period config for bucket, user, and anonymous limits. It exposes `GET` for inspection and `POST` for mutation through `RGWHandler_Ratelimit`.

## Important APIs, types, and functions

- `RGWOp_Ratelimit_Info` is a read operation requiring `ratelimit=read` caps. It parses `ratelimit-scope`, `uid`, `bucket`, `tenant`, and `global`, then returns JSON for the requested scope.
- `RGWOp_Ratelimit_Set` is a write operation requiring `ratelimit=write` caps. It parses maximum operation/byte limits and `enabled`, forwards writes to the master zone, merges the requested changes into existing `RGWRateLimitInfo`, and persists them.
- `RGWOp_Ratelimit_Set::set_ratelimit_info()` is the shared field-merging helper. It only applies provided non-negative numeric values and applies `enabled` when provided. If no valid rate-limit field is present, it sets `op_ret = -EINVAL`.
- `RGWHandler_Ratelimit::op_get()` and `op_post()` create the read and set operations.

## Control flow

The `GET` path validates `global` manually because `RESTArgs::get_bool()` treats an empty boolean as true. For non-global bucket scope, it loads a bucket by `tenant` and `bucket`, decodes `RGW_ATTR_RATELIMIT` if present, and emits `bucket_ratelimit`. For non-global user scope, it loads the user, decodes the same attr, and emits `user_ratelimit`. For global scope, it reads `RGWPeriodConfig` for the current realm id through `s->penv.cfgstore`, tolerates missing config, and emits bucket, user, and anonymous rate-limit blocks. Any unrecognized parameter combination returns `-EINVAL`.

The `POST` path parses all optional numeric limits with `RESTArgs::get_int64()` and validates boolean text for `enabled` and `global`. It first forwards the request to the master zone through `rgw_forward_request_to_master()`. It then builds an initial `RGWRateLimitInfo` from supplied fields, and for user or bucket scope it loads the existing object, decodes existing rate-limit attrs, reapplies supplied fields so updates are merge-style, encodes `RGWRateLimitInfo`, and stores via `merge_and_store_attrs()`. For global scope, it reads period config, selects the bucket, user, or anonymous rate-limit member based on `ratelimit-scope`, merges fields, and writes period config back with `write_period_config()`.

## State and persistence behavior

Bucket and user rate limits are stored as encoded `RGWRateLimitInfo` in `RGW_ATTR_RATELIMIT` on bucket/user attrs. Global rate limits are stored in realm period config as `RGWPeriodConfig::bucket_ratelimit`, `user_ratelimit`, and `anon_ratelimit`. The code uses merge-and-store for attrs so it updates only the rate-limit attr while preserving other attrs. Global writes use `cfgstore->write_period_config()` and therefore affect configuration propagated through period metadata.

## Dependencies and integration points

The implementation depends on `rgw_sal.h` for users and buckets, `rgw_sal_config.h` for period config, `rgw_process_env.h` for site/config store access, `rgw_op.h` for forwarding helpers and operation base behavior, `RESTArgs` parsing, `RGWRateLimitInfo` encode/decode, and JSON formatter output.

## Risks and edge cases

- `set_ratelimit_info()` ignores provided negative numeric values without directly returning an error. If at least one other field is valid, a request with a negative field can succeed while silently ignoring that field.
- The helper sets `op_ret` on the operation object instead of returning a status, so all callers must check `op_ret` after calling it.
- The write path calls `set_ratelimit_info()` before loading existing user/bucket/global state and then again after decoding existing state; this is redundant but also means `ratelimit_configured` remains true across the second call.
- All writes are forwarded before local validation of target object existence. Forwarding failures stop local work; forwarded success followed by local attr failure can leave local metadata temporarily inconsistent until sync.
- Boolean parsing is manually guarded because empty booleans are otherwise accepted as true; future boolean parameters need the same care.
- Global scope requires a valid `ratelimit-scope` of `bucket`, `user`, or `anon`; non-global scopes require the matching identity parameter.

## Test signals

Tests should cover `GET` bucket/user/global with missing attrs, malformed encoded attrs, missing user or bucket, invalid `global` boolean text, and invalid scope combinations. Mutation tests should cover each limit field, `enabled`, merge behavior preserving unspecified fields, negative numeric handling, user and bucket attr persistence, global bucket/user/anonymous config writes, forwarding behavior from non-master zones, and cap enforcement for read versus write operations.
