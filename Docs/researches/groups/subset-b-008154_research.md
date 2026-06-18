# subset-b-008154 research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/pool/srv_pool_check.c -->
# sources/object-store/daos/src/pool/srv_pool_check.c

## Purpose
`srv_pool_check.c` implements the server-side pool "glance" path used by DAOS check and catastrophic recovery logic. It inspects stopped local pool storage, captures VOS target presence/state and pool-service RDB clues, and analyzes whether a set of pool-service replicas can still elect a leader or needs catastrophic recovery bootstrap from a best replica.

## Important APIs, types, and functions
The public entry points are `ds_pool_clue_init`, `ds_pool_clue_fini`, `ds_pool_clues_init`, `ds_pool_clues_fini`, `ds_pool_clues_print`, `ds_pool_clues_find_rank`, and `ds_pool_check_svc_clues`. The key data contracts come from `struct ds_pool_clue`, `struct ds_pool_svc_clue`, `struct ds_pool_clues`, and `struct rdb_clue`. Internally, `pool_glance` opens the pool service RDB and loads `ds_pool_prop_label`, `ds_pool_svc_load` metadata, RDB membership, and map version. `compare_logs` compares RDB last term/index pairs independently of the volatile current term.

## Control flow
`ds_pool_clue_init` initializes one clue for a pool UUID on one local directory class. For normal directories it first scans every VOS target file with `ds_mgmt_file(..., VOS_FILE, ...)` and `stat`, classifying targets as nonexistent, empty, or normal. It then checks for the pool-service RDB path and, if present, delegates to `pool_glance`. `pool_glance` opens storage with `rdb_open`, calls `rdb_glance`, starts a local transaction, reads the label, and loads the service map version and RDB clue. Errors are stored in `pc_rc` while UUID/rank/dir remain valid for reporting.

`ds_pool_clues_init` walks normal, newborn, and zombie pool directories through management iterators. `glance_at_one` applies an optional phase-producing filter, grows the clue array, and records a clue for each accepted UUID. `ds_pool_check_svc_clues` then evaluates a nonempty set of service clues for one pool: first it tries to find any voting replica with a majority of voting members whose logs are not newer than its own; if no such candidate exists, it chooses the replica with the newest pool map version and, among those, newest RDB log for catastrophic recovery advice.

## State and persistence behavior
This file reads persistent state without starting the pool service. Persistent signals include target VOS file existence and size, pool labels in RDB, pool-map version, RDB replica membership, voted rank, log term/index, snapshot base term/index, and object ID state. It intentionally only glances service RDBs from the normal pool directory, while target clues also record newborn and zombie directory membership. It owns heap allocations for labels, target status arrays, RDB replica lists, and clue arrays; `ds_pool_clue_fini` and `ds_pool_clues_fini` release these.

## Dependencies and integration points
The code integrates the DAOS management storage layout, RDB storage API, pool service loader, DAOS check fail injection, and system xstream assumptions. Callers must invoke it on xstream 0 with local pools stopped, because it opens RDB files directly and scans target files rather than using live pool handles. The catastrophic recovery advice is later consumed by pool check/recovery orchestration to decide whether normal service startup is possible.

## Risks and test signals
The main risks are misclassifying local corruption as absence, leaking partially allocated clues on RDB/read errors, and choosing a stale replica during catastrophic recovery. The label length check is a deliberate corruption guard. The disabled in-file tests document expected `compare_logs` and `ds_pool_check_svc_clues` cases: single-replica membership, missing voters, insufficient quorums, conflicting map versions, and newer log tie-breaks. External tests should exercise stopped-pool scanning, missing target files, corrupt labels, absent RDBs, and mixed RDB membership where only some replicas can get a majority.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/pool/srv_pool_check.c -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/pool/srv_pool_chkpt.c -->
# sources/object-store/daos/src/pool/srv_pool_chkpt.c

## Purpose
`srv_pool_chkpt.c` owns the per-pool-target checkpoint ULT that drives VOS checkpointing for pools whose storage backend needs explicit checkpoints. It converts pool checkpoint properties and WAL usage notifications into periodic or threshold-based calls to `vos_pool_checkpoint`.

