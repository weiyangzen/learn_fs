# sources/distributed-fs/ceph/src/rgw/rgw_aio_throttle.h

## Purpose
Declares RGW AIO throttle implementations and the `make_throttle()` factory that selects blocking or coroutine-yielding behavior.

## Important APIs, Types, and Functions
- `Throttle` stores the common window, pending size, pending/completed lists, and waiter state.
- `BlockingAioThrottle` is for synchronous/threaded contexts.
- `YieldingAioThrottle` is for coroutine strand contexts.
- `make_throttle(window_size, optional_yield)` selects `YieldingAioThrottle` when a yield context exists.

## Control Flow
The header documents the call-context constraints and declares the `Aio` overrides. The factory makes async mode transparent to callers.

## State and Persistence
No durable state. Runtime state is owned by throttle instances and must be empty at destruction.

## Dependencies and Integration Points
Includes Ceph mutex, async completion, yield context, and the abstract AIO interface. Used by RGW data paths that submit bounded concurrent RADOS/cache operations.

## Risks and Edge Cases
Choosing the wrong throttle for the execution model can deadlock or race. `window` units are caller-defined, so callers must pass costs consistently.

## Test Signals
Construction tests should verify factory selection, interface substitutability, and lifecycle requirements for both concrete throttles.
