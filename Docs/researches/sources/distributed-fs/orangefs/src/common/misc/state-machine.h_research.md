# sources/distributed-fs/orangefs/src/common/misc/state-machine.h

## Purpose

`state-machine.h` defines the generic state-machine model used by OrangeFS client and server operations. It supplies state codes, transition and parallel-jump table shapes, the `PINT_smcb` control block, frame access constants, executor prototypes, and utility macros for logging and server-to-server message array initialization.

## Important APIs, types, and macros

- `enum PINT_state_code` defines state/table flags: `SM_NONE`, `SM_NEXT`, `SM_RETURN`, `SM_EXTERN`, `SM_NESTED`, `SM_JUMP`, `SM_TERM`, `SM_PJMP`, and `SM_RUN`.
- `PINT_serv_init_msgarray_params(sm_p, __fsid)` initializes server-to-server msgpair parameters from the active server config, falling back to client job timeout/retry defaults when no config is available.
- `PINT_STATE_STACK_SIZE` fixes nested state-machine stack depth at 8.
- `struct PINT_state_stack_s` stores a saved state and previous base frame for nested returns.
- `PINT_smcb` is the per-running-operation control block with execution state, frame qlist, operation lookup callback, operation identifiers and flags, parent-child tracking, job context, terminate callback, user pointer, and immediate-completion marker.
- `struct PINT_state_machine_s` names a machine and points at its first state.
- `struct PINT_state_s` describes one state: name, parent machine, flag, action function or nested machine pointer, parallel-jump table, and transition table.
- `struct PINT_pjmp_tbl_s` maps task return values to child machines for parallel jumps.
- `struct PINT_tran_tbl_s` maps state return values to next states or terminal/return behavior.
- `PINT_sm_action` defines action return values: deferred, complete, terminate, and catastrophic error.
- `SM_ACTION_STRING`, `SM_ACTION_ISERR`, and `SM_ACTION_ISVALID` support validation and diagnostics.
- `JMP_NOT_READY` and `DEFAULT_ERROR` are common transition values. `SM_STATE_RETURN` and `SM_NESTED_STATE` are sentinel-like helpers used by generated tables.
- Prototypes expose state-machine execution, SMCB allocation/free, op and flag helpers, and frame stack functions.

## Control flow contract

State definitions pair action return values with transition tables. The executor calls an action function, then uses `job_status_s.error_code` to choose a transition. `SM_JUMP` enters nested machines while preserving a return state and base-frame location. `SM_RETURN` returns from a nested machine. `SM_PJMP` is for parallel child state-machine launches using pushed frames and a PJMP table. `SM_TERM` and `SM_ACTION_TERMINATE` together mark operation termination.

The `PINT_state_machine_current_machine_name()` macro assumes machine names begin with `pvfs2_` and strips that prefix for diagnostics. State and machine pointers must remain valid for the lifetime of every SMCB using them.

## State and persistence behavior

This header defines only in-memory execution state. It does not persist state-machine progress. Each `PINT_smcb` owns its frame list entries and, depending on task id, may own frame payload memory as implemented in `state-machine-fns.c`.

## Dependencies and integration points

The header depends on `job.h`, `quicklist.h`, `server-config-mgr.h`, and PVFS internal definitions. It is included by common executor code and by generated or handwritten client/server state-machine tables. The server msgarray macro integrates state-machine operations with the active `server_configuration_s` to pick timeouts and retry behavior.

## Risks and edge cases

- The name-stripping macro blindly advances six characters into machine names, so nonconforming names produce misleading diagnostics.
- Stack depth is fixed and enforced in implementation with assertions.
- `PINT_serv_init_msgarray_params()` references `server_job_context` and expects a surrounding server-side compilation context.
- The exposed `PINT_smcb` struct invites direct field mutation by callers, which can bypass invariants maintained by the helper functions.

## Test signals

Compile tests should cover client and server users because the header pulls in server config manager state for msgarray initialization. Runtime tests should exercise machines with nested jumps, returns, PJMP tables, terminal transitions, cancellation, and invalid action returns while checking that current machine/state name macros remain safe for expected naming conventions.
