# subset-b-006940 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/OSDMap.h -->
# sources/distributed-fs/ceph/src/osd/OSDMap.h

## Purpose
`OSDMap.h` declares Ceph's authoritative in-memory model of the OSD cluster map. It describes OSD membership, up/in/down/lost state, OSD addresses and feature masks, pool definitions, CRUSH topology, temporary PG mappings, upmap overrides, blocklists, removed/purged snap queues, stretch-mode state, full/backfill/nearfull ratios, and compatibility requirements. OSDs, monitors, clients, peering code, placement code, and recovery code use this header to decide where objects map, which daemons are eligible, what feature set is safe, and how map epochs are encoded or incrementally mutated.

## Important APIs, Types, and Functions
Important small types include `osd_info_t`, which stores clean/up/down/lost interval epochs; `osd_xinfo_t`, which stores extended liveness/features/dead-epoch data; and `PGTempMap`, a compact encoded map from `pg_t` to temporary acting OSD vectors. `PGTempMap` owns a backing `bufferlist` plus a btree index into encoded vector payloads, so callers can iterate and decode temporary mappings without the memory cost of ordinary vector maps.

The nested `OSDMap::Incremental` class represents a diff from the previous map epoch. It carries full-map fallbacks, encoded CRUSH changes, pool additions/removals/renames, OSD address and state mutations, weights, `pg_temp`, `primary_temp`, primary affinity, up-thru/lost/last-clean interval updates, blocklist/range-blocklist additions and removals, heartbeat address updates, upmap/upmap-primary mutations, removed and purged snap deltas, CRUSH-node/device-class flags, ratio changes, release requirements, and CRCs. Helper methods manage pending OSD state toggles, new pool copies, erasure profiles, and propagation of base pool properties to tiers.

The `OSDMap` class itself exposes identity and epoch APIs (`get_fsid`, `get_epoch`, `set_epoch`, `get_encoding_features`), state queries (`exists`, `is_up`, `is_down`, `is_in`, `is_out`, `is_dead`, `is_noup`, `is_nodown`, `is_noin`, `is_noout`), address lookup (`identify_osd`, `get_addrs`, cluster and heartbeat address getters), feature compatibility (`get_features`, `get_min_compat_client`, `get_up_osd_features`), pool lookup (`get_pools`, `get_pg_pool`, `lookup_pg_pool_name`, `get_pg_pool_size`, `get_pool_crush_rule`), placement (`map_to_pg`, `object_locator_to_pg`, `pg_to_raw_osds`, `pg_to_raw_up`, `pg_to_acting_osds`, `pg_to_up_acting_osds`, `get_primary_shard`, `calc_pg_role`), upmap balancing (`try_pg_upmap`, `calc_pg_upmaps`, `check_pg_upmaps`, `clean_pg_upmaps`, primary read-balance scoring), map mutation (`apply_incremental`, `dedup`, `clean_temps`), and human/JSON output (`print`, `dump`, `print_tree`, `summarize_mapping_stats`, `check_health`).

## Control Flow
Typical control flow begins with a monitor producing an `Incremental` or full map, encoding it with feature-dependent rules, and OSDs/clients decoding it into an `OSDMap`. `apply_incremental()` mutates the prior map into a new epoch, updating pools, CRUSH data, OSD state vectors, address tables, temp maps, upmap tables, snap queues, blocklists, ratios, and feature requirements. After decode or mutation, `post_decode()` and cached counters/features keep fast query results coherent.

Object placement flows from logical object identity to `pg_t` with `map_to_pg()` or `object_locator_to_pg()`. Placement then computes raw CRUSH output through `_pg_to_raw_osds()`, adjusts that raw vector with `_apply_upmap()`, strips nonexistent OSDs, computes up and primary candidates, applies primary affinity, and finally overlays `pg_temp` and `primary_temp` in `_pg_to_up_acting_osds()`. Public helpers expose either raw CRUSH output, raw-up output, acting-only output, or full up/acting output. For erasure-coded pools, `get_primary_shard()` and `pgtemp_primaryfirst()`/undo helpers translate between acting vector positions and shard IDs, including optimized EC primary-first ordering.

Administrative and balancing paths use `calc_pg_upmaps()` and read-balance helpers to build pending incremental changes. These routines derive PGs by OSD, calculate desired distributions from OSD weights or primary affinity, identify overfull and underfull OSDs, choose remap candidates, and pack upmap results into an `Incremental`. Health and reporting paths walk the same state for full flags, utilization summaries, CRUSH tree dumps, pool dumps, and read-balance scores.

## State and Persistence
`OSDMap` is an encoded persistent cluster contract. Its serialized state includes the epoch, timestamps, pools, OSD state/weights/info/xinfo/UUIDs/addresses, CRUSH map, blocklists, temp and upmap overrides, snap queues, cluster snapshots, ratios, stretch mode, and release requirements. Some cached state is deliberately not serialized, including `num_osd`, `num_up_osd`, `num_in_osd`, cached up-OSD features, and CRC flags; these are recalculated or set during decode/mutation.

The header is careful about memory sharing. Address vectors, UUID vectors, `pg_temp`, primary-temp, and primary-affinity arrays live behind shared pointers so maps can be copied cheaply; `deepish_copy_from()` clones mutable side structures but deliberately does not deep-copy CRUSH, relying on incremental application to allocate a new wrapper when needed. `PGTempMap` persists compact encoded data and must call `rebuild()` after appends if pointer stability is needed.

## Dependencies and Integration Points
The header depends on Ceph base types, mempool containers, `pg_pool_t` and OSD types, `CrushWrapper`, feature/release definitions, `entity_addrvec_t`, `snap_interval_set_t`, and formatter/encoding support. It integrates with monitors for map construction and incremental mutation, OSD peering for membership and interval decisions, objecter/client mapping, PG mapping caches (`OSDMapMapping`), PG recovery decisions, scrub/snap trim logic through removed/purged snap queues, health checks, balancers, CRUSH rule validation, and admin output.

