# sources/distributed-fs/ceph-client/kernel/livepatch/transition.h

## Purpose
`transition.h` declares the internal livepatch transition interface used by core and patching code.

## Important APIs, Types, and Functions
It exposes `extern struct klp_patch *klp_transition_patch` and declares `klp_init_transition()`, `klp_cancel_transition()`, `klp_start_transition()`, `klp_try_complete_transition()`, `klp_reverse_transition()`, and `klp_force_transition()`.

## Control Flow
Core enable/disable code initializes and starts transitions through this API, sysfs reversal and force paths use the reverse/force calls, and state compatibility code uses `klp_transition_patch` to identify previously installed patches during callbacks.

## State and Persistence Behavior
The header itself has no state but exposes the single global active-transition pointer. Only one transition can run at a time.

## Dependencies and Integration Points
It includes `<linux/livepatch.h>`. It bridges `core.c`, `state.c`, and the scheduler/ftrace transition implementation.

## Risks and Test Signals
Any new caller must hold the livepatch mutex or otherwise satisfy transition serialization. Tests should verify concurrent enable/disable attempts return busy and do not corrupt `klp_transition_patch`.
