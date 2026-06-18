# sources/distributed-fs/ceph/src/rgw/rgw_user.cc

## Purpose
`rgw_user.cc` implements user helper functions for bucket-stat synchronization, bucket usage collection, tenant validation, anonymous user setup, and access/secret key generation.

## Important APIs, Types, and Functions
`rgw_sync_all_stats()` lists all buckets for an owner/tenant, loads each bucket, syncs owner stats, checks bucket shards, and completes stat flushing. `rgw_user_get_all_buckets_stats()` builds a bucket metadata usage map from listed buckets. `rgw_validate_tenant_name()` allows only alnum and underscore. `rgw_get_anon_user()` populates anonymous user info. `rgw_generate_access_key()` generates unique public access key ids and checks duplicates through SAL. `rgw_generate_secret_key()` generates a random secret.

## Control Flow
Bucket listing loops on `listing.next_marker` with chunk size from config. Access-key generation loops until a generated key is not found by `get_user_by_access_key()`, returning only `-ENOENT` as success.

## State and Persistence Behavior
The stat sync function mutates persisted bucket/owner stats via SAL bucket and driver methods. Key generation only returns strings; persistence of keys is handled by callers.

## Dependencies and Integration Points
Depends on RADOS SAL headers, bucket/user types, random generation, RGW error constants, and `rgw_list_buckets_max_chunk`. Used by admin/user management paths.

## Risks
Access-key generation can loop indefinitely under pathological duplicate/random failures. `rgw_sync_all_stats()` logs shard-check errors but does not fail on them. Tenant validation depends on C locale `isalnum()` behavior for signed chars.

## Test Signals
Cover paginated bucket listing, load failures, stat sync failure, flush failure, bucket usage map population, invalid tenant characters, anonymous user clearing, duplicate access key retry, and secret key length/charset.