## Risks
Placement correctness depends on applying CRUSH, upmap, removed-nonexistent filtering, primary affinity, and temp mappings in the right order. Using raw mapping APIs for data placement is explicitly unsafe. `PGTempMap` stores pointers into encoded buffer storage, so rebuild and append semantics are delicate. Feature-gated encoding must stay compatible across releases; missing a significant feature can make old clients or OSDs misdecode maps. State helpers assert on invalid OSD indexes, so callers must validate external input before calling direct getters. The no-up/no-down/no-in/no-out checks combine global, OSD, CRUSH-node, and device-class flags, making policy bugs easy when one layer is forgotten.

## Test Signals
Useful coverage includes encode/decode and incremental round trips across feature sets, `PGTempMap` rebuild/equality/iteration, mapping tests with CRUSH, upmap, primary-temp, pg-temp, nonexistent OSDs, and EC primary-first conversions. Regression tests should exercise release compatibility, blocklist range matching, snap queue deltas, `clean_temps()`, upmap balancing cancellation/packing, read-balance scoring, state flag precedence, and generated simple maps. Integration signals include peering tests that verify epoch and acting-set transitions after map changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/OSDMap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/OSDMapMapping.cc -->
# sources/distributed-fs/ceph/src/osd/OSDMapMapping.cc

## Purpose
`OSDMapMapping.cc` implements the precomputed PG mapping cache and the parallel work queue used to populate it. It materializes, for every pool and PG slot in an `OSDMap`, the up set, up primary, acting set, and acting primary, then builds a reverse acting map from OSD to PGs. This avoids repeated CRUSH/upmap/temp calculation in callers that need to scan large portions of the map.

## Important APIs and Functions
`OSDMapMapping::_init_mappings()` synchronizes the internal per-pool tables with the current `OSDMap` pools, preserving reusable mappings when pool `pg_num` and size are unchanged and dropping removed or resized pools. `update(const OSDMap&)` performs a complete synchronous rebuild by initializing mappings, updating every pool range, and finishing. `update(const OSDMap&, pg_t)` refreshes one PG row in an existing table. `_update_range()` calls `OSDMap::pg_to_up_acting_osds()` for each PG slot and writes the row. `_build_rmap()` constructs `acting_rmap`, skipping `CRUSH_ITEM_NONE`, and `_finish()` rebuilds the reverse map and records the epoch.

The file also implements `ParallelPGMapper::Job::finish_one()`, `ParallelPGMapper::WQ::_process()`, and `ParallelPGMapper::queue()`. `queue()` splits either an explicit PG vector or every pool's `[ps, ps_end)` ranges into work items of `pgs_per_item`, increments the job shard count before enqueue, and asserts that at least one item was queued.

## Control Flow
Full synchronous rebuild is linear: `_start()` calls `_init_mappings()`, every pool range is recalculated by `_update_range()`, and `_finish()` builds reverse OSD-to-PG indexes and copies `osdmap.get_epoch()`. The parallel path is similar, but `OSDMapMapping::start_update()` creates a `MappingJob`, initializes table shape in the constructor, and asks `ParallelPGMapper` to queue all ranges. Worker threads process each `Item`, call either `Job::process(pgs)` or `Job::process(pool, begin, end)`, then call `finish_one()`. When the final shard finishes, the job stamps `finish`, calls `complete()` (which invokes `_finish()`), wakes waiters, and completes any registered finish context.

Abort handling is cooperative. `Job::abort()` marks the job aborted, steals the finish context, waits for all already-started shards to finish, then completes the finish context with `-ECANCELED`. The work queue drops aborted items in `_dequeue()` by calling `finish_one()` and deleting the item instead of processing it.

## State and Persistence
The mapping is process-local cache state, not durable storage. `PoolMapping` rows contain six regions: acting primary, up primary, acting count, up count, acting OSD vector capacity equal to pool size, and up OSD vector capacity equal to pool size. `OSDMapMapping` owns the `pools` table, `acting_rmap`, `epoch`, and `num_pgs`. `ParallelPGMapper::Job` owns timing, shard count, abort state, an optional completion context, a mutex, and a condition variable.

## Dependencies and Integration Points
The implementation depends directly on `OSDMap` placement APIs, `pg_pool_t` pool shape, Ceph work queues/thread pools, `Context` completion callbacks, and CRUSH's `CRUSH_ITEM_NONE` sentinel. OSD services that need PG-to-OSD or OSD-to-PG mappings can use this cache instead of recomputing against `OSDMap` repeatedly.

## Risks
Parallel updates mutate shared `OSDMapMapping` tables from multiple work items. Correctness relies on work item ranges being non-overlapping and table shape being fixed before workers start. `queue()` asserts that at least one item exists, so an empty map or zero `pgs_per_item` would be hazardous. `PoolMapping::set()` truncates oversized vectors to pool size to avoid table overflow, which prevents crashes but can make the cache less accurate if upstream mapping ever returns more entries than expected. `acting_rmap` indexes by OSD id and assumes acting OSD ids are below `osdmap.get_max_osd()`.

## Test Signals
Tests should compare cached `get()` results with direct `OSDMap::pg_to_up_acting_osds()` for replicated and EC pools, verify pool resize/removal behavior, check single-PG update, validate reverse acting maps, and exercise parallel completion, wait, finish-context, and abort paths. Edge cases include `CRUSH_ITEM_NONE`, temp/upmap changes, pool size changes, and explicit PG-vector queueing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/OSDMapMapping.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/OSDMapMapping.h -->
# sources/distributed-fs/ceph/src/osd/OSDMapMapping.h

