# sources/distributed-fs/ipfs-kubo/core/shutdown/state.go

Purpose: tracks daemon-wide graceful shutdown state for health checks and diagnostics. Important APIs are `MarkStarted`, `StartedAt`, and `InProgress`.

Control flow: `MarkStarted` uses atomic compare-and-swap to record the first shutdown timestamp in Unix nanoseconds and returns whether the caller won. `StartedAt` converts the stored timestamp to `time.Time` or returns zero time. `InProgress` checks whether the timestamp is nonzero.

State and persistence: process-global atomic `startedAt`; no disk persistence.

Dependencies/integration: sync/atomic and time. Used by daemon signal handling and health checks such as Docker `ipfs diag healthy`.

Risks: global state is intentionally monotonic for a process and cannot be reset except in tests. Tests cover initial, repeated, timestamp preservation, and concurrent behavior.
