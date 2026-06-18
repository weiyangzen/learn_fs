# sources/distributed-fs/seaweedfs/weed/s3api/s3tables/handler_bucket_get_list_delete.go

## Purpose
This file implements table-bucket read, list, and delete operations.

## Important APIs and functions
`handleGetTableBucket` fetches metadata and optional bucket policy, authorizes `GetTableBucket`, and returns bucket details. `handleListTableBuckets` paginates table buckets under the tables root, applies prefix and per-bucket visibility filtering, and returns summaries plus continuation token. `handleDeleteTableBucket` validates input, loads metadata/policy, authorizes delete, checks emptiness, and removes both the table object entry and bucket directory.

## Control flow and state behavior
Get parses `tableBucketARN`, derives bucket name, reads `ExtendedKeyMetadata`, optionally reads `ExtendedKeyPolicy`, then authorizes using bucket ARN and metadata owner. List defaults `MaxBuckets` to 100, caps it at 1000, lists from the continuation token with inclusive handling on first page, skips hidden/non-directory/non-table entries, filters prefix, unmarshals metadata, loads policy if present, and filters invisible buckets instead of failing. Delete reads metadata/policy and checks authorization inside one filer-client block, then lists children with limit 10 and treats any non-hidden child as non-empty. Deletion separately removes the table-object bucket path and the table bucket directory, returning failure only if both operations fail.

## Dependencies and integration points
The handlers depend on ARN parsing, path helpers, metadata marker checks, filer list/delete RPCs, permission checks, and extended-attribute metadata/policy format.

## Risks and edge cases
List pagination can return a continuation token after collecting `maxBuckets`, but filtering means the underlying scan may traverse more entries than returned. Delete emptiness ignores hidden entries only; metadata-only or stray entries can block deletion. Delete cleanup can succeed partially, logging one failed removal while returning success. Authorization-denied get/delete responses differ: get returns forbidden while some namespace flows hide resources with not found.

## Test signals
No direct tests in this subset cover these handlers. Behavior should be verified by S3 Tables integration tests, especially list pagination/filtering and delete partial cleanup.