## Purpose
`OSDMapMapping.h` declares the cache and work-queue interfaces used to precompute PG placement for an `OSDMap`. It separates generic parallel PG/range processing (`ParallelPGMapper`) from the concrete `OSDMapMapping` table that stores up/acting mappings and reverse acting membership.

## Important APIs, Types, and Members
`ParallelPGMapper::Job` is the unit of asynchronous mapping work. It tracks start/finish time, outstanding shard count, the source `OSDMap`, abort state, a completion `Context`, locking, and a condition variable. Subclasses implement `process(const std::vector<pg_t>&)`, `process(int64_t poolid, unsigned ps_begin, unsigned ps_end)`, and `complete()`. The public methods `set_finish_event()`, `is_done()`, `get_duration()`, `wait()`, `wait_for()`, `abort()`, `start_one()`, and `finish_one()` define the lifecycle.

`ParallelPGMapper::Item` carries either an explicit vector of PGs or a pool/range shard. `WQ` is a `ThreadPool::WorkQueue<Item>` that owns enqueue/dequeue/process hooks and delegates actual work to a `Job`.

`OSDMapMapping::PoolMapping` stores one fixed-width row per PG slot. `row_size()` reserves columns for acting primary, up primary, acting count, up count, acting vector, and up vector. `get()` decodes optional outputs from a row; `set()` writes counts and vector values, truncating counts to pool size as a defensive bound. `OSDMapMapping` exposes `get()`, `get_primary_and_shard()`, `get_osd_acting_pgs()`, `update(map, pgid)`, `start_update()`, `get_epoch()`, and `get_num_pgs()`.

## Control Flow
Callers can build the cache synchronously via the private testing-only `update(const OSDMap&)` or asynchronously via `start_update()`. `start_update()` constructs a `MappingJob`, which initializes table dimensions immediately, then queues all pool ranges in a `ParallelPGMapper`. Each worker range calls `_update_range()`. When all ranges finish, `MappingJob::complete()` calls `_finish()` to build reverse maps and stamp the epoch.

Read APIs assume the mapping is already built for the target epoch. `get()` finds the pool mapping and row by `pgid.pool()` and `pgid.ps()`. `get_primary_and_shard()` also resolves the EC shard id by finding the acting primary's vector position; replicated pools use the plain `spg_t(pgid)`.

## State and Persistence
This header declares only in-memory cache structures. `pools` maps pool id to fixed row tables; `acting_rmap` maps OSD id to the PGs for which that OSD is in the acting set; `epoch` indicates which OSDMap epoch the cache reflects; and `num_pgs` totals mapped PG slots. `ParallelPGMapper` owns a queue of heap-allocated `Item`s and relies on work-queue finish hooks to delete them.

## Dependencies and Integration Points
The header uses `osd_types.h` for PG and shard identifiers, Ceph `ThreadPool::WorkQueue`, `Context`, `Cond`, and Ceph time helpers. It is a direct consumer of `OSDMap` placement but only forward-declares `OSDMap` to keep the header lightweight. Tests use friendship through `OSDMapTest`.

## Risks
`PoolMapping` has fixed row capacity based on pool size; any mapping result larger than size is truncated. Read APIs use `ceph_assert()` for pool and `ps` validity, so callers must not query stale or mismatched maps. `Job` lifetime is external to `ParallelPGMapper`; `start_update()` returns a `unique_ptr<MappingJob>` that must outlive queued work. Abort/wait semantics depend on every started shard eventually calling `finish_one()`.

## Test Signals
Header-level tests should check lifecycle transitions in `Job`, finish-context immediate completion after work is done, timeout behavior in `wait_for()`, abort completion status, row encoding/decoding, EC primary shard resolution, and reverse-map access bounds. Integration tests should validate asynchronous rebuilds against direct OSDMap mappings under pool changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/OSDMapMapping.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/ObjectVersioner.h -->
# sources/distributed-fs/ceph/src/osd/ObjectVersioner.h

## Purpose
`ObjectVersioner.h` is a small historical interface sketch for managing multiple versions of an object in the OSD object store. It declares an `ObjectVersioner` class around one `pobject_t` and operations to list versions, inspect head/committed/tail versions, prepare a new version in an `ObjectStore::Transaction`, roll back, and commit.

## Important APIs, Types, and Functions
The only state member is `pobject_t oid`. Public methods are `get_versions(list<version_t>&)`, `head()`, `committed()`, `tail()`, `prepare(ObjectStore::Transaction&, version_t)`, `rollback_to(version_t)`, and `commit_to(version_t)`. The header assumes `pobject_t`, `version_t`, `list`, and `ObjectStore::Transaction` are available from including context; it does not include their defining headers itself.

## Control Flow
The intended flow is transactional copy/version management: inspect existing versions, call `prepare()` with an object-store transaction and target version to create or stage a new version, then either `commit_to()` the new version or `rollback_to()` a previous version. No implementation is present in this file, so the exact object naming, clone/stash mechanism, and commit metadata behavior are not visible here.

## State and Persistence
The object id is in-memory state. Persistence would be through `ObjectStore::Transaction` operations issued by the missing implementation, presumably creating, removing, renaming, or marking object generations. There is no declared locking, reference management, encoding, or durable metadata schema in this header.

## Dependencies and Integration Points
The interface is conceptually related to the OSD rollback/stash machinery now implemented in `PGBackend`, but this header itself is standalone and not included by the other files in this work item. It depends on object-store and OSD object/version types.

## Risks
The header is incomplete as a self-contained declaration because it omits includes or forward declarations for `pobject_t`, `version_t`, `list`, and `ObjectStore::Transaction`. It also declares no virtual destructor, no namespace, no implementation, and no error return path. If used directly, callers cannot tell whether rollback/commit can fail or what transaction ordering is required.

