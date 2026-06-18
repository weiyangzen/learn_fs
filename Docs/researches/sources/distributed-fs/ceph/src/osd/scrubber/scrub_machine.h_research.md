# sources/distributed-fs/ceph/src/osd/scrubber/scrub_machine.h

## Purpose

`scrub_machine.h` declares the scrub FSM events, states, timer-token support, and primary/replica state structure used by the scrubber. It is the contract for the state-machine topology implemented in `scrub_machine.cc`.

## Important APIs, types, and functions

- `NamedSimply` is a state-name helper.
- `reservation_status_t` tracks replica remote reservation state.
- Event macros define operation-carrying reservation events (`ReplicaGrant`, `ReplicaReject`, `ReplicaReserveReq`, `ReplicaRelease`), value events (`ReserverGranted`), and simple scrub lifecycle events (`StartScrub`, `IntervalChanged`, `FullReset`, `NextChunk`, `ScrubFinished`, etc.).
- `ScrubMachine` inherits `ScrubFsmIf` and `boost::statechart::state_machine`, stores PG id/listener, exposes query methods, and wraps `process_event()`/`initiate()`.
- `scheduled_event_state_t` and `timer_event_token_t` provide cancelable scheduled-event delivery through listener callbacks.
- Primary states: `NotActive`, `PrimaryActive`, `PrimaryIdle`, `Session`, `ReservingReplicas`, `ActiveScrubbing`, and chunk substates.
- Replica states: `ReplicaActive`, `ReplicaIdle`, `ReplicaActiveOp`, `ReplicaWaitUpdates`, and `ReplicaBuildingMap`.
- `ReplicaActive::RtReservationCB` is the async-reserver callback that relocks the PG and feeds `ReserverGranted` back to the scrubber.

## Control flow

The declared topology has three quiescent modes: inactive, primary active/idle, and replica active/idle. Primary scrub work starts with `StartScrub`, enters a `Session`, optionally reserves replicas, then runs the active chunk submachine. Active chunk flow is represented as independent state classes so object range blocking, inter-chunk sleeps, pushes, last-update waits, map building, replica map waits, and digest-update waits each own their event reactions.

Replica flow begins with `ReplicaActivate`, handles reservation messages in `ReplicaActive`, and enters `ReplicaActiveOp` for a single primary map request. Full reset is ignored in replica active base state, while interval change returns to `NotActive`.

## State and persistence behavior

Statechart state instances own short-lived state: reservation objects, perf counter pointers, abort reason, timer tokens, `entered_at` timestamps, duplicate-call guard flags, pending reservation nonce, and reservation granted status. Persistent PG/OSD effects are intentionally abstracted behind `ScrubMachineListener`.

## Dependencies and integration points

The header includes Boost.Statechart, Ceph contexts/messages, `scrubber_common.h`, `scrub_machine_if.h`, `scrub_machine_lstnr.h`, and `scrub_reservations.h`. It is consumed by `PgScrubber` and message/event routing code that translates PG/OSD events into FSM events.

## Risks

The event set is broad and state-specific. Adding a new event or transition requires checking cleanup behavior in `Session`, `PrimaryActive`, and `ReplicaActive`. Timer state asserts that callback tokens are retained until fired or canceled. The header documents that interval changes are distinct from full resets because replicas release interval-specific state independently; confusing those events could send invalid releases or leak remote state.

## Test signals

State-machine tests should assert permitted transitions, ignored/deferred events, timer cancellation on state exit, interval versus full reset behavior, duplicate replica request handling, reservation nonce behavior, and status queries such as `is_reserving()`, `is_primary_idle()`, and `is_accepting_updates()`.
