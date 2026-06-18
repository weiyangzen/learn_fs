# sources/distributed-fs/ceph/src/osd/scrubber/scrub_machine_if.h

## Purpose

`scrub_machine_if.h` declares `Scrub::ScrubFsmIf`, the narrow interface exposed by the scrub FSM to its owner. It hides Boost.Statechart implementation details while allowing the scrubber to drive events and query important state.

## Important APIs, types, and functions

- `process_event(const sc::event_base&)` sends arbitrary Boost.Statechart events into the FSM.
- `is_primary_idle()`, `is_reserving()`, and `is_accepting_updates()` expose key state predicates needed by `PgScrubber` and PG event routing.
- `assert_not_in_session()` verifies the FSM is outside primary scrub session substates.
- `get_time_scrubbing()` reports elapsed time since `Session` construction.
- `get_reservation_status()` returns optional status for the `ReservingReplicas` state, including current/remaining replica reservation progress.
- `initiate()` starts the underlying state machine.

## Control flow

The owner constructs a concrete `ScrubMachine`, treats it as `ScrubFsmIf`, calls `initiate()`, and then routes scrub-related PG/OSD events to `process_event()`. State queries are used to validate event legality and report scrub status.

## State and persistence behavior

This interface owns no state itself. It defines read-only state accessors plus event injection. Implementations return transient FSM state and do not imply durable persistence.

## Dependencies and integration points

The file depends on Boost.Statechart event/state headers and `scrubber_common.h`. It is implemented by `ScrubMachine` and consumed by `PgScrubber`/PG scrub event routing.

## Risks

Because `process_event()` accepts the base event type, callers can submit events inappropriate for the current state; correctness relies on concrete FSM reactions. Query functions are only as valid as the state machine's internal state. `assert_not_in_session()` can abort if the caller uses it as a soft check.

## Test signals

Tests should validate that the concrete FSM satisfies this interface across activation, reservation, update-wait, idle, interval reset, and inactive states, and that reservation status is `nullopt` outside `ReservingReplicas`.