## Test Signals
If this interface is still built anywhere, compilation coverage is the first signal. A real implementation would need tests for version list ordering, head/committed/tail semantics, prepare-then-commit, prepare-then-rollback, idempotent rollback, transaction durability, and interaction with object removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/ObjectVersioner.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/OpRequest.cc -->
# sources/distributed-fs/ceph/src/osd/OpRequest.cc

## Purpose
`OpRequest.cc` implements the tracked wrapper around incoming OSD messages. `OpRequest` owns a `Message` reference, extracts request identity/source metadata, lazily derives operation read/write flags, records major scheduling/execution milestones for `TrackedOp`, exposes formatter dumps, releases heavyweight message resources after unregistering, and filters tracked operations by client address.

## Important APIs and Functions
The constructor initializes `TrackedOp` from the message receive stamp, stores the raw `Message*`, adjusts warning intervals for low-priority work, extracts `reqid` from `MOSDOp`, `MOSDRepOp`, or `MOSDRepOpReply`, and records the source instance. `_dump()` writes the current flag point, optional client info, and the tracked event timeline with per-event duration. `_dump_op_descriptor()` delegates to `Message::print()`. `_unregistered()` clears data/payload, releases throttles, and drops the connection pointer.

`maybe_init_op_info()` lazily populates `OpInfo` from a `MOSDOp` and `OSDMap`, then emits an LTTng tracepoint when tracing is enabled. `mark_flag_point()` and `mark_flag_point_string()` add tracked events, update `last_event_detail`, OR in the reached flag, set the latest flag, and trace the transition. `filter_out()` parses filter strings as `entity_addr_t` values and matches the request source address with exact, nonce-zeroed, and port-zeroed forms.

## Control Flow
Request processing code creates an intrusive `OpRequestRef`, then marks milestones as the request moves through PG queueing, PG entry, delay, start, sub-op wait, and commit-sent phases. The first code path that needs semantic operation flags calls `maybe_init_op_info()`; later accessors in the header read cached `OpInfo`. Administrative tracking calls `_dump()` and `_dump_op_descriptor()` through the `TrackedOp` interface. When the op leaves tracking, `_unregistered()` strips message buffers and connection references to reduce memory pressure and avoid stale connection retention.

## State and Persistence
All state is in memory and tied to the lifetime of the `OpRequest`. Persistent effects come only from the operation that later uses the request, not from `OpRequest` itself. Important state includes the owned message pointer, `reqid`, source instance, accumulated/recent flag points, last event detail, dequeued time, `hitset_inserted`, optional coroutine handles, `osd_parent_span`, map epoch fields, and lazy `OpInfo`.

## Dependencies and Integration Points
The implementation depends on `TrackedOp`, Ceph formatting, message classes (`MOSDOp`, `MOSDRepOp`, `MOSDRepOpReply`), `OSDMap`, operation utility parsing (`OpInfo::set_from_op()`), Ceph config priorities, message throttle/connection APIs, and optional LTTng tracepoints. PG request queues, OSD schedulers, op trackers, tracing, and admin dump paths all consume its state.

## Risks
`maybe_init_op_info()` casts the request to `MOSDOp` and should only be called for client op messages. `last_event_detail` stores a raw `const char*`; the string overload marks an event but does not update `last_event_detail`, so delayed-state reporting relies on callers passing stable C strings to `mark_delayed()`. `filter_out()` returns true when no valid filter addresses parse, which is easy to misread. `_unregistered()` clears connection/data, so later code must not expect payloads or connection state after unregistering.

## Test Signals
Tests should cover construction for each supported message type, lazy `OpInfo` initialization and idempotence, state-string transitions for every mark method, dump output with and without client sources, unregister resource clearing, tracing-neutral builds, and address filtering with full address, nonce-zeroed, port-zeroed, and invalid filters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/OpRequest.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/OpRequest.h -->
# sources/distributed-fs/ceph/src/osd/OpRequest.h

## Purpose
`OpRequest.h` declares the OSD's tracked operation wrapper. It bridges raw `Message` ownership, `TrackedOp` observability, operation semantic flags from `OpInfo`, request state milestones, source/request identity, coroutine handles, and map epoch gating used by PG and OSD scheduling code.

## Important APIs, Types, and Members
`OpRequest` derives from `TrackedOp` and is reference-counted through `boost::intrusive_ptr` as `OpRequestRef`. Public accessors expose `OpInfo` properties such as read/write/cache capability, read/write caps, promote/cache-skip behavior, return-vector allowance, EC direct/sync read flags, class info, and RMW ordering. `maybe_init_op_info(const OSDMap&)` is the lazy initializer.

Message APIs include templated `get_req<T>()`, `get_req()`, `get_nonconst_req()`, `get_source()`, `has_feature()`, and `get_reqid()`. State tracking APIs include `state_flag()`, `_get_state_string()`, static `get_state_string()`, `mark_queued_for_pg()`, `mark_reached_pg()`, `mark_delayed()`, `mark_started()`, `mark_sub_op_sent()`, and `mark_commit_sent()`. Map handling fields include `check_send_map`, `sent_epoch`, and `min_epoch`; other public state includes `hitset_inserted`, `osd_parent_span`, optional `CoroHandles`, and dequeued-time accessors.

Private state includes the owned raw `Message*`, `osd_reqid_t`, source instance, reached/latest flag bits, last event detail, dequeued time, and six milestone bit constants. Protected overrides implement dump descriptor, unregister cleanup, and filtering.

