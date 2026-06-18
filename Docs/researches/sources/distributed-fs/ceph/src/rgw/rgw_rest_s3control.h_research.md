# sources/distributed-fs/ceph/src/rgw/rgw_rest_s3control.h

## Purpose
`rgw_rest_s3control.h` declares `RGWRESTMgr_S3Control`, the REST manager that serves S3Control resources under `/v20180820`.

## Important APIs, Types, and Functions
`RGWRESTMgr_S3Control` derives from `RGWRESTMgr`, grants `RGWRESTMgr_S3` friend access to protected resource-manager lookup, and exposes a constructor that registers nested S3Control resources in the `.cc` file.

## Control Flow
The manager is created by the S3 REST manager when S3Control is enabled. URI dispatch descends through its registered resources, currently `configuration/publicAccessBlock`, and then returns a resource-specific handler.

## State and Persistence Behavior
The header owns no persistent state. The manager's registration tree is in-memory process state. Durable account public-access configuration is handled by `rgw_rest_s3control.cc`.

## Dependencies and Integration Points
It depends only on `rgw_rest.h` for `RGWRESTMgr`. The integration point is `RGWRESTMgr_S3`, which can expose this manager as a nested resource under the S3 frontend.

## Risks
Because the class is small, most risk is in registration coverage. If the constructor is not updated when adding S3Control APIs, requests will not dispatch even if operation classes exist.

## Test Signals
Dispatch tests should confirm that S3Control-enabled frontends route `/v20180820/configuration/publicAccessBlock` to the correct handler and that disabled S3Control does not expose the route.
