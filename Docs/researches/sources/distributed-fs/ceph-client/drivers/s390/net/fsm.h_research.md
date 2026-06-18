# sources/distributed-fs/ceph-client/drivers/s390/net/fsm.h

## Purpose
`fsm.h` defines the generic finite state machine types and inline operations used by the s390 networking drivers. It provides the data model for FSM descriptors, FSM instances, transition templates, timers, and event dispatch.

## Important APIs, Types, And Functions
- `fsm_function_t` is the action function signature.
- `fsm` stores the jump matrix dimensions and diagnostic name arrays.
- `fsm_instance` stores the current atomic state, instance name, optional user fields, wait queue, and optional debug history.
- `fsm_node` describes one transition table entry.
- `fsm_timer` binds a Linux timer to an FSM event and argument.
- Declares lifecycle and timer helpers implemented in `fsm.c`: `init_fsm()`, `kfree_fsm()`, `fsm_getstate_str()`, `fsm_settimer()`, `fsm_deltimer()`, `fsm_addtimer()`, and `fsm_modtimer()`.
- Inline `fsm_event()` validates current state and event, looks up the matrix entry, optionally records debug history, and invokes the action.
- Inline `fsm_newstate()` atomically sets state and wakes waiters; `fsm_getstate()` reads current state.

## Control Flow
Callers build a template array of `fsm_node` entries and pass it to `init_fsm()`. After that, `fsm_event()` is the hot path: it reads the current state, validates indexes against the descriptor, computes the jump-matrix slot, and invokes the action if present. Actions usually call `fsm_newstate()` or emit more events. Timers are represented as delayed calls to `fsm_event()`.

## State And Persistence Behavior
The header defines runtime-only state. `fsm_instance.state` is atomic and can be observed by concurrent contexts, but action execution itself is not serialized by the FSM helper. Wait queues are woken on state changes, but this CTCM code mostly uses the FSM for event dispatch rather than blocking waits.

## Dependencies And Integration Points
The header depends on Linux kernel, timer, wait queue, allocation, string, scheduler, and atomic APIs. It is included by both CTCM and MPC headers and therefore forms a foundational local API. Debug switches are compile-time macros.

## Risks
- `fsm_event()` does not lock around state lookup and action invocation. Concurrent events can race unless callers provide external serialization.
- Missing state/event actions are not fatal by default; they return nonzero and optionally log only when debug is enabled.
- `fsm_newstate()` accepts any integer without range validation, so action functions must set valid states.
- Timer callbacks run in timer context and call arbitrary action functions; those actions must be safe for that context.

## Test Signals
- Static checks should confirm every state set by action functions is within the instance's configured range.
- Concurrency tests should focus on callers that can emit events from IRQ, tasklet, timer, and process contexts.
- Debug builds with history enabled can validate unexpected missing transitions during fault injection.