## Control Flow
The class takes over a single message reference at construction and releases it in the destructor with `request->put()`. Callers generally pass `OpRequestRef` through OSD and PG queues, marking milestones as the op advances. `TrackedOp` uses `_get_state_string()` and `_dump()` to report blocked/slow requests. Code that needs permissions or op semantics first calls `maybe_init_op_info()` and then uses the many thin accessors to avoid reparsing the request.

## State and Persistence
The wrapper is runtime-only. It owns a message reference and transient tracking fields but does not persist anything itself. The map epoch fields are important control state: `sent_epoch` tracks the client's map epoch, while `min_epoch` gates when the op can be handled. `hit_flag_points` records every reached milestone; `latest_flag_point` drives the current displayed state.

## Dependencies and Integration Points
The header depends on OSD op utilities/types, `TrackedOp`, tracing types, and coroutine handles. It forward-uses `OSDMap` in the initializer signature. Integration points include `OpTracker`, OSD scheduler items, PG wait queues, capability checks through `OpInfo`, LTTng tracepoints in the implementation, and Crimson-specific connection feature handling.

## Risks
The destructor unconditionally calls `request->put()`, so construction requires a non-null message reference. Many accessors assume `op_info` has been initialized; the header exposes `op_info_needs_init()` to help call sites avoid stale zero flags. `has_feature()` aborts under Crimson because Crimson keeps connection state separately. The public mutable fields simplify call-site integration but make invariants around map epochs and hitset insertion dependent on convention.

## Test Signals
Useful tests include intrusive reference lifetime, state transition strings, delayed detail behavior, lazy op-info requirement checks, map-wait field handling, connection feature behavior in non-Crimson builds, and tracked-op filter/dump integration. Request scheduling tests should verify milestones remain ordered and meaningful in slow-op diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/OpRequest.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/PG.cc -->
# sources/distributed-fs/ceph/src/osd/PG.cc

## Purpose
`PG.cc` implements the common placement-group base behavior shared by concrete PG types. It manages PG locking and intrusive lifetime, logging prefixes, snap mapping, primary-state cleanup, capability checks, recovery queueing/completion, split/merge bookkeeping, client backoff messages, heartbeat peer sets, persistent PG metadata reads/writes/upgrades, snap trim queues, op requeue ordering, scrub event forwarding, backfill space reservation, stale-message discard rules, peering-event dispatch, deletion work, stats publishing, and small OSD-service callbacks.

## Important APIs and Functions
Lifetime and locking are implemented by `get()`, `put()`, debug ref helpers, `lock()`, `unlock()`, `is_locked()`, the constructor/destructor, and `PGLockWrapper`. `gen_prefix()`, `get_peering_perf()`, `get_perf_logger()`, and recovery-state logging integrate with diagnostics.

Snap and object metadata helpers are `remove_snap_mapped_object()`, `clear_object_snap_mapping()`, `update_object_snap_mapping()`, `update_snap_map()`, and `filter_snapc()`. Primary and recovery state helpers include `clear_primary_state()`, `queue_recovery()`, `finish_recovery()`, `_finish_recovery()`, `start_recovery_op()`, `finish_recovery_op()`, `clear_recovery_state()`, `cancel_recovery()`, `on_new_interval()`, `on_clean()`, `on_active_exit()`, and reservation callbacks.

Split/merge and deletion helpers include `split_into()`, `start_split_stats()`, `finish_split_stats()`, `merge_from()`, `do_delete_work()`, and `C_DeleteMore::complete()`. Backoff management is handled by `add_backoff()`, `release_backoffs()`, `clear_backoffs()`, and `rm_backoff()`. Persistent state code includes `init()`, `read_state()`, `read_info()`, `peek_map_epoch()`, `_has_removal_flag()`, `upgrade()`, and `prepare_write()`.

Request control includes `op_has_sufficient_caps()`, `requeue_op()`, `requeue_ops()`, `requeue_map_waiters()`, `can_discard_op()`, `can_discard_replica_op()`, `can_discard_scan()`, `can_discard_backfill()`, and `can_discard_request()`. Peering and map transitions are handled by `do_peering_event()`, `queue_peering_event()`, `queue_null()`, `find_unfound()`, `handle_advance_map()`, `handle_activate_map()`, `handle_initialize()`, and `handle_query_state()`.

Scrub methods include `start_scrubbing()`, `on_scrub_schedule_input_change()`, `scrub_requested()`, `replica_scrub()` overloads, `forward_scrub_event()` overloads, priority helpers, and scrub-state wait checks. Stats and heartbeat helpers include `publish_stats_to_osd()`, `with_pg_stats()`, `dump_pgstate_history()`, `dump_missing()`, `pg_stat_adjust()`, `with_heartbeat_peers()`, and heartbeat peer/probe updates.

## Control Flow
PGs are constructed with an OSD service, current map, pool, and `spg_t`, then initialized either from new placement data (`init()`) or from disk (`read_state()`). Disk load reads omap keys, decodes `pg_info_t`, `PastIntervals`, purged snaps, fast info, and the PG log/missing set, upgrades if needed, initializes current up/acting/role from the OSDMap, sets collection options, injects an initialize peering event, and persists any dirty state.

Map changes flow through `handle_advance_map()` and `handle_activate_map()`, delegating state-machine work to `PeeringState`, updating the OSD shard epoch, requeueing map waiters, and refreshing scrub schedules if pool settings changed. Peering events are filtered by `old_peering_evt()` and then passed to `recovery_state.handle_event()`, followed by `write_if_dirty()` so state changes are captured.

Client and replica requests may block on ordered wait queues. `requeue_ops()` preserves request ordering by pushing waitlists back in reverse order, and it may divert ops to `waiting_for_readable` if readability is still blocked. `can_discard_request()` rejects stale messages based on same-primary/same-interval epochs, force-op-resend epochs, split epochs, down OSDs in the next map, and peering reset epochs.

