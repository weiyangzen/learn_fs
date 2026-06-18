# sources/distributed-fs/ceph/src/rgw/rgw_aio_throttle.cc

## Purpose
Implements blocking and yielding AIO throttles that limit outstanding operation cost and collect completions for RGW async IO.

## Important APIs, Types, and Functions
- `Throttle::waiter_ready()` interprets the active wait condition.
- `BlockingAioThrottle::{get,put,poll,wait,drain}` use a mutex and condition variable.
- `YieldingAioThrottle::{get,put,poll,wait,drain}` use coroutine completions instead of blocking.
- `YieldingAioThrottle::async_wait()` creates an async completion tied to the yield executor.

## Control Flow
`get()` allocates a pending entry, rejects costs larger than the window with `-EDEADLK`, otherwise increments `pending_size`, waits for availability if needed, queues the pending entry, and invokes the submitted operation. `put()` moves entries from pending to completed, decrements cost, and wakes the waiting thread/coroutine if its condition is met. `wait()` waits for at least one completion; `drain()` waits for no pending entries.

## State and Persistence
Only runtime lists and counters are kept. No durable state is persisted. Completed result lists transfer ownership to callers by moving the intrusive owning list.

## Dependencies and Integration Points
Implements the `Aio` interface from `rgw_aio.h`. Blocking mode uses Ceph mutex/condition_variable; yielding mode uses Boost.Asio yield contexts and Ceph async completions.

## Risks and Edge Cases
All public functions must be called from one thread for blocking or one coroutine strand for yielding. The yielding `get()` sets `waiter=Available` before `async_wait()` but relies on `put()` to reset it. Oversized costs become completed error entries rather than throwing. Destructors assert both pending and completed lists are empty, so callers must drain and consume results.

## Test Signals
Tests should cover window backpressure, oversized cost errors, poll/wait/drain semantics, concurrent callback wakeups, yielding wakeup on the correct executor, and destructor assertions after proper drain.
