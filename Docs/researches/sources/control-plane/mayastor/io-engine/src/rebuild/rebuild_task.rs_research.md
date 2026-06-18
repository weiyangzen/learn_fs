# sources/control-plane/mayastor/io-engine/src/rebuild/rebuild_task.rs

## Purpose
This file implements the per-segment copy worker and task pool used by rebuild backends.

## Important APIs, Types, And Functions
`TaskResult` reports task id, block, optional error, and whether data was transferred. `RebuildTask` owns a DMA buffer, completion sender, and last error/result. `RebuildTask::copy_one` performs read, write, and optional verify for one segment. `RebuildTasks` preallocates task buffers, tracks active/total/done/transferred counts, schedules segment rebuild futures, and awaits completions. `RebuildTaskCopier` abstracts direct or wrapped segment copy implementations.

## Control Flow
`RebuildTasks::new` creates an unbuffered MPSC channel and one DMA buffer per task. `schedule_segment_rebuild` sends a future to the current reactor, locks the task, runs the copier, stores a `TaskResult`, and sends it back. `await_one_task` receives a result, decrements active count, and updates counters on success.

## State, Persistence, And Dependencies
State is in-memory task buffers and counters. Persistent impact is destination data written by the descriptor. Dependencies include `DmaBuf`, Mayastor reactors, futures MPSC, `parking_lot::Mutex`, `Arc`, `Rc`, `VerboseError`, and `SEGMENT_SIZE`.

## Integration Points
Bdev and nexus backends schedule work through this pool. `RebuildDescriptor` implements `RebuildTaskCopier` for the direct copy case; nexus and partial wrappers implement it for synchronized or bitmap-filtered copies.

## Risks
The async future holds a `parking_lot::MutexGuard` across await, explicitly allowed in code; this is safe only because each task is uniquely scheduled, but future changes could introduce deadlocks. Active count is managed by callers and `await_one_task`, so missed sends or channel termination can desynchronize manager state. Each task preallocates a large DMA buffer, so concurrency directly affects memory use.

## Test Signals
Tests should cover successful transfer, unwritten-source skip, read/write/verify errors, channel close behavior, counter updates, one-buffer-per-task allocation failures, and reactor scheduling assumptions.
