# sources/distributed-fs/ceph/src/rgw/rgw_request.h

## Purpose

Declares lightweight request holder types used by RGW request handling and load generation.

## Important APIs, Types, and Functions

`RGWRequest` stores an id, `req_state*`, and `RGWOp*`, with `init_state()` to attach request state. `RGWLoadGenRequest` extends it with method, resource, content length, and an atomic failure flag pointer.

## Control Flow and Data Flow

Request processing can allocate an `RGWRequest` with an id, later attach the frontend `req_state`, and associate an operation. Load-generation code can use the derived type to represent synthetic HTTP requests and signal failures through shared atomic state.

## State and Persistence Behavior

Only transient pointers and request metadata are held. The class does not own `req_state`, `RGWOp`, or the failure flag.

## Dependencies and Integration Points

Depends on RGW common state, ACL, RADOS user types, operation declarations, QueueRing, and atomics. Integrated with request scheduling/dispatch and load generator paths.

## Risks and Edge Cases

Raw pointers and null defaults require careful ownership and initialization. `RGWLoadGenRequest` stores content length as `int`, so very large synthetic requests may not be representable. The destructor is virtual but performs no cleanup of associated operation/state pointers.

## Test Signals

Cover request initialization, loadgen construction, queueing through request rings, cleanup ownership expectations, and failure flag propagation.
