# subset-b-006952 research

Grouped research report for the Ceph OSD scrubber backend, scrub scheduling/FSM support, replica reservation/local resource management, shared scrub interfaces, and the `osdc` library build fragment. Sections are ordered according to `Docs/researches/research_groups.tsv` for `subset-b-006952`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/scrubber/scrub_backend.cc -->
# sources/distributed-fs/ceph/src/osd/scrubber/scrub_backend.cc

## Purpose

`scrub_backend.cc` implements `ScrubBackend`, the comparison and repair backend used by `PgScrubber` once scrub maps have been built. It decodes replica maps, merges primary and replica object listings into a per-chunk authoritative object set, chooses an authoritative copy for each object, compares object metadata/data digests/snapsets/hinfo/attributes across shards, records inconsistencies, schedules digest and snap mapper fixes, and marks bad peers missing during repair.

## Important APIs, types, and functions

- `scrub_chunk_t::scrub_chunk_t()` initializes per-chunk state and installs an empty local `ScrubMap` under the current `pg_shard_t`.
- Primary and replica `ScrubBackend` constructors bind the scrubber listener, PG backend listener, pool metadata, local shard, scrub level, repair mode, and EC optimization flags. The primary constructor also records acting shards excluding itself and sizes the EC CRC digest map for deep EC scrub when supported.
- `new_chunk()`, `get_primary_scrubmap()`, and `decode_received_map()` manage the current chunk's map collection.
- `scrub_compare_maps()` is the primary comparison entry point. It inserts the local map into cleaned metadata, merges all received maps, calls `update_authoritative()`, creates a metadata-safe map via `clean_meta_map()`, validates snapshot metadata, and returns inconsistent-object wrappers plus snap mapper fixes.
- `scrub_process_inconsistent()` and `repair_object()` are the repair path. They cluster-log a summary, require `m_repair`, then call `PgScrubBeListener::force_object_missing()` for shards in `m_missing` or `m_inconsistent`.
- `select_auth_object()` and `possible_auth_shard()` choose an authoritative shard. They prefer primary first, then highest object version, then richer digest information, while rejecting shards with read/stat/OI/snapset/hinfo/size errors or non-primary EC status.
- `compare_obj_in_maps()`, `match_in_shards()`, and `compare_obj_details()` classify per-object discrepancies and fill `inconsistent_obj_wrapper`/`shard_info_wrapper`.
- `setup_ec_digest_map()` performs EC-specific CRC reconstruction/verification for deep scrub with EC plugins that support CRC encode/decode.
- `scrub_snapshot_metadata()`, `process_clones_to()`, `scan_snaps()`, `scan_object_snaps()`, and `clean_meta_map()` validate head/clone ordering, snapset contents, clone sizes/overlap, SnapMapper consistency, and partial chunk metadata boundaries.

## Control flow

The active scrub FSM builds a local map and receives replica maps, then calls `scrub_compare_maps()`. That function constructs `all_chunk_objects` from every map, then `update_authoritative()` either just accumulates omap stats for a single-shard acting set or invokes `compare_smaps()` for multi-shard comparison. `compare_smaps()` iterates all object ids and calls `compare_obj_in_maps()`.

For each object, the backend clears `m_current_obj`, selects an auth object, optionally validates EC CRC relationships, compares every shard against the auth object, records missing shards, object-level discrepancies, digest mismatches, snapset/hinfo/object-info inconsistencies, and possible digest repair requests. If there are missing or inconsistent shards, `inconsistents()` stores authoritative peers in the current chunk and records `m_missing`/`m_inconsistent`; if replicas agree but object info digests are stale, it may queue digest fixes instead. After object comparison, `update_authoritative()` writes selected authoritative object entries into `m_cleaned_meta_map` so snapshot metadata is validated against the selected good copy.

Snapshot validation walks the cleaned map in reverse object order, treating head objects as snapset anchors and clone entries as expected reverse-ordered snap ids. It logs missing or unexpected clones, validates clone sizes and overlap accounting, updates scrub stats, submits digest fixes, and leaves incomplete clone groups in `m_cleaned_meta_map` when the chunk ended before the full clone set.

## State and persistence behavior

Most state is per scrub session or per chunk. `this_chunk` owns received maps, union object ids, per-chunk authoritative peer lists, inconsistency wrappers, error counters, EC digest data, and queued digest fixes. Session-wide state includes `m_auth_peer`, `m_missing`, `m_inconsistent`, `m_cleaned_meta_map`, and accumulated `m_omap_stats`.

