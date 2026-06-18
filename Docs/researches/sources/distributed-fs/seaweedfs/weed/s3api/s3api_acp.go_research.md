# sources/distributed-fs/seaweedfs/weed/s3api/s3api_acp.go

## Purpose
`s3api_acp.go` contains small access-control-policy helpers for account identification and bucket ownership checks. It determines requester account IDs from headers and enforces bucket-owner-only operations unless the requester is an admin.

## Important APIs, Types, and Functions
The file defines `getAccountId(r *http.Request) string` and the method `(*S3ApiServer).checkAccessByOwnership(r *http.Request, bucket string) s3err.ErrorCode`.

## Control Flow
`getAccountId` reads the SeaweedFS/S3 account ID header and falls back to anonymous account ID when absent. `checkAccessByOwnership` reads bucket metadata from `bucketRegistry`, allows errors to propagate, allows admins based on capabilities, then compares the request account ID with the bucket owner ID. Non-admin, non-owner requests are denied.

## State and Persistence Behavior
The helper reads bucket metadata but does not mutate it. Authorization decisions are per request. Account identity is sourced from request headers, while admin status is derived from server auth state.

## Dependencies and Integration Points
It depends on `bucketRegistry.GetBucketMetadata`, `isUserAdmin`, account constants, S3 header constants, and S3 error codes. It is used by ACL/ACP handlers that require bucket ownership.

## Risks and Edge Cases
The comment notes admin is by capability, not account ID, because account-less identities can share an admin-looking ID. Correctness depends on upstream authentication setting trusted account headers; this helper itself does not verify signatures. Missing owner metadata causes denial unless admin.

## Test Signals
Tests should cover bucket lookup errors, admin bypass, owner allow, anonymous/non-owner deny, and buckets with nil owner metadata.
