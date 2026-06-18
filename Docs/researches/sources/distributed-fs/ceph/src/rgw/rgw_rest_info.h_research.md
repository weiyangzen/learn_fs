# sources/distributed-fs/ceph/src/rgw/rgw_rest_info.h

## Purpose

`rgw_rest_info.h` declares the authenticated admin REST info handler and manager.

## Important APIs and Types

`RGWHandler_Info` derives from `RGWHandler_Auth_S3`, dispatches GET requests, and skips extra permission loading. `RGWRESTMgr_Info` creates the handler for the info resource.

## Control Flow, State, and Integration

The manager produces a handler, S3 admin auth is applied, and the implementation returns an info GET operation. The endpoint is read-only and state access is delegated to the SAL driver.

## Risks and Test Signals

The header is small. Tests should ensure handler creation, GET dispatch, and authenticated cap enforcement remain wired when REST resources are registered.
