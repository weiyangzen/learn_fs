# sources/distributed-fs/seaweedfs/weed/s3api/s3api_path_validation.go

## Purpose

This file implements S3 route path validation middleware to prevent unsafe bucket/object/query segments from normalizing into unintended filer paths.

## Important APIs, Types, and Functions

Functions are `hasPathSegmentQuery`, `hasInvalidPathSegment`, and `validateRequestPath`.

## Control Flow

The middleware validates mux-captured `bucket` and `object` variables and only parses query values when raw query text indicates `versionId` or `uploadId`, including percent-encoded names. Invalid values return `ErrInvalidRequest`.

## State and Persistence Behavior

No state is persisted. It protects downstream filer path joins from `..`, `.`, slashes, backslashes, and unsafe path segments.

## Dependencies and Integration Points

The file depends on Gorilla mux, `s3_constants` validation helpers, and `s3err`. It integrates with production `SkipClean(true)` routing before IAM/filer access.

## Risks and Edge Cases

The security risk is authorizing one bucket while path normalization accesses another. Query path-segment validation protects version/upload entry names.

## Test Signals

Companion tests cover traversal, encoded traversal, empty captures, unsafe query values, encoded query names, and allocation behavior.