## Important APIs, types, and functions
The public API is `ds_start_chkpt_ult(struct ds_pool_child *child)` and `ds_stop_chkpt_ult(struct ds_pool_child *child)`. The central state is `struct chkpt_ctx`, which tracks the pool child, VOS handle, backing `umem_store`, current committed WAL ID, WAL wait ID, checkpoint thresholds, current/total used blocks, scheduler request, and an Argobots eventual. VOS callbacks are `update_cb` and `wait_cb`; scheduling helpers are `yield_fn`, `wait_fn`, `wake_fn`, and `need_checkpoint`.

## Control flow
`ds_start_chkpt_ult` starts only when `vos_pool_needs_checkpoint(child->spc_hdl)` is true. It creates a scheduler request with GC priority and deep stack, then launches `chkpt_ult`. The ULT initializes an ABT eventual, fills `chkpt_ctx`, and calls `vos_pool_checkpoint_init` with update and wait callbacks. Its loop calls `need_checkpoint`: disabled mode only sleeps, lazy mode checkpoints only on WAL block threshold, and timed mode checkpoints when either the threshold is crossed or the configured frequency elapses. When checkpointing is needed, it calls `vos_pool_checkpoint`, handles shutdown specially, logs other errors, and restarts the timer.

`wait_cb` is invoked by VOS when checkpointing must wait for WAL commitment. If the requested checkpoint transaction is already committed it yields to make scheduler progress, otherwise it records `cc_wait_id` and blocks on the eventual unless the store is faulty. `update_cb` records WAL usage and committed ID, wakes a sleeping ULT when block usage crosses threshold, and wakes a waiting checkpoint when the committed ID catches up or the store becomes faulty.

## State and persistence behavior
The persistent behavior is VOS pool checkpoint creation over WAL-backed storage. The ULT keeps only volatile scheduling state but reacts to persistent WAL usage counts and pool properties. Checkpoint parameters are read from `struct ds_pool`: `sp_checkpoint_mode`, `sp_checkpoint_freq`, and `sp_checkpoint_thresh`; threshold changes recalculate `cc_max_used_blocks`. `vos_pool_checkpoint_fini` unregisters callbacks before the eventual is freed.

## Dependencies and integration points
This file is started from pool-child startup in `srv_target.c` after VOS pool open and stopped during pool-child shutdown. It depends on scheduler request sleep/wakeup/yield, Argobots event synchronization, the VOS checkpoint API, `umem_store` WAL ID comparison, and pool property propagation. `ds_pool_tgt_prop_update` wakes this ULT when checkpoint properties change.

## Risks and test signals
Risks include missed wakeups between VOS callbacks and scheduler sleep, incorrect threshold recalculation when total blocks change, blocking forever if faulty-store or WAL ID updates are mishandled, and excessive checkpoint frequency under timed mode. Useful tests should vary checkpoint mode/frequency/threshold at runtime, simulate WAL usage crossing thresholds, verify shutdown unblocks waits, and confirm `vos_pool_checkpoint_fini` runs even after checkpoint errors.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/pool/srv_pool_chkpt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/pool/srv_pool_map.c -->
# sources/object-store/daos/src/pool/srv_pool_map.c

## Purpose
`srv_pool_map.c` applies target-state operations to an in-memory DAOS pool map and advances the map version only when actual target or rank-domain state changes occur. It is the shared state-transition engine behind exclude, drain, reintegrate, extend, rebuild finish, and rebuild revert paths.

## Important APIs, types, and functions
The exported function is `ds_pool_map_tgts_update(uuid_t pool_uuid, struct pool_map *map, struct pool_target_id_list *tgts, int opc, bool exclude_rank, uint32_t *tgt_map_ver, bool print_changes)`. Internal helpers are `update_one_tgt`, `update_one_dom`, `update_tgt_up_to_upin`, and `update_tgt_down_drain_to_downout`. It manipulates `struct pool_target`, `struct pool_domain`, `struct pool_target_id_list`, component status fields, component flags, in/out versions, failure sequence (`co_fseq`), and pool-map version.

