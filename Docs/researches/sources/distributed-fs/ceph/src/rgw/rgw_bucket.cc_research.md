# sources/distributed-fs/ceph/src/rgw/rgw_bucket.cc

Purpose: implements bucket key parsing/formatting helpers and a utility to transfer bucket and object ownership through the SAL layer.

Important APIs/types/functions: `init_bucket()`, `rgw_bucket_parse_bucket_key()`, `rgw_make_bucket_entry_name()`, `rgw_parse_url_bucket()`, and `rgw_chown_bucket_and_objects()`.

Control flow: `rgw_bucket_parse_bucket_key()` parses `[tenant/]name:instance[:shard_id]`, with optional tenant and shard id. `rgw_parse_url_bucket()` parses S3 tenant-qualified `tenant:bucket`, allowing `:bucket` as explicit legacy tenant. `rgw_chown_bucket_and_objects()` first changes bucket ownership, skips object ACL rewrites when ObjectOwnership is `BucketOwnerEnforced`, then lists all object versions in batches of 1000 and calls `Object::chown()` for each.

State/persistence: parsing functions derive metadata keys. `rgw_chown_bucket_and_objects()` persists bucket owner metadata and object ACL/owner changes through SAL bucket/object operations.

Dependencies/integration: integrates with SAL `Driver`, `Bucket`, `Object`, `User`, object ownership helpers, Ceph errno/logging, and optional yields.

Risks: parsing uses delimiter assumptions; bucket names with unexpected delimiters can misparse. `strict_strtol(shard.data())` depends on null-terminated view data from the original string. Chown loops can be expensive, partially complete on error, and writes progress to `cerr`.

Test signals: parse/format round-trips for tenantless, tenant-qualified, idless, and sharded keys; S3 URL bucket parsing; chown behavior with BucketOwnerEnforced; partial-list continuation and failure propagation.
