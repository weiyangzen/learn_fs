# sources/distributed-fs/ceph/src/rgw/rgw_rest_ratelimit.h

## Purpose

`rgw_rest_ratelimit.h` declares the authenticated REST handler and REST manager for RGW rate-limit administration. It connects the ratelimit endpoint to S3-authenticated request handling and exposes a manager that creates the handler for RGW routing.

## Important APIs, types, and functions

- `RGWHandler_Ratelimit` derives from `RGWHandler_Auth_S3`, so requests use S3 authentication. It overrides `op_get()` and `op_post()` to create the concrete read and write operations implemented in `rgw_rest_ratelimit.cc`.
- `RGWHandler_Ratelimit::read_permissions()` returns success, leaving capability enforcement to `RGWOp_Ratelimit_Info::check_caps()` and `RGWOp_Ratelimit_Set::check_caps()`.
- `RGWRESTMgr_Ratelimit` derives from `RGWRESTMgr` and overrides `get_handler()` to return a new `RGWHandler_Ratelimit` with the provided auth strategy registry.

## Control flow

When the REST manager is selected for the ratelimit endpoint, `get_handler()` constructs an authenticated S3 handler. The handler's verb dispatch maps `GET` to ratelimit inspection and `POST` to ratelimit update. The header does not declare `PUT` or `DELETE`, so unsupported methods fall through to base behavior.

## State and persistence behavior

The header stores no persistent state. Handler instances are request-scoped. Persistent behavior is entirely in the `.cc` file: encoded user/bucket attrs and global period config writes.

## Dependencies and integration points

It depends on `rgw_rest.h` and `rgw_rest_s3.h` for REST manager and authenticated handler base classes. Under `WITH_RADOSGW_RADOS`, it includes `rgw_sal_rados.h`, tying the endpoint to RADOS-backed SAL builds. The manager signature accepts a SAL driver, request state, auth registry, and frontend prefix, matching the RGW REST manager contract.

## Risks and edge cases

- Because `read_permissions()` always succeeds, operation-level caps are the only protection beyond authentication. Any future ratelimit operation must implement `check_caps()` correctly.
- `get_handler()` ignores the driver and request state parameters, so handler construction cannot vary by backend or request context without modifying this manager.
- Only `GET` and `POST` are exposed. Clients expecting `PUT` for updates would not be served by this handler.

## Test signals

Route tests should verify that the manager returns `RGWHandler_Ratelimit`, `GET` produces the info op, `POST` produces the set op, read/write caps are enforced by the concrete ops, and unauthenticated or incorrectly signed requests fail through the S3 auth base.
