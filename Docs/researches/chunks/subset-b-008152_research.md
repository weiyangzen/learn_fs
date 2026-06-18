# sources/object-store/daos/src/pool/srv_pool.c lines 1-9038

## Chunk Scope

This chunk covers the main body of the DAOS pool service implementation from the file header through the beginning of `pool_attr_del_handler`. It includes pool service metadata creation and loading, replicated service lifecycle callbacks, pool connect/disconnect/query/property/ACL/upgrade RPC handlers, duplicate metadata operation tracking, pool map mutation and service replica reconfiguration, rebuild/reintegration integration, rank eviction, and rank-list transfer helpers. The final lines stop mid-function in `pool_attr_del_handler`; its completion belongs to the next chunk.

## Purpose

`srv_pool.c` implements the server-side pool service (PS), the replicated metadata authority for a DAOS pool. In this chunk it owns durable pool metadata in RDB, coordinates the in-memory `ds_pool` cache and IV distribution, handles client and management RPCs, and translates pool membership changes into pool map commits and rebuild/reconfiguration work.

The file is not just an RPC switchboard. It manages a multi-layer state machine:

- RDB stores the authoritative pool map, properties, handle records, user attributes, operation replay records, server handles, and upgrade status.
- `ds_rsvc` provides replicated-service leadership, leader lookup, map distribution, replica add/remove, and stop/start semantics.
- `ds_pool` caches the pool map/properties and exposes IV namespaces to local targets.
- Container service state is co-located with the pool service and stepped up/down with the pool leader.
- Rebuild and self-heal are scheduled after map updates, SWIM rank-death events, or management operations.

## Important Types and State

- `struct pool_svc` is the central service object. It embeds `struct ds_rsvc`, stores the pool UUID, the associated `struct ds_pool`, combined container service pointer, RDB paths (`ps_root`, `ps_handles`, `ps_user`, `ps_ops`), a metadata rwlock, event state, cached pool-space state, global layout version, service redundancy factor, duplicate-op settings, and two cancellable schedulers for service reconfiguration and container RF checking.
- `struct pool_svc_events` and `struct pool_svc_event_set` collect CaRT rank events. Events are coalesced by rank so the latest event wins. The handler delays processing by `CRT_EVENT_DELAY` and can pause/retry if exclusion fails.
- `struct pool_svc_sched` is a small Argobots-based scheduling guard. It serializes/cancels background ULTs (`ps_reconf_sched`, `ps_rfcheck_sched`) and lets step-down wait for completion.
- `struct pool_space_cache` caches aggregate pool-space query results for `ps_cache_intvl`.
- `struct pool_svc_failed` records pools that failed local startup and makes `pool_svc_lookup_leader` fail fast with `-DER_NO_SERVICE`.
- Durable RDB keys used in this chunk include pool map version/buffer, connectable flag, open handle count, handle KVS, user attribute KVS, pool properties, duplicate service-op KVS, server pool/container handles, upgrade global version/status, object layout version, and container-recovery marker.

## Metadata Creation and Loading

`init_pool_metadata` builds the initial pool map with `gen_pool_buf`, applies user-supplied properties on top of `pool_prop_default`, adjusts default redundancy factor if the domain tree cannot satisfy it, writes the pool map and properties, marks the pool connectable, creates handle/user-attribute/service-op KVSs, initializes handle counters, duplicate-op limits, and server pool/container handles.

`write_map_buf`, `locate_map_buf`, `read_map_buf`, and `read_map` are the core RDB pool-map accessors. They persist both map version and serialized `pool_buf`, and convert between the serialized buffer and a live `pool_map`.

`pool_prop_write` and `pool_prop_read` are the property translation layer between `daos_prop_t` and RDB keys. They enforce version-gated properties and value validation for EC cell size, data threshold, EC/RP PDA, global layout version, object layout version, checkpoint bounds, and service-op settings. `pool_prop_read` synthesizes default/not-set entries for older global versions.

`ds_pool_svc_load` validates the stored pool global version against the software-supported `DAOS_POOL_GLOBAL_VERSION`, emits a RAS event for incompatible downgrades, and loads the durable map. A missing map plus missing version is treated as a new uninitialized DB.

## Service Lifecycle

Pool services are RDB-backed replicated services:

