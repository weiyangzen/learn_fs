# Research: subset-b-006951

Grouped research for Ceph OSD scheduler and scrubber files. Each section preserves the source path for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/scheduler/OpSchedulerItem.h -->
# sources/distributed-fs/ceph/src/osd/scheduler/OpSchedulerItem.h

## Purpose
`OpSchedulerItem.h` defines the polymorphic work payloads that enter Ceph OSD operation queues. `OpSchedulerItem` wraps one `OpQueueable` implementation plus scheduling metadata: cost, priority, start time, owner global id, and expected map epoch. The wrapper gives schedulers a common interface for queue sharding, PG ordering, op inspection, scheduler-class classification, reserved recovery pushes, and eventual execution under the PG lock.

## Important APIs, Types, and Functions
- `OpSchedulerItem::OpQueueable` is the base queueable contract. Subclasses expose `get_queue_token()`, `get_ordering_token()`, `maybe_get_op()`, `get_scheduler_class()`, `get_time_queued()`, and `run(OSD*, OSDShard*, PGRef&, TPHandle&)`.
- `OpSchedulerItem` is move-only and forwards most behavior to `qitem`. It stores `qos_cost` set by `mClockScheduler` only when an item enters the dmclock queue.
- `PGOpQueueable` binds queueing and ordering to a `spg_t`, maps `pgid.ps()` to queue token, and centralizes `priority_to_scheduler_class()`.
- `PGOpItem` wraps client/backoff/subop requests. Client `CEPH_MSG_OSD_OP` and backoff are `SchedulerClass::client`; EC reads are classified from message priority for recovery/backfill throttling; most other messages are `immediate`.
- `PGPeeringItem`, `PGSnapTrim`, `PGScrub`, `PGScrubItem` derivatives, `PGRecovery`, `PGRecoveryContext`, `PGDelete`, and `PGRecoveryMsg` model peering, scrub FSM events, recovery work, deletion, and recovery protocol messages.
- The `fmt::formatter<OpSchedulerItem>` mirrors the ostream output and includes class, priority, optional `qos_cost`, raw cost, map epoch, and reserved pushes.

## Control Flow and State
Schedulers receive `OpSchedulerItem` instances and call `get_queue_token()` for shard placement, `get_ordering_token()` for PG-lock serialization, and `get_scheduler_class()`/priority/cost for queue policy. On dequeue, the OSD calls `run()` on the contained queueable. Scrub queueables are a notable bridge: `PGScrub`, `PGScrubResched`, `PGScrubAppliedUpdate`, `PGRepScrub`, `PGScrubGotReplMaps`, and related classes convert queued scheduler items back into PgScrubber state-machine callbacks implemented in `OpSchedulerItem.cc`.

## State and Persistence Behavior
The file itself does not persist data. Its state is in-memory scheduling metadata and references to `OpRequest`, `PGPeeringEvent`, or context callbacks. `epoch_queued` and `map_epoch` are critical temporal guards for later stale-event checks. `qos_cost` is a transient mClock accounting value and intentionally omitted for high-priority/immediate queue paths.

## Dependencies and Integration Points
It depends on OSD core types (`OSD`, `OSDShard`, `PG`, `OpRequest`, `PGPeeringEvent`, `MOSDOp`), mClock scheduler classes (`SchedulerClass`), and the thread-pool handle. Integration is direct with `mClockScheduler`, weighted-priority queues, OSDService queue helpers, PG peering/recovery code, snap trimming, and scrubber state-machine event dispatch.

## Risks and Edge Cases
The base `peering_requires_pg()` aborts unless overridden, so callers must only ask it on peering items. The EC read class logic is sensitive: misclassification can let recovery subops overwhelm immediate queues or can starve recovery. `qitem` is assumed valid for nearly all format/run paths. Scrub token and epoch fields are only meaningful if the corresponding `.cc` run methods preserve them when forwarding events.

## Test Signals
Useful tests exercise class selection for client, EC read/write, and recovery messages; move-only ownership; printed/fmt output; scrub queue item event routing; and scheduler behavior with `qos_cost` visible only after mClock queuing. Existing scrub tests also depend on `PGScrubItem` derivatives preserving message names and activation tokens in logs/query paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/scheduler/OpSchedulerItem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/scheduler/mClockScheduler.cc -->
# sources/distributed-fs/ceph/src/osd/scheduler/mClockScheduler.cc

## Purpose
`mClockScheduler.cc` implements Ceph's dmclock-backed OSD operation scheduler. It combines a strict high-priority side queue with a dmclock `PullPriorityQueue` for costed QoS scheduling. Immediate-class and priority-above-cutoff operations bypass normal dmclock selection; other operations receive a scaled cost and are admitted into the mClock queue with class-based counters.

