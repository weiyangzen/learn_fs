# sources/distributed-fs/ceph/src/rgw/rgw_rest_metadata.h

## Purpose

`rgw_rest_metadata.h` declares RGW admin REST operations for metadata list/get/put/delete and the handler/manager that exposes them.

## Important APIs and Types

Read operations `RGWOp_Metadata_List`, `RGWOp_Metadata_Get`, and `RGWOp_Metadata_Get_Myself` require `metadata` read caps. `RGWOp_Metadata_Put` requires `metadata` write caps, has private body-reading state, records update status and on-disk version, and reports op type `RGW_OP_ADMIN_SET_METADATA`. `RGWOp_Metadata_Delete` requires `metadata` write caps. `RGWHandler_Metadata` dispatches GET/PUT/DELETE. `RGWRESTMgr_Metadata` creates the handler.

## Control Flow and State

Operation dispatch is query-sensitive for GET: `myself`, `key`, or list. PUT stores response header state (`update_status`, `ondisk_version`) for `send_response()`. The header itself does not persist metadata.

## Dependencies and Integration Points

The declarations depend on RGW REST and S3 auth headers. The implementation integrates with RADOS metadata managers and admin tools.

## Risks and Test Signals

The operation classes expose cap boundaries for powerful metadata mutation APIs. Tests should verify read/write cap separation, correct op type for PUT audit handling, and dispatch priority where `myself` takes precedence over `key`.
