# sources/distributed-fs/ceph-client/tools/perf/util/rwsem.c

## Purpose

`sources/distributed-fs/ceph-client/tools/perf/util/rwsem.c` implements perf's read/write semaphore abstraction over `pthread_rwlock_t`, with an optional mutex-backed error-checking mode.

## Important APIs, Types, and Functions

Public functions are `init_rwsem`, `exit_rwsem`, `down_read`, `up_read`, `down_write`, and `up_write`.

## Control Flow

In normal mode, initialization and destruction call pthread rwlock init/destroy. Read and write acquisition call `pthread_rwlock_rdlock` and `pthread_rwlock_wrlock`; unlock calls `pthread_rwlock_unlock`. If global `perf_singlethreaded` is true, lock/unlock operations are no-ops returning success. In `RWS_ERRORCHECK` mode, all operations use the embedded perf mutex instead.

## State and Persistence Behavior

State is in-memory inside caller-owned `struct rw_semaphore`. There is no persistence. Locking state is process/thread runtime state.

## Dependencies and Integration Points

It depends on `util.h` for `perf_singlethreaded`, `rwsem.h`, pthread rwlocks, and optionally perf mutex helpers. It provides a Linux-kernel-like naming style for userspace perf code.

## Risks and Edge Cases

No-op behavior under `perf_singlethreaded` assumes no concurrent access. Error-check mode collapses reader/writer distinction into a mutex. Return values from pthread functions are propagated but many callers may not check them. Destroying a locked rwlock remains caller misuse.

## Test Signals

Tests should cover normal init/destroy, parallel readers, writer exclusion, `perf_singlethreaded` no-op behavior, error-check mode compile coverage, and error propagation from invalid lifecycle usage where practical.