## Important APIs, Types, and Functions
- `calc_scaled_cost()` delegates cost scaling to `MclockConfig`.
- `enqueue()` classifies the item by `SchedulerClass` and priority. Immediate and cutoff-priority items go to `enqueue_high()`, while normal items get `set_qos_cost()` and enter `scheduler.add_request()`.
- `enqueue_front()` emulates front insertion by putting immediate/cutoff items at the front of their high-priority subqueue; dmclock cannot front-insert, so normal front requests are put in high priority `0`.
- `enqueue_high()` records immediate-class counters and inserts into `high_priority`.
- `dequeue()` first drains `high_priority` in descending priority order, then pulls from dmclock, returning either a work item or a future time from dmclock.
- `get_scheduler_op_type()` maps peering and selected EC op classes to counter labels.
- `dump()` and `display_queues()` expose high-priority, client, and dmclock queue state.

## Control Flow and State
Normal enqueue flow is: derive scheduler id from `item.get_scheduler_class()`, compute scheduler op type, inspect priority and cost, choose high-priority or dmclock path, update perf-counter accounting, then log queue state. Dequeue flow is strict: any high-priority queue wins before dmclock. The high-priority map is ordered by descending priority and each list is drained from `back()`, while `enqueue_high()` pushes to `front()` for normal enqueue and `back()` for front enqueue so dequeue order is stable for the intended semantics.

## State and Persistence Behavior
All state is in memory: dmclock client registry/config, `scheduler`, and `high_priority`. Persistent effects are limited to perf counters through `MclockConfig::get_mclock_counter()` and `put_mclock_counter()`. Cost information is stamped into `OpSchedulerItem::qos_cost` only for dmclock queued operations, affecting diagnostics but not persistence.

## Dependencies and Integration Points
The implementation depends on `dmclock_server.h`, `MclockConfig`, `ClientRegistry`, Ceph perf counters, message type constants, and `OpSchedulerItem`. It is selected as an `OpScheduler` implementation by the OSD op queue configuration and returns `WorkItem`, including timed futures that tell the dispatcher when dmclock wants another pull.

## Risks and Edge Cases
The strict high-priority path can starve dmclock if immediate/cutoff work is continuous. `enqueue_front()` for non-high-priority work changes class behavior by bypassing dmclock. `dequeue()` asserts that callers checked `empty()` before a none result. Counter classification is incomplete by design and returns `unknown` for many operations. The TODO about moving immediate-class checking into `OpSchedulerItem` marks a boundary risk.

## Test Signals
Tests should cover high-priority ordering, immediate queue precedence over dmclock, front insertion behavior, scaled cost propagation, future-time dequeue returns, empty assertions, dump formatting, and EC read/write counter classification across immediate and recovery classes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/scheduler/mClockScheduler.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/scheduler/mClockScheduler.h -->
# sources/distributed-fs/ceph/src/osd/scheduler/mClockScheduler.h

## Purpose
`mClockScheduler.h` declares the `ceph::osd::scheduler::mClockScheduler` class, an `OpScheduler` implementation that uses dmclock QoS for ordinary OSD work while preserving a separate strict queue for high-priority and immediate operations.

## Important APIs, Types, and Functions
- `mClockScheduler` derives from `OpScheduler` and implements `enqueue`, `enqueue_front`, `dequeue`, `empty`, `dump`, `print`, and `get_type`.
- `mclock_queue_t` aliases `crimson::dmclock::PullPriorityQueue<scheduler_id_t, OpSchedulerItem, true, true, 2>`.
- `SubQueue` is a descending-priority map from priority to lists of `OpSchedulerItem`.
- Constructors initialize `MclockConfig`, `ClientRegistry`, and the dmclock queue with idle/erase/check timers, `AtLimit::Wait`, and anticipation timeout from config.
- `get_scheduler_id()` maps an item to `{item.get_scheduler_class(), client_profile_id_t()}`.
- `get_cost_per_io()` exposes mClock cost calibration for scrub cost calculations elsewhere.

## Control Flow and State
The header establishes the two-lane design: `high_priority` handles strict-priority work, while `scheduler` handles dmclock-managed requests. `cutoff_priority` determines when a non-immediate item bypasses dmclock. `immediate_class_priority` is `max()` so immediate-class items sort ahead of all explicit numeric high priorities.

## State and Persistence Behavior
State is runtime-only. The class owns a `ClientRegistry`, `MclockConfig`, dmclock queue, and high-priority subqueues. It may initialize perf counters through `MclockConfig::init_logger()` depending on `init_perfcounter`, but no scheduler queue state is persisted.

## Dependencies and Integration Points
The header integrates with `OpScheduler`, `OpSchedulerItem`, Ceph config, `mclock_common`, `CephContext`, Boost variant, and dmclock. OSD code using `OpScheduler` can treat it polymorphically while mClock-specific code can query `get_cost_per_io()`.

## Risks and Edge Cases
The `num_shards > 0` assertion protects cost/profile initialization. The high-priority invariant says map entries never hold empty lists; this is maintained in the implementation. Because `get_scheduler_id()` currently ignores client profile id, all clients within a scheduler class share the same profile identity unless surrounding mClock config differentiates elsewhere. The class comment still has a TODO for config explanation.

