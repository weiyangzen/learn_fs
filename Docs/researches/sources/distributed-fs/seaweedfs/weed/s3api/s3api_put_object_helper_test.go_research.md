# sources/distributed-fs/seaweedfs/weed/s3api/s3api_put_object_helper_test.go

## Purpose

This test file verifies request-reader selection for regular and AWS chunked streaming PUT bodies.

## Important APIs, Types, and Functions

Tests cover `getRequestDataReader` and `getRequestAuthType` with memory-backed IAM.

## Control Flow

Cases check regular pass-through, signed streaming rejection with IAM disabled, unsigned streaming processing with IAM disabled, checksum-trailer detection, unsigned streaming with IAM enabled, and auth-type classification.

## State and Persistence Behavior

No filer state is touched. The important persistence implication is whether chunk framing is stripped before upload bytes are stored.

## Dependencies and Integration Points

The file depends on memory credential store IAM, auth-type constants, S3 error codes, and HTTP request bodies.

## Risks and Edge Cases

The tests protect the regression where chunked data with checksum headers was stored incorrectly when IAM was disabled. They do not assert decoded body bytes.

## Test Signals

Reader identity checks are good classification signals; byte-level chunked decoding tests would be stronger.
