# Research: sources/distributed-fs/openafs/src/rx/rx_atomic.h

## sources/distributed-fs/openafs/src/rx/rx_atomic.h

### Purpose
`rx_atomic.h` provides RX's small integer atomic abstraction across Windows, AIX, Darwin, Linux kernel, Solaris, GCC builtins, and a mutex-protected fallback.

### Important APIs and Types
- Defines `RX_ATOMIC_INIT(i)` and `rx_atomic_t`.
- Exposes inline operations: `rx_atomic_set`, `rx_atomic_read`, `rx_atomic_inc`, `rx_atomic_inc_and_read`, `rx_atomic_add`, `rx_atomic_add_and_read`, `rx_atomic_dec`, `rx_atomic_dec_and_read`, and `rx_atomic_sub`.
- Uses platform primitives: Windows `Interlocked*`, AIX `fetch_and_add`, Darwin `OSAtomic*` or kernel compatibility wrappers, Linux kernel `atomic_t`, Solaris `atomic_*_32`, GCC `__sync_*`, or a process-wide `rx_atomic_mutex`.

### Control Flow and State
Most implementations are direct wrappers. The fallback implementation serializes all atomic variables with one global mutex when `RX_ENABLE_LOCKS` is available. No data is persisted; values live in the caller-owned `rx_atomic_t`.

### Dependencies and Integration Points
The header depends on platform feature macros and may include `rx_kmutex.h`, `rx_pthread.h`, or `rx_lwp.h` for fallback locking. It is used by RX statistics, wait counters, event reference counts, and other shared counters.

### Risks and Edge Cases
- The fallback mutex path has much broader contention and depends on `rx_atomic_mutex` being initialized before use.
- `rx_atomic_read` and `rx_atomic_set` are plain volatile accesses on several native paths, not full memory barriers.
- Solaris stores `volatile unsigned int` while the API returns `int`; negative values or overflow semantics need care.
- Darwin OSAtomic APIs are legacy/deprecated in modern user-space, but this source targets older OpenAFS portability.

### Test Signals
Run concurrency stress tests for event cancellation/refcounting and stats counters under pthread builds. Build matrix coverage is important because most behavior is preprocessor-selected. Fallback builds should verify `rx_atomic_mutex` initialization and absence of deadlocks.
