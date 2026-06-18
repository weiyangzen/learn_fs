# sources/distributed-fs/ceph/src/osd/scrubber/scrub_reservations.cc

## Purpose

`scrub_reservations.cc` implements primary-side sequential reservation of replica OSD scrub resources. It sends `MOSDScrubReserve` requests to acting-set replicas, validates grant/reject responses with nonces, records perf counters, releases granted reservations on destruction, and supports interval-change discard without release messages.

## Important APIs, types, and functions

- `ReplicaReservations::ReplicaReservations()` builds a sorted list of acting secondaries, records the number of replicas, and either starts the first reservation request or skips reservations for high-priority/no-reservation scrubs.
- `send_next_reservation_or_complete()` increments the request nonce, sends a request to the next replica, records send time, and returns true once all replicas have granted.
- `handle_reserve_grant()` validates nonce and expected sender, logs latency/progress, aborts on nonce-valid wrong-sender grant, and advances to the next replica.
- `handle_reserve_rejection()` filters stale responses, logs failure duration/counter, adjusts the release range when the expected peer rejected, and reports a valid failure to the FSM.
- `release_all()` sends release messages to all replicas that were successfully requested/granted so far.
- `discard_remote_reservations()` clears local tracking without messages for interval change.
- `log_success_and_duration()` and `log_failure_and_duration()` update reservation perf counters and histograms.
- `get_last_sent()`, `active_requests_cnt()`, and `gen_prefix()` support status and logging.

## Control flow

Construction starts the process unless the current scrub urgency does not require remote reservations. Requests are serialized in sorted `pg_shard_t` order to reduce cross-PG reservation contention. Each valid grant triggers the next request; the final grant returns true to the FSM so it can enter active scrubbing. A valid rejection returns true to the FSM as a failure and the destructor releases prior reservations. Stale responses with old nonces are ignored.

## State and persistence behavior

State includes the sorted secondary vector, iterator to the next replica, last send timestamp, reference to the primary state's request nonce, perf counter indexes, and optional process start time. The object uses RAII: destruction releases tracked remote reservations and logs aborted duration if the process did not already succeed or fail. No durable state is persisted; remote OSD resource state is managed through request/release messages.

## Dependencies and integration points

The implementation depends on `ScrubMachineListener`, `PG`, `OSDService`, `MOSDScrubReserve`, acting-set access, cluster messaging, OSD logger counters, and Ceph cluster log/debug facilities. It is owned by `Session` in the primary FSM.

## Risks

Nonce handling is central. Stale responses must be ignored, while wrong-sender valid-nonce grants abort because they imply protocol corruption. `release_all()` releases the half-open prefix `[begin, next_to_request)`, so iterator adjustments on rejection are correctness-critical. Destructor release means ownership transfer paths must call `discard_remote_reservations()` on interval change to avoid invalid release attempts. High-priority scrubs intentionally skip reservations, which can exceed remote concurrency expectations.

## Test signals

Tests should cover no-replica completion, high-priority skip counter, grant chains, rejection after partial grants, stale grant/reject nonces, wrong sender grant/reject behavior, release message targets, destructor abort counters, successful duration histogram, and interval discard without release.
