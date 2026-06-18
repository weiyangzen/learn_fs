# sources/distributed-fs/seaweedfs/weed/s3api/s3tables/handler_policy.go

## Purpose
This file implements table-bucket policies, table policies, and resource tag operations for S3 Tables resources.

## Important APIs and functions
`extractResourceOwnerAndBucket` derives owner and bucket name from stored metadata and resource path. Bucket policy handlers are `handlePutTableBucketPolicy`, `handleGetTableBucketPolicy`, and `handleDeleteTableBucketPolicy`. Table policy handlers are `handlePutTablePolicy`, `handleGetTablePolicy`, and `handleDeleteTablePolicy`. Tag handlers are `handleTagResource`, `handleListTagsForResource`, and `handleUntagResource`. `resolveResourcePath` maps bucket/table ARNs to filer paths and the tag extended attribute key.

## Control flow and state behavior
Policy put handlers validate required ARN/name/policy fields, parse bucket/table identity, load metadata, authorize against owner and existing bucket policy where applicable, then store policy bytes under `ExtendedKeyPolicy`. Get handlers load metadata and policy, distinguish missing resource from missing policy, authorize, and return policy text. Delete handlers load metadata and current bucket policy, authorize, and remove `ExtendedKeyPolicy`, treating missing policy as non-fatal in delete paths.

Tagging resolves the resource ARN, reads metadata for owner and bucket, optionally reads bucket policy and bucket tags for context, reads existing resource tags, authorizes with request tag keys/resource tags, merges or deletes tags in-memory, and writes the updated JSON map under `ExtendedKeyTags`. Listing tags returns an empty map when the tag attribute is absent.

## Dependencies and integration points
The file depends on ARN parsing, path helpers, metadata structs, filer extended-attribute helpers, `CheckPermissionWithContext`, `PolicyContext`, and resource tag/policy request types. It shares authorization context with bucket and namespace handlers.

## Risks and edge cases
Policy JSON is accepted as an opaque string here; validation is likely delegated to permission evaluation or omitted. Tag updates are read-modify-write without CAS, so concurrent tag changes can be lost. `extractResourceOwnerAndBucket` derives bucket name from path component position, coupling it to `GetTableBucketPath`/`GetTablePath`. Permission for table policies uses bucket policy but not table policy itself before overwrite/delete. Deleting absent policy returns success, which is idempotent but may hide client mistakes.

## Test signals
No direct tests in this subset cover policy/tag handlers. Permission tests elsewhere likely exercise `CheckPermissionWithContext`; handler-level tests should verify missing-policy status codes, tag merge/delete concurrency expectations, and ARN resolution.