Recovery control queues primary PGs only when primary and peered. Recovery completion clears recovery state, waits for sync, purges strays, publishes stats, and notifies the scrubber. Backfill reservation estimates required bytes, adjusts EC pools by data chunk count and stripe size, checks full/backfill-full policy under `OSDService::stat_lock`, and records primary/local byte reservations for stats adjustment.

Deletion scans collection objects in bounded batches, removes snap mapper entries and objects, schedules more delete work on commit, and finally clears PG info/log, removes the collection, flushes, and asks the OSD to finish deletion or reinstantiates if racing with merge.

## State and Persistence
Runtime state includes the lock/refcount, OSD pointers, collection handle, `PeeringState`, snap mapper, scrubber, wait queues, backoffs, recovery counters, heartbeat peers/probes, backfill reservation bytes, projected log/update state, unstable/publish stats, snap trim queues, and deletion sleep flag. Persistent PG state is stored in the PG metadata object omap: info version, info, big info/past intervals/purged snaps, fast info, PG log, and missing set. Object snap mappings are persisted through `SnapMapper` in the object store transaction. Collection operations persist split, merge, delete, and rollback cleanup effects.

## Dependencies and Integration Points
`PG.cc` depends on `OSD`, `OSDService`, `PeeringState`, `PGLog`, `PGBackend`, `SnapMapper`, `ObjectStore`, `ScrubPgIF`, session/capability objects, many OSD message classes, timers/reservers, op scheduler items, and perf counters. It is the glue between map advancement, peering, backend IO/recovery, scrub scheduling, client request gating, monitor/OSD service callbacks, and durable object-store metadata.

## Risks
The class relies heavily on holding `_lock`; several methods assert lock ownership or assume serialized PG event execution. Request ordering is fragile because many wait queues interact. Backoff release races with session reset and new backoffs, requiring lock ordering between `backoff_lock` and `Backoff::lock`. Recovery counters must stay balanced, especially when clearing recovery or suspending backfill. Persistent writes combine info, log, missing, and snap mapper updates; missed dirty writes can corrupt peering state. Deletion must handle objects appearing during removal and races with merge. In debug-ref code, the shown `put_with_id()` deletes when `newref` is nonzero, which is suspicious and should be verified against build configuration and tests.

## Test Signals
Tests should cover read/write of PG state, prepare-write omap keys, map advancement and peering event filtering, request discard decisions across map epochs/features, wait-queue requeue order, snap mapper updates/removals, split/merge state transfer, backoff add/release/session reset, recovery queue and completion, backfill reservation/full checks, scrub event forwarding on active/inactive PGs, deletion batches, stats publishing, and heartbeat peer updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/PG.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/PG.h -->
# sources/distributed-fs/ceph/src/osd/PG.h

## Purpose
`PG.h` declares the abstract base class for Ceph OSD placement groups. It defines the contract between concrete PG implementations, `PeeringState`, scrubber code, OSD services, PG backends, recovery scheduling, request queues, snap trimming, collection split/merge, and admin/stat reporting. Concrete classes such as primary-log PGs provide object-operation specifics while this base class centralizes shared peering, lifecycle, state, and callback plumbing.

## Important APIs, Types, and Members
`PGRecoveryStats` records per-state enter/exit/event/time totals and can dump plain or formatted recovery-state statistics. `PG` derives from `DoutPrefixProvider`, `PeeringState::PeeringListener`, and `Scrub::PgScrubBeListener`. Key identity members are `pg_whoami`, `pg_id`, `coll`, `ch`, `pgmeta_oid`, and references to `pool` and `info` owned by `recovery_state`.

Public state/query APIs expose current state, OSDMap epoch/ref, pool, history, acting/up sets, role, primary, past intervals, EC metadata, scrub state, snap-trim counters, stats counters, heartbeat peers, and recovery/backfill flags. Initialization and persistence APIs include `init()`, `read_state()`, `peek_map_epoch()`, `read_info()`, `_has_removal_flag()`, `prepare_write()`, and `write_if_dirty()`.

The abstract surface for concrete PGs includes `split_colls()`, `plpg_on_role_change()`, `plpg_on_pool_change()`, `start_recovery_ops()`, `get_watchers()`, `do_request()`, `clear_cache()`, `get_cache_obj_count()`, `snap_trimmer()`, `do_command()`, cache-agent methods, `check_local()`, `_clear_recovery_state()`, `_split_into()`, `kick_snap_trim()`, `snap_trimmer_scrub_complete()`, `get_pgbackend()`, and `_range_available_for_scrub()`.

Protected members define wait queues for map, peered, readable, active, flush, scrub, cache-full, clean-to-primary-repair, unreadable/degraded/blocked objects, degraded callbacks, and on-disk waits. Recovery state includes `recovery_queued`, `recovery_ops_active`, `waiting_on_backfill`, backfill intervals, reservations, projected log, projected last update, and recovery-state machine. Backoff state, heartbeat peers/probes, snap trim queues, unstable stats, and publish stats are also declared here.

## Control Flow
The class lifecycle starts with construction, collection setup, and either new-PG `init()` or disk `read_state()`. OSD map changes enter through `handle_advance_map()` and `handle_activate_map()`, while state-machine events enter through `queue_peering_event()` and `do_peering_event()`. Activation callbacks (`on_activate`, `on_replica_activate`, `on_activate_committed`, `on_active_actmap`, `on_clean`, `on_active_exit`) coordinate waiters, recovery, snap trim, scrub, and backend state.

Requests enter concrete `do_request()` but are managed by shared discard, capability, wait, and requeue helpers. Recovery scheduling calls `queue_recovery()`, concrete `start_recovery_ops()`, `start_recovery_op()`, `finish_recovery_op()`, and `find_unfound()`. Scrub scheduling wraps `ScrubPgIF` calls and protects active-state transitions. Split and merge paths update `PeeringState`, snap mapper bits, collection state, and source PG metadata.

