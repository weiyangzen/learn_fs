# sources/distributed-fs/seaweedfs/weed/s3api/auth_copy_source_test.go

## Purpose

`s3api/auth_copy_source_test.go` verifies authorization of the source object in S3 CopyObject flows. It was read as a complete 304-line file.

## Important APIs, Types, and Functions

`newCopyRequest` builds destination PUT requests with `X-Amz-Copy-Source`. Tests cover auth disabled, nil identity denial, admin bypass, prefix-scoped identities, IAM integration receiving source resource, IAM allow, versionId propagation, presigned URL session token preservation, and preservation of the copy-source header.

## Control Flow

Tests construct `IdentityAccessManagement` instances directly, often with `MockIAMIntegration`, then call `AuthorizeCopySource(req, identity, sourceBucket, sourceObject, versionId)` and inspect returned S3 errors plus captured synthetic request fields.

## State and Persistence Behavior

State is in-memory IAM identity configuration and request objects. Tests assert the original destination request is not mutated when a synthetic GET request is built for source authorization.

## Dependencies and Integration Points

Depends on IAM action resolution, STS/IAM integration hooks, S3 constants/errors, HTTP request handling, and copy-source parsing semantics.

## Risks and Edge Cases

The covered regressions include authorizing only the destination, dropping STS session tokens from presigned URLs, losing `versionId`, mutating the original PUT, or omitting `X-Amz-Copy-Source` from policy condition evaluation.

## Test Signals

Strong focused regression signal for CopyObject source authorization and STS/IAM behavior. Additional tests could cover URL-encoded source keys and malformed copy-source headers.
