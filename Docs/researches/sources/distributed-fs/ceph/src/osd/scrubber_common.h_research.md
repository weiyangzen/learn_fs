# sources/distributed-fs/ceph/src/osd/scrubber_common.h

## Purpose

`scrubber_common.h` defines shared scrub types and interfaces used across the OSD scrubber: passkey access, clocks, scheduling restrictions, scrub schedule/delay types, PG backend services, perf counter index groups, and the broad `ScrubPgIF` interface used by PG code to interact with the scrubber.

## Important APIs, types, and functions

- `AsyncScrubResData` carries PG, requesting shard, request epoch, and nonce for async replica reservation callbacks.
- `ScrubberPasskey` grants selected scrub classes access to private PG methods.
- `random_bool_with_probability()` provides a small scheduling helper.
- `scrub_prio_t`, `act_token_t`, `OSDRestrictions`, `ScrubPGPreconds`, `schedule_result_t`, and `scrub_schedule_t` define common scrub scheduling inputs/results.
- `delay_cause_t` enumerates reasons scrub start or active scrub can be delayed/aborted.
- `PgScrubBeListener` is the backend-facing PG service interface, including pool info, primary shard, forced missing marking, PG info, EC encode/decode/CRC helpers, hinfo/non-primary checks, and object size translation.
- `ScrubCounterSet` groups per-pool/per-mode performance counter indexes.
- `ScrubPgIF` is the high-level PG-to-scrubber API for event triggering, active/queued state, map handling, session start, operator commands, query/dump, write blocking/preemption, callbacks, stats, store cleanup, schedule updates, recovery notifications, reservation message routing, and asok debug.
- Formatters are provided for preconditions, OSD restrictions, schedules, and delay causes.

## Control flow

The file is not an implementation unit, but it defines the contracts that connect OSD scheduling, PG state, the FSM, and the backend. PG code calls `ScrubPgIF` methods to notify updates, start scrubs, route replica messages, and query state. The backend calls `PgScrubBeListener` methods for PG metadata and EC operations. The scheduler passes `OSDRestrictions` and `ScrubPGPreconds` to `start_scrub_session()` and interprets `schedule_result_t`.

## State and persistence behavior

Most declarations are lightweight value types or pure interfaces. `scrub_schedule_t` stores in-memory target and not-before times. `OSDRestrictions` and `ScrubPGPreconds` are intentionally compact copyable snapshots. Persistent effects are delegated to concrete `ScrubPgIF` and `PgScrubBeListener` implementations: PG flags, object missing state, stats, SnapMapper/store cleanup, digest updates, and recovery-triggered scheduling.

## Dependencies and integration points

The header includes Ceph time, formatting, scrub types, random helpers, object store types, OSD perf counters, EC utilities, and `OpRequest`. It is included by scrub scheduling, FSM, backend, and PG integration code.

## Risks

`ScrubberPasskey` expands private PG access to selected classes; adding friends broadens encapsulation. `ScrubPgIF` is large and side-effect-heavy, so implementations must preserve locking, epoch checks, and callback ordering. `OSDRestrictions` and `ScrubPGPreconds` rely on compact layout static assertions. `delay_cause_t` and formatter switches should be updated together for new causes.

## Test signals

Tests should validate formatting for restrictions/schedules/delay causes, passkey-limited access boundaries where possible, `ScrubPgIF` event routing under epoch mismatch, write-block/preemption semantics, start-session result classification, and `PgScrubBeListener` EC helper behavior in backend tests.