The backend does not directly persist scrub state. Persistence effects are delegated: `submit_digest_fixes()` asks the scrubber to update data/omap digest metadata, SnapMapper fix lists are returned to the caller, `force_object_missing()` causes PG recovery/repair machinery to rebuild bad shards, and `add_to_stats()` updates PG object stats from scrubbed metadata.

## Dependencies and integration points

This file is tightly coupled to `ScrubMap`, `object_info_t`, `SnapSet`, `MOSDRepScrubMap`, `PGPool`, `PG`/`PrimaryLogPG` services exposed through `PgScrubBeListener`, `SnapMapReaderI`, Ceph logging, EC utility APIs, and inconsistency wrapper types from `osd_types`. It is called from the active scrub workflow after `build_primary_map_chunk()`/replica map delivery and before `PgScrubber` finalizes a chunk.

## Risks

Auth selection is correctness-critical: choosing a corrupt, stale, or non-primary EC shard as auth can drive false repair. EC CRC handling is complex and depends on plugin behavior, padding, legacy hinfo rules, and available shard sets. Snapshot metadata validation relies on object ordering and careful partial-chunk handling; mistakes can emit false clone errors or skip real ones. Repair calls mark objects missing rather than copying data directly, so wrong `m_missing`/`m_inconsistent` classification can trigger unnecessary recovery. Some error paths abort the OSD on unexpected decode/backend failures, which is intentional but high impact.

## Test signals

Comments call out tests that depend on log text, including scrub map auth-selection formatting and `qa/standalone/scrub/osd-scrub-snaps.sh` grepping `scan_snaps()` messages. Useful tests would cover replicated digest mismatch repair, stale digest age limits, missing/corrupt OI/SS/hinfo attributes, optimized and legacy EC sizes, EC CRC encode/decode mismatch cases, partial clone sets at chunk boundaries, SnapMapper add/update/overwrite fixes, and repair-mode `force_object_missing()` behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/scrubber/scrub_backend.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/scrubber/scrub_backend.h -->
# sources/distributed-fs/ceph/src/osd/scrubber/scrub_backend.h

## Purpose

`scrub_backend.h` declares the scrub comparison backend interface and the data structures used to carry object, chunk, auth-selection, digest-fix, and inconsistency state between the scrubber frontend and the backend implementation.

## Important APIs, types, and functions

- `ScrubBeListener` is the backend's view of `PgScrubber`: logging, primary check, PG id/map, stats updates, and digest-fix submission.
- `PgScrubBeListener` is referenced from `scrubber_common.h` and supplies PG/pool/backend services such as `force_object_missing()`, EC helpers, and PG info.
- `data_omap_digests_t`, `digests_fixes_t`, `shard_info_map_t`, `shard_to_scrubmap_t`, `auth_peer_t`, `wrapped_err_t`, and `inconsistent_objs_t` define the backend's core collection vocabulary.
- `omap_stat_t` and `error_counters_t` collect session/chunk statistics.
- `objs_fix_list_t` returns both inconsistent object/snapset wrappers and SnapMapper fix orders from `scrub_compare_maps()`.
- `shard_as_auth_t` carries possible-auth status, error text, decoded `object_info_t`, map iterator, and digest. It distinguishes not-found, not-usable, usable, and EC non-primary not-usable-without-error cases.
- `auth_selection_t` holds the selected auth iterator/shard/OI plus the per-shard error map and a `digest_match` flag.
- `object_scrub_data_t` stores per-object missing/inconsistent shard sets and whether digest repair is needed.
- `scrub_chunk_t` owns received maps, union object set, missing digest fixes, authoritative peers, inconsistency wrappers, counters, EC digest map, and large-omap warning state.
- `ScrubBackend` exposes chunk setup, map decode, metadata cleanup on replicas, map comparison, inconsistent-object repair, omap stats, and authoritative-peer count.

## Control flow

The header shows the intended lifecycle. A `ScrubBackend` is created for a scrub session. `new_chunk()` creates per-chunk state and a local `ScrubMap`. The scrubber fills the local map, decodes remote maps with `decode_received_map()`, then the primary calls `scrub_compare_maps()` to get object inconsistencies and snap fixes. When in repair mode, the caller can invoke `scrub_process_inconsistent()` to repair selected missing/inconsistent objects.

Private helpers divide the backend into phases: merge maps, clean metadata map, compare object maps, select auth, build EC digest maps, decide digest repair, process snapshots, scan SnapMapper, and translate logical to on-disk sizes.

