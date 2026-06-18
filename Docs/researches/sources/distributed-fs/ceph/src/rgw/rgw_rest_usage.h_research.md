# sources/distributed-fs/ceph/src/rgw/rgw_rest_usage.h

## Purpose
`rgw_rest_usage.h` declares the S3-authenticated usage REST handler and manager for RGW usage reporting/trimming endpoints.

## Important APIs, Types, and Functions
`RGWHandler_Usage` derives from `RGWHandler_Auth_S3`, overrides GET and DELETE op factories, and bypasses `read_permissions()` by returning success.

`RGWRESTMgr_Usage` returns a new `RGWHandler_Usage` using the S3 auth registry.

## Control Flow
The manager produces a handler, the inherited S3 auth path authorizes the request, and method selection maps GET/DELETE to usage ops implemented in the `.cc` file.

## State and Persistence Behavior
The header contains no persistent state. It exposes read/write usage behavior through operation objects.

## Dependencies and Integration Points
It depends on `rgw_rest.h` and `rgw_rest_s3.h`. Integration is through S3 auth and whichever frontend resource path registers `RGWRESTMgr_Usage`.

## Risks
Because `read_permissions()` always returns 0, capability checks must remain in operation classes. Adding methods without explicit cap checks would bypass admin authorization expectations.

## Test Signals
Dispatch tests should verify GET/DELETE creation, S3 auth application, and operation-level caps for usage read/write.
