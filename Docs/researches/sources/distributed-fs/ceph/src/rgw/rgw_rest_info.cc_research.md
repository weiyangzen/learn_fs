# sources/distributed-fs/ceph/src/rgw/rgw_rest_info.cc

## Purpose

`rgw_rest_info.cc` implements the admin REST info endpoint. It returns general RGW backend information, currently the accessible storage backend name and cluster id.

## Important APIs and Functions

`RGWOp_Info_Get` is a local `RGWRESTOp` requiring `info` read caps. `execute()` writes an `info.storage_backends` array with one object containing `driver->get_name()` and `driver->get_cluster_id()`. `RGWHandler_Info::op_get()` always returns this operation for GET requests.

## Control Flow

After admin authentication and cap verification, execution starts formatter output with the flusher, opens the expected object/array sections, emits backend data, closes sections, and flushes. There is no separate custom `send_response()`; normal RGW op handling finishes the response.

## State and Persistence Behavior

The endpoint is read-only. It queries driver identity and cluster id and does not mutate metadata or object state.

## Dependencies and Integration Points

It depends on `rgw_op.h`, `rgw_rest_info.h`, and SAL driver methods. It integrates with admin REST mounts through `RGWRESTMgr_Info` in the header and with capability checks through `caps.check_cap("info", RGW_CAP_READ)`.

## Risks and Test Signals

The response schema is intentionally extensible but currently has only one backend object. Tests should verify cap enforcement, valid cluster id output, JSON/XML formatter shape, and behavior when `driver->get_cluster_id()` returns an error-like or empty string.