## Control flow
`ds_pool_map_tgts_update` starts from the current pool-map version, iterates each requested target ID, resolves the `pool_target` and owning rank domain, applies `update_one_tgt`, then optionally updates the rank-domain state through `update_one_dom`. At the end it sets `*tgt_map_ver` to the highest target-related version or zero if no target changed, and updates the map's version only if the local version advanced.

`update_one_tgt` encodes the legal status machine. `MAP_EXCLUDE` moves UP/UPIN to DOWN and refuses NEW. `MAP_DRAIN` allows only UPIN to DRAIN and refuses NEW/UP. `MAP_REINT` moves DOWN/DOWNOUT to UP and records DOWN2UP when appropriate. `MAP_EXTEND` promotes NEW to UP. `MAP_ADD_IN` promotes UP to UPIN. `MAP_EXCLUDE_OUT` and `MAP_FINISH_REBUILD` finalize DOWN/DRAIN to DOWNOUT and UP to UPIN. `MAP_REVERT_REBUILD` reverses DRAIN or UP transitions back to their prior states using flags and fseq.

## State and persistence behavior
This file mutates an in-memory pool-map object; persistence happens later through the pool service that stores and broadcasts the map. Versioning is precise: `co_in_ver`, `co_out_ver`, and `co_fseq` record when targets entered or left active service, while the pool map's global version is only bumped after at least one real state change. Domain updates keep rank-level status consistent with target transitions, especially SWIM rank eviction and rebuild completion.

## Dependencies and integration points
Callers include pool-service map update logic in `srv_pool.c`, with declaration in `srv_pool_map.h`. The code depends on DAOS pool-map helpers such as `pool_map_find_target`, `pool_map_find_dom_by_rank`, `pool_map_node_status_match`, `update_dom_status_by_tgt_id`, and `pool_map_set_version`. It integrates with rebuild, reintegration, extension, drain, and SWIM exclusion workflows.

## Risks and test signals
The major risks are illegal state transitions, version increments on no-ops, rank-domain status drifting from target status, and incorrect rebuild revert behavior when `PO_COMPF_DOWN2UP` or `co_fseq` is involved. Tests should cover every operation/status pair, repeated idempotent requests, mixed target batches, nonexistent targets/ranks, `exclude_rank` domain updates, and `tgt_map_ver == 0` when no rebuild/reintegration ULT should be scheduled.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/pool/srv_pool_map.c -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/pool/srv_pool_map.h -->
# sources/object-store/daos/src/pool/srv_pool_map.h

## Purpose
`srv_pool_map.h` is the narrow internal header for server pool-map target updates. It exposes the state-transition function implemented in `srv_pool_map.c` to the rest of the pool server.

## Important APIs, types, and functions
The only declaration is `ds_pool_map_tgts_update`. It accepts a pool UUID, mutable `struct pool_map`, target ID list, map operation opcode, rank-eviction/domain-update flag, optional output target-map version, and print flag.

## Control flow
There is no executable control flow in this header. It exists to avoid exposing the implementation helpers while allowing pool-service code to update target states through one controlled API.

## State and persistence behavior
The header itself stores no state. The declared function mutates in-memory pool maps and returns enough version information for callers to decide whether downstream rebuild, drain, or reintegration work should run before the pool service persists or broadcasts the map.

## Dependencies and integration points
Consumers need the DAOS pool-map type definitions and target-list structures before including this header. The main integration point is pool-service map update handling in `src/pool/srv_pool.c`.

## Risks and test signals
The risk is interface drift: operation semantics, `evict_rank`, or `tgt_map_ver` behavior must remain synchronized with the implementation and callers. Build coverage catches signature drift; behavioral coverage belongs to tests around `ds_pool_map_tgts_update`.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/pool/srv_pool_map.h -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/pool/srv_pool_scrub_ult.c -->
# sources/object-store/daos/src/pool/srv_pool_scrub_ult.c