## Test Signals
Header-level expectations are mostly integration tests: constructor behavior with default and custom dmclock ages, `empty()` reflecting both queues, `print()` including type and cutoff, `get_type()` returning `mClockScheduler`, and `get_cost_per_io()` feeding scrub cost computation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/scheduler/mClockScheduler.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/scrubber/PrimaryLogScrub.cc -->
# sources/distributed-fs/ceph/src/osd/scrubber/PrimaryLogScrub.cc

## Purpose
`PrimaryLogScrub.cc` specializes the generic `PgScrubber` for `PrimaryLogPG`. It provides replicated-primary-log-specific stat reconciliation, digest repair submission, known-error listing, and per-object stat accounting while scrub progresses through ordered hobject ranges.

## Important APIs, Types, and Functions
- `get_store_errors()` reads object or snapset errors from `Scrub::Store`, scoped to the PG pool and `scrub_ls_arg_t` cursor.
- `submit_digest_fixes()` translates backend-proposed data/omap digest updates into `PrimaryLogPG` simple op contexts and queues them as MODIFY log entries.
- `add_to_stats()` accumulates scrubbed object stats in `m_scrub_cstat`.
- `_scrub_finish()` reconciles scrub-collected stats with `pg_info_t` stats, repairs invalid or mismatched stats, logs real mismatches, and clears object contexts after repair.
- `_scrub_clear_state()` resets `m_scrub_cstat`.
- `stats_of_handled_objects()` adds stats for objects already passed by the active scrub range when primary-side object handling occurs concurrently.

## Control Flow and State
Digest repair flow is asynchronous. The method sets `num_digest_updates_pending` to the number of fixes, builds an op context for each object, updates or clears data/omap digests, calls `finish_ctx()`, registers a success callback that decrements the pending count, and queues a scrub digest update when all callbacks complete. Finish flow compares accumulated scrub stats against PG stats and chooses among invalid-stat overwrite, error-reporting repair path, or silent bookkeeping correction.

## State and Persistence Behavior
The file mutates persistent PG state through `PrimaryLogPG::finish_ctx()`, `simple_opc_submit()`, and `recovery_state.update_stats()`. Digest fixes become PG log MODIFY entries with new object info digests. Stat repairs update `pg_info_t` stats and then publish/share PG info. The local `m_scrub_cstat` is transient session state.

## Dependencies and Integration Points
It depends on `PrimaryLogPG`, `PeeringState`, scrub backend digest fix structures, `Scrub::Store`, OSD cluster log, and PG object context APIs. It is called by `PgScrubber::scrub_finish()`, `ScrubBackend` via `ScrubBeListener`, admin scrub-ls paths, and object mutation paths that report handled-object stats.

## Risks and Edge Cases
Missing object contexts or mismatched object-info names decrement pending digest updates and log errors; if all fixes fail before callback registration, the code relies on later state-machine behavior not waiting forever. The code intentionally assigns, not increments, `num_digest_updates_pending`, assuming old chunk updates cannot arrive after a new chunk starts. Stat mismatches are treated differently depending on whether object-level errors exist, so incorrect error counts can change operator-visible severity. Repair clears object context cache.

## Test Signals
Tests should cover digest set/clear operations, callback-triggered digest update events, missing object context handling, invalid stats repair, mismatched stats with and without object errors, repair mode fixed-count increments, object-context cache clearing, and `get_store_errors()` object vs snapset selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/scrubber/PrimaryLogScrub.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/scrubber/PrimaryLogScrub.h -->
# sources/distributed-fs/ceph/src/osd/scrubber/PrimaryLogScrub.h

## Purpose
`PrimaryLogScrub.h` declares the `PrimaryLogScrub` subclass used by `PrimaryLogPG`. It narrows generic scrubber extension points to primary-log behavior: final stat handling, store-error lookup, object stat aggregation, and digest-fix submission.

## Important APIs, Types, and Functions
- `PrimaryLogScrub(PrimaryLogPG*)` constructs the generic `PgScrubber` base and stores a typed `PrimaryLogPG*`.
- `_scrub_finish()` and `_scrub_clear_state()` override base lifecycle hooks.
- `get_store_errors()` provides admin-facing access to stored inconsistent object/snapset records.
- `stats_of_handled_objects()` updates scrub accounting for objects processed before the current range.
- `add_to_stats()` and `submit_digest_fixes()` implement `ScrubBeListener` hooks expected by `ScrubBackend`.
- `m_scrub_cstat` stores accumulated `object_stat_collection_t` for the active scrub.

## Control Flow and State
The class is mostly a typed adapter. Generic `PgScrubber` owns the FSM, range, map collection, and store; this subclass handles the `PrimaryLogPG` operations that cannot be expressed through the generic `PG` interface. `m_pl_pg` is a const pointer alias to the same PG object as the base but with the richer primary-log API.

## State and Persistence Behavior
The header declares only transient `m_scrub_cstat`; persistence is in the `.cc` implementation through PG log and stats updates. `_scrub_clear_state()` ensures accumulated stats do not leak across sessions.

## Dependencies and Integration Points
It includes `pg_scrubber.h`, scrub message headers, `OSD`, `MOSDOp`, `MOSDRepScrub`, `MOSDRepScrubMap`, and `MOSDScrubReserve`. It integrates with `ScrubBackend` through virtual methods and with `PrimaryLogPG` through typed access.

