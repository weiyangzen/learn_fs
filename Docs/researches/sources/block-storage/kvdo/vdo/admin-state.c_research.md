# File Research: sources/block-storage/kvdo/vdo/admin-state.c

## Purpose

Implements the administrative state machine used by VDO components to serialize and validate load, drain, suspend, resume, save, stop, recovery, rebuild, and generic operation transitions.

## Main Responsibilities

- Defines all exported `struct admin_state_code` instances.
- Tags each state code with semantic flags:
  - `normal`,
  - `draining`,
  - `loading`,
  - `quiescing`,
  - `quiescent`,
  - `operating`.
- Computes valid next states for requested operations.
- Starts operations with optional waiters and initiator callbacks.
- Finishes operations and notifies waiters.
- Provides typed start/finish helpers for:
  - draining,
  - loading,
  - resuming,
  - generic operations.
- Provides validation helpers for operation categories.

## State Model

States are represented as pointers to immutable state-code objects, not as a numeric enum. This lets callers compare identity for exact states while also querying categories through flags.

Examples:
- `VDO_ADMIN_STATE_NORMAL_OPERATION`: normal.
- `VDO_ADMIN_STATE_OPERATING`: normal and operating.
- `VDO_ADMIN_STATE_SAVING`: draining, quiescing, operating.
- `VDO_ADMIN_STATE_SAVED`: quiescent.
- `VDO_ADMIN_STATE_LOADING`: normal, operating, loading.
- `VDO_ADMIN_STATE_RECOVERING`: draining and operating.
- `VDO_ADMIN_STATE_SUSPENDED_OPERATION`: operating, with next state preserving suspended/saved state.

## Important Functions

- `get_next_state()` validates whether an operation can start from the current state and returns the state to install after completion.
- `begin_operation()` is the core transition routine.
- `vdo_finish_operation()` records result, installs `next_state`, and completes waiter when appropriate.
- `vdo_start_draining()` starts a drain only from normal state, or completes immediately if already quiescent.
- `vdo_finish_draining_with_result()` finishes a draining state.
- `vdo_start_loading()` and `vdo_finish_loading_with_result()` handle loading states.
- `vdo_start_resuming()` and `vdo_finish_resuming_with_result()` handle resume operations.
- `vdo_resume_if_quiescent()` directly returns quiescent states to normal operation.
- `vdo_start_operation()` and `vdo_start_operation_with_waiter()` handle generic operating states.

## Behavior Details

`begin_operation()` rejects starts if:
- the requested operation has no valid next state from the current state,
- another waiter is already registered,
- the current state is already operating.

If an initiator is provided, `begin_operation()` sets `starting = true`, calls the initiator, clears `starting`, then handles synchronous completion if the operation finished during initiator execution. This avoids completing the waiter while the initiator call stack is still active.

`vdo_finish_operation()` preserves operation result in the waiter before completing it. If called while `starting` is true, it records completion and defers final transition until initiator return.

## Dependencies and Interactions

- Used by `action-manager.c`, `block-map.c`, `block-allocator.c`, and other VDO subsystems.
- Uses `completion.c` to notify operation waiters.
- Uses VDO status codes for busy and invalid-state failures.

## Notable Edge Cases

- A drain request on an already quiescent state completes its waiter and returns false.
- Suspended operations preserve the current quiescent state as their next state.
- `VDO_ADMIN_STATE_PRE_LOADING` only starts from initialized and ends in pre-loaded.
- Exact-state helpers in the header coexist with category-based validation here.
