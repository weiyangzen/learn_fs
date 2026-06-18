# File Research: sources/block-storage/kvdo/vdo/action-manager.c

## Purpose

Implements `struct action_manager`, a generic asynchronous coordinator for applying an operation across multiple VDO zones while preserving single-operation semantics for a shared context.

## Main Responsibilities

- Allocates and initializes action managers with:
  - zone count,
  - zone-to-thread resolver,
  - initiator thread,
  - shared context,
  - optional default scheduler,
  - embedded `VDO_ACTION_COMPLETION`,
  - embedded admin state.
- Maintains exactly two action slots:
  - one current action,
  - one pending action.
- Rejects a third concurrent schedule request with `VDO_COMPONENT_BUSY`.
- Runs each action as:
  - preamble on initiator thread,
  - optional zone action on each zone thread in order,
  - conclusion back on initiator thread,
  - parent completion notification.
- Integrates with `admin-state.c` using operation state codes.
- Supports default follow-up work via a scheduler called after each action if no pending explicit action exists.

## Key Structures

- `struct action`
  - `in_use`,
  - admin operation code,
  - preamble callback,
  - per-zone action callback,
  - conclusion callback,
  - parent completion,
  - action-specific context,
  - next slot pointer.
- `struct action_manager`
  - reusable completion,
  - admin state,
  - two `struct action` slots,
  - current slot pointer,
  - zone/thread metadata,
  - default scheduler,
  - shared context,
  - current acting zone.

## Important Functions

- `vdo_make_action_manager()` allocates and initializes the manager and circular two-slot action list.
- `vdo_get_current_manager_operation()` returns the manager’s current admin operation code.
- `vdo_get_current_action_context()` returns the active action-specific context if any.
- `vdo_schedule_default_action()` asks the default scheduler to schedule work only during normal operation.
- `vdo_schedule_action()` schedules a generic `VDO_ADMIN_STATE_OPERATING` action.
- `vdo_schedule_operation()` schedules a named admin operation without extra context.
- `vdo_schedule_operation_with_context()` is the core scheduler and optional action-context entry point.

## Behavior Details

`launch_current_action()` first starts the admin operation with `vdo_start_operation()`. If state transition fails, it stores the error in the parent and skips preamble/conclusion work. Otherwise, it prepares the reusable completion for either zone traversal or direct conclusion.

Zone traversal is serialized through one completion. `apply_to_zone()` runs on the current zone’s thread, increments `acting_zone`, prepares the same completion for the next zone or conclusion, and invokes the zone callback.

`finish_action_callback()` copies the current action locally before running conclusion or parent notification, avoiding use-after-free if callbacks destroy the manager. It clears the slot, advances to the next slot, possibly schedules default work, finishes the admin operation, completes the parent, then launches pending/default work.

## Dependencies and Interactions

- Uses `admin-state.c` to enforce valid operation transitions.
- Uses `completion.c` for requeueing callbacks across VDO worker threads.
- Used by multi-zone systems such as the block map and slab depot/block allocator paths.

## Notable Edge Cases

- At least one of preamble, zone action, or conclusion is expected by contract; NULL preamble/conclusion are replaced by no-op implementations.
- Scheduling is asserted to happen on the initiator thread.
- Preamble errors skip zone actions but still route to conclusion/finish logic.
- Only one pending action is supported.
