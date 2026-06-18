# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_rest_user.h

## Purpose
This header declares the REST handler and manager for the RADOS RGW user admin resource.

## Important APIs, Types, And Functions
- `RGWHandler_User` derives from `RGWHandler_Auth_S3`, overrides the HTTP method operation selectors, and returns zero from `read_permissions()`.
- `RGWRESTMgr_User::get_handler()` constructs a user handler with the auth strategy registry.

## Control Flow
The admin REST resource manager creates `RGWHandler_User` for `/admin/user` requests. The handler inspects method and subresource state, then returns the concrete operation implemented in `rgw_rest_user.cc`.

## State And Persistence Behavior
This header does not persist state. It routes to operations that read and mutate persistent user, subuser, access-key, caps, and quota metadata.

## Dependencies And Integration Points
It depends on the generic REST framework and S3-authenticated handler base. It integrates with admin REST registration and operation-level cap checks.

## Risks And Edge Cases
Like other admin handlers in this directory, permissive `read_permissions()` places responsibility on every concrete operation to implement cap checks. New subresources must be added in both the handler dispatch and implementation with correct authorization.

## Test Signals
Tests should verify handler construction, dispatch for GET/PUT/POST/DELETE subresources, and cap enforcement at the operation level.
