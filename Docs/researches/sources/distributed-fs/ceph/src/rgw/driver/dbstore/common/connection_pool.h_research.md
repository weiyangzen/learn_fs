<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/dbstore/common/connection_pool.h -->
# sources/distributed-fs/ceph/src/rgw/driver/dbstore/common/connection_pool.h

## Purpose
This header defines a small generic, thread-safe database connection pool for RGW DBStore backends. It limits the number of open database connections, creates connections on demand through a factory, blocks when the pool is exhausted, and returns borrowed connections automatically through RAII handles.

## Important APIs, Types, And Functions
- `ConnectionPoolBase<Connection>` owns the synchronization primitives and `boost::circular_buffer<std::unique_ptr<Connection>>` of idle connections. Its private `put()` returns a connection to the pool and wakes one waiter when transitioning from empty to non-empty.
- `ConnectionHandle<Connection>` is a move-only RAII wrapper around a borrowed `std::unique_ptr<Connection>`. Its destructor and move assignment return the currently held connection to the original pool.
- `factory_of<F, T>` is a C++20 concept requiring `factory(dpp)` to return `std::unique_ptr<T>` and the factory to be move constructible.
- `ConnectionPool<Connection, Factory>` combines a factory and maximum capacity. `get(dpp)` borrows an idle connection, creates a new one while under capacity, or waits on a condition variable until another handle returns a connection.

## Control Flow
Callers construct `ConnectionPool` with a factory and a maximum connection count. On `get()`:
1. The pool mutex is locked.
2. If an idle connection exists, it is popped from the circular buffer.
3. Else if `total < capacity`, a new connection is created by the factory and `total` is incremented.
4. Else the caller waits on `cond` until a returned connection is available, logs wait/done messages, and pops the returned connection.
5. A `ConnectionHandle` is returned. When destroyed or overwritten by move assignment, the handle calls `pool->put()` to make the connection reusable.

## State And Persistence
The pool keeps only process-local state: idle connection objects, a count of total created connections, a mutex, and a condition variable. It does not persist connection state itself. Failed or poisoned connections are not distinguishable from healthy connections in the current API, so every returned connection is reused.

## Dependencies And Integration Points
The header depends on C++20 concepts, mutex/condition variable primitives, `std::unique_ptr`, `boost::circular_buffer`, and Ceph logging through `common/dout.h`. It is intended for DBStore backend implementations such as SQLite connection pools that can provide a factory returning database connection objects.

## Risks And Edge Cases
- The factory is called while holding the pool mutex. Slow connection creation blocks unrelated borrowers and returners.
- `total` is incremented even if `factory(dpp)` returns `nullptr`; this can permanently consume capacity with invalid handles.
- There is a TODO for reporting connection errors. A handle cannot tell the pool to discard a broken connection.
- `ConnectionHandle` move assignment returns its current connection, then copies `o.pool`, but it does not clear `o.pool`. This is acceptable because `o.conn` is moved away, yet the moved-from handle still carries a stale pool pointer.
- `ConnectionHandle` relies on `pool` being valid whenever `conn` is non-null. Destroying a pool before all handles is unsafe.
- `get()` has no timeout, cancellation, or `optional_yield` support; exhausted pools can block RGW request threads indefinitely.
- A zero-capacity pool will always enter the wait path and can never be signaled with a real connection.

## Test Signals
Tests should cover borrowing and automatic return, capacity enforcement, concurrent wait and wake behavior, move construction/assignment, zero or one capacity behavior, factory failure returning null, and destruction ordering. Stress tests should verify that the number of simultaneously created connections never exceeds capacity and that returned handles are reusable across threads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/dbstore/common/connection_pool.h -->
