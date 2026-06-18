# `sources/distributed-fs/ceph/src/osd/scheduler/OpSchedulerItem.cc`

## Purpose

`OpSchedulerItem.cc` implements the `run()` methods for concrete scheduler queueable items declared in `OpSchedulerItem.h`. Each method is a small dispatch adapter from a queued work item to the correct `OSD` or `PG` method, with PG lock release where ownership conventions require it.

## Important APIs And Functions

- Client and peering dispatch: `PGOpItem::run()` and `PGPeeringItem::run()`.
- Snap trim and scrub dispatch: `PGSnapTrim::run()`, `PGScrub::run()`, scrub-reschedule/update/unblock/digest/replmap item runs, and replica scrub item runs.
- Replica scrub message dispatch: `PGScrubReplicaPushes`, `PGScrubScrubFinished`, `PGScrubGetNextChunk`, `PGScrubChunkIsBusy`, and `PGScrubChunkIsFree`.
- Recovery dispatch: `PGRecovery::run()`, `PGRecoveryContext::run()`, `PGDelete::run()`, and `PGRecoveryMsg::run()`.

## Control Flow And State Behavior

Most methods call a single target method and then `pg->unlock()`. `PGOpItem` passes the held `PGRef`, `OpRequestRef`, and thread-pool handle to `OSD::dequeue_op()`. `PGPeeringItem` sends a peering event to `OSD::dequeue_peering_evt()` and does not unlock in this method, implying the callee owns or manages that path's lock convention. Snap trim and scrub items call the corresponding `PG` methods with `epoch_queued` and sometimes `activation_index`, then unlock.

Recovery items also update latency counters. `PGRecovery::run()` increments `l_osd_recovery_queue_lat` based on `time_queued`, calls `OSD::do_recovery()` with reserved pushes and priority, then unlocks. `PGRecoveryContext::run()` increments `l_osd_recovery_context_queue_lat`, completes a captured context, then unlocks. `PGDelete::run()` calls `OSD::dequeue_delete()` and does not unlock locally, matching that callee's ownership convention.

`PGRecoveryMsg::run()` computes queue latency, switches on the message type, increments recovery-message latency counters, then dispatches the request through `OSD::dequeue_op()` and unlocks. The switch cases have no `break` statements, so a push message increments all subsequent counters, a push-reply increments all later counters, and so on. That fallthrough is a key behavior to verify against intended metrics semantics.

## Persistence Behavior

This file has no direct persistence logic. It mutates OSD/PG runtime state by invoking operations that may later write PG logs, object data, recovery metadata, or scrub state. The queued epochs (`epoch_queued`) guard against stale work in the target PG methods rather than being persisted here.

## Dependencies And Integration Points

It includes `OpSchedulerItem.h`, `OSD.h`, and `osd_tracer.h`. It is tightly integrated with `OSD`, `OSDShard`, `PG`, scrubber methods, peering events, recovery reservations, `ThreadPool::TPHandle`, OSD perf counters, and message type constants such as `MSG_OSD_PG_PUSH`, `MSG_OSD_PG_PULL`, and `MSG_OSD_PG_SCAN`.

## Risks And Edge Cases

- Lock ownership is subtle. Most run methods unlock the PG, but peering and delete paths do not; changing target methods requires rechecking lock contracts.
- The missing `break` statements in `PGRecoveryMsg::run()` may be intentional cumulative accounting or a counter bug. Tests should lock down expected counter increments.
- `PGRecoveryContext::run()` calls `c.release()->complete(handle)`; ownership must be valid and non-null when queued.
- Many scrub methods ignore `osd` or `sdata`, which is fine for method signature uniformity but can hide stale queue context issues.
- Work may be queued for an old epoch; each PG method must validate `epoch_queued`.

## Test Signals

Scheduler item tests can use fake OSD/PG objects to verify each run method calls the correct target and unlocks exactly when expected. Integration signals include OSD perf counters for recovery queue latency, scrub state-machine progress, absence of PG lock leaks/deadlocks, and recovery-message dispatch behavior. Counter tests should specifically cover the switch fallthrough behavior in `PGRecoveryMsg::run()`.