## State and Persistence
The header defines both durable and volatile PG state. Durable state is mediated through `PeeringState`, `PGLog`, `pg_info_t`, `PastIntervals`, the PG metadata object, collection layout, and snap mapper. Volatile state includes locks/refcounts, wait queues, projected log state, active recovery counts, backoffs, reservations, heartbeat peers, scrubber state, unpublished stat deltas, and agent/cache state. The class comments explicitly describe wait-list ordering because it is part of the correctness contract for request ordering.

## Dependencies and Integration Points
`PG.h` depends on Ceph mempool/intrusive pointer utilities, admin finishers, OSD and PG types, `SnapMapper`, sessions/backoffs, timers, `PGLog`, `OSDMap`, `PGBackend`, peering events/state, recovery and missing-location types, scrub interfaces, and manager perf metric types. It integrates with `OSDService`, `OSDShard`, `ObjectStore`, `PGBackend`, scrub backends, monitor/OSD messaging, op scheduling, and dynamic perf stats.

## Risks
This header exposes a large callback contract; concrete PGs must maintain invariants expected by `PeeringState`, scrubber, backend, and OSDService simultaneously. Many helpers require the PG lock, but the type system does not enforce it. Wait queue ordering is documented but easy to break when adding a new blocking condition. Public inline stats mutators clamp negative byte counts, which protects counters but can hide upstream accounting bugs. Abstract hooks make it possible for concrete implementations to forget to clear cache/recovery/scrub state on interval changes.

## Test Signals
Tests should verify concrete PG implementations satisfy all abstract hooks, lock assertions, peering listener callbacks, scrub listener callbacks, wait queue ordering, recovery counters, split/merge contracts, snap trim accounting, stats publication, byte reservation accounting for EC and replicated pools, and PGBackend delegation through `PGLogEntryHandler`. Compile-time coverage across feature flags (`PG_DEBUG_REFS`, `CEPH_DEBUG_MUTEX`, Crimson) is also important.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/PG.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/PGBackend.cc -->
# sources/distributed-fs/ceph/src/osd/PGBackend.cc

## Purpose
`PGBackend.cc` implements shared backend behavior for replicated and erasure-coded PG backends. It handles recovery-delete message batching and replies, rollback/rollforward/trim interpretation of log modification descriptors, temp object cleanup, object listing and attribute helpers, rollback object stashing/restoration, partial-write last-complete tracking for optimized EC behavior, backend construction, and scrub-map scanning.

## Important APIs and Functions
Recovery delete support is implemented by `recover_delete_object()`, `send_recovery_deletes()`, `handle_message()`, `handle_recovery_delete()`, and `handle_recovery_delete_reply()`. The sender batches deletes by `osd_max_push_cost` and `osd_max_push_objects`; replicas remove missing objects and reply; the primary marks peers recovered and calls `on_global_recover()` once no peer or local missing entry remains.

Rollback and trim logic centers on `rollback()`, `rollforward()`, `trim()`, and `trim_after_remove()`. Local visitor classes walk `ObjectModDesc` entries and translate high-level log changes into `ObjectStore::Transaction` operations: truncate appended data, restore attributes, unstash removed objects, remove created objects, update snap mappings, clone old extents back from rollback generations, trim rollback generations, and handle EC omap journal entries.

Storage helpers include `try_stash()`, `remove()`, `on_change_cleanup()`, `objects_list_partial()`, `objects_list_range()`, `objects_get_attr()`, `objects_get_attrs()`, `rollback_setattrs()`, `rollback_append()`, `rollback_stash()`, `rollback_try_stash()`, `rollback_extents()`, and `trim_rollback_object()`. `partial_write()` updates `pg_info_t::partial_writes_last_complete` for nonprimary EC shards that were not written by an optimized partial write. `build_pg_backend()` chooses `ReplicatedBackend` or `ECSwitch` and loads the erasure-code plugin for EC pools. `be_scan_list()` builds scrub-map metadata and invokes backend-specific deep scrub.

## Control Flow
Incoming backend messages first pass through `handle_message()`, which consumes recovery-delete messages before delegating unknown messages to `_handle_message()` implemented by concrete backends. Delete recovery starts when a recovering primary sees peers missing an object that is a delete; it records per-peer deletes in the recovery handle, then `run_recovery_op()` implementations eventually call `send_recovery_deletes()`. Replies update peer recovery state and may complete global recovery.

Rollback flow is visitor-driven. A PG log entry's `mod_desc` is asserted rollback-capable, visited, and each operation prepends or appends transaction fragments so object state returns to the prior version. Trim/rollforward similarly visits modification descriptors but removes no-longer-needed rollback objects or applies EC omap journal cleanup. Scrub scanning is incremental: first stat/getattrs populate a `ScrubMap::object`; deep scrub may return `-EINPROGRESS`; otherwise the builder advances to the next object.

## State and Persistence
`PGBackend` stores `cct`, `store`, `coll`, collection handle, parent listener, and `temp_contents`. Persistent effects are all `ObjectStore::Transaction` operations against `coll`, normal object generations (`NO_GEN`), rollback generations (`version_t`), shard-specific `ghobject_t`s, omap headers/keys, snap mappings, and temp collection objects. Recovery delete state is transient in `RecoveryHandle::deletes`, while partial-write state is persisted through updated `pg_info_t`.

## Dependencies and Integration Points
The implementation depends on concrete backend classes (`ReplicatedBackend`, `ECSwitch`), erasure-code plugin registry, `PGLog`, `ObjectStore`, scrub map types, OSD map features, recovery delete messages, `ObjectModDesc` visitor APIs, `PGBackend::Listener` callbacks, `C_GatherBuilder`, and Ceph logging/config. It is called by PG recovery, PG log trimming, rollback, scrub, and backend message dispatch.

