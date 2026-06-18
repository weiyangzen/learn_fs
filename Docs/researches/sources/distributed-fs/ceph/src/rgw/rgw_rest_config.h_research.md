# sources/distributed-fs/ceph/src/rgw/rgw_rest_config.h

## Purpose

`rgw_rest_config.h` declares the authenticated admin REST config resource for RGW. Its current surface is the zone configuration GET operation.

## Important APIs and Types

`RGWOp_ZoneConfig_Get` derives from `RGWRESTOp`, requires `zone` read caps, returns the operation name `get_zone_config`, and leaves `execute()` empty because `send_response()` emits the zone params. `RGWHandler_Config` derives from `RGWHandler_Auth_S3`, dispatches GET operations, and skips extra permission loading by returning 0 from `read_permissions()`. `RGWRESTMgr_Config` creates the handler for this REST mount.

## Control Flow and Integration

The manager is asked for a handler, the handler authenticates through S3 admin auth, and `op_get()` chooses the zone-config operation based on query args. This follows the standard RGW admin REST manager/handler/op layering.

## State, Risks, and Tests

The header declares read-only behavior; state access happens in the implementation. Risks are mostly capability and dispatch correctness: wrong caps would expose zone parameters, and an overbroad `op_get()` would accept unsupported config types. Tests should cover manager creation, authenticated GET dispatch, and cap rejection.