## State and persistence behavior

The class stores configuration and pool identity for the session, per-chunk state in `std::optional<scrub_chunk_t>`, session-wide omap stats, authoritative peer mapping, missing/inconsistent mappings, cleaned metadata carry-over, and EC digest sizing. The header does not define durable state itself; durable changes are delegated through listener calls for digest fixes, stats, SnapMapper fixes returned to the caller, and forced missing objects.

## Dependencies and integration points

This header sits between `PgScrubber`/`PrimaryLogScrub`, `ScrubMap`, `PGPool`, `OSDMap`, `SnapMapReaderI`, `MOSDRepScrubMap`, EC utilities, and Ceph formatting/logging. `friend class PgScrubber` and `friend class TestScrubBackend` indicate tight integration with scrub orchestration and unit-style testing.

## Risks

The API assumes `this_chunk` is initialized before map access, primary-only methods are only called on primaries, and listeners outlive the backend. `shard_as_auth_t` embeds an iterator into `received_maps`, so it depends on map lifetime and no invalidating mutations. Formatter text is test-sensitive. EC behavior depends on correct `m_ec_digest_map_size`, pool type flags, hinfo requirements, and `logical_to_ondisk_size()` translation.

## Test signals

Tests should validate construction for primary versus replica, chunk reset semantics, auth-selection formatting, missing-digest list formatting, empty/single-acting-set behavior, EC digest map sizing only on deep EC scrub with CRC support, and that `scrub_compare_maps()` returns both object and snap fix lists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/scrubber/scrub_backend.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/scrubber/scrub_job.cc -->
# sources/distributed-fs/ceph/src/osd/scrubber/scrub_job.cc

## Purpose

`scrub_job.cc` implements scrub scheduling primitives for a single PG. It maintains shallow and deep scrub targets, randomizes regular schedules, handles operator-forced targets, delays failed targets, chooses the next eligible target, and defines urgency-to-policy helper functions used by OSD scrub scheduling.

## Important APIs, types, and functions

- `SchedEntry::dump()` serializes a queue entry for admin/query output, including PG id, level, urgency, schedule, last issue, and whether the target is forced.
- `SchedTarget::reset()` restores defaults for the same PG/level; `up_urgency_to()` raises urgency monotonically.
- `ScrubJob` constructor initializes shallow/deep targets, the random generator, Ceph context, OSD id, and log prefix.
- `get_target()`, `is_queued()`, `clear_both_targets_queued()`, and `set_both_targets_queued()` are queue-state helpers.
- `adjust_shallow_schedule()` uses uniform randomization around the shallow interval for periodic scrubs and preserves fixed target time for higher urgencies.
- `adjust_deep_schedule()` uses a normal distribution around the deep interval, clamped to two standard deviations, for periodic deep scrubs.
- `guaranteed_offset()` computes an offset large enough to make a faked last-scrub stamp eligible.
- `operator_forced()` marks a shallow/deep target as operator requested or must repair and schedules it at `PgScrubber::scrub_must_stamp()`.
- `earliest_eligible()` and `earliest_target()` use `cmp_entries()`/`cmp_future_entries()` from `scrub_queue_entry.h`.
- `delay_on_failure()` maps delay causes to config retry delays and pushes the target's `not_before`.
- Static policy helpers such as `requires_reservation()`, `observes_noscrub_flags()`, `has_high_queue_priority()`, and `is_repair_implied()` translate urgency into behavior gates.

## Control flow

The OSD owns a `ScrubJob` per PG while the PG is registered for scrub scheduling. Configuration or PG state updates call the adjust methods to compute future shallow/deep schedule times. The OSD scrub queue asks for the earliest target, and when a target is ready `earliest_eligible()` identifies which scrub should run. Operator commands raise urgency and set immediate timestamps. If start or mid-scrub work fails, `delay_on_failure()` postpones retry and records `last_issue`.

## State and persistence behavior

State is in memory: two `SchedTarget`s, registration/blocked flags, last delay cause, blocked-since timestamp, and random generator. The job does not persist schedules itself; its state is reflected into the OSD scrub queue and admin output. Retry delays derive from runtime config keys such as `osd_scrub_retry_delay`, `osd_scrub_retry_after_noscrub`, `osd_scrub_retry_pg_state`, `osd_scrub_retry_trimming`, and `osd_scrub_retry_new_interval`.

## Dependencies and integration points