## Purpose
`srv_pool_scrub_ult.c` starts, stops, and wires the per-pool-target checksum/tree scrubber ULT. It adapts VOS scrub callbacks to DAOS pool/container state, telemetry, scheduler yielding/sleeping, and automatic target drain on detected corruption or policy decisions.

## Important APIs, types, and functions
The exported functions are `ds_start_scrubbing_ult` and `ds_stop_scrubbing_ult`. The main ULT is `scrubbing_ult`. Callback helpers include `cont_lookup_cb`, `cont_put_cb`, `cont_is_stopping_cb`, `drain_pool_tgt_cb`, `drain_pool_tgt_ult`, and `is_idle`. `sc_add_pool_metrics` creates telemetry counters/gauges/timestamps for completed scrubs, checksum calculations, bytes scrubbed, corruption, duration, busy time, and next-scrub timing under `pool_path/tgt_ID/scrubber/...`.

## Control flow
`ds_start_scrubbing_ult` checks the `DAOS_CSUM_SCRUB_DISABLED` environment variable and, if enabled, creates a deep-stack `SCHED_REQ_SCRUB` ULT. `scrubbing_ult` fills a `struct scrub_ctx` with the VOS pool handle, pool pointer, scheduler callbacks, container lookup/put callbacks, idle test, telemetry pointers, and drain callback. It then repeatedly calls `vos_scrub_pool`; normal iterations sleep for one second, errors sleep for one minute, pool shutdown exits, and `-DER_SHUTDOWN` exits immediately.

When VOS needs a container, `cont_lookup_cb` looks up the pool/container child, copies checksum state and handle into `struct cont_scrub`, and marks the container as scrubbing under its mutex. `cont_put_cb` clears that flag, broadcasts the scrub condition variable, and drops the container reference. If drain is needed, `drain_pool_target` builds an UP/UPIN/NEW rank list and calls `dsc_pool_svc_update_target_state` to transition the local rank/target to DRAIN through the pool service.

## State and persistence behavior
The ULT does not directly persist scrub progress. It drives VOS traversal and checksum verification through `vos_scrub_pool`, updates in-memory container `sc_scrubbing` state to coordinate with container stop, and records process telemetry counters. Drain actions change pool-map target state through the pool service, which is persistent and broadcast to the cluster.

## Dependencies and integration points
This file integrates pool-child startup/shutdown, VOS scrub implementation, container child lookup, server checksum state, Argobots mutex/condition synchronization, telemetry producer APIs, rank discovery, and pool-service target-state update RPCs. It is started by `pool_child_start` only for unrestricted pools and stopped before pool-child reference drain during shutdown.

## Risks and test signals
Risks include stale container scrubbing flags if lookup/put paths are unbalanced, telemetry path format drift that breaks Prometheus label extraction, blocking or racing while draining a target from within scrub context, and repeatedly hammering VOS after persistent scrub errors. Tests should verify scrub ULT disablement, start/stop behavior, metric creation, container stop waiting on `sc_scrubbing`, corruption-to-drain behavior, and clean shutdown while `vos_scrub_pool` is active.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/pool/srv_pool_scrub_ult.c -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/pool/srv_target.c -->
# sources/object-store/daos/src/pool/srv_target.c

## Purpose
`srv_target.c` is the target-side runtime for DAOS pools. It owns per-xstream `ds_pool_child` objects, system-xstream `ds_pool` objects, pool handle caching, VOS pool open/close, maintenance ULTs, map/property propagation, target query RPCs, target discard/reintegration cleanup, warmup bulk transfer, and container recovery after target/device replacement.

