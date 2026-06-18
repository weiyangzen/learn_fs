# sources/distributed-fs/ceph/src/rgw/driver/rados/shard_io.h

## Purpose
Provides reusable Boost.Asio coroutine algorithms for concurrent operations across sharded RADOS objects. It supports normal writes, revertible writes with rollback on error/cancellation, and reads that abort outstanding requests on first error.

## Important APIs, types, and functions
- `Result { Success, Retry, Error }` classifies each shard completion.
- Abstract interfaces `RevertibleWriter`, `Writer`, and `Reader` define async operation initiation and completion classification.
- `async_writes(RevertibleWriter&)` applies writes with bounded concurrency and reverts completed writes if a failure or cancellation occurs.
- `async_writes(Writer&)` applies writes with bounded concurrency, retry support, and best-effort completion of other shards after errors.
- `async_reads(Reader&)` issues bounded concurrent reads and terminal-cancels outstanding operations after an error.
- RADOS adapters `RadosRevertibleWriter`, `RadosWriter`, and `RadosReader` convert `prepare_*()` methods into `librados::async_operate()` calls.
- Internal handlers manage intrusive shard lists, cancellation slots, waiter wakeups, and retry/revert scheduling.

## Control flow
Each algorithm converts the input map of shard id to object name into stable `Shard` records and maintains `sending`, `outstanding`, and sometimes `completed` lists. It sends work until `max_concurrent` is reached, awaits a wakeup, then reacts to completions. `on_complete()` returning `Retry` pushes the shard back to `sending`; `Error` records the first failure. Revertible writes move completed shards into a revert send list after failure and switch cancellation handling so only terminal cancellation stops reverts.

## State and persistence behavior
This header does not define a concrete persistent schema, but it executes RADOS object operations prepared by subclasses. Revertible writers are expected to provide inverse operations that restore pre-write state. Cancellation signals are per-shard and forwarded to underlying async RADOS operations through associated cancellation slots.

## Dependencies and integration points
Depends on Boost.Asio composed operations/cancellation/deferred tokens, Boost.Intrusive lists, `librados_asio`, Ceph logging, and RADOS operation types. Consumers subclass the abstract interfaces to implement cls or object operations for sharded RGW metadata/data structures.

## Risks and edge cases
`max_concurrent` must be nonzero; zero would cause the coroutine to wait without outstanding operations. Retry classification can loop forever if callers return `Retry` without backoff or attempt limits. Revert failures are logged but the original failure is returned. The algorithms assume the input map outlives operation initiation because shards hold iterators into it through the composed operation call. Reentrant cancellation handling is carefully staged; changes here are high risk.

## Test signals
Unit tests should use fake Writer/Reader implementations to verify bounded concurrency, retry scheduling, first-error behavior, cancellation propagation, revert ordering, terminal cancellation during revert, empty input, `max_concurrent` limits, and RADOS adapter invocation of `prepare_*()`.
