# sources/distributed-fs/ceph/src/osd/ECCommonL.h

## Purpose

Declares the legacy common EC abstractions in namespace `ECLegacy`. It is the type contract used by `ECBackendL` for older async reads, RMW write sequencing, extent cache pins, and hinfo lookup.

## Important APIs, Types, and Functions

Important declarations include `ECCommonL`, `ec_extent_t`, `read_request_t`, `read_result_t`, `ReadCompleter`, `ClientAsyncReadStatus`, `ReadOp`, `ReadPipeline`, `RMWPipeline`, `RMWPipeline::Op`, `RMWPipeline::pipeline_state_t`, and `UnstableHashInfoRegistry`. Virtual surface area includes `handle_sub_write()` and `objects_read_and_reconstruct()`. Header template methods implement `ReadPipeline::check_recovery_sources()` and `filter_read_op()`.

## Control Flow and Data Flow

`ReadPipeline` accepts object-to-logical-range maps plus wanted shard ids, computes/records per-source reads, tracks in-flight shards, and completes through a `ReadCompleter`. `RMWPipeline::Op` carries the PG transaction plan, remote read requirements/results, temp object sets, pending sub-op replies, callbacks, and a `ECExtentCacheL::write_pin`. The pipeline queues model ordered transitions from state gate to reads to commit. `UnstableHashInfoRegistry` provides shared refs for hash-info values that must live until corresponding transactions apply.

## State and Persistence Behavior

This header declares in-memory state: `tid_to_read_map`, `shard_to_read_map`, `in_progress_client_reads`, `ECExtentCacheL cache`, `tid_to_op_map`, intrusive wait queues, `completed_to`, `committed_to`, and `pipeline_state`. Persistent behavior is produced only by concrete `generate_transactions()` implementations and the backend's sub-write handlers.

## Dependencies and Integration Points

Dependencies include Boost intrusive containers, `sharedptr_registry`, `ErasureCodeInterface`, `ECUtilL`, `ECTypes`, optional Crimson object context and transaction headers, `ECTransactionL`, `ECExtentCacheL`, `ECListener`, and `fmt` stream formatters. It integrates tightly with `ECBackendL.cc`, which supplies concrete transaction generation and message handlers.

## Risks and Edge Cases

The intrusive queues require `Op` objects to outlive their list membership; `tid_to_op_map` owns them, so erasing the map at the wrong time can invalidate queue entries. `filter_read_op()` erases source/object mappings while iterating and cancels pulls through callbacks. `pipeline_state_t` gates cache validity globally for the pipeline, so one invalidating operation can block later RMW reads. `Op` destructor deletes `on_all_commit`, making callback ownership transfer explicit and potentially fragile.

## Test Signals

Compile legacy users, instantiate move-only `ReadOp`, exercise template cancellation with down OSD maps, check pipeline state transitions and formatting, verify hinfo registry ref sharing, and run sanitizer tests around intrusive queue cleanup on normal finish and `on_change()`.
