# sources/distributed-fs/ceph/src/rgw/rgw_aio.h

## Purpose
Defines RGW's abstract asynchronous IO interface, result types, intrusive owning result list, error helper, and factory functions for librados/D3N operation callbacks.

## Important APIs, Types, and Functions
- `AioResult` carries object id, request id, read data, result code, and aligned internal user data.
- `AioResultEntry` enables intrusive list ownership.
- `AioResultList` is an owning intrusive list that disposes entries on destruction.
- `Aio` declares `get`, `put`, `poll`, `wait`, and `drain`.
- `check_for_errors()` returns the first negative completion result.

## Control Flow
The interface contract is that callers submit with `get()` and receive completions from previous operations, while async callbacks return entries via `put()`. `poll()`, `wait()`, and `drain()` expose nonblocking, next-completion, and all-completion retrieval.

## State and Persistence
State is per-request runtime state. Durable effects depend on operation callbacks supplied by callers.

## Dependencies and Integration Points
Uses librados forward declarations, RGW raw object types, Ceph yield contexts, Boost intrusive lists, and function2 move-only callbacks. Implemented by throttle classes in `rgw_aio_throttle.*`.

## Risks and Edge Cases
`AioResult` is noncopyable/nonmovable because entries are intrusive and may contain placement state. Callers must drain before destroying implementations. `cost` semantics are implementation-specific and can reject oversized operations.

## Test Signals
Interface-level tests should verify result ownership, disposal on list destruction, first-error detection, id/object association, and correct behavior of concrete throttles.
