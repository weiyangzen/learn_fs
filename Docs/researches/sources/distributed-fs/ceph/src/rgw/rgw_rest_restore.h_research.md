# sources/distributed-fs/ceph/src/rgw/rgw_rest_restore.h

## Purpose

`rgw_rest_restore.h` declares the authenticated REST handler and manager for RGW restore status/list operations. It exposes only `GET` handling and delegates concrete operation selection to the implementation file.

## Important APIs, types, and functions

- `RGWHandler_Restore` derives from `RGWHandler_Auth_S3`, so restore inspection requires S3-authenticated requests. It overrides `op_get()` to select object restore status or bucket restore listing.
- `RGWHandler_Restore::read_permissions()` returns success, leaving caps to the concrete restore operations.
- `RGWRESTMgr_Restore` derives from `RGWRESTMgr` and returns a new `RGWHandler_Restore` from `get_handler()`.

## Control flow

When the restore endpoint is routed, the manager constructs `RGWHandler_Restore`. The handler authenticates through the S3 auth base, then `op_get()` checks request args in the `.cc` file and returns a restore-status op for object-specific requests or a restore-list op otherwise. No write verbs are declared in this handler.

## State and persistence behavior

The header contains no persistence logic and no long-lived state. Restore data access is delegated by the `.cc` operations to the restore service behind the SAL driver.

## Dependencies and integration points

It includes `rgw_rest.h` and `rgw_rest_s3.h` for REST manager and authenticated handler base definitions. The manager signature integrates with the generic RGW REST routing layer and passes the auth strategy registry into the handler.

## Risks and edge cases

- As with other small RGW admin-style handlers, operation-level cap checks are required because `read_permissions()` returns `0`.
- The manager ignores the SAL driver and request state when constructing the handler, so backend-specific restore routing would require changes.
- Only `GET` is supported. Any future restore mutation endpoint needs explicit verb mapping and caps.

## Test signals

Route tests should verify manager construction, S3 auth enforcement, `GET` dispatch to object status when the `object` subresource exists, `GET` dispatch to list otherwise, rejection of unsupported verbs, and concrete operation caps for `buckets=read`.