## Risks and Edge Cases
Because the base `PgScrubber` implementation asserts in default `add_to_stats()` and `submit_digest_fixes()`, using a plain `PgScrubber` where `PrimaryLogScrub` is required would crash. The const pointer means the object assumes PG lifetime exceeds scrubber lifetime.

## Test Signals
Construction through `PrimaryLogPG`, virtual dispatch from backend to subclass methods, stat reset across sessions, and admin error-list forwarding are the main signals. Tests should verify that replicated PGs instantiate this subclass and not the generic base for primary-log scrub behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/scrubber/PrimaryLogScrub.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/scrubber/ScrubStore.cc -->
# sources/distributed-fs/ceph/src/osd/scrubber/ScrubStore.cc

## Purpose
`ScrubStore.cc` implements persistent storage for scrub-discovered inconsistencies. It maintains shallow and deep error databases as OMAP entries on special temporary objects in the PG collection, caches access through `MapCacher`, and merges shallow/deep results for admin listing.

## Important APIs, Types, and Functions
- Key helpers build ordered virtual hobject-style string keys for object errors (`SCRUB_OBJ_*`) and snapset errors (`SCRUB_SS_*`), with pool and hash boundaries.
- `Store::Store()` creates/touches shallow `scrub_<pgid>` and deep `deep_scrub_<pgid>` objects and initializes `OSDriver`/`MapCacher` backends.
- `add_object_error()` stores deep errors in `deep_db` only during deep scrub and stores shallow-masked errors in `shallow_db`.
- `add_snap_error()` stores snapset errors only in the shallow DB.
- `flush()` writes staged `results` maps into OMAP through `MapCacher::set_keys()`.
- `reinit()` always clears shallow OMAP and clears deep OMAP only for deep scrubs.
- `get_object_errors()` and `get_snap_errors()` page sorted error records after a supplied object id.
- `merge_encoded_error_wrappers()` combines same-object shallow and deep wrappers.

## Control Flow and State
During a scrub session, backend comparisons call `add_error()` for each detected inconsistency, which stages encoded bufferlists in `at_level_t::results`. `flush()` writes staged results to the object store transaction and clears the staging maps. Admin listing creates a range from the supplied start cursor to the pool-specific end key and walks one or both caches. Object errors are merge-sorted across shallow and deep DBs; equal keys are decoded, reconciled, re-encoded, and returned once.

## State and Persistence Behavior
Persistent state lives in OMAP entries on two special PG temp objects. Shallow DB is recreated for every scrub; deep DB is preserved across shallow scrubs and recreated for deep scrubs. `cleanup()` removes both DB objects on interval cleanup. `current_level` affects both writes and merge policy. The destructor asserts that staged results were flushed or cleared.

## Dependencies and Integration Points
The store uses `ObjectStore`, `ObjectStore::Transaction`, `OSDriver`, `MapCacher`, `hobject_t` string ordering, `inconsistent_obj_wrapper`, `inconsistent_snapset_wrapper`, librados error types, and `PgScrubber` logging. `PrimaryLogScrub::get_store_errors()` is the admin read path; `PgScrubber::persist_scrub_results()` is the write path.

## Risks and Edge Cases
Key ordering depends on `hobject_t::to_str()` and virtual hash boundaries; changes there can break pagination. Merge policy has an unresolved comment for newer shallow versions versus deep read-failure version zero. Shallow DB masks deep-only object error bits, so callers must query merged object errors to see full state. `flush(nullptr)` clears staged results without writing if called with null, which is deliberate but risky if misused.

## Test Signals
Tests should cover shallow/deep reinit behavior, OMAP clear/remove transactions, object and snap key ordering, pagination with `start_after` and `max_return`, merging same-object wrappers at equal and different versions, shallow masking of deep errors, and destructor assertions after flush.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/scrubber/ScrubStore.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/scrubber/ScrubStore.h -->
# sources/distributed-fs/ceph/src/osd/scrubber/ScrubStore.h

## Purpose
`ScrubStore.h` declares `Scrub::Store`, the scrubber-owned persistent error database. The abstraction hides the two-level shallow/deep OMAP layout and exposes typed add, flush, cleanup, reinit, and listing operations.

## Important APIs, Types, and Functions
- `Store(PgScrubber&, ObjectStore&, Transaction*, spg_t, coll_t)` initializes backing objects.
- `add_object_error()`, `add_snap_error()`, and overloaded `add_error()` stage encoded inconsistencies.
- `is_empty()`, `flush()`, `cleanup()`, and `reinit()` manage staged and persistent state.
- `get_snap_errors()` and `get_object_errors()` return encoded bufferlists for admin APIs.
- `at_level_t` bundles one DB object's `ghobject_t`, `OSDriver`, `MapCacher`, and staged `results`.
- `collect_specific_store()`, `clear_level_db()`, and `merge_encoded_error_wrappers()` are private helpers for listing and lifecycle.

