# sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_ownership_test.go

## Purpose

This test file verifies how SeaweedFS assigns object owner metadata during S3 PUT-like writes, focusing on `setObjectOwnerFromRequest`.

## Important APIs, Types, and Functions

`TestSetObjectOwnerFromRequest` constructs `S3ApiServer`, optional `BucketRegistry`, `BucketMetaData`, AWS `s3.Owner`, and `filer_pb.Entry` values. The output contract is `entry.Extended[s3_constants.ExtAmzOwnerKey]`.

## Control Flow

Table rows cover `BucketOwnerEnforced`, `ObjectWriter`, `BucketOwnerPreferred`, nil registry, missing metadata, missing owner, nil owner ID, and empty uploader account id. Bucket-owner-enforced uses the bucket owner when available; other modes and failure cases fall back to the uploader.

## State and Persistence Behavior

No filer writes occur. The tested persistence contract is owner identity stored in `Entry.Extended` so list/version/ACL behavior can expose correct owner information.

## Dependencies and Integration Points

The test depends on bucket registry cache internals, bucket metadata object-ownership settings, AWS SDK owner structs, `filer_pb.Entry`, and S3 constants.

## Risks and Edge Cases

The key risk is wrong owner attribution in bucket-owner-enforced mode. The test also guards nil and cache-miss fallbacks, but does not cover ACL grants or multipart/copy integrations.

## Test Signals

The table-driven coverage is a focused signal for owner selection and fallback behavior.