## Important APIs, types, and functions
Important exported APIs include `ds_pool_child_find`, `ds_pool_child_lookup`, `ds_pool_child_put`, `ds_pool_child_state`, `ds_pool_child_start`, `ds_pool_child_stop`, `ds_pool_cache_init/fini`, `ds_pool_lookup[_internal]`, `ds_pool_get/put`, `ds_pool_start`, `ds_pool_stop`, `ds_pool_hdl_hash_init/fini`, `ds_pool_hdl_lookup`, `ds_pool_tgt_connect`, `ds_pool_tgt_disconnect`, `ds_pool_tgt_map_update`, `ds_pool_tgt_prop_update`, `ds_pool_lookup_map_bc`, `ds_pool_put_map_bc`, `ds_pool_srv_open`, `ds_pool_tgt_query_handler`, `ds_pool_tgt_query_map_handler`, `ds_pool_tgt_discard_handler`, `ds_pool_tgt_warmup_handler`, and `ds_pool_recov_cont_handler`.

Core types include `struct ds_pool_child`, `struct ds_pool`, `struct ds_pool_hdl`, `struct ds_pool_map_bc`, `struct pool_query_xs_arg`, `struct tgt_discard_arg`, and `struct pool_recov_cont_args`. Internal ULTs include GC, flush, EC epoch reporting, discard, and recovery work.

## Control flow
Pool startup begins on system xstream in `ds_pool_start`: it creates or holds a `ds_pool` in the LRU cache, initializes pool-wide locks/groups/IV namespace/metrics, creates pool children on target xstreams through `pool_child_add_all`, starts the EC epoch-report ULT for unrestricted pools, starts the IV namespace, and starts the pool service. Each child created by `pool_child_create` initializes per-target metrics and points `spc_state` into the pool's state array. `pool_child_start` optionally recreates storage, opens the VOS pool with external flush/checkpoint flags, applies VOS feature flags to pool-level disable/immutable state, starts GC/flush/scrub/checkpoint ULTs, and starts all container children.

Pool shutdown reverses the flow. `ds_pool_stop` marks the pool stopping, stops the pool service, disconnects all target handles, stops IV and EC reporting, aborts rebuild/migration, waits until the LRU has no other users, deletes pool children, and releases the start reference. `pool_child_stop` transitions to STOPPING, stops container children and server container handles, stops scrub, waits for outstanding child references, stops checkpoint/GC/flush, closes VOS, and returns the child to NEW.

Map updates arrive through `ds_pool_tgt_map_update`, which creates a new pool map from a buffer, updates the CRT secondary group, placement map, failed-target counts, cached bulk map, pool map version, per-child map version, and optionally launches DTX resync. Property updates through `ds_pool_tgt_prop_update` cache IV properties in `ds_pool`, collectively applies VOS controls/upgrades to children, wakes checkpoint ULTs when checkpoint properties change, and asks the pool service to upgrade VOS pools.

Query/disconnect/map RPC handlers validate pool handles, query local or aggregate VOS space, combine results across ranks, transfer pool maps through bulk handles, and invalidate IV connection state on disconnect. Discard and recovery flows use asynchronous ULTs and collectives: discard iterates local containers and objects with VOS iterators and calls `vos_discard`; recovery bulk-fetches the authoritative container list, creates missing container children, builds a temporary dbtree, and destroys orphan shards under `sp_recov_lock`.

## State and persistence behavior
Persistent state is primarily VOS pool/container data, VOS durable format version, pool map/properties persisted by the pool service, SMD pool/device metadata, and IV namespace state. Volatile state includes LRU pool objects, pool-child lists in TLS, pool-handle hash entries, CRT secondary groups, cached pool-map bulk descriptors, scheduler requests, child reference counts, stopping flags, and discard/recovery status. The code carefully sequences reference waits before VOS close and uses locks (`sp_lock`, `sp_mutex`, `sp_recov_lock`) around map/properties/recovery-sensitive state.

## Dependencies and integration points
This file integrates most pool target subsystems: VOS, BIO/SMD, container children, pool service, rebuild/migration, DTX resync, IV namespace, placement map, CRT groups and bulk transfer, telemetry, Argobots, scheduler request classes, and management storage paths. It calls into `srv_pool_scrub_ult.c` and `srv_pool_chkpt.c` for scrub/checkpoint ULTs, and uses utilities from `srv_util.c` for collectives and rank/target filtering.