## Control Flow and State
The public lifecycle is: construct with an object-store transaction, call `reinit()` at scrub start for the selected level, call `add_error()` while comparing maps, call `flush()` to persist staged entries, query via listing APIs, and call `cleanup()` when interval changes remove obsolete store objects. `mutable` DB optionals permit lazy cache reads from `const` listing methods.

## State and Persistence Behavior
`current_level` records whether the active scrub is shallow or deep and controls which database receives errors and whether deep records are cleared. Persistent state is external OMAP; in-memory state is the cache plus staged `results` maps. The class intentionally separates object errors from snapset errors through key namespaces.

## Dependencies and Integration Points
The declaration depends on `MapCacher`, `SnapMapper::OSDriver`, OSD formatters/types, `ObjectStore`, scrub types, and librados object ids. It is owned by `PgScrubber` and exposed to `PrimaryLogScrub` for listing.

## Risks and Edge Cases
The optional DB members are expected to be present after construction; many implementation paths assert this. Callers must pass transactions for persistent lifecycle operations. Because the class returns encoded bufferlists rather than decoded domain objects, callers must preserve wrapper encoding compatibility.

## Test Signals
Interface tests should verify construction touches DB objects, reinit level semantics, flush idempotence, empty checks, cleanup transaction contents, object/snap listing contracts, and merge behavior through public `get_object_errors()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/scrubber/ScrubStore.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/scrubber/osd_scrub.cc -->
# sources/distributed-fs/ceph/src/osd/scrubber/osd_scrub.cc

## Purpose
`osd_scrub.cc` implements the OSD-wide scrub service. It owns resource accounting, the scrub scheduling queue, CPU/time/recovery/snaptrim gates, performance counters, and the periodic tick that selects a PG scrub target and asks that PG to start scrubbing.

## Important APIs, Types, and Functions
- `OsdScrub::initiate_scrub()` is the periodic scheduler tick.
- `restrictions_on_scrubbing()` computes `OSDRestrictions` from local scrub resources, random backoff, recovery activity, allowed time window, CPU load, and snap-trim queue pressure.
- `is_sched_target_eligible()` filters queued `SchedEntry` instances based on those restrictions and each target urgency's observer rules.
- `initiate_a_scrub()` locks the selected PG and calls `PG::start_scrubbing()`.
- `on_config_change()` relocks every queued PG and calls `on_scrub_schedule_input_change()`.
- Forwarders enqueue/dequeue/remove scrub jobs and manipulate local resources and blocked-PG counts.
- `create_scrub_perf_counters()`/`destroy_scrub_perf_counters()` manage four labeled counter sets.

## Control Flow and State
Each tick logs blocked PGs and snap-trim load, captures current time, computes restrictions, optionally dumps jobs, pops the first ready eligible queue entry, and attempts to start it. A target-specific failure means that PG or target handles requeueing; an OSD-wide failure generally reflects resource limits. Eligibility is intentionally cheap and only checks conditions that do not require reshuffling all queue entries.

## State and Persistence Behavior
`OsdScrub` state is runtime-only: `ScrubResources`, `ScrubQueue`, CPU count cache, perf-counter pointers, and service references. It does not persist scrub schedules directly; PG scrub-job state is published through PG stats by `PgScrubber`.

## Dependencies and Integration Points
It depends on `ScrubSchedListener` for PG locking, remote reservation dumping, node id, and snap-trim queue totals; on `ScrubQueue` for schedule storage; on `ScrubResources` for local concurrency; and on OSD perf counters. OSD heartbeat updates load average, OSD tick invokes `initiate_scrub()`, and admin sockets call dump methods.

## Risks and Edge Cases
Random backoff is skipped when max concurrency is already reached, so logs distinguish the primary gate. CPU load uses the last cached CPU count and a fresh `getloadavg()`. Time-window checks use local time and modulo intervals where begin equals end means always permitted. `initiate_a_scrub()` dequeues before locking the PG, so missing PGs are target failures. The code assumes PG-level logic requeues when appropriate.

## Test Signals
Tests should cover restriction combinations, urgency observer behavior, allowed hour/day wraparound, random backoff probability hooks, CPU threshold behavior, snaptrim limit gating, PG lock failure, config-change rescheduling, and perf-counter creation/removal for replicated/EC shallow/deep labels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/scrubber/osd_scrub.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/scrubber/osd_scrub.h -->
# sources/distributed-fs/ceph/src/osd/scrubber/osd_scrub.h

## Purpose
`osd_scrub.h` declares `OsdScrub`, the OSDService component that offloads scrub initiation, queue manipulation, resource accounting, environment checks, and scrub performance counters from the main OSD class.

## Important APIs, Types, and Functions
- Public scheduler entry points: `initiate_scrub()`, `on_config_change()`, `dump_scrubs()`, `dump_scrub_reservations()`.
- PG-facing scheduling/resource methods: `inc_scrubs_local()`, `dec_scrubs_local()`, `mark_pg_scrub_blocked()`, `clear_pg_scrub_blocked()`, `enqueue_scrub_job()`, `enqueue_target()`, `dequeue_target()`, `remove_from_osd_queue()`.
- Environment helpers: `scrub_sleep_time()`, `scrub_time_permit()`, `update_load_average()`.
- Private gates: `restrictions_on_scrubbing()`, `is_sched_target_eligible()`, `initiate_a_scrub()`, `scrub_random_backoff()`, `scrub_load_below_threshold()`.
- Perf-counter indexing maps scrub level and pool type to labeled counters.

## Control Flow and State
The class owns one `ScrubQueue` and one `ScrubResources` bookkeeper. PGs register/update their `ScrubJob` targets through the public queue methods. The OSD periodically calls `initiate_scrub()`, which consults private gates and calls back into locked PGs.

## State and Persistence Behavior
No durable state is declared. Runtime state includes service/config references, queue, resource counters, blocked count through queue, CPU count cache, perf counters, and a log prefix. Schedules are represented by queued copies of `ScrubJob` targets and by PG-owned scrub-job objects.

## Dependencies and Integration Points
It depends on `osd_scrub_sched.h`, `scrub_resources.h`, `scrubber_common.h`, OSD perf counters, and Ceph config. It is reached from OSDService methods and PG scrubbers, and its `get_perf_counters()` is used by `PgScrubber` for labeled scrub metrics.

## Risks and Edge Cases
The header notes that `OsdScrub` itself is not protected by a single OSDService lock; protected mutable queue state lives inside `ScrubQueue`. The `PerfCounters*` ownership map requires destructor cleanup. Time-window and load behavior depend on mutable config and system calls.

## Test Signals
Public API tests can use mock `ScrubSchedListener` implementations to validate queue selection, resource reservation, config-change callbacks, blocked-PG accounting, sleep-time selection, and perf-counter lookup for all four level/pool combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/scrubber/osd_scrub.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/scrubber/osd_scrub_sched.cc -->
# sources/distributed-fs/ceph/src/osd/scrubber/osd_scrub_sched.cc

## Purpose
`osd_scrub_sched.cc` implements `ScrubQueue`, the OSD-local queue of PG scrub targets. It wraps `not_before_queue_t<SchedEntry>` with locking, enqueue/dequeue/update helpers, admin dumping, and a counter for PGs blocked on locked objects during scrub.

## Important APIs, Types, and Functions
- `enqueue_scrub_job()` enqueues both shallow and deep targets from a `ScrubJob`.
- `enqueue_target()` enqueues one `SchedTarget`.
- `dequeue_target()` removes a specific PG/level entry.
- `remove_from_osd_queue()` removes all entries for a PG.
- `pop_ready_entry()` advances queue time and dequeues the first entry satisfying a caller-provided eligibility predicate.
- `get_pgs()` returns PG ids for entries satisfying a predicate.
- `for_each_job()` supports debug/admin traversal.
- `dump_scrubs()` emits queued inactive scrub entries with eligibility.
- `mark_pg_scrub_blocked()`, `clear_pg_scrub_blocked()`, and `get_blocked_pgs_count()` maintain blocked counters.

## Control Flow and State
All queue operations lock `jobs_lock` before touching `to_scrub`. Selection advances the not-before queue to `time_now`, logs if time moved backwards, and then dequeues by predicate. Enqueueing copies `SchedEntry` snapshots from the PG-owned scheduling target, so PG code must keep target queued flags in sync.

## State and Persistence Behavior
State is runtime-only. `to_scrub` stores queued scheduling entries; `blocked_scrubs_cnt` is an atomic count for diagnostics and scheduling context. No queue contents are persisted here.

## Dependencies and Integration Points
The queue depends on `not_before_queue_t`, `ScrubJob`, `SchedTarget`, `SchedEntry`, `OSDRestrictions`, and `ScrubSchedListener` for node id in logs. `OsdScrub` owns the queue and supplies eligibility logic.

## Risks and Edge Cases
PG locks must not be acquired while holding `jobs_lock`; the design returns PG ids or dequeued candidates for callers to lock later. Removing by PG class deletes all levels, while `dequeue_target()` removes one level. Blocked counter underflow is asserted. Queue copies can diverge from PG scrub-job flags if callers forget to update both.

## Test Signals
Unit tests should validate ordering by `not_before`, predicate filtering, removal by PG and by level, time-backwards handling, dump fields, `get_pgs()` predicates, and blocked-counter increment/decrement assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/scrubber/osd_scrub_sched.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/scrubber/osd_scrub_sched.h -->
# sources/distributed-fs/ceph/src/osd/scrubber/osd_scrub_sched.h

## Purpose
`osd_scrub_sched.h` declares the OSD scrub scheduling interfaces: `ScrubSchedListener`, which abstracts services supplied by OSDService, and `ScrubQueue`, which stores PG scrub targets until they are eligible to run.

## Important APIs, Types, and Functions
- `ScrubSchedListener` requires `get_nodeid()`, `get_locked_pg()`, `get_scrub_reserver()`, and `get_snap_trim_queue_total()`.
- `ScrubQueue` exposes enqueue, dequeue, removal, dump, iteration, selection, and blocked-PG accounting.
- `EntryPred` and `EligibilityPred` let callers query or select entries without embedding OSD policy in the queue.
- `jobs_lock` protects `not_before_queue_t<SchedEntry> to_scrub`.
- `time_now()` is virtual and protected for unit tests.

## Control Flow and State
`ScrubQueue` is a passive container. PG-owned `ScrubJob` objects produce queued `SchedEntry` values; `OsdScrub` periodically asks the queue for a ready entry using eligibility rules computed from OSD restrictions. The selected entry is removed from the queue before the caller tries to lock/start the PG.

## State and Persistence Behavior
The declaration contains only in-memory state. Persistence and published schedule status are handled by PG scrub jobs and PG stats elsewhere. `blocked_scrubs_cnt` is atomic because blocked/unblocked notifications can be used as lightweight global diagnostics.

## Dependencies and Integration Points
It depends on `AsyncReserver<spg_t, Finisher>` for remote scrub reservations, `not_before_queue_t`, `ScrubJob`, `PG`, and core OSD types. The friend test classes indicate direct unit-test access to internals.

## Risks and Edge Cases
The file's diagram documents several ownership boundaries: `OsdScrub` owns the queue, while `PgScrubber` owns `ScrubJob` and copies scheduling targets into the queue. That copy-based design makes synchronization of queued flags important. The header explicitly warns not to acquire PG locks while `jobs_lock` is held.

## Test Signals
Mock listeners and overridden `time_now()` are intended test hooks. Tests should verify listener interactions, queue locking behavior, ready-entry selection under restrictions, and blocked-count accounting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/scrubber/osd_scrub_sched.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/scrubber/pg_scrubber.cc -->
# sources/distributed-fs/ceph/src/osd/scrubber/pg_scrubber.cc

## Purpose
`pg_scrubber.cc` implements the PG-level scrubber behind `ScrubPgIF`, `ScrubMachineListener`, and `ScrubBeListener`. It owns scrub session lifecycle, scheduling target manipulation, state-machine event forwarding, local/remote map collection, range selection, preemption/blocking behavior, persistent error recording, repair finish handling, replica request handling, and query/debug reporting.

## Important APIs, Types, and Functions
- Event forwarders (`initiate_regular_scrub()`, `send_*`, `active_pushes_notification()`, `digest_update_notification()`) validate epoch/token/abort relevance and feed the FSM.
- Scheduling methods (`schedule_scrub_with_osd()`, `update_scrub_job()`, `scrub_requested()`, `start_scrub_session()`, `on_mid_scrub_abort()`, `requeue_penalized()`) synchronize PG scrub targets with `OsdScrub`.
- Session setup (`set_op_parameters()`, `on_init()`, `on_replica_init()`, `reset_epoch()`) establishes flags, PG state bits, backend, store, range start, and counters.
- Chunk processing (`select_range()`, `select_range_n_notify()`, `build_primary_map_chunk()`, `build_replica_map_chunk()`, `build_scrub_map_chunk()`) drives backend object listing and scrub-map construction.
- Replica map protocol (`get_replicas_maps()`, `_request_scrub_map()`, `replica_scrub_op()`, `prep_replica_map_msg()`, `send_replica_map()`, `map_from_replica()`) coordinates primary/replica scans.
- Finish and repair (`maps_compare_n_cleanup()`, `persist_scrub_results()`, `apply_snap_mapper_fixes()`, `scrub_finish()`, `emit_scrub_result()`, `cleanup_on_finish()`) compare maps, store errors, repair metadata, update stats, and schedule follow-up repairs.
- Query/debug methods dump active schedule, blocked/reserving state, session counters, and asok debug block/unblock controls.

## Control Flow and State
A periodic or operator target reaches `start_scrub_session()` after OSD-wide selection. The method verifies primary/active/clean state, snap trimming, no-scrub flags, and local resource reservation. It freezes `m_active_target`, sets PG scrub flags and mode, removes queued sibling targets, resets the executing target, and queues a `PGScrub` work item. The FSM then calls `on_init()`, selects chunks, waits for writes/recovery updates, requests replica maps, builds the local map, compares all maps, processes digest fixes, advances to the next chunk, and finally emits results and requeues future targets.

Range selection uses config-derived shallow/deep min/max chunk sizes, halves max size after preemptions, avoids splitting clone/head groups, checks `_range_available_for_scrub()`, and records `[m_start,m_end)` plus `m_max_end`. Writes intersecting the active range either preempt if allowed, freeing the range by setting `m_end = m_start`, or block and increment counters. Replica requests carry min epoch, range, deep flag, preemption permission, priority, and blocked-op state; replicas use activation tokens to discard stale queued events.

## State and Persistence Behavior
Persistent mutations include PG state flags, scrub timestamps, scrub error counters, omap stats, object digest fixes, snap mapper repairs, PG info sharing, and stored inconsistency OMAP entries through `Scrub::Store`. Transient state includes `m_active`, `m_queued_or_active`, `m_active_target`, `m_subset_last_update`, chunk bounds, map builders, maps-collection status, callbacks, preemption state, backend, local resource wrapper, and session counters. Interval changes reset scrub state and ensure PG scrub flags are cleared.

## Dependencies and Integration Points
The implementation depends on `ScrubMachine`, `ScrubBackend`, `ScrubStore`, `OSDService`, `PGBackend`, `SnapMapper`, `MOSDRepScrub`, `MOSDRepScrubMap`, `MOSDScrubReserve`, `ScrubJob`, `ScrubResources`, and PG recovery state. OSDService queue helpers create `OpSchedulerItem` scrub events. PrimaryLogScrub overrides backend hooks for stats and digest fixes.

## Risks and Edge Cases
Epoch and interval checks are pervasive; missing one can process stale scrub messages after peering changes. Queue state is split between PG scrub-job targets and OSD queue copies, so abort/requeue paths must update queued flags carefully. Auto-repair is capped by `osd_scrub_auto_repair_num_errors`; above the cap, repair is disabled. `build_replica_map_chunk()` aborts on unexpected backend errors. Snap mapper fixes synchronously wait for transaction apply. `m_sessions_counter` is explicitly test-only and approximate. Operator abort during transient queued/active state may require reissue.

## Test Signals
High-value tests include periodic scheduling, operator forced/periodic/abort commands, no-scrub/nodeep-scrub behavior, interval-change cleanup, local reservation failure, replica reservation failure, chunk selection at clone/head boundaries, preemption budget and chunk divisor changes, write blocking/unblocking, stale token/epoch message drops, map collection with unsolicited maps, snap mapper repair, digest-update completion, auto deep-scrub-on-error, failed repair state, and query/dump fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/scrubber/pg_scrubber.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/scrubber/pg_scrubber.h -->
# sources/distributed-fs/ceph/src/osd/scrubber/pg_scrubber.h

## Purpose
`pg_scrubber.h` declares the PG scrubber core and supporting data structures. `PgScrubber` is the non-FSM implementation layer used by `PG`/`PrimaryLogPG`, the scrub FSM, and the scrub backend. It owns session state, scheduling targets, scrub ranges, map builders, store/backend objects, repair flags, preemption state, and OSD/PG integration methods.

## Important APIs, Types, and Functions
- `Scrub::MapsCollectionStatus` tracks whether the primary local map and all requested replica maps are available.
- `io_counters_replicated` and `io_counters_ec` map scrub I/O operations to unlabeled perf-counter ids.
- `scrub_flags_t` holds priority, auto-repair, after-repair check, and deep-scrub-on-error flags.
- `PgScrubber` implements `ScrubPgIF` methods used by PGs, `ScrubMachineListener` methods used by the FSM, and `ScrubBeListener` methods used by `ScrubBackend`.
- Public APIs cover scheduling, operator commands, replica messages, state/query reporting, callback registration, precondition setup, store cleanup, and debug commands.
- Protected hooks `_scrub_finish()`, `_scrub_clear_state()`, `add_to_stats()`, and `submit_digest_fixes()` are specialized by `PrimaryLogScrub`.
- Private helpers manage target updates, range selection, scrub store lifecycle, replica map requests, persistent results, snap mapper fixes, and preemption.

## Control Flow and State
The header shows a deliberate separation: `ScrubMachine` owns state transitions, while `PgScrubber` owns the effects behind those transitions. The `m_queued_or_active` flag spans the full period from committed scheduling through active scrub and teardown, while `m_active` marks actual scrub session work. `m_active_target` freezes the selected shallow/deep target. `m_start`, `m_end`, and `m_max_end` represent current and largest sent ranges. `m_maps_status` tracks map collection without fake replica entries.

## State and Persistence Behavior
Declared persistent-facing state includes scrub flags that drive PG state bits and stats, `m_store` for known errors, and methods that update PG recovery stats. The actual persisted mutations occur in the `.cc` file. Runtime-only state includes callbacks, map builders, backend, local resource wrapper, session counters, active target, preemption data, and cached config values.

## Dependencies and Integration Points
The header depends on `PG`, `ScrubStore`, `osd_scrub_sched`, `scrub_backend`, `scrub_machine_lstnr`, `scrub_machine_if`, and `scrub_reservations`. It integrates with OSDService, PGBackend, SnapMapper, scrub scheduler, replica reservations, admin sockets, and scrub perf counters.

## Risks and Edge Cases
Base `stats_of_handled_objects()`, `add_to_stats()`, and `submit_digest_fixes()` assert because real primary-log behavior must come from `PrimaryLogScrub`. Many methods assume PG lock, primary role, or active session state. Token and epoch fields are central to stale-event safety. Preemption is protected by its own mutex because writes can race with scrub progress.

## Test Signals
Tests should validate interface dispatch into `PrimaryLogScrub`, maps-status transitions and dump output, scrub flag formatting, queued/active state semantics, preemption reset/adjust behavior, config-cacher effects on chunk sizing, callback cancellation, reservation-required urgency rules, and query/status structures for active, blocked, reserving, queued, scheduled, and not-queued states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/scrubber/pg_scrubber.h -->
