# sources/distributed-fs/ceph/src/osd/ECBackendL.cc

## Purpose

Implements the legacy erasure-coded PG backend (`ECLegacy::ECBackendL`) that adapts `ECCommonL` to the classic `PGBackend`/`ECSwitch` objectstore environment. It owns legacy EC recovery orchestration, sub-read/sub-write message dispatch, RMW transaction submission, hash-info validation for non-overwrite EC pools, and backend-specific scrub/read helpers.

## Important APIs, Types, and Functions

Key local types are `ECRecoveryHandle`, `RecoveryMessages`, `SendPushReplies`, `RecoveryReadCompleter`, and `ECClassicalOp`. The central entry points are `ECBackendL::ECBackendL`, `open_recovery_op`, `run_recovery_op`, `recover_object`, `_handle_message`, `handle_sub_write`, `handle_sub_read`, `handle_sub_write_reply`, `handle_sub_read_reply`, `submit_transaction`, `objects_read_async`, and `be_deep_scrub`. `RecoveryBackend` methods implement the legacy recovery state machine using `PushOp` and `PushReplyOp`. `ECClassicalOp::generate_transactions()` delegates per-shard transaction generation to `ECTransactionL::generate_transactions()`.

## Control Flow and Data Flow

Construction wires `read_pipeline`, `rmw_pipeline`, and `recovery_backend` around the same erasure-code implementation and stripe layout. Incoming OSD messages enter `_handle_message()`, which switches on EC sub-write, EC sub-read, their replies, and PG push/push-reply messages. Sub-writes log non-primary operations, queue the shard transaction plus local log transaction, and reply through `SubWriteCommitted`; sub-reads read shard ranges from the local store, optionally perform fragmented subchunk reads, optionally fetch attrs, validate legacy hinfo digests when overwrites are disabled, and return `ECSubReadReply`.

Recovery batches objects in `ECRecoveryHandle`; `run_recovery_op()` moves them into `recovery_ops` and drives `continue_recovery_op()`. The legacy state machine reads a chunk of missing shard data, decodes into `returned_data`, pushes missing shard buffers and attrs, waits for push replies, and either loops or reports peer/global recovery completion. Client reads flow through `objects_read_async()`, which aligns requested logical ranges to stripe/chunk bounds, calls `objects_read_and_reconstruct()`, and slices decoded results back into caller buffers.

## State and Persistence Behavior

Persistent mutations are objectstore transactions: sub-writes queue shard transactions and local PG log transactions, recovery writes temporary or final shard objects, and completed recovery can rename temp objects into place. Runtime state includes `read_pipeline.tid_to_read_map`, `rmw_pipeline.tid_to_op_map` and intrusive queues inherited from `ECCommonL`, `recovery_backend.recovery_ops`, temp object sets managed through the listener/switcher, and unstable hinfo entries in `unstable_hashinfo_registry`. `on_change()` clears RMW, read, and recovery state on interval change; `check_recovery_sources()` cancels or reschedules reads whose source OSDs went down.

## Dependencies and Integration Points

This file depends on `ECCommonL`, `ECTransactionL`, `ECExtentCacheL`, `ECUtilL`, `ECMsgTypes`, `ECInject`, `ECSwitch`, `PrimaryLogPG`, `MOSDECSubOp*`, and `MOSDPGPush*`. It uses `PGBackend::Listener`/`ECListener` for PG metadata, missing sets, message sends, stats, log operations, recovery callbacks, temp object management, and transaction queueing. The objectstore surface is reached through `switcher->store`, `switcher->ch`, and `switcher->coll`.

## Risks and Edge Cases

Read retry logic must preserve `obj_to_source`, `source_to_obj`, and `want_to_read` consistency or recovery cancellation can drop the wrong object. Legacy hinfo handling is high risk: missing, undecodable, or size-mismatched hinfo causes EIO/failed pull, while sanitization must keep the internal hinfo attr from leaking to higher layers. The recovery code assumes the requested extent length and decoded shard buffer sizes match stripe math exactly. `handle_sub_read_reply()` has many iterator and in-place mutation paths, including error injection erases, so malformed replies or partial cancellation can expose assertion-only failures. Deep scrub intentionally degrades digest semantics for EC overwrites, so tests should distinguish unsupported digest behavior from corruption.

## Test Signals

Useful tests cover EC read success, redundant fast read, retry after one shard EIO, cancellation on map change, subchunk fragmented reads, attr fetch failure, legacy hinfo missing/bad digest/size mismatch, RMW commit ordering, backfill/asynchronous recovery temp object cleanup, recovery source loss after first read, snap recovery metadata, dummy roll-forward ops, and deep scrub digest/hash mismatch reporting.
