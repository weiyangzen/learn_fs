# sources/distributed-fs/ceph/src/rgw/rgw_rest_account.h

## Purpose

Declares the REST handler and manager for account administration endpoints.

## Important APIs, Types, and Functions

`RGWHandler_Account` derives from `RGWHandler_Auth_S3`, overrides method factories for GET/PUT/POST/DELETE, and allows `read_permissions()` to return success after auth. `RGWRESTMgr_Account` returns a new account handler for matching routes.

## Control Flow and Data Flow

The manager creates an authenticated S3-style account handler. The handler chooses account operation classes based on HTTP method, with PUT further distinguishing quota subresource in the implementation.

## State and Persistence Behavior

No persistent state is declared. Handlers are allocated per request and deleted by REST manager ownership.

## Dependencies and Integration Points

Depends on `rgw_rest.h` and `rgw_rest_s3.h`. Integrated into admin/account REST resource registration.

## Risks and Edge Cases

`read_permissions()` returning 0 means fine-grained authorization relies on each operation's `check_caps()`. Manager ignores the `driver`, `req_state`, and frontend prefix arguments when constructing the handler.

## Test Signals

Route `/account` requests through the manager, verify auth strategy use, method factory outputs, operation-level cap checks, and handler cleanup.