- `ds_pool_svc_dist_create` selects service replicas from a generated map, starts distributed `DS_RSVC_CLASS_POOL` replicas, then issues `POOL_CREATE` through an `rsvc_client` with retry/rechoose behavior.
- `ds_pool_svc_start` checks for a local RDB file before starting a local replica. `ds_pool_svc_stop` stops a local service replica without destroying storage.
- `pool_svc_alloc_cb` allocates and wires `struct pool_svc`, initializes RDB paths, locks, event primitives, schedulers, and the co-located container service.
- `pool_svc_step_up_cb` is the leader activation path. It waits for primary group initialization, reads DB state, updates `ds_pool`, requests map distribution, steps up the container service, loads self-heal policy, initializes event handling, schedules service reconfiguration/RF check, pushes properties/handles/server handles into IV, resumes upgrade if needed, regenerates rebuild tasks, and initializes telemetry.
- `pool_svc_step_down_cb` clears leader metrics, stops event handling, cancels scheduled work, steps down the container service, and clears persistent `ps_error` state if the leader was serving a DB-layout error.
- `pool_svc_map_dist_cb` is the replicated-service callback that reads the committed map from RDB and distributes it through IV.

`pool_svc_lookup_leader` is the common RPC entry gate. It rejects failed pools, resolves the current leader, and propagates persistent pool-service data errors quickly instead of letting clients time out.

## Event Handling and Self-Heal

CaRT rank events are registered on leader step-up unless the pool is in restricted/check mode. `queue_event` inserts or overwrites per-rank entries, wakes the event ULT, and updates the debounce timestamp. `events_handler` waits until the debounce deadline, processes an event set, and on failure puts the set back and pauses until another event or map change resumes it.

`handle_event` delegates dead-rank processing to `pool_svc_exclude_ranks` unless exclusion is globally disabled. It also handles alive events by restarting WIP rebuild tasks for UPIN ranks and requesting map distribution for ranks already up in the pool map.

`pool_svc_check_node_status` runs at event initialization and queues dead events for UPIN ranks whose SWIM/group status is missing or dead. `ds_pool_eval_self_heal_handler` resumes event handling when system and pool self-heal policies allow pool exclusion, and resumes rebuild through `ds_rebuild_admin_start` when rebuild policy allows it.

## Duplicate Write Operation Tracking

This chunk implements idempotent metadata-write RPC handling via the `ps_ops` RDB KVS:

- `pool_op_is_write` excludes read-only and non-service operations from tracking.
- `ds_pool_svc_ops_lookup` encodes `(client UUID, client HLC time)` into a `ds_pool_svc_op_key` and returns stored `ds_pool_svc_op_val` for duplicate/retry RPCs.
- `ds_pool_svc_ops_save` stores definitive non-retryable operation results and maintains `ds_pool_prop_svc_ops_num`.
- `pool_op_check_delete_oldest` trims the lexical KVS when count or age exceeds configured limits.
- `pool_op_lookup` and `pool_op_save` wrap this for pool RPC handlers.

Several handlers include fault-injection branches (`DAOS_MD_OP_PASS_NOREPLY`, `DAOS_MD_OP_FAIL_NOREPLY`, and new-leader variants) to validate replay/idempotency under reply loss or leader changes.

## RPC Control Flow

Most write handlers follow the same pattern: locate leader, begin RDB transaction, take `ps_lock` for write, call `pool_op_lookup`, skip mutations on duplicates/fault injection, perform mutation, call `pool_op_save`, commit, update IV/metrics if needed, release lock/transaction, set leader hint, and reply.

Important handlers in this chunk:

- `ds_pool_create_handler` initializes an empty RDB root and container metadata. It can trigger a campaign for first-create optimization and transitions the rsvc from `UP_EMPTY` to `UP`.
- `pool_connect_handler` validates connectability, check-mode readiness, immutable pool flags, handle uniqueness/exclusive-handle rules, layout compatibility with client, ACL-derived capabilities, and origin machine. It distributes the handle via IV, writes the handle record, increments handle count/metrics, transfers the map buffer, and optionally queries space.
- `pool_disconnect_handler` closes containers by pool handles, broadcasts target disconnect, removes handles from RDB, updates handle counts/metrics, and is duplicate-op protected.
- `ds_pool_evict_handler` validates an explicit handle list or finds handles by machine/all, disconnects them, and on pool destroy marks `connectable=0`, invalidates server handles, and stops the IV namespace leader.
- `pool_query_handler`, `pool_query_info_handler`, `ds_pool_prop_get_handler`, `ds_pool_prop_set_handler`, `ds_pool_acl_update_handler`, and `ds_pool_acl_delete_handler` cover read/write metadata queries, map transfer, target space query, property IV update, ACL merge/removal, and rebuild status inference.
- `pool_list_cont_handler`, `pool_filter_cont_handler`, and `ds_pool_svc_list_cont` bridge pool service RPCs to the container service and transfer results through bulk handles with `-DER_TRUNC` retry semantics.
- `ds_pool_ranks_get_handler` is server-to-server only and returns available ranks by bulk transfer.
- `ds_pool_rebuild_stop_handler`, `ds_pool_rebuild_start_handler`, and exported helpers call rebuild admin stop/start under PS leadership.
- `pool_attr_set_handler` is fully covered and writes user attributes through `ds_rsvc_set_attr`. `pool_attr_del_handler` starts at the end of this chunk and continues later.

## Pool Map Mutation and Reconfiguration

`pool_svc_update_map_internal` is the authoritative map update path. It begins an RDB transaction, optionally checks pool self-heal exclusion policy, handles incremental reintegration container-recovery flags, creates a temporary map from the committed map, resolves target addresses to IDs, applies `ds_pool_map_tgts_update`, rejects/removes leadership if the update excludes the current service rank, enforces RF checks for excludes, writes the new map to RDB, synchronously removes undesired PS replicas before commit, commits, updates local `ds_pool`, requests map distribution, resumes paused event handling, schedules async PS reconfiguration, schedules RF check for excludes, and updates telemetry.

`pool_svc_update_map` wraps that path with system self-heal policy checks and rebuild scheduling. It uses `REBUILD_ENV`, fail injection, pool self-heal flags, reintegration mode, delayed rebuild policy, and target-map-version output to decide whether and when to call `ds_rebuild_schedule`.

Management and internal wrappers include:

- `ds_pool_extend_handler` discards rank state, extends the pool map, and skips RF check.
- `pool_update_handler` handles exclude/drain/reintegrate style target updates, invoking discard or container recovery for reintegration depending on `sp_reint_mode`.
- `pool_svc_exclude_ranks` converts dead rank events into rank-wide exclude map updates.
- `ds_pool_tgt_exclude_out`, `ds_pool_tgt_add_in`, `ds_pool_tgt_finish_rebuild`, and `ds_pool_tgt_revert_rebuild` expose internal target state transitions.

`pool_svc_reconf_ult` maintains the service-replica set according to `ps_svc_rf` and the current/provided map. It waits for pending events unless doing synchronous removal, plans add/remove lists with `ds_pool_plan_svc_reconfs`, adds replicas using the current RDB size and VOS DF version, removes replicas, notifies the management service of replica changes, and eventually destroys removed replicas outside synchronous-remove mode. `pool_svc_schedule_reconf` suppresses stale schedule requests by comparing map versions.

## Upgrade Behavior

Upgrade state is modeled by `ds_pool_prop_upgrade_global_version`, `ds_pool_prop_upgrade_status`, and current global/object layout versions. `ds_pool_upgrade_if_needed` distinguishes management-command upgrades from leader-step-up resume and handles not-started, in-progress, completed, and failed states.

`pool_upgrade_props` is the metadata migration routine. It evicts existing handles for management-triggered upgrades, marks the pool non-connectable, backfills missing properties, creates or recreates the service-op KVS when needed, enables duplicate-op tracking only if RDB size is large enough, initializes server handles, commits changed metadata, updates cached duplicate-op settings, and refreshes property IV.

Object-layout upgrade is scheduled through `pool_check_upgrade_object_layout` as a rebuild `RB_OP_UPGRADE`. If no layout upgrade is scheduled, `ds_pool_mark_upgrade_completed_internal` upgrades containers and `__ds_pool_mark_upgrade_completed` marks success/failure, bumps global/object layout versions on success, restores connectability, and updates property IV.

## Persistence and Concurrency

