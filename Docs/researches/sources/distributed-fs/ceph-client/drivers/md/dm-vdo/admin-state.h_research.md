# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/admin-state.h

## Purpose
This header defines VDO administrative state data structures, exported state-code pointers, inline state predicates, and operation transition APIs.

## Important APIs, Types, And Functions
- `struct admin_state_code` names a state and classifies it with booleans: normal, draining, loading, quiescing, quiescent, and operating.
- Exported state pointers cover normal operation, generic operation, formatting, pre-loading, loading variants, recovery/rebuild, saving/saved, scrubbing, stopping/stopped, suspending/suspended, suspended operation, and resuming.
- `struct admin_state` stores current state, next state, waiter completion, and synchronous-start flags.
- `vdo_admin_initiator_fn` is an optional callback invoked when an operation starts.
- Inline helpers read/write current state and test state classes or exact states.
- Public transition functions start/finish loading, draining, resuming, generic operations, resume if quiescent, and finish operations.

## Control Flow
Users initialize an `admin_state` by setting its code, usually to one of the exported pointers. They call a start function with an operation code and optional waiter/initiator. Later they call the matching finish function to transition to the computed next state and notify the waiter. Inline predicates let other subsystems gate I/O, drains, and lifecycle work.

## State And Persistence Behavior
The header describes in-memory administrative state only. The current code is accessed with `READ_ONCE` and `WRITE_ONCE`, giving simple visibility guarantees for lockless readers but not replacing higher-level serialization around state transitions.

## Dependencies And Integration Points
It includes VDO completion and type headers. The interface is used by the action manager and VDO lifecycle components to reject overlapping operations, identify quiescent states, and coordinate waiters.

## Risks
- Because state codes are pointers to exported constants, direct pointer comparisons are expected and must remain stable.
- Inline predicates expose flags directly; changes to state flag definitions affect many callers.
- `vdo_set_admin_state_code()` is public but documented primarily for initialization/internal use; arbitrary external use could bypass transition validation.

## Test Signals
Compile users of all predicates and transition prototypes, verify initialization to each exported state, test lockless predicate reads under transition stress, and validate that direct state-code pointer comparisons match expected lifecycle behavior.
