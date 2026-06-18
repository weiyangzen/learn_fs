# sources/distributed-fs/ceph/src/osd/scrubber/scrub_machine.cc

## Purpose

`scrub_machine.cc` implements the Boost.Statechart scrub FSM declared in `scrub_machine.h`. It coordinates primary and replica scrub lifecycle: active/idle registration, replica reservation, chunk selection, waiting for pushes/updates, map building, replica map waits, digest-update waits, success/failure accounting, abort/interval cleanup, and replica-side reservation/map service.

## Important APIs, types, and functions

- `NamedSimply` updates the listener-visible FSM state name on state construction.
- `on_event_creation()`/`on_event_discard()` provide debug tracing for event lifetimes.
- `ScrubMachine::{assert_not_in_session,is_reserving,is_primary_idle,is_accepting_updates,get_time_scrubbing,get_reservation_status}` expose state queries through `ScrubFsmIf`.
- `NotActive`, `PrimaryActive`, `PrimaryIdle`, `Session`, `ReservingReplicas`, and `ActiveScrubbing` implement primary lifecycle.
- `RangeBlocked`, `PendingTimer`, `NewChunk`, `WaitPushes`, `WaitLastUpdate`, `BuildMap`, `DrainReplMaps`, `WaitReplicas`, and `WaitDigestUpdate` implement active primary chunk progression.
- `ReplicaActive`, `ReplicaIdle`, `ReplicaActiveOp`, `ReplicaWaitUpdates`, and `ReplicaBuildingMap` implement replica-side reservation and map request handling.
- `ReplicaActive::handle_reservation_request()` integrates with the OSD async scrub reserver or legacy immediate reservation path.
- `ReplicaReservations` is owned by `Session` while the primary is reserving/holding remote resources.

## Control flow

When a PG becomes active primary, `NotActive` transitions to `PrimaryActive`, whose constructor schedules the PG with the OSD. `StartScrub` from `PrimaryIdle` resets the epoch and enters `ReservingReplicas`. Reservations are requested through `ReplicaReservations`; grants either continue to the next replica or transition to `ActiveScrubbing`, while a valid rejection flags reservation failure and returns to idle.

`ActiveScrubbing` starts counters and scrub initialization, then cycles through `PendingTimer -> NewChunk -> WaitPushes -> WaitLastUpdate -> BuildMap -> WaitReplicas -> WaitDigestUpdate`. Chunk selection can block on object locks and enter `RangeBlocked`, which schedules an alarm. `BuildMap` handles local map creation, `-EINPROGRESS` requeues, and preemption. `WaitReplicas` waits until all maps are available, then either preempts or calls `maps_compare_n_cleanup()` and waits for digest updates. `WaitDigestUpdate` calls `on_digest_updates()` until the scrubber emits `NextChunk` or `ScrubFinished`; successful finish records duration and calls `scrub_finish()`.

On replicas, `ReplicaActive` receives reservation requests and release messages. Async reservations enqueue a callback in the scrub reserver; immediate reservations send grant/reject directly. `StartReplica` enters `ReplicaActiveOp`, waits for active pushes to drain, builds a replica map in `ReplicaBuildingMap`, sends preempted or normal map responses via listener callbacks, and returns idle.

## State and persistence behavior

The FSM keeps state in Boost.Statechart state objects. `ScrubMachine::m_session_started_at` measures active session duration. `Session` owns remote reservations, perf counter pointers, and abort reason. Timer callbacks are represented by RAII `timer_event_token_t`; leaving a state cancels its timer. Replica state tracks pending reservation nonce, granted flag, and reservation status. Durable effects are all delegated through `ScrubMachineListener`: queue registration/removal, PG scrub state flags, callback scheduling/canceling, perf counters, cluster log warnings, map requests/responses, digest handling, and final scrub cleanup.

## Dependencies and integration points

The implementation depends on Boost.Statechart, `ScrubMachineListener`, `ReplicaReservations`, `ScrubStore`, `PG`, `OSDService`, `MOSDScrubReserve`, `MOSDRepScrub`, `MOSDRepScrubMap`, Ceph logging, and OSD perf counters. It is the stateful coordinator between high-level `PgScrubber` methods and lower-level backend/map building code.

## Risks

FSM transitions carry cleanup semantics. Wrong transitions can leak reservations, clear PG scrub state too early, or requeue a PG incorrectly. Timer callbacks must be canceled safely to avoid events after state exit. Preemption requires draining replica maps before starting the next chunk. `WaitReplicas` uses `all_maps_already_called` to avoid invoking futurized compare cleanup more than once. The async reservation grant path is nonce-sensitive; mismatches must be discarded. Unexpected new replica chunk requests are logged as warnings and restart current handling.

## Test signals

Tests should cover primary activation/deactivation, reservation grant/reject/stale response paths, high-priority no-reservation scrubs, blocked-range alarm and unblocked transition, map-build `-EINPROGRESS`, local/replica preemption, duplicate `GotReplicas` events, digest update to next-chunk/finish paths, operator abort and interval reset cleanup, async reservation cancellation, and replica map build preemption.
