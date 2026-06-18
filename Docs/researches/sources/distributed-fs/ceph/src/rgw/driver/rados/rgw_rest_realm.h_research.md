# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_rest_realm.h

## Purpose
This header declares the REST manager for the RADOS RGW realm admin resource.

## Important APIs, Types, And Functions
- `RGWRESTMgr_Realm::RGWRESTMgr_Realm()` registers realm subresources such as `period`.
- `RGWRESTMgr_Realm::get_handler()` constructs the authenticated realm handler implemented in the `.cc` file.

## Control Flow
Admin REST registration instantiates this manager for `/admin/realm`. The manager creates a handler per request, and the handler selects realm get/list operations or delegates to the registered period resource.

## State And Persistence Behavior
The header has no direct state. Its implementation routes to operations that read and mutate config-store realm and period objects.

## Dependencies And Integration Points
It depends only on the generic REST manager header, keeping realm operation details in the implementation file. It integrates with the admin REST resource registry.

## Risks And Edge Cases
Because the concrete handler is hidden in the implementation, route additions require constructor registration and handler dispatch updates together. `get_handler()` ignores the frontend path string, so path validation is handled by the resource manager tree.

## Test Signals
Tests should verify manager construction registers `period`, handler creation succeeds with an auth registry, and `/admin/realm?list` versus `/admin/realm/period` dispatch remains stable.
