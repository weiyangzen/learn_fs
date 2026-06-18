# sources/distributed-fs/ceph/src/osd/scrubber/scrub_reservations.h

## Purpose

`scrub_reservations.h` declares `Scrub::ReplicaReservations`, the primary-side helper responsible for reserving and later freeing scrub resources on replica OSDs during a primary scrub session.

## Important APIs, types, and functions

- `reservation_nonce_t` aliases the nonce type from `MOSDScrubReserve`.
- The constructor accepts a `ScrubMachineListener`, a nonce reference owned by `PrimaryActive`, and scrub performance counter indexes.
- `handle_reserve_grant()` processes valid grant replies and tells the FSM whether all replicas are reserved.
- `handle_reserve_rejection()` verifies and records rejection, returning whether it is a real reservation failure.
- `discard_remote_reservations()` tells the helper not to release tracked remotes, intended for interval changes.
- `get_last_sent()` reports the one replica currently expected to answer.
- `log_failure_and_duration()` lets callers record timeout/failure causes.
- Private helpers send releases/requests, validate nonce/sender, and log success duration.

## Control flow

The header documents serialized reservation: request one replica, wait for grant, then request the next. Any rejection terminates the attempt and causes already granted reservations to be released. Release is normally done at session end by the helper destructor, except interval change where replicas discard interval-specific reservations themselves.

## State and persistence behavior

The helper holds a PG pointer, OSD service pointer, sorted secondary list, iterator frontier, last request send time, reference to the nonce counter, perf counter set, and optional start timestamp. It is an RAII owner for remote reservations while in scope. Remote state is held on other OSDs and is represented locally only by the iterator frontier.

## Dependencies and integration points

It depends on `MOSDScrubReserve`, `scrubber_common.h`, `osd_scrub_sched.h`, `scrub_machine_lstnr.h`, `PG`, and OSD messaging/perf infrastructure. The FSM `Session` owns it in `std::optional`.

## Risks

Because the nonce is a reference to primary FSM state, lifetime must be bounded by `PrimaryActive`. The class assumes only one outstanding request at a time. Incorrect use of `discard_remote_reservations()` could leak remote reservations until interval cleanup; failing to call it on interval change could send releases that replicas no longer associate with the old interval. Timeouts are described in comments but handled by caller/FSM infrastructure, so callers must invoke failure logging and cleanup.

## Test signals

Header-level contract tests should validate status reporting fields, active request count, one-outstanding-reply invariant, RAII release/discard behavior, and nonce reuse across interval resets.
