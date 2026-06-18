# sources/distributed-fs/ceph/src/osd/ReplicatedBackend.h

## Purpose
`ReplicatedBackend.h` declares the replicated-pool implementation of `PGBackend`. It defines the public backend contract used by `PrimaryLogPG` plus the private state machines for replicated write commit tracking and recovery push/pull progress.

## Important APIs, Types, And Functions
`ReplicatedBackend` overrides recovery handle creation/execution, `recover_object()`, message dispatch, recovery-source validation, lifecycle cleanup, omap accessors, synchronous/local reads, EC capability stubs, deep scrub hooks, on-disk size calculation, and `submit_transaction()`. `RPGHandle` batches outgoing `PushOp` and `PullOp` vectors per target shard. `push_info_t` and `pull_info_t` track `ObjectRecoveryInfo`, `ObjectRecoveryProgress`, object contexts, stats, lock managers, source peers, and cache hints. `InProgressOp` tracks a replicated client mutation by tid, waiting shards, commit callback, original op, and version.

Private helpers declared here cover message-specific handlers, recovery chunk building, pushed-data trimming, temp recovery writes, clone subset calculations, `MOSDRepOp` generation, commit processing, and PCT timer behavior. `pct_callback_t` adapts the PG lock/ref protocol to `common::intrusive_timer`.

## Control Flow
The public `_handle_message()` override dispatches OSD PG messages into private handlers. `submit_transaction()` starts the replicated write path and `op_commit()`/`do_repop_reply()` close it after local and peer commits. `recover_object()` chooses pull or push based on local missing state, then `run_recovery_op()` emits accumulated network messages. The header also documents that replicated reads are synchronous/local and that `call_write_ordered()` can invoke callbacks inline because replicated submission is ordered in `submit_transaction()`.

## State And Persistence Behavior
The header’s state declarations show which data survives only in memory: `pushing`, `pulling`, `pull_from_peer`, `in_progress_ops`, and `pct_callback`. Durable state is not stored directly by the backend object; it is written through `ObjectStore::Transaction` and parent PG log operations implemented in the `.cc` file. Recovery locks in `push_info_t`/`pull_info_t` must be released on completion or reset.

## Dependencies And Integration Points
The class integrates with `PGBackend`, `ObjectStore`, `ObjectContext`, missing/recovery types, scrub types, `MapCacher`-independent omap calls, Ceph messenger messages, and parent listener callbacks. It assumes replicated-pool semantics: availability for recovery requires any copy, readability requires the local shard, and EC encode/decode APIs are invalid.

## Risks And Test Signals
Header-level risks are ownership and lifecycle contracts: every map entry needs cleanup on `on_change()`/`clear_recovery_state()`, callbacks need PG locking, and EC stubs must never be reached for replicated pools. Tests should exercise message dispatch, recovery cancellation, state dump output, commit callback release, and compile-time/interface conformance against `PGBackend`.
