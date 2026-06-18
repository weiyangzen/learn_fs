# sources/distributed-fs/ceph/src/rgw/rgw_rest_usage.cc

## Purpose
`rgw_rest_usage.cc` implements admin-style REST operations for reading and trimming RGW usage records. It exposes GET for usage reporting and DELETE for usage log trimming through `RGWHandler_Usage`.

## Important APIs, Types, and Functions
`RGWOp_Usage_Get` derives from `RGWRESTOp`, requires `usage` read caps, parses `uid`, `bucket`, `tenant`, `start`, `end`, `show-entries`, `show-summary`, and comma-separated `categories`, optionally loads the target bucket, and calls `RGWUsage::show()`.

`RGWOp_Usage_Delete` requires `usage` write caps, parses the same target/time filters, optionally loads the bucket, requires `remove-all=true` for an unscoped full trim, and calls `RGWUsage::trim()`.

`RGWHandler_Usage::op_get()` and `op_delete()` allocate the two operation classes.

## Control Flow
The usage handler is S3-authenticated through its base class. GET builds filters and category map, then streams usage output through `flusher`. DELETE builds filters and either rejects an unqualified delete without explicit `remove-all`, or trims matching records.

## State and Persistence Behavior
GET is read-only and accesses persistent usage records through `RGWUsage::show()`. DELETE mutates usage-log persistence through `RGWUsage::trim()`. Bucket scoping uses `driver->load_bucket()` if a bucket name is provided; user scoping uses `driver->get_user(rgw_user(uid_str))`.

## Dependencies and Integration Points
The file depends on `rgw_usage.h`, REST arg helpers, SAL user/bucket APIs, `str_list` category parsing, and `RGWHandler_Usage` declarations. It integrates with admin caps and S3 auth via `RGWHandler_Auth_S3`.

## Risks
The delete operation has a guard against deleting all usage without `remove-all=true`; keeping that guard intact is important for operational safety. User objects are constructed even when `uid` is empty, so downstream `RGWUsage` behavior determines how empty users are interpreted.

## Test Signals
Tests should cover GET with user, bucket, tenant, time range, categories, entries/summary toggles, missing bucket errors, DELETE scoped by user/bucket/time, unscoped DELETE rejection without `remove-all`, and successful unscoped trim only with `remove-all=true`.
