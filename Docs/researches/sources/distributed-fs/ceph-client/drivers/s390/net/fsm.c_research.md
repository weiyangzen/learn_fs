# sources/distributed-fs/ceph-client/drivers/s390/net/fsm.c

## Purpose
`fsm.c` implements a generic table-driven finite state machine helper used by the CTCM driver and exported to other modules. It allocates FSM instances, builds jump matrices from `fsm_node` templates, dispatches events, stores atomic state, and provides timer helpers that translate Linux timer expiry into FSM events.

## Important APIs, Types, And Functions
- `init_fsm()` allocates `fsm_instance`, `fsm`, and a `nr_states * nr_events` jump matrix, validates template entries, and installs action functions.
- `kfree_fsm()` frees the jump matrix, FSM descriptor, and instance.
- `fsm_getstate_str()` returns the current state name or `"Invalid"`.
- `fsm_settimer()` initializes an `fsm_timer` with `timer_setup()`.
- `fsm_deltimer()` deletes a timer.
- `fsm_addtimer()` and `fsm_modtimer()` arm or rearm timers and store the event/argument to dispatch on expiry.
- Under `FSM_DEBUG_HISTORY`, `fsm_print_history()` and `fsm_record_history()` maintain a circular event/state history.
- Exports all public helpers with `EXPORT_SYMBOL`.

## Control Flow
`init_fsm()` is called by CTCM channel, device, and MPC group initialization. It converts a sparse list of `(state,event,function)` entries into a direct-indexed matrix indexed as `nr_states * event + state`. Runtime event dispatch mostly happens through the inline `fsm_event()` in `fsm.h`, but the action functions and table backing are provided here. Timer expiry runs `fsm_expire_timer()`, obtains the enclosing `fsm_timer`, and calls `fsm_event()` with the stored event and argument.

## State And Persistence Behavior
FSM state is stored in `fsm_instance.state` as an `atomic_t`; state names, event names, and jump matrices are allocated per instance. Timers store only the target FSM, event, and argument. All state is in-memory and freed by `kfree_fsm()`. There is no persistent storage.

## Dependencies And Integration Points
The implementation depends on Linux allocation, timers, exports, and module metadata. It relies on `fsm.h` for types and inline dispatch. CTCM integrates by embedding `fsm_instance *` pointers and `fsm_timer` objects in driver structures.

## Risks
- `fsm_addtimer()` does not reject already-active timers despite the header comment claiming `-1` is possible; callers must delete or avoid duplicate adds themselves.
- `timer_delete()` is used rather than a synchronous delete, so callers freeing structures must ensure no timer callback can still race.
- The jump matrix is per-instance rather than shared per template, which is simple but increases allocation pressure.
- Invalid template entries free partial allocations through `kfree_fsm()`; future changes must preserve `this->f` assignment ordering.

## Test Signals
- Unit-style tests should initialize small FSMs, dispatch valid and missing events, validate state names, and verify out-of-range template entries fail.
- Timer tests should verify expiry dispatches the expected event/argument and deletion prevents callback under expected synchronization.
- Driver tests should watch for timer-after-free warnings during device teardown.
