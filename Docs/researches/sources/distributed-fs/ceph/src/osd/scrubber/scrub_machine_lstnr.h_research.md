# sources/distributed-fs/ceph/src/osd/scrubber/scrub_machine_lstnr.h

## Purpose

`scrub_machine_lstnr.h` declares listener interfaces that let the FSM and preemption logic call back into `PgScrubber`, `PG`, OSD services, logging, counters, timers, and map-building/cleanup operations without embedding those concrete types into FSM state logic.

## Important APIs, types, and functions

- `Scrub::preemption_t` exposes `is_preemptable()`, `was_preempted()`, `adjust_parameters()`, `do_preempt()`, and `disable_and_test()`.
- `ScrubMachineListener` provides environment accessors (`get_pg_cct()`, `get_clog()`, `get_whoami()`, `get_spgid()`, `get_pg()`), perf counter access, and callback scheduling/cancelation.
- State/queue methods include `set_state_name()`, `rm_from_osd_scrubbing()`, `schedule_scrub_with_osd()`, `set_queued_or_active()`, `clear_queued_or_active()`, `reset_epoch()`, and block markers.
- Primary chunk methods include `select_range_n_notify()`, `search_log_for_updates()`, `pending_active_pushes()`, `build_primary_map_chunk()`, `get_replicas_maps()`, `maps_compare_n_cleanup()`, `on_digest_updates()`, and `scrub_finish()`.
- Replica methods include `build_replica_map_chunk()`, `on_replica_init()`, `replica_handling_done()`, `prep_replica_map_msg()`, `send_replica_map()`, and `send_preempted_replica()`.
- Reservation methods include `flag_reservations_failure()` and `is_reservation_required()`.

## Control flow

FSM states call listener methods as side effects when entering states or reacting to events. For example, primary activation schedules the PG with the OSD, reservation failure flags retry delay, `NewChunk` asks the scrubber to select a range, `BuildMap` asks the backend to build the local map, `WaitReplicas` asks for comparison/cleanup, and replica states use listener calls to send map or preemption responses.

## State and persistence behavior

The listener interface manipulates external state but owns none itself. Implementations are responsible for PG references and locks around scheduled callbacks, interval validation before invoking callbacks, PG-visible scrub flags, active/local map availability state, replica interaction state, and final cleanup. Callback cancelation is explicitly best-effort but guarantees exactly destruction or invocation.

## Dependencies and integration points

The file depends on Ceph logging, `Context`, versioning, `PG`, `PerfCounters`, `ScrubCounterSet`, and common scrub types. It is the major seam between FSM logic and `PgScrubber` implementation.

## Risks

Many methods have ordering-sensitive side effects. `clear_pgscrub_state()` must clear internal state and PG-visible flags while running pending callbacks safely. Scheduled callbacks must maintain/lock PG references and discard events on interval mismatch. Map availability and digest update notifications must not race with state transitions. Misreporting `is_reservation_required()` changes whether remote resources are reserved.

## Test signals

Mock-listener FSM tests can assert exact call order for primary start, chunk processing, preemption, replica request handling, and cleanup. Integration tests should inspect blocked-scrub reporting, queued/active flag clearing, callback cancelation, reservation failure retry, map request/response messaging, and cluster warning emission.