The implementation integrates with `PgScrubber` for the must-scrub timestamp, `scrub_queue_entry.h` comparators, `scrubber_common.h` delay and schedule types, `CephContext` config, Ceph debug logging, and `ceph::Formatter` output.

## Risks

Scheduling decisions are priority-sensitive. Incorrect comparator use can starve a target or run lower-priority work first. Randomization must be disabled for forced/repair urgencies or operator requests could be delayed. `earliest_target()` without `now` is documented as potentially wrong when both targets are already eligible. Delay cause mapping changes retry behavior and can make PGs appear stuck if too long. Static urgency policy helpers must stay consistent with the table documented in the header.

## Test signals

Useful tests include deterministic comparator cases for ripe and future entries, shallow/deep randomization boundaries, forced scrub immediacy, delay cause to config-key mapping, blocked/queued state descriptions, and each urgency's policy exemptions for flags, reservations, load, recovery, max concurrency, and repair limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/scrubber/scrub_job.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/scrubber/scrub_job.h -->
# sources/distributed-fs/ceph/src/osd/scrubber/scrub_job.h

## Purpose

`scrub_job.h` declares the per-PG scrub scheduling model. It defines scheduling configuration, target state, and the `ScrubJob` object that tracks shallow/deep scrub deadlines, queue state, urgency, retry issues, and behavior-policy helpers.

## Important APIs, types, and functions

- `must_scrub_t` marks mandatory versus ordinary proposed schedules.
- `sched_params_t` carries a proposed time and mandatory flag.
- `sched_conf_t` groups shallow/deep intervals, randomization ratios, and invalid-stamp behavior.
- `SchedTarget` wraps a `SchedEntry` with a scrubber-local `queued` flag and helpers for reset, urgency raising, level/urgency inspection, and queued element projection.
- `ScrubJob` contains `pgid`, OSD id, `shallow_target`, `deep_target`, registration and blocking flags, `last_issue`, blocked timestamp, `CephContext`, RNG, and log prefix.
- Core methods choose eligible targets, adjust schedules, delay retries, apply operator requests, compute guaranteed fake offsets, expose scheduling state, and manage queued flags.
- Static methods translate `urgency_t` into behavior requirements and exemptions.
- `fmt` formatters serialize `sched_params_t`, `SchedTarget`, `ScrubJob`, and `sched_conf_t`.

## Control flow

`ScrubJob` is constructed with shallow and deep targets for the same PG. Configuration-driven code updates the targets through `adjust_shallow_schedule()` and `adjust_deep_schedule()`. The OSD queue uses `SchedTarget::queued_element()` and comparators to order work, then `ScrubJob` methods report the earliest eligible or earliest future target. Runtime events such as operator commands, failed reservations, blocked state, or completed repairs mutate urgency and `not_before`.

## State and persistence behavior

All scheduling state is in memory and mirrored indirectly by the OSD's scrub queue. `registered` means the OSD manages the job. `queued` flags are duplicated at the target level because the queue owns `SchedEntry` copies while the scrubber tracks whether those copies are enqueued. `blocked` and `blocked_since` support health/query reporting for long object locks. The RNG is per job, which can influence reproducibility in tests unless seeded/mocked externally.

## Dependencies and integration points

The header depends on `scrubber_common.h` for scrub levels, urgency, delay causes, and schedule types; `scrub_queue_entry.h` for queue entries/comparators; Ceph time/format utilities; and `PgScrubber` implementation for behavior referenced in `scrub_job.cc`.

## Risks

The shallow/deep targets must remain consistent with queue contents. If queue flags are not cleared when dequeued or set when enqueued, admin state and scheduling decisions become misleading. Static urgency policy methods encode operational semantics documented in the long table; future urgency additions require updating all helpers and formatters. The header notes that the no-argument `earliest_target()` can be wrong when both targets are eligible.

## Test signals

Tests should exercise `SchedTarget` reset/urgency monotonicity, shallow/deep target selection with both eligible and both future targets, state descriptions for unregistered/queued/scrubbing jobs, blocked flag reporting, and exhaustive urgency policy helper expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/scrubber/scrub_job.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/scrubber/scrub_machine.cc -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/scrubber/scrub_machine.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/scrubber/scrub_machine.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/scrubber/scrub_machine.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/scrubber/scrub_machine_if.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/scrubber/scrub_machine_if.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/scrubber/scrub_machine_lstnr.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/scrubber/scrub_machine_lstnr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/scrubber/scrub_queue_entry.h -->
# sources/distributed-fs/ceph/src/osd/scrubber/scrub_queue_entry.h

## Purpose

