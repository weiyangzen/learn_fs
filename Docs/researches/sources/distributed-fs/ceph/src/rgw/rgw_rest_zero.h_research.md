# sources/distributed-fs/ceph/src/rgw/rgw_rest_zero.h

## Purpose
`rgw_rest_zero.h` declares the zero REST manager, an unauthenticated benchmarking endpoint that avoids backend reads/writes and serves a shared in-memory zero-byte resource.

## Important APIs, Types, and Functions
`ZeroResource` is forward declared. `RESTMgr_Zero` derives from `RGWRESTMgr`, owns a `std::unique_ptr<ZeroResource>`, constructs it, and overrides `get_handler()` to create a request handler.

## Control Flow
Frontend registration creates one `RESTMgr_Zero`. Each request asks it for a handler, and the handler uses the shared resource to service GET/HEAD/PUT/DELETE as implemented in the `.cc` file.

## State and Persistence Behavior
The manager owns process-local state only. `ZeroResource` is not persisted and exists for the lifetime of the manager.

## Dependencies and Integration Points
It depends on `<memory>` and `rgw_rest.h`. It integrates with RGW REST manager registration and uses the auth strategy registry only as an unused `get_handler()` parameter.

## Risks
The endpoint intentionally bypasses authentication and backend storage. It should remain isolated from normal object namespaces and only be enabled for benchmarking or diagnostics.

## Test Signals
Tests should confirm manager construction, handler creation with unused auth registry, shared state across paths handled by one manager, and no backend SAL calls for zero endpoint operations.
