# sources/distributed-fs/ceph/src/rgw/rgw_rest_dedup.h

## Purpose

`rgw_rest_dedup.h` declares the authenticated admin REST handler and manager for RGW deduplication endpoints.

## Important APIs and Types

`RGWHandler_Dedup` derives from `RGWHandler_Auth_S3`, dispatches GET and POST operations, and returns 0 from `read_permissions()`. `RGWRESTMgr_Dedup` creates a dedup handler for the registered REST resource.

## Control Flow and Integration

The manager returns a handler, S3 admin auth authenticates the request, and the implementation maps query argument `op` to a dedup operation. Operation-level caps enforce read or write permission.

## State, Risks, and Tests

The header itself has no state. The main risk is overbroad handler registration because all behavior is selected by query args. Tests should verify the manager constructs `RGWHandler_Dedup`, GET/POST dispatches only known ops, and unknown ops return no operation.