## Risks and test signals
The highest risks are lifecycle races: starting while stopping, child references held during shutdown, map updates racing with handle fetch and EC reporting, stale pool-map bulk handles, discard/recovery overlap with rebuild/reintegration, and partial storage loss where `spc_no_storage` must let DAOS check proceed. Test signals should include pool start/stop idempotence, VOS open failure and lost-shard handling, GC/flush/scrub/checkpoint ULT cleanup, handle lookup retry behavior before IV handle fetch completes, aggregate space query correctness, map bulk truncation and update ordering, property propagation to VOS, target discard retries under busy objects, and recovery creating missing containers while deleting orphans.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/pool/srv_target.c -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/pool/srv_util.c -->
# sources/object-store/daos/src/pool/srv_util.c

## Purpose
`srv_util.c` provides shared pool-server utility logic: rank and target list construction from pool maps, collective/broadcast helpers, pool-map bulk transfer, pool-service replica reconfiguration planning, target-state lookup, failed-target discovery, and NVMe faulty/reintegration reactions.

## Important APIs, types, and functions
Public APIs include `map_ranks_init`, `map_ranks_failed`, `map_ranks_fini`, `ds_pool_map_rank_up`, `ds_pool_bcast_create`, `ds_pool_transfer_map_buf`, `ds_pool_plan_svc_reconfs`, `ds_pool_get_ranks`, `ds_pool_get_tgt_idx_by_state`, `ds_pool_get_failed_tgt_idx`, `ds_pool_thread_collective[_reduce]`, `ds_pool_task_collective[_reduce]`, and the exported `nvme_reaction_ops`. Internal planning types are `struct reconf_domain` and `struct reconf_map`; NVMe reaction state uses `struct update_targets_arg`.

## Control flow
Rank helpers scan the pool map's rank domains and produce `d_rank_list_t` values matching requested component states. `ds_pool_bcast_create` builds an excluded-rank list from DOWN/DOWNOUT ranks plus optional caller exclusions, then creates a CORPC request over the pool group. `ds_pool_transfer_map_buf` validates remote bulk size, then performs a bulk PUT of a cached pool-map buffer and reports `-DER_TRUNC` with the required size when needed.

Pool-service reconfiguration planning starts with `compute_svc_reconf_objective`, initializes an ephemeral map of desired domains and existing replicas through `init_reconf_map`, removes undesired/out-of-map replicas, adds replacements with randomized but balanced domain selection, removes excess replicas from crowded domains, and finally calls `balance_replicas` to improve distribution. `filter_only` short-circuits after identifying undesired replicas.

Collective helpers build a bitmap of excluded local target indexes based on pool-map target states and dispatch thread or task collectives. NVMe reactions are intentionally asynchronous relative to hardware polling. `nvme_reaction` lists SMD pools, optionally starts affected pool children for reintegration, checks whether affected targets are already in the expected pool-map state, submits client-side exclude/reintegrate requests to the pool leader when needed, and tears down targets after successful faulty exclusion. System target failure kills the engine; system target auto-reintegration is rejected.

## State and persistence behavior
Most functions read volatile cached pool maps and return heap-allocated rank/target lists to callers. Broadcast and map bulk helpers operate over CRT/IV state without modifying persistence. Service reconfiguration planning is pure except for random placement decisions. NVMe reaction paths change persistent/cluster-visible state indirectly through pool service target exclude/reintegrate RPCs and local pool-child start/stop, reflecting SMD device replacement or failure state.

## Dependencies and integration points
The file depends on pool-map traversal APIs, CRT CORPC/bulk APIs, Argobots event synchronization, SMD pool lists, BIO reaction hooks, DAOS client pool target update calls, and target-child lifecycle APIs from `srv_target.c`. `srv_pool_scrub_ult.c` uses `ds_pool_get_ranks` for drain destinations; `srv_target.c` uses collective helpers and target-index filtering; pool service code uses reconfiguration planning for service replica membership.

