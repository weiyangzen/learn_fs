# sources/distributed-fs/orangefs/src/io/trove/trove-dbpf/dbpf-sync.c

## Purpose
Implements metadata sync coalescing for queued DBPF keyval and dspace operations. It can delay completion of `TROVE_SYNC` metadata mutations until a shared DB sync boundary so multiple operations are made durable together.

## Important APIs, Types, And Functions
Main functions are `dbpf_sync_context_init`, `dbpf_sync_context_destroy`, `dbpf_sync_coalesce`, `dbpf_sync_coalesce_enqueue`, `dbpf_sync_coalesce_dequeue`, `dbpf_queued_op_set_sync_high_watermark`, `dbpf_queued_op_set_sync_low_watermark`, and `dbpf_queued_op_set_sync_mode`. Internal `sync_array[COALESCE_CONTEXT_LAST][TROVE_MAX_CONTEXTS]` separates keyval and dspace contexts per TROVE context id.

## Control Flow
Queue enqueue/dequeue calls update sync/non-sync counters for sync-capable operation types. After a service function completes, `dbpf_sync_coalesce` immediately completes non-sync-capable operations and non-`TROVE_SYNC` operations. For sync-capable `TROVE_SYNC` operations, it selects keyval or dspace DB, checks collection metadata sync mode, and either completes immediately with periodic syncs disabled/enabled by watermarks or queues completed operations in the context sync queue. When low/high watermark criteria are met, it calls `dbpf_db_sync`, moves the current and queued ready ops to the completion queue, signals the completion condition, and resets coalesce counters.

## State And Persistence
State is in-memory counters and ready-to-complete queues per context/type. Persistent effect is explicit `dbpf_db_sync` on `coll_p->keyval_db` or `coll_p->ds_db`, making prior metadata mutations durable. Collection fields `c_low_watermark`, `c_high_watermark`, and `meta_sync_enabled` control behavior.

## Dependencies And Integration Points
Depends on DBPF queue primitives, thread completion macros, collection fields from `dbpf.h`, DB wrappers, PINT events, and operation type macros. It is invoked from enqueue/dequeue paths and from the worker loop after service completion.

## Risks And Test Signals
Risks include delayed completions that can starve below watermarks, counter imbalance if operations are removed through unusual paths, event-end inconsistency for dspace create pointer/value, mode changes while a sync queue is populated, and lock ordering around sync queues/completion queues. Tests should cover high/low watermark boundaries, metadata sync disabled mode, mixed sync/non-sync ops, keyval versus dspace separation, error from `dbpf_db_sync`, and per-context isolation.