`scrub_queue_entry.h` defines the queueable scrub scheduling entry and ordering helpers used by the OSD scrub queue and `ScrubJob`. It formalizes urgency levels, schedule fields, queue projection functions, and priority comparators.

## Important APIs, types, and functions

- `urgency_t` enumerates periodic regular scrubs and higher-priority scrubs: `must_scrub`, `after_repair`, `repairing`, `operator_requested`, and `must_repair`.
- `SchedEntry` stores `spg_t`, scrub level, urgency, `scrub_schedule_t`, and last delay cause. `dump()` is implemented in `scrub_job.cc`.
- `cmp_ripe_entries()` orders eligible entries by higher urgency, earlier scheduled-at time, higher level ordering, earlier not-before, then a tie breaker.
- `cmp_future_entries()` orders non-eligible entries by earliest not-before, higher urgency, earlier scheduled-at, then level.
- `cmp_entries()` chooses the ripe comparator when one or both entries are eligible at a supplied time and future comparator otherwise.
- `project_not_before()` and `project_removal_class()` adapt `SchedEntry` to the generic not-before queue.
- `operator<()` delegates eligible ordering to `cmp_ripe_entries()`.
- `fmt` formatters stringify urgency and schedule entries for logs.

## Control flow

When scrub targets are enqueued, the generic queue projects `not_before` for readiness and uses `operator<()`/comparators to select eligible work. `ScrubJob` also uses `cmp_entries()` to decide whether shallow or deep work should run first for a PG at a given time.

## State and persistence behavior

`SchedEntry` is a small value object copied into queues. It carries transient scheduling state but no persistence. The removal class projection groups entries by PG id so queue users can remove or replace all entries for a PG.

## Dependencies and integration points

The header depends on `scrubber_common.h` for `scrub_schedule_t`, scrub levels, and `delay_cause_t`, plus Ceph formatting/time types. It is included by `scrub_job.h` and OSD scrub scheduling code.

## Risks

Comparator semantics determine scrub fairness and operator command latency. The ordering intentionally treats higher urgency as "better" by comparing `r.urgency <=> l.urgency`; reversing this would invert priority. Future-entry ordering prioritizes earliest `not_before`, so scheduled-at time is secondary until the entry ripens. Tie handling returns `greater`, which can affect stability in ordered containers.

## Test signals

Comparator tests should cover all combinations of ripe/future shallow/deep entries, urgency precedence, scheduled-at ties, not-before ties, removal by PG id, and formatting for admin output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/scrubber/scrub_queue_entry.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/scrubber/scrub_reservations.cc -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/scrubber/scrub_reservations.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/scrubber/scrub_reservations.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/scrubber/scrub_reservations.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/scrubber/scrub_resources.cc -->
# sources/distributed-fs/ceph/src/osd/scrubber/scrub_resources.cc

## Purpose

`scrub_resources.cc` implements local OSD scrub concurrency accounting. It enforces `osd_max_scrubs` for primary scrub sessions, allows high-priority scrubs to bypass the limit, logs counter changes, exposes dump output, and uses RAII to release local resources.

## Important APIs, types, and functions

- `ScrubResources::ScrubResources()` stores an upward logging callback and config proxy.
- `can_inc_scrubs()` checks the local primary scrub counter under lock.
- `inc_scrubs_local(bool is_high_priority)` increments the counter and returns a `LocalResourceWrapper` if high priority or below limit; otherwise returns `nullptr`.
- `can_inc_local_scrubs_unlocked()` compares `scrubs_local` to `conf->osd_max_scrubs` and logs denial.
- `dec_scrubs_local()` decrements under lock and asserts the counter remains non-negative.
- `dump_scrub_reservations()` emits current local count and configured max.
- `LocalResourceWrapper` destructor calls back to `dec_scrubs_local()`.

## Control flow

Scrub start code asks `inc_scrubs_local()` for a resource wrapper. If it receives `nullptr`, regular scrub initiation is delayed. If it receives a wrapper, the PG owns that wrapper for the scrub lifetime. Destruction of the wrapper releases the local slot. High-priority scrubs always increment, so the counter may exceed `osd_max_scrubs`; this blocks later regular scrubs until the count drops.

## State and persistence behavior

State is a single in-memory `scrubs_local` counter protected by `ceph::mutex`. There is no durable persistence. The local resource wrapper encodes ownership and release with RAII.

## Dependencies and integration points

