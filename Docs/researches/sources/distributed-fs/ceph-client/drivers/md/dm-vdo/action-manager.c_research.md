# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/action-manager.c

## Purpose
`action-manager.c` implements a VDO helper that serializes administrative actions across a multi-zone object. Each action can run an initiator-thread preamble, an asynchronous per-zone callback on each zone thread, an initiator-thread conclusion, and then notify a parent completion. It allows one active action and one pending action.

## Important APIs, Types, And Functions
- `struct action` stores in-use state, associated admin operation, preamble, zone action, conclusion, parent completion, action context, and circular next pointer.
- `struct action_manager` stores the completion used to requeue work, `struct admin_state`, two action slots, current action pointer, zone count, default scheduler, zone-thread getter, initiator thread id, manager context, and current zone index.
- `vdo_make_action_manager()` allocates the manager, initializes the two-slot ring, sets normal admin state, and initializes a `VDO_ACTION_COMPLETION`.
- `vdo_schedule_operation_with_context()` is the main scheduler, filling the current or next slot or completing the parent with `VDO_COMPONENT_BUSY`.
- `launch_current_action()` starts the admin operation and invokes the preamble, arranging requeue to the first zone or conclusion.
- `apply_to_zone()` runs zone actions one zone at a time on zone-specific threads.
- `finish_action_callback()` clears the completed slot, optionally schedules default or pending work, runs conclusion, finishes admin state, and continues parent completion.

## Control Flow
Scheduling must happen on the configured initiator thread. If no action is active, the new action launches immediately; otherwise it fills the one pending slot. Launch calls `vdo_start_operation()` against the manager admin state. If the operation cannot start, the parent gets the error, conclusion is suppressed, and the action finishes. Otherwise the preamble is called. On successful preamble, the manager completion is requeued across zone threads through `apply_to_zone()`. After the last zone, the completion requeues back to the initiator thread and runs `finish_action_callback()`.

Errors are preserved through `preserve_error()`, which propagates completion result to the parent, resets the manager completion, and reruns it. Preamble errors skip zone actions and go directly to finish.

## State And Persistence Behavior
There is no disk persistence. Runtime state is the two-slot action queue and embedded admin state. `vdo_start_operation()`/`vdo_finish_operation()` prevent overlapping admin operations. The copied `struct action` in `finish_action_callback()` avoids use-after-free if the conclusion or parent continuation frees the manager.

## Dependencies And Integration Points
The manager depends on `admin-state`, `completion`, `status-codes`, `memory-alloc`, `permassert`, thread ids from `types.h`, and VDO completion scheduling. VDO subsystems such as block maps or slab depots can use it to apply operations to all zones while preserving per-zone thread affinity.

## Risks
- Only one pending action is supported; additional schedules fail with `VDO_COMPONENT_BUSY`.
- Scheduling from the wrong thread is asserted log-only, so production behavior depends on callers obeying the contract.
- Parent completions may run during error or finish paths; ownership/lifetime must account for callbacks freeing the manager or context.
- Default action scheduling is attempted only when current operation is normal and no pending action is in use.

## Test Signals
Test immediate action, queued pending action, third-action busy result, NULL preamble/action/conclusion defaults, preamble failure, operation-start failure, per-zone thread routing, zero/one/many zones if allowed by callers, parent completion result propagation, default scheduler launch, and manager-freeing conclusion callbacks.
