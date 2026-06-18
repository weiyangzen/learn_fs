# sources/distributed-fs/ceph/src/osd/ReplicatedBackend.cc

## Purpose
`ReplicatedBackend.cc` implements the `PGBackend` for replicated pools. It handles replicated client mutations, replica sub-ops and replies, recovery push/pull traffic, local object reads, deep scrub reads, and progress updates for `pg_committed_to`. Unlike erasure-coded backends, reads are direct object-store reads and EC hooks abort if called.

## Important APIs, Types, And Functions
The implementation defines context helpers for sending messages after transactions and scheduling recovery work. `generate_transaction()` lowers a `PGTransaction` into an `ObjectStore::Transaction`, preserving object initialization, deletion, rename, clone, truncate, attrs, omap, alloc hints, and buffer updates while collecting temp objects. Client write replication centers on `submit_transaction()`, `issue_op()`, `generate_subop()`, `do_repop()`, `repop_commit()`, `do_repop_reply()`, and `op_commit()`.

Recovery centers on `recover_object()`, `prepare_pull()`, `start_pushes()`, `prep_push_to_replica()`, `prep_push()`, `build_push_op()`, `handle_pull()`, `handle_pull_response()`, `handle_push()`, `handle_push_reply()`, `submit_push_data()`, and `submit_push_complete()`. Deep scrub uses `be_deep_scrub_read_data()` and `be_deep_scrub()` to compute data and omap digests while respecting configured stride/key limits. `send_pct_update()`, `maybe_kick_pct_update()`, and `cancel_pct_update()` manage delayed committed-to updates.

## Control Flow
For a primary write, `submit_transaction()` applies stat deltas, converts the PG transaction, registers an `InProgressOp`, sends `MOSDRepOp` messages to all acting recovery/backfill peers, logs the operation locally, queues the local transaction, and marks the operation applied. Replicas receive `MOSDRepOp` in `do_repop()`, decode shipped transactions/logs, update temp tracking and local PG log state, queue local transactions, and send an on-disk `MOSDRepOpReply` from `repop_commit()`. The primary removes peers from `waiting_for_commit` in `do_repop_reply()` and runs the final commit context when all commits arrive.

Recovery either pulls missing local objects from a peer or pushes local objects to missing peers. Pulls select an available source from missing-location state, compute copy/clone subsets, and send `MOSDPGPull`. Pushes are chunked by configured max cost/object limits and may use existing clone overlap on the receiver to reduce data transfer. Completion calls back to the parent PG with local, peer, or global recover notifications.

## State And Persistence Behavior
In-memory state includes `in_progress_ops`, `pushing`, `pulling`, `pull_from_peer`, and a scheduled PCT timer callback. Persistent writes are object-store transactions and PG log entries. Recovery writes may target temporary recovery objects until a complete object is atomically renamed into place. Omap and attrs are copied alongside data; zero extents are reconstructed from fiemap/copy subset state.

## Dependencies And Integration Points
The backend depends on `PGBackend::Listener` for PG locks, log updates, stats, recovery notifications, message sends, timers, temp-object tracking, and object-context locks. It uses Ceph message types `MOSDRepOp`, `MOSDRepOpReply`, `MOSDPGPush`, `MOSDPGPull`, `MOSDPGPushReply`, and `MOSDPGPCT`, plus `ObjectStore`, `PGTransaction`, scrub types, missing maps, and OSD feature flags.

## Risks And Test Signals
Risk is concentrated in commit quorum accounting, interval-change cleanup, mixed-version transaction encoding, clone-overlap calculations, temp-object rename/removal, recovery progress monotonicity, deep scrub digest compatibility, and failure paths that call `on_failed_pull()`. Test signals include replicated write/commit latency counters, recovery push/pull tests with snaps and sparse objects, deep scrub digest tests, PCT feature tests, object-store EIO injection, degraded/backfill repair tests, and interval reset tests.
