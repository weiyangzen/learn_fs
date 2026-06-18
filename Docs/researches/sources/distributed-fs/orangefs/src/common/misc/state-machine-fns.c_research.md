# sources/distributed-fs/orangefs/src/common/misc/state-machine-fns.c

## Purpose

`state-machine-fns.c` implements the generic OrangeFS state-machine executor declared by `state-machine.h`. It drives current state invocation, transition-table lookup, nested-machine stack handling, parallel child state-machine starts, frame stack management, cancellation/termination flags, and allocation/freeing of `PINT_smcb` control blocks.

## Important APIs and functions

- `PINT_state_machine_halt()` is a stub that returns 0 for shutdown compatibility.
- `PINT_state_machine_terminate(smcb, r)` notifies a parent SMCB when a child finishes, copies the child frame error into the matching parent frame, decrements `children_running`, posts a `job_null()` to resume the parent when the last child exits, and calls the SMCB termination callback.
- `PINT_state_machine_invoke(smcb, r)` validates that the current state is runnable, logs entry/exit, calls the state's action function, interprets `SM_ACTION_*`, marks `op_terminate` on terminate, and starts PJMP child frames after a complete parallel-jump state.
- `PINT_state_machine_start(smcb, r)` marks the operation initially immediate, sets the base frame, invokes the first state, and continues while states complete synchronously.
- `PINT_state_machine_next(smcb, r)` uses the current state's transition table and `r->error_code` to choose the next state, handles `SM_TERM`, `SM_RETURN`, nested `SM_JUMP`, cancellation, and loops while invoked states complete.
- `PINT_state_machine_continue(smcb, r)` advances the machine and calls termination cleanup when the next step returns terminate.
- `PINT_state_machine_locate(smcb)` resolves `smcb->op` through the caller-provided `op_get_state_machine` callback, follows initial nested jumps, and sets `current_state`.
- `PINT_smcb_alloc()` allocates and initializes a control block, optionally allocates an initial zeroed frame, stores operation lookup and terminate callbacks, and locates the initial machine.
- `PINT_smcb_free()` frees all frame entries and only frees frame payloads whose `task_id` is zero; nonzero child/task frames are treated as externally owned.
- `PINT_sm_frame()`, `PINT_sm_push_frame()`, and `PINT_sm_pop_frame()` implement indexed access to a qlist-backed frame stack.
- `PINT_smcb_set_op()`, `PINT_smcb_op()`, `PINT_smcb_set_complete()`, `PINT_smcb_complete()`, `PINT_smcb_set_cancelled()`, `PINT_smcb_cancelled()`, `PINT_smcb_immediate_completion()`, and `PINT_smcb_invalid_op()` expose control flags and op validation.

## Control flow

A caller allocates an SMCB with `PINT_smcb_alloc()` and a machine resolver. `PINT_state_machine_locate()` stores the first runnable state, pushing return states for leading nested jumps. `PINT_state_machine_start()` invokes the first action and then uses `PINT_state_machine_continue()` to process synchronous completions. Each state action writes a result into `job_status_s`, especially `error_code`, and returns `SM_ACTION_DEFERRED`, `SM_ACTION_COMPLETE`, or `SM_ACTION_TERMINATE`.

When a state completes, `PINT_state_machine_next()` searches the transition table for an entry matching `r->error_code`, defaulting to the entry whose `return_value` is `DEFAULT_ERROR`. `SM_RETURN` pops the nested state stack and continues from the saved parent state. `SM_JUMP` pushes the current state and enters a nested machine's first state. `SM_TERM` or `op_terminate` ends the machine. Deferred states stop execution until an external job completion calls continue again.

Parallel jump states (`SM_PJMP`) run their action first. If complete, `PINT_sm_start_child_frames()` counts frames above the current frame, creates child SMCBs for each, maps task ids through the state's PJMP table, starts children, and returns deferred if any children were launched. Child termination updates the parent and schedules a null job to resume the parent after the last child.

## State and persistence behavior

All state is in memory. `PINT_smcb` tracks the current state, nested state stack, frame qlist, base frame index, operation id and flags, parent-child relationships, running child count, job context, termination callback, user pointer, and immediate-completion flag. There is no persistent storage.

Frame ownership is task-id dependent: task id zero frames are freed by `PINT_smcb_free()`, while nonzero task frames are not. Child SMCBs push references to existing frame payloads, so parent and child lifetimes must be coordinated by the state-machine protocol.

## Dependencies and integration points

This file depends on qlist, gossip debug logging, PVFS op constants, job null scheduling, `job_status_s`, and client/server state-machine definitions. It is a common executor reused by client and server generated state tables. The user-provided `PINT_state_machine_complete()` is declared in the header, while termination behavior is supplied per SMCB through a callback.

## Risks and edge cases

- Transition table lookup assumes every table eventually has a `DEFAULT_ERROR` sentinel; a malformed table can walk off the end.
- Nested state depth is limited by `PINT_STATE_STACK_SIZE` and overflow is guarded only by `assert()`.
- `PINT_sm_pop_frame()` unconditionally writes `*task_id` and `*error_code`, so callers must pass non-null pointers.
- PJMP child start logs errors when child start returns negative but does not undo already-started children or decrement `children_running` for that failure path.
- Parent frame error propagation matches child current frame pointer against parent frame payload pointers. Duplicate frame pointers or unexpected frame ownership could propagate errors to the wrong entry.
- The executor is not internally synchronized. Callers must serialize access to each SMCB from the job/event system.

## Test signals

Focused tests should build small synthetic state machines for complete, deferred, terminate, default-error, nested jump/return, cancellation, and PJMP child flows. Tests should assert immediate-completion flag transitions, parent resume after last child, frame indexing around nested base frames, task-id ownership on free, invalid op classification, and failure behavior for missing resolver or malformed operation ids.
