# sources/distributed-fs/ceph/src/rgw/rgw_aio.cc

## Purpose
Implements wrappers that turn librados read/write operations and D3N cache reads into `Aio::OpFunc` callbacks consumable by RGW AIO throttles.

## Important APIs, Types, and Functions
- `Aio::librados_op()` overloads for `ObjectReadOperation` and `ObjectWriteOperation`.
- `Aio::d3n_cache_op()` wraps a D3N L1 cache async read.
- Internal `state` stores AIO completion state in `AioResult::user_data`.
- `cb()` transfers librados completion return values back to the owning throttle.

## Control Flow
For non-yield librados operations, the wrapper creates a librados completion with `AioResult` as callback arg, places state in `user_data`, submits `ctx.aio_operate()`, and either waits for `cb()` or immediately returns failed submissions to the throttle. For yield-based operations, it uses `librados::async_operate()` bound to the coroutine strand so the handler can call `Aio::put()` without locking. D3N cache operations assert a yield context and delegate to `D3nL1CacheRequest`.

## State and Persistence
No durable state is owned here. Runtime state includes completion objects, result buffers, tracing context pointers, and cache request objects. RADOS operations mutate or read persistent objects according to the caller-supplied operation.

## Dependencies and Integration Points
Depends on librados C++ and asio wrappers, D3N cache request/driver headers, RGW tracing, and `Aio` throttle implementations.

## Risks and Edge Cases
The placement-new state must fit in `AioResult::user_data`; the static assert guards this. If `aio_operate()` fails synchronously, cleanup must mirror callback cleanup. Yield operations depend on all public throttle calls occurring on the same strand. D3N cache reads require async/yield mode.

## Test Signals
Tests should cover synchronous submit failure, read/write completion result propagation, data buffer movement for reads, trace context pass-through for writes, yield and non-yield paths, and D3N yield assertion/put behavior.