## Risks and test signals
Risks include rank-list leaks, empty-map handling, excluding the wrong local targets from collectives, reconfiguration imbalance or attempts to remove the current leader from an undesired state, nondeterminism from randomized placement, and NVMe reaction loops that repeatedly send exclude/reint while pool maps are stale. The disabled in-file unit tests define many service-reconfiguration edge cases. Additional tests should cover down ranks, all-targets-down rank failure classification, bulk truncation, collective target bitmaps, SMD/pool-map inconsistency tolerance, system target failure policy, and reint/faulty transitions returning 0/1/error according to `bio_reaction_ops`.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/pool/srv_util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/vos/evt_iter.c -->
# sources/object-store/daos/src/vos/evt_iter.c

## Purpose
`evt_iter.c` implements evtree iterators for VOS extent trees. It prepares embedded or cloned iterator handles, probes first or matching extents, iterates forward/backward through visible/covered/raw records, fetches entries and anchors, deletes the current raw entry, and marks the current record corrupted for scrub/check paths.

## Important APIs, types, and functions
The exported APIs are `evt_iter_prepare`, `evt_iter_finish`, `evt_iter_probe`, `evt_iter_next`, `evt_iter_empty`, `evt_iter_delete`, `evt_iter_corrupt`, and `evt_iter_fetch`. Important helpers are `evt_validate_options`, `evt_iter_is_sorted`, `evt_iter_probe_sorted`, `evt_iter_probe_find`, `evt_iter_move`, `evt_iter_is_ready`, `evt_iter_intent`, `should_skip`, and `ent_array_reset`. It uses `struct evt_iterator`, `struct evt_context`, `struct evt_filter`, `struct evt_rect`, `struct evt_entry_array`, and `daos_anchor_t`.

## Control flow
`evt_iter_prepare` validates skip options, converts the tree handle to an `evt_context`, either reuses the embedded context iterator or clones the context, initializes default extent/epoch filters, direction, options, and state. Sorted iterators are used for visible or covered iteration and fill `it_entries`; raw iterators walk the tree trace directly.

`evt_iter_probe` resets the entry array, then either calls `evt_iter_probe_sorted` or performs a tree search using `EVT_FIND_FIRST`/`EVT_FIND_SAME`. Sorted probing fills all matching entries, sorts/filters by visibility, chooses first/last or binary-searches from an anchor rectangle, and skips unavailable or hole/data entries as requested. Raw probing fills the array for a first/same search, checks the current descriptor's DTX availability, and establishes READY or FINI state. `evt_iter_next` advances by array index or by `evt_move_trace`, honoring `it_skip_move` after deletion.

`evt_iter_fetch` validates READY state and copies either the sorted entry or the raw node entry into the caller's `evt_entry`, fills in bytes-per-record, and writes an anchor containing the current rectangle. `evt_iter_delete` is only supported for raw iterators; it optionally fetches the entry, starts a transaction, deletes the current leaf node entry, adjusts iterator state/trace, and avoids moving twice by setting `it_skip_move`. `evt_iter_corrupt` transactionally sets the current descriptor's bio address corrupted flag.

## State and persistence behavior
Iterator state is volatile in `tc_iter`: state enum, options, direction, index, filters, entry array, and trace position. Deletion and corruption are persistent mutations when the underlying `umem_instance` has transactions; they use `evt_tx_begin`, `umem_tx_add`, `evt_node_delete`, and `evt_tx_end`. Anchors serialize `struct evt_rect` into `daos_anchor_t`, so anchor compatibility is enforced with a compile-time size assert.

## Dependencies and integration points
The iterator depends on lower evtree primitives in `evt_priv.h` and sibling implementation files: context handle conversion, context cloning/refcounting, trace movement, entry-array fill/sort, descriptor availability checks, node/descriptor access, transaction helpers, and checksum/entry fill utilities. It is used by VOS query/object paths and heavily exercised by `src/vos/tests/evt_ctl.c`, including delete, anchor, visible, covered, and raw iteration cases.

