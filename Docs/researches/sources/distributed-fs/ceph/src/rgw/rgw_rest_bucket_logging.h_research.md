# sources/distributed-fs/ceph/src/rgw/rgw_rest_bucket_logging.h

## Purpose

Declares the S3 bucket logging REST handler factory.

## Important APIs, Types, and Functions

`RGWHandler_REST_BucketLogging_S3` derives from `RGWHandler_REST_S3`, overrides permission initialization/reading to return success, disables quota support, and exposes static `create_get_op()`, `create_put_op()`, and `create_post_op()` factories.

## Control Flow and Data Flow

The surrounding S3 handler can route `?logging` requests to this handler and call the static factories to create operation instances implemented in the `.cc` file. Operation-level permission checks perform the real IAM and ownership checks.

## State and Persistence Behavior

No state is stored in the handler declaration. Persistence is handled by the operation implementations against bucket attrs and log objects.

## Dependencies and Integration Points

Depends on `rgw_rest_s3.h`. Integrated with S3 bucket subresource routing and bucket logging operation classes.

## Risks and Edge Cases

Returning success from handler-level permission hooks means tests must ensure operation-level `verify_permission()` always runs and enforces access. `supports_quota()` returns false because logging configuration operations should not be quota-charged.

## Test Signals

Route GET/PUT/POST `?logging` requests through the S3 dispatcher, verify quota bypass, operation-level permission enforcement, and factory ownership/cleanup.
