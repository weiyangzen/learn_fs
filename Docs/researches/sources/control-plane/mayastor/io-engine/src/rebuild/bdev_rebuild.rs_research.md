# sources/control-plane/mayastor/io-engine/src/rebuild/bdev_rebuild.rs

## Purpose
This file implements the generic bdev-to-bdev rebuild job. It is the base data-copy engine used directly for arbitrary block-device rebuilds and indirectly by snapshot rebuilds.

## Important APIs, Types, And Functions
`BdevRebuildJob` wraps `RebuildJob` and dereferences to it. `BdevRebuildJobBuilder` accepts a range, options, notification callback, and optional `SegmentMap`. `build` creates a `RebuildDescriptor`, allocates a `RebuildTasks` pool, chooses `FullRebuild` or `PartialRebuild`, and returns a frontend job. `BdevRebuildJobBackend<R>` implements `RebuildBackend`.

## Control Flow
The builder opens and validates source/destination through `RebuildDescriptor::new`. Without a bitmap, the backend walks every segment in range. With a bitmap, the descriptor validates map range and `PartialRebuild` schedules only dirty segments. `schedule_task_by_id` takes the next block from the range walker, submits the segment copy to the task pool, and increments active task count.

## State, Persistence, And Dependencies
Runtime state is the descriptor, range walker, task pool, and callback. No durable state is stored. It depends on `SegmentMap`, generic rebuild state/manager/task modules, and the `gen_rebuild_instances!` macro for global in-process job lookup.

## Integration Points
Consumers call `BdevRebuildJob::builder()` and then use inherited `RebuildJob` methods to start/stop/pause/resume/stats. Snapshot rebuild composes this builder. The notification function lets upper layers react to state changes with source/destination URI context.

## Risks
`PartialRebuild::is_partial` currently returns false, so stats for that path may mislabel partial work. Task scheduling mutates `active` outside the task pool method, which requires backend implementations to stay disciplined. Rebuild instances are keyed by destination URI and must run on an SPDK thread.

## Test Signals
Test full and bitmap rebuilds, invalid map range, same source/destination rejection, callback invocation on state changes, job instance store/lookup/remove behavior, and stats for partial-vs-full rebuilds.
