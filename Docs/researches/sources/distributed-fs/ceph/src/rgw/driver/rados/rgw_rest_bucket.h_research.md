# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_rest_bucket.h

## Purpose
This header declares the REST handler and manager for the RADOS bucket admin resource.

## Important APIs, Types, And Functions
- `RGWHandler_Bucket` derives from `RGWHandler_Auth_S3` and overrides `op_get()`, `op_put()`, `op_post()`, and `op_delete()` to select the concrete bucket admin operation implemented in `rgw_rest_bucket.cc`.
- `read_permissions()` returns zero, leaving authorization to each operation's `check_caps()`.
- `RGWRESTMgr_Bucket::get_handler()` constructs `RGWHandler_Bucket` with the configured auth registry.

## Control Flow
The REST manager is registered for an admin bucket resource. On each request it creates a handler, the handler reads method and subresource state from `req_state`, and the selected `RGWRESTOp` parses arguments and executes.

## State And Persistence Behavior
This file has no direct persistence. It controls routing into operations that mutate or read bucket metadata, quotas, sync flags, bucket links, index state, and objects.

## Dependencies And Integration Points
The header depends on the generic REST framework and S3-authenticated REST handler base. It is integrated by the admin REST resource registration layer.

## Risks And Edge Cases
Returning zero from `read_permissions()` is intentional but means every new operation added to the handler must implement correct cap checks. `get_handler()` ignores the path string and driver at construction time, so operation code must rely on the base framework to attach request state and driver later.

## Test Signals
Tests should verify that each HTTP method reaches the intended operation and that operation-level cap checks are enforced despite permissive handler-level permission reading.
