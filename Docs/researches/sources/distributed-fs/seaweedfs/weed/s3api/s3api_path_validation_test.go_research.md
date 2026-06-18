# sources/distributed-fs/seaweedfs/weed/s3api/s3api_path_validation_test.go

## Purpose

This test file validates S3 path-validation middleware security and hot-path allocation behavior.

## Important APIs, Types, and Functions

Tests cover `validateRequestPath` and `hasPathSegmentQuery` using Gorilla mux, `httptest`, and response-code checks.

## Control Flow

Tests mirror production routes with `SkipClean(true)`, reject traversal and encoded traversal, reject empty captured vars, validate unsafe `versionId`/`uploadId` values including encoded names and repeated values, pass unrelated queries, and assert zero allocations on common unrelated raw queries.

## State and Persistence Behavior

No persistent state changes. Tests observe status codes and whether inner handlers ran.

## Dependencies and Integration Points

The file depends on mux route matching and the validation middleware boundary before IAM authorization and filer path normalization.

## Risks and Edge Cases

Covered risks include path traversal across buckets and unsafe query-derived entry names. Future path-like query params would need additional coverage.

## Test Signals

The route-level security tests and allocation assertion are strong regression signals.
