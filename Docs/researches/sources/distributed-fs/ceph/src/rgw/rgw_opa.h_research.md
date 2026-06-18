# sources/distributed-fs/ceph/src/rgw/rgw_opa.h

## Purpose
`rgw_opa.h` declares the OPA authorization hook used by RGW request processing.

## Important APIs, Types, And Functions
It includes `rgw_common.h` and `rgw_op.h`, then declares `int rgw_opa_authorize(RGWOp*& op, req_state* s)`. Passing `RGWOp*&` lets the implementation log through the active operation and preserve the calling signature used in request processing.

## Control Flow
There is no control flow in the header. The declaration is consumed by `rgw_process.cc`, which conditionally calls it when `rgw_use_opa_authz` is true.

## State And Persistence
No state is stored here. All state is request-local in `req_state` or config-driven in the implementation.

## Dependencies And Integration Points
This header is the integration point between the request pipeline and `rgw_opa.cc`. Its dependency on `rgw_op.h` means consumers need the full `RGWOp` type rather than a lightweight forward declaration.

## Risks And Test Signals
The main risk is include coupling: any broad changes in `rgw_op.h` can increase compile impact for OPA consumers. Test signals are compile/link coverage with OPA enabled and request-processing tests with `rgw_use_opa_authz`.