## Risks
Rollback correctness is highly sensitive to EC optimized writes, shard-specific object sizes, written-shard sets, and OI attribute versions. `rollback_setattrs(only_oi=true)` decodes and rewrites object_info; malformed or missing `OI_ATTR` would be serious. Recovery delete completion depends on missing sets being updated before checking global completion. `objects_list_partial()` must filter generated rollback/temp/meta objects correctly. `build_pg_backend()` asserts that EC plugin loading succeeds, so profile/config errors abort. Many unexpected store errors abort rather than propagate.

## Test Signals
Tests should cover recovery delete batching/replies, rollback of append/setattrs/remove/create/snap/extents, EC optimized written/unwritten shard behavior, omap journal trim/delete cases, partial-write last-complete transitions, temp cleanup on interval changes, object list filtering in fixed and legacy collection-list modes, attr helpers, backend construction for replicated and EC pools, and scrub scan handling of ENOENT/EIO/EINPROGRESS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/PGBackend.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/PGBackend.h -->
# sources/distributed-fs/ceph/src/osd/PGBackend.h

## Purpose
`PGBackend.h` declares the abstract backend interface that concrete replicated and erasure-coded implementations use to provide object IO, replication, recovery, scrub, repair, rollback, and omap behavior for a PG. It also declares the callback interface (`Listener`) that lets a backend call back into its owning PG without depending on a concrete PG class.

## Important APIs, Types, and Members
`PGBackend::Listener` is the central integration surface. It provides recovery callbacks (`on_local_recover`, `on_global_recover`, `on_peer_recover`, `begin_peer_recover`, failed/canceled pulls, remove missing object), locking/refcount helpers, context blessing, message sending, transaction queueing, map/interval access, acting/backfill shard sets, missing/info/log access, object context and lock management, operation logging, snap mapping, committed/version/stat updates, recovery scheduling, timers, identity, connection and monitor command helpers, perf counters, cluster log streams, full checks, repaired stat increments, byte accounting, scrub preemption, and EC listener access.

Backend lifecycle and recovery APIs include `open_recovery_op()`, `run_recovery_op()`, `recover_delete_object()`, `send_recovery_deletes()`, `recover_object()`, `can_handle_while_inactive()`, `handle_message()`, `_handle_message()`, `check_recovery_sources()`, `on_change_cleanup()`, `on_change()`, and `clear_recovery_state()`. Predicate APIs expose recoverability/readability, EC chunk sizing, CRC encode/decode support, object-to-shard sizing, nonprimary/hinfo/optimized-EC flags, EC encode/decode helpers, EC omap journal operations, and omap iteration/get/check operations.

Write and log APIs include `submit_transaction()`, `call_write_ordered()`, `try_stash()`, `rollback()`, `rollforward()`, `trim()`, `trim_after_remove()`, `partial_write()`, and `remove()`. Object access APIs include `objects_list_partial()`, `objects_list_range()`, attr getters, sync/local/async reads, optional readv, extent-to-shard conversion, scrub scans, deep scrub, and backend factory `build_pg_backend()`.

## Control Flow
The parent PG constructs a concrete backend through `build_pg_backend()` and then calls backend methods while holding PG locks as documented. Client writes are translated by concrete backends into `submit_transaction()` calls with log entries, stats deltas, hitset history, commit callbacks, tids, reqids, and `OpRequestRef`. Recovery opens a backend-specific `RecoveryHandle`, calls `recover_object()` or `recover_delete_object()` for objects, then `run_recovery_op()` sends or applies the accumulated work. Incoming messages call shared `handle_message()` before concrete `_handle_message()`.

Rollback/trim flows are shared by the base implementation and invoked through `PG::PGLogEntryHandler`. Scrub flows call `be_scan_list()` for common metadata scanning and backend-specific `be_deep_scrub()` for data verification. Omap APIs abstract replicated local omap and EC omap-journal behavior behind one PG-facing interface.

## State and Persistence
The base class stores context, object store pointer, collection id, collection handle reference, parent listener, and a set of temp objects to remove on interval reset. Concrete subclasses own replication/EC-specific pending operations, caches, and recovery state. Persistence is expressed entirely through `ObjectStore::Transaction`, object generations, omap updates, PG log entries, snap mappings, and queued transactions through the parent listener.

## Dependencies and Integration Points
The header depends on EC support types, extent cache, object store, scrubber types, log client, PG transactions, coroutine handles, `PGLog`, `OSDMap`, and many OSD data types. It is the seam between `PG`/`PeeringState` and concrete object-storage protocols: replicated backends, EC switch/backends, scrub/repair, recovery reservations, OSD messaging, object contexts, and object store transactions all meet here.

## Risks
`Listener` is very large and assumes calls occur under the same PG locks as parent code. Mis-blessed contexts or lock misuse can race PG destruction or interval changes. The base class provides default false/no-op implementations for some EC-only methods; a concrete backend must override all methods relevant to its pool type. Temp object tracking must stay synchronized with actual temp collection contents or interval cleanup can leak objects. Omap behavior differs significantly between replicated and optimized EC pools, so callers must not assume local-object semantics for all backends.

## Test Signals
Interface tests should use mock listeners to verify callback ordering for recovery, transaction queueing, locking, and message sending. Concrete backend tests should cover replicated and EC transaction submission, recovery handles, message dispatch while inactive, interval cleanup, rollback/trim through `PGLogEntryHandler`, omap APIs, scrub scans/deep scrub, EC encode/decode and shard sizing, read paths, write ordering callbacks, and auto-repair support flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/PGBackend.h -->
