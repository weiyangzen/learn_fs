# sources/distributed-fs/ceph-client/tools/perf/util/trigger.h

## Purpose

`trigger.h` implements a tiny state machine for operations that wait for an observed event, such as signal-driven transitions.

## Important APIs, Types, and Functions

`struct trigger` contains a volatile enum state and name. States are `TRIGGER_ERROR`, `TRIGGER_OFF`, `TRIGGER_ON`, `TRIGGER_READY`, and `TRIGGER_HIT`. Inline operations are `trigger_is_available()`, `trigger_is_error()`, `trigger_on()`, `trigger_ready()`, `trigger_hit()`, `trigger_off()`, `trigger_error()`, `trigger_is_ready()`, and `trigger_is_hit()`. `DEFINE_TRIGGER(name)` creates an off trigger.

## Control Flow and State

The intended transition is OFF to ON to READY to HIT, with HIT able to return to READY. Invalid transitions warn once. Error/off states make ready/hit/off operations no-op except explicit error.

## Dependencies and Integration Points

It depends on perf's `WARN_ONCE` support. It is used by command code that needs lightweight trigger coordination without a full synchronization primitive.

## Risks and Test Signals

The state is volatile but not atomic, so this is not a complete thread-safety primitive. Tests should check transition warnings, no-op behavior for off/error states, and `DEFINE_TRIGGER` initialization.