The implementation depends on Ceph mutexes, config proxy, `Formatter`, `fmt`, Ceph assertions, and an owner-provided log callback. It integrates with OSD scrub scheduling/start code rather than the replica remote reservation protocol.

## Risks

Leaking a `LocalResourceWrapper` or failing to keep it for the full scrub lifetime skews concurrency. High-priority bypass can exceed configured limits by design, so callers must correctly classify priority. `dec_scrubs_local()` asserts non-negative; double-release is fatal. All counter accesses must remain under `resource_lock`.

## Test signals

Tests should cover below-limit acquisition, at-limit denial, high-priority bypass, RAII decrement on destruction, double-release prevention, dump formatting, and threaded acquisition/release contention.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/scrubber/scrub_resources.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/scrubber/scrub_resources.h -->
# sources/distributed-fs/ceph/src/osd/scrubber/scrub_resources.h

## Purpose

`scrub_resources.h` declares `ScrubResources` and `LocalResourceWrapper`, the local OSD resource bookkeeper used to limit concurrent primary scrub operations.

## Important APIs, types, and functions

- `log_upwards_t` is a simple callback for owner-level logging.
- `ScrubResources` owns `scrubs_local`, `resource_lock`, logging callback, and config reference.
- `can_inc_scrubs()` reports whether a regular local scrub can start.
- `inc_scrubs_local()` attempts to reserve a local primary scrub slot and returns a unique RAII wrapper on success.
- `dec_scrubs_local()` releases one slot.
- `dump_scrub_reservations()` reports local state to a formatter.
- `LocalResourceWrapper` represents an acquired slot and releases it in its destructor.

## Control flow

The OSD scheduler or `PgScrubber` attempts to acquire a local resource before starting a primary scrub. The returned `unique_ptr<LocalResourceWrapper>` is held for the active scrub session. When the session ends or aborts, destruction returns the count.

## State and persistence behavior

State is process-local and protected by a Ceph mutex. `scrubs_local` may exceed the configured limit only due to high-priority acquisitions. No persistent disk or cluster state is written.

## Dependencies and integration points

The header depends on `ceph_mutex`, `config_proxy`, `Formatter`, `osd_types`, and standard functional/string headers. It is part of OSD scrub scheduling/resource enforcement.

## Risks

The destructor-based release model requires strict ownership. Moving/destroying wrappers at unexpected times changes concurrency accounting. The config reference must outlive the resource object. Callers must not call `dec_scrubs_local()` manually for a wrapper they still own.

## Test signals

Tests should check the RAII ownership contract, high-priority behavior above `osd_max_scrubs`, concurrent access under lock, and formatter output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/scrubber/scrub_resources.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/scrubber_common.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/scrubber_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osdc/CMakeLists.txt -->
# sources/distributed-fs/ceph/src/osdc/CMakeLists.txt

## Purpose

`src/osdc/CMakeLists.txt` defines the static `osdc` library target for a small subset of Ceph OSD client support sources.

## Important APIs, types, and functions

- `set(osdc_files Filer.cc ObjectCacher.cc)` lists sources compiled into this target.
- A comment states that `error_code.cc`, `Objecter.cc`, and `Striper.cc` are part of `libcommon` rather than this static library.
- `add_library(osdc STATIC ${osdc_files})` creates the `osdc` static library.
- `target_link_libraries(osdc ceph-common)` links it against `ceph-common`.
- `if(WITH_EVENTTRACE) add_dependencies(osdc eventtrace_tp) endif()` adds an optional build dependency when event tracing is enabled.

## Control flow

CMake configures the source list, creates the target, links common Ceph support, and conditionally orders eventtrace tracepoint generation before building `osdc`.

## State and persistence behavior

No runtime state is involved. The file affects generated build system state: target definitions, link dependencies, and optional build ordering.

## Dependencies and integration points

This build fragment integrates with Ceph's top-level CMake, `ceph-common`, optional `WITH_EVENTTRACE`, and source files under `src/osdc`. Downstream targets may link against `osdc` to use `Filer` and `ObjectCacher`.

## Risks

Adding sources here that are already compiled into `libcommon` can produce duplicate symbols or target layering problems. Omitting a required source creates unresolved references for consumers. The eventtrace dependency is conditional; eventtrace-generated artifacts must match the target's actual include/use pattern.

## Test signals

Build tests should configure both `WITH_EVENTTRACE=ON` and `OFF`, build `osdc`, and build downstream consumers. Link tests should catch accidental movement of `Objecter`, `Striper`, or error-code sources between `osdc` and `ceph-common`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osdc/CMakeLists.txt -->
