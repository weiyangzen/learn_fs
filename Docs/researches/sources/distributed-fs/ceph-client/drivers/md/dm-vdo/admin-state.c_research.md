# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/admin-state.c

## Purpose
`admin-state.c` implements VDO administrative state transitions. It defines the canonical state-code objects, validates whether operations can begin from the current state, tracks waiters, supports loading/draining/resuming operation families, and completes transitions to next states.

## Important APIs, Types, And Functions
- Static `VDO_CODE_*` objects define state names and flags such as `normal`, `draining`, `loading`, `quiescing`, `quiescent`, and `operating`.
- Exported pointers such as `VDO_ADMIN_STATE_NORMAL_OPERATION`, `VDO_ADMIN_STATE_SAVING`, `VDO_ADMIN_STATE_SUSPENDING`, and `VDO_ADMIN_STATE_RESUMING` identify states by pointer identity.
- `get_next_state()` encodes allowed transitions and final states for operations.
- `begin_operation()` validates state, waiter absence, sets `waiter`, `next_state`, current operation, and optionally calls an initiator.
- `vdo_finish_operation()` completes an operating state, updates final state when initiation has unwound, sets waiter result, and launches waiter completion.
- Specialized wrappers include `vdo_start_loading()`, `vdo_finish_loading_with_result()`, `vdo_start_draining()`, `vdo_finish_draining_with_result()`, `vdo_start_resuming()`, and `vdo_finish_resuming_with_result()`.
- `vdo_resume_if_quiescent()` moves quiescent states back to normal operation.

## Control Flow
Start functions first validate the requested operation class. Generic operations require `operation->operating`; loading requires `operation->loading`; draining requires `operation->draining`; resuming requires the exact resume state. `begin_operation()` rejects starts if the current code is already operating, the operation is invalid from the current state, or another waiter exists. If accepted, it installs the waiter and next state, switches current state to the operation, and invokes an optional initiator with `starting=true`.

If an initiator completes synchronously, `vdo_finish_operation()` may be deferred until `starting` is false by using the `complete` flag. Normal finish sets waiter result, changes to `next_state`, forgets and launches the waiter completion. Draining short-circuits if already quiescent by launching the waiter without starting a new operation.

## State And Persistence Behavior
State is in-memory only in `struct admin_state`. The code uses pointer-valued state codes and `READ_ONCE`/`WRITE_ONCE` accessors from the header. A single `waiter` serializes administrative operations. `next_state`, `starting`, and `complete` handle synchronous and asynchronous operation completion without double finishing.

## Dependencies And Integration Points
The file depends on VDO logging, memory helpers, assertions, completions, status codes, and type definitions. `action-manager.c` uses `vdo_start_operation()` and `vdo_finish_operation()` to serialize zone actions. Broader VDO lifecycle code uses the loading, draining, saving, stopping, suspending, and resuming wrappers.

## Risks
- State identity relies on exported pointer constants; callers must not fabricate equivalent structs.
- `get_next_state()` is the central policy table; missing a transition produces `VDO_INVALID_ADMIN_STATE`.
- A stale waiter blocks all new operations with `VDO_COMPONENT_BUSY`.
- Quiescent drain calls launch the waiter and return false, which callers must not misinterpret as an error path requiring another completion.
- Incorrect initiator behavior can stress the `starting`/`complete` handshake.

## Test Signals
Test allowed and rejected transitions from every state, concurrent waiter rejection, synchronous initiator finish, asynchronous finish, invalid operation-class checks, quiescent drain shortcut, resume from quiescent states, result propagation to waiters, and pointer identity assumptions for state comparisons.