## Risks and test signals
Risks include misuse of skip options, sharing embedded iterators across references, binary-search off-by-one errors for reverse anchors, stale anchors after aggregation/clipping returning the wrong error, skipping unavailable DTX records incorrectly for purge/discard/migration/check intents, and corrupt/delete transaction offset mistakes. Tests should cover visible and covered sorted iteration, reverse iteration, skip holes/data, anchor find returning `-DER_AGAIN` when raw records changed, raw delete of first/middle/last records, corruption marking, unavailable DTX filtering, and iterator finish/refcount cleanup.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/vos/evt_iter.c -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/vos/evt_priv.h -->
# sources/object-store/daos/src/vos/evt_priv.h

## Purpose
`evt_priv.h` defines the private evtree implementation contract shared by VOS event-tree source files. It contains durable-format constants, iterator/context structures, transaction helpers, rectangle filtering helpers, node/descriptor accessors, checksum helper declarations, search opcodes, context handle operations, and internal tree traversal/manipulation declarations.

## Important APIs, types, and functions
Key constants include `EVT_TX_MINOR_MAX_DF`, rebuild minor epoch ranges, node flags `EVT_NODE_LEAF`/`EVT_NODE_ROOT`, iterator states, `MAX_RECT_WIDTH`, `EVT_TRACE_MAX`, null offsets, node magic, and handle magic values. Core types are `struct evt_iterator`, `struct evt_trace`, `struct evt_context`, `struct evt_extent`, and `enum evt_find_opc`.

Important inline helpers include `evt_off2node`, `evt_off2desc`, `evt_tx_begin`, `evt_tx_end`, `evt_tcx_addref`, `evt_tcx_decref`, `evt_filter_rect`, `evt_epoch_uncertain`, `evt_ent2rect`, `evt_nd_off_rect_read_at`, `evt_node_is_leaf`, `evt_node_is_root`, `evt_node_entry_at`, `evt_node_desc_at`, and `evt_entry_punched`. Declared implementation hooks include descriptor checksum helpers, `evt_tcx_clone`, `evt_node_delete`, `evt_ent_array_sort`, `evt_ent_array_fill`, `evt_rect_cmp`, `evt_tcx2hdl`, `evt_hdl2tcx`, `evt_move_trace`, `evt_node_rect_read_at`, `evt_entry_fill`, and `evt_dtx_check_availability`.

## Control flow
The header has no standalone execution, but it shapes evtree control flow. Open contexts cache durable root metadata, tree order/depth, feature bits, umem instance, policy ops, descriptor callbacks, embedded iterator storage, and scratch trace space. Iterators use filters with extent and epoch ranges, options, direction, index, and sorted entry arrays. Traversal code uses trace entries from root to leaf, converts umem offsets to durable nodes/descriptors, filters rectangles differently for internal nodes versus leaf records, and delegates transaction boundaries to inline helpers.

## State and persistence behavior
`struct evt_context` bridges volatile handle state and persistent evtree state: it points at the durable root and umem pool while caching order/depth/features to reduce persistent reads. Node and descriptor helpers assert durable magic values. `evt_tx_begin`/`evt_tx_end` only create PMDK/umem transactions when the tree's umem instance supports transactions, preserving compatibility with DRAM and persistent backends. Minor epoch constants reserve upper bits for normal, rebuild, distributed transaction, and future record classes, which affects durable ordering and rebuild visibility.

## Dependencies and integration points
The header depends on public evtree declarations and VOS internals. It is consumed by evtree implementation files such as iterator, insert, delete, find, and tests. It integrates with VOS punch semantics, DTX availability checks, checksum layout, BIO address state, umem transactions, policy callbacks, and DAOS epoch/extent types.

## Risks and test signals
Risks include durable-format compatibility mistakes in minor epoch ranges, `MAX_RECT_WIDTH` violations, incorrect context refcount cleanup for embedded iterator arrays, filtering internal nodes too aggressively, transaction abort/commit misuse, and offset-to-pointer assertions masking corrupt persistent state. Tests should validate handle lifetime, PMEM and non-PMEM transaction paths, punch filtering, rebuild minor epoch ordering, checksum count/buffer calculations, node accessor invariants, and interoperability with `evt_iter.c` anchor/fetch/delete behavior.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/vos/evt_priv.h -->