The authoritative state changes happen under RDB transactions and `ps_lock`. Read paths use `ABT_rwlock_rdlock`; write paths use `ABT_rwlock_wrlock`. The code is careful to commit RDB before updating local caches, and resigns leadership if the local map cache cannot be updated after a successful commit.

IV is used as the distribution/cache layer for pool maps, properties, pool handles, server handles, and namespace leadership. Map distribution is requested after leader step-up and committed map updates. Property IV is updated after property writes and upgrades. Handle IV is updated on connect and invalidated on destroy.

Background ULTs are explicitly cancellable and step-down waits for them. Event handling has a retry/pause loop to avoid losing exclusion events. Pool-space caching is protected by its own mutex and only used when `ps_cache_intvl > 0`.

## Dependencies and Integration Points

Primary dependencies visible in this chunk:

- RDB APIs: transactions, KVS create/destroy/update/delete/fetch/iterate, rank membership, leader hints, RDB size, resign/campaign.
- Replicated service APIs: `ds_rsvc_*`, `rsvc_client_*`, distributed start/stop/add/remove, map distribution.
- Pool map APIs: `pool_map_create`, `pool_buf_extract`, `pool_map_extend`, target/rank lookup, state updates, RF failure counts.
- Security APIs: ACL validation/merge/removal, credential origin, pool capability checks.
- Container service APIs: combined service step-up/down, metadata init, list/filter, RF check, close handles, upgrade.
- Rebuild APIs: query, regenerate, schedule, admin stop/start, restart WIP rank.
- CaRT/DAOS RPC and bulk APIs for client RPCs, CORPC broadcasts, rank/cont/map transfers, and event callbacks.
- Telemetry/RAS integrations for metrics, pool start failure, incompatible DF version, and service-replica notifications.

## Risks and Edge Cases

- Map updates commit durable state before local cache update; failure afterward forces leader resignation, but clients may see transient leadership churn.
- `pool_svc_update_map_internal` must coordinate RF checks, self-removal, service replica removal, rebuild scheduling, and event resumption. Small ordering bugs here can cause unavailable service replicas or stale maps.
- Duplicate-op tracking depends on client UUID/time uniqueness and on enough RDB capacity. It is disabled for old pools or small RDBs, so retry behavior differs by layout/version/capacity.
- Upgrade disables new connections and evicts handles. Partial failures leave explicit failed/in-progress status and preserve old global version, but the pool may need management intervention.
- `pool_prop_read` and `pool_prop_write` carry many version gates and defaulting paths. Missing or incorrectly typed properties can break older-pool compatibility.
- Event handling coalesces by rank; this is intentional, but alive/dead races rely on latest-event semantics plus pool-map status checks.
- Pool service self-exclusion handling resigns when possible but rejects if this is the only replica. Tests should exercise single-replica and multi-replica cases.
- Container list/filter handlers include unbraced `if (rc == -DER_NONEXIST) rc = -DER_NO_HDL;` followed by a comment. It is functionally intentional because unlock/tx-end is deferred, but visually easy to misread.
- This chunk ends before `pool_attr_del_handler` completes, so final attribute delete/list/get behavior must be reconciled with the next chunk.

## Test Signals

Useful validation signals for this chunk include:

- Pool create/connect/disconnect/evict/property/ACL RPC tests with duplicate RPC replay and no-reply fault injection.
- Layout upgrade tests that cover not-started, in-progress resume, failed retry, object-layout rebuild scheduling, and post-upgrade connectability.
- Pool map update tests for exclude, exclude-out, add-in, drain, reintegrate, extend, invalid target address reporting, RF rejection, current-leader self-removal, and rebuild scheduling policy.
- SWIM/group event tests that verify dead-rank coalescing, pause/resume after failed exclude, alive-rank map distribution, and rebuild restart for WIP ranks.
- Service-reconfiguration tests for replica add/remove, stale schedule suppression, synchronous removal before map commit, management notification, and failure of replica operations.
- Property compatibility tests for older global versions and missing KVS/properties, especially service-op KVS migration and server-handle migration.
- Bulk transfer tests for map, container list/filter, ranks, and `-DER_TRUNC` retry flows.
- Metrics/telemetry checks for leader, map version, open handles, target/rank counts, connect/disconnect/evict/query counters, and degraded rebuild status.
