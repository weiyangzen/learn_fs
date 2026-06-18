# Research: subset-b-008223

This grouped report covers the OpenStack Swift container replication, server, sharding, sync, sync-store, updater, and object package marker files assigned to subset-b-008223. Each file section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/container/replicator.py -->
# sources/object-store/openstack-swift/swift/container/replicator.py

## Purpose

`swift/container/replicator.py` specializes Swift's generic database replicator for container databases. It replicates normal container DB rows, sharding metadata, sync-store state, and reconciler queue entries. The file is also the server-side RPC extension used by the container server's `REPLICATE` endpoint.

The core responsibilities are:

- Keep local container DBs synchronized with peer replicas using `swift.common.db_replicator`.
- Exchange container shard range rows in addition to ordinary DB replication metadata.
- Stop object-row replication once a container has started sharding, so cleaving rather than old replication paths moves rows to shard containers.
- Detect objects recorded under the wrong storage policy and enqueue those rows into local reconciler containers under `.misplaced_objects`.
- Keep the local `sync_containers` symlink store in step when container metadata changes or DBs are deleted.
- Create, replicate, and eventually clean up local reconciler container DBs produced during a replication pass.

## Important APIs, Types, and Functions

`check_merge_own_shard_range(shards, broker, logger, source)` filters incoming shard range dictionaries before merging. It specifically protects a broker whose own shard range has an epoch from being overwritten by a remote copy of the same own shard range that lacks an epoch. This is a compatibility workaround for historical data and logs a warning when it ignores such a remote row.

`ContainerReplicator` extends `db_replicator.Replicator` with container-specific constants: `server_type = 'container'`, `brokerclass = ContainerBroker`, `datadir = DATADIR`, and default port `6201`.

Key `ContainerReplicator` methods:

- `report_up_to_date(full_info)` compares reported account-server fields with current container fields.
- `_gather_sync_args(replication_info)` appends status-change, row count, and storage-policy fields to replication sync args when multiple storage policies exist.
- `_handle_sync_response(...)` consumes remote replication info, updates local policy/timestamps if needed, and fetches shard ranges when a new enough remote advertises `shard_max_row`.
- `_sync_shard_ranges(broker, http, local_id)` sends all local shard range rows with the `merge_shard_ranges` RPC.
- `_choose_replication_mode(...)` always tries shard-range replication, but defers object replication for sharding or sharded DBs.
- `_fetch_and_merge_shard_ranges(http, broker)` calls remote `get_shard_ranges`, filters through `check_merge_own_shard_range`, and merges the result.
- `find_local_handoff_for_part(part)` finds a local device for a reconciler container, preferring a local primary and then any local weighted device.
- `get_reconciler_broker(timestamp)`, `feed_reconciler(container, item_list)`, and `dump_to_reconciler(broker, point)` build and fill local reconciler DBs for misplaced policy rows.
- `_post_replicate_hook(...)` updates sync-store symlinks, dumps misplaced rows to reconciler containers, and advances the reconciler sync point only when replication has majority success.
- `cleanup_post_replicate(...)` refuses to delete a handoff DB that is required for sharding.
- `delete_db(broker)` pre-removes sync-store symlinks and delays reconciler DB cleanup until reconciler replication is complete.
- `replicate_reconcilers()` pushes generated reconciler containers to their proper nodes, then removes local cleanup candidates.
- `run_once(...)` initializes per-pass reconciler and sync-store state, delegates the main scan to the parent, then replicates any generated reconciler work.

`ContainerReplicatorRpc` extends `db_replicator.ReplicatorRpc` for container replication RPCs:

- `_db_file_exists(db_path)` treats any DB sidecar returned by `get_db_files` as existence.
- `_parse_sync_args(args)` accepts older sync args and optional newer policy/status fields.
- `_get_synced_replication_info(broker, remote_info)` reconciles policy index before returning local replication info.
- `_abort_rsync_then_merge(db_file, old_filename)` aborts a normal rsync-then-merge if the local DB began sharding after the sync handshake.
- `_post_rsync_then_merge_hook(existing_broker, new_broker)` carries existing shard ranges into a newly rsynced DB.
- `merge_shard_ranges(broker, args)` and `get_shard_ranges(broker, args)` expose the shard-range replication RPC methods used by peers.

`main()` wires the daemon entry point, including once-mode device and partition overrides.

## Control Flow

A normal once pass starts in `run_once`: it constructs `reconciler_containers`, `reconciler_cleanups`, and a `ContainerSyncStore`, then calls the generic DB replicator scan. For each DB, generic replication calls into the container overrides.

When a peer responds to sync:

1. `_handle_sync_response` decodes remote info.
2. If storage policy indexes disagree, it updates the local broker's policy index with a new `status_changed_at`.
3. If timestamps differ, it merges remote create, put, and delete timestamps.
4. If the remote has sharding support, it pulls and merges remote shard ranges.
5. It delegates remaining response handling to the generic replicator.

Replication mode selection is sharding-aware. `_choose_replication_mode` first tries to push shard ranges if the peer understands `shard_max_row`. If `broker.sharding_initiated()` is true, the method refuses normal object replication, records a deferred stat, and returns only the shard-range replication result. This is important because object movement must happen via sharder cleaving; ordinary replication of the retiring DB could keep reintroducing rows or interfere with sharded state.

After normal replication, `_post_replicate_hook` performs two side effects. It refreshes the sync-store symlink for sync-enabled containers, and it handles misplaced rows. For containers that do not have multiple policies, it simply slides `reconciler_sync` to `max_row`. For multi-policy containers, it calls `dump_to_reconciler`, which batches rows from `broker.get_misplaced_since(point, self.per_diff)` by reconciler container name, translates each row to a queue entry, and merges those items into local reconciler brokers. The reconciler sync point advances only if a majority of peer replication responses were successful.

At the end of the pass, any local reconciler DBs created or discovered are replicated to their owning nodes in `replicate_reconcilers`. The method then disables the cleanup bypass, calls `delete_db` for reconciler cleanup candidates, and waits for the cooperative pool.

Incoming `REPLICATE` requests hit `ContainerReplicatorRpc` through `server.py`. The sync handshake is policy-aware, rsync merges preserve shard ranges, and explicit shard-range RPCs move sharding metadata without requiring a full DB transfer.

## State and Persistence Behavior

The main persistent state is in container SQLite DBs managed by `ContainerBroker`. This file reads and mutates:

- Replication info rows and sync points.
- Container timestamps: `created_at`, `put_timestamp`, `delete_timestamp`, `status_changed_at`.
- Storage policy index and policy-reporting fields.
- Shard range rows, including own shard range epoch-sensitive data.
- Reconciler sync point and misplaced-object query results.
- Normal object rows when generic replication is still allowed.

Reconciler queue state is persisted as container DBs under the special `MISPLACED_OBJECTS_ACCOUNT`. `get_reconciler_broker` creates a local broker on a local device for the reconciler container derived from the object's timestamp. These DBs are cached for the duration of `run_once`.

Sync-store state is persisted outside SQLite as symlinks in each device's `sync_containers` tree. Replication refreshes the symlink when metadata changes and removes it before deleting a DB.

Shard range replication is all-or-nothing only at the per-RPC level. `_sync_shard_ranges` currently sends all shard ranges every cycle rather than maintaining shard-range sync points. This is explicitly called out as a future optimization.

## Dependencies and Integration Points

This module depends heavily on:

- `swift.common.db_replicator` for the base replicator and RPC protocol.
- `swift.container.backend.ContainerBroker` for DB metadata, object rows, shard ranges, misplaced rows, and DB lifecycle operations.
- `swift.container.reconciler` for policy mismatch detection and queue-entry translation.
- `swift.container.sync_store.ContainerSyncStore` for local sync symlink maintenance.
- `swift.common.storage_policy.POLICIES` for deciding when extended sync args are needed.
- `swift.common.utils.majority_size`, `get_db_files`, `node_to_string`, and `NormalTimestamp`.

Runtime integration points include:

- The container server `REPLICATE` endpoint, which dispatches into `ContainerReplicatorRpc`.
- The container sharder, which relies on the replicator not doing ordinary object replication after sharding starts.
- The object/container reconciler pipeline, which consumes the local reconciler containers populated here.
- Account updates indirectly, via reported fields that the updater and broker maintain.
- Container sync, via `ContainerSyncStore` updates after replication or deletion.

## Risks and Edge Cases

Shard-range epoch handling is subtle. If `check_merge_own_shard_range` is bypassed or altered incorrectly, an old remote own shard range without epoch can erase important local epoch state and confuse sharding progress.

The refusal to replicate object rows after sharding starts is intentional but high impact. A false positive in `broker.sharding_initiated()` would defer normal replication; a false negative would allow object rows to replicate while cleaving is expected to own movement.

Reconciler sync point advancement depends on majority replication. If rows are enqueued locally but replication lacks majority, the low sync point is retained so rows can be retried. Bugs here can either duplicate reconciler work or lose misplaced-object repairs.

`find_local_handoff_for_part` must find a local device. If ring/local-device metadata is stale, reconciler broker creation can fail or pick a fallback device with zero weight.

The shard-range RPC sends all shard ranges. Very large shard-range tables may make replication heavier than normal object-row diffs.

`delete_db` has different behavior for reconciler DBs during `run_once`. Mistakes in the `reconciler_cleanups`/`reconciler_containers` lifecycle can leave local reconciler DBs around or delete them before they are replicated.

## Test Signals

Useful tests should cover:

- `check_merge_own_shard_range` preserving local own-shard-range epoch data when remote rows are stale.
- `_gather_sync_args` and `_parse_sync_args` compatibility with both old and new replication argument lengths.
- `_choose_replication_mode` deferring object replication only when sharding has actually begun.
- `_handle_sync_response` policy-index repair, timestamp merge, and shard-range pull behavior.
- RPC `merge_shard_ranges` and `get_shard_ranges` response semantics.
- Reconciler batching: rows grouped by reconciler container, failure retaining low sync point, majority success advancing sync.
- Sync-store updates on post-replicate and symlink removal before DB deletion.
- Reconciler container replication and cleanup ordering in `run_once`.

Integration-level signals include sharding rolling-upgrade tests where peers may not support shard-range RPCs, multi-policy misplaced-object reconciliation tests, and handoff cleanup tests where a sharding-required DB must not be deleted.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/container/replicator.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/container/server.py -->
# sources/object-store/openstack-swift/swift/container/server.py

## Purpose

`swift/container/server.py` implements the WSGI container server. It owns the HTTP API used by proxies, object updaters, replication daemons, sharders, and account servers to create containers, update container metadata, record object rows, list objects or shard ranges, delete containers or object rows, and dispatch replication RPCs.

The file bridges request-level protocol details to `ContainerBroker` persistence. It validates placement paths and timestamps, enforces drive and free-space checks, manages container metadata, reports container stats to account servers, redirects object updates to shard containers when possible, and serializes listings in the expected Swift formats.

## Important APIs, Types, and Functions

Module-level helpers:

- `gen_resp_headers(info, is_deleted=False)` converts broker info into backend and client-visible response headers. Deleted containers still expose backend timestamps but suppress client-facing object stats.
- `get_container_name_and_placement(req)` validates a container-level path and internal container naming rules.
- `get_obj_name_and_placement(req)` validates an object-level update path and internal object naming rules.

`ContainerController(BaseStorageServer)` is the WSGI app. Important attributes initialized in `__init__` include:

- `root`, `mount_check`, `node_timeout`, and `conn_timeout` for local device and backend I/O.
- `realms_conf` and `allowed_sync_hosts` for validating `X-Container-Sync-To`.
- `replicator_rpc`, an instance of `ContainerReplicatorRpc`.
- `auto_create_account_prefix` and `shards_account_prefix` to distinguish internal auto-created accounts from shard accounts.
- `sync_store`, a `ContainerSyncStore` updated when sync metadata changes.
- `fallocate_reserve`/`fallocate_is_percent` for free-space admission.

Core helper methods:

- `_get_container_broker(drive, part, account, container, **kwargs)` maps request placement to the SQLite DB path and returns a broker.
- `get_and_validate_policy_index(req)` parses `X-Backend-Storage-Policy-Index` and rejects unknown policies.
- `account_update(req, account, container, broker)` sends container stats to account servers listed in request headers.
- `_update_sync_store(broker, method)` refreshes local sync symlinks.
- `_redirect_to_shard(req, broker, obj_name)` returns a relative `301 Moved Permanently` to a shard object path when the caller opted in and a shard range owns the object.
- `_update_or_create(...)`, `_should_autocreate(...)`, `_maybe_autocreate(...)`, and `_update_metadata(...)` centralize DB creation, auto-create rules, policy validation, and metadata mutation.

Public HTTP methods:

- `DELETE(req)` dispatches to `DELETE_container` or `DELETE_object`.
- `PUT(req)` dispatches to `PUT_object`, `PUT_shard`, or `PUT_container`.
- `HEAD(req)` returns container metadata and object stats.
- `GET(req)` chooses object or shard listings based on `X-Backend-Record-Type` and DB sharding state.
- `REPLICATE(req)` dispatches JSON replication RPCs.
- `UPDATE(req)` merges object rows from proxy-side batching.
- `POST(req)` updates metadata and optionally the put timestamp.

Listing helpers:

- `update_shard_record(record, shard_record_full=True)` serializes `ShardRange` or namespace records.
- `update_object_record(record)` serializes object listing rows and applies `swift_bytes` content-type overrides.
- `GET_shard(...)`, `GET_object(...)`, and `_create_GET_response(...)` implement filtered listings and content negotiation.

`app_factory` and `main` are the paste.deploy and command-line entry points.

## Control Flow

All requests pass through `__call__`. The controller builds a `Request`, stores the transaction id on the logger, rejects invalid internal UTF-8 paths, checks that the method is public, invokes the method, catches `HTTPException` and unexpected errors, and logs a Swift-formatted access line.

For container creation:

1. `PUT` validates the path, timestamp, sync-to header, drive, and free space.
2. `PUT_container` determines the storage policy from the explicit backend policy index or the default policy header.
3. `_update_or_create` initializes a new DB or updates an existing one, while rejecting policy conflicts on live containers.
4. `_update_metadata` saves ACL, sync, versioning, and sys/user metadata. A changed sync target resets sync points to `-1`.
5. `account_update` sends the latest stats to the account servers listed in the request.
6. The response is `201 Created` or `202 Accepted` with the container policy index.

For object updates:

1. `PUT_object` or `DELETE_object` validates or defaults the object policy index.
2. `_maybe_autocreate` creates internal auto-create containers when allowed, but deliberately does not auto-create shard accounts unless the caller explicitly asks with `X-Backend-Auto-Create`.
3. `_redirect_to_shard` may return a relative quoted location to the shard account/container/object when the caller accepts redirects.
4. If no redirect is returned, the broker records the put or delete row in the local container DB.

For shard range writes:

1. `PUT` detects `X-Backend-Record-Type: shard`.
2. `PUT_shard` parses the JSON body into `ShardRange` objects.
3. `_maybe_autocreate` creates the receiving container if permitted.
4. Metadata is updated and shard ranges are merged into the broker.

For reads:

1. `GET` validates query parameters and fetches broker info with stale reads allowed.
2. If `X-Backend-Record-Type` is `shard`, or `auto` on a `SHARDING`/`SHARDED` DB, it calls `GET_shard`.
3. `GET_shard` applies shard listing semantics: deleted override, marker/end-marker/includes/reverse, state aliases, optional namespace format, include-deleted, fill-gaps, and include-own for auditing.
4. Otherwise `GET_object` lists object rows, using the retiring DB when sharding is in progress via `broker.get_brokers()[0]`.
5. `_create_GET_response` adds persisted metadata, serializes XML/JSON/text, sets last-modified, and returns `204` when the body is empty.

For replication:

1. `REPLICATE` validates placement and free space.
2. It loads the JSON RPC args from `wsgi.input`.
3. It dispatches to `ContainerReplicatorRpc`, which implements generic DB replication and container shard-range extensions.

## State and Persistence Behavior

The durable state is the container DB file under `devices/<drive>/containers/<part>/<suffix>/<hash>/<hash>.db`. `ContainerController` creates brokers for these paths and uses broker methods to persist:

- Container lifecycle timestamps and status-changed timestamp.
- Storage policy index.
- Container metadata, including ACLs, sync metadata, versions metadata, sysmeta, and user metadata.
- Object rows: name, timestamp encodings, size, content type, etag, delete marker, and object policy index.
- Shard range rows and namespace metadata.
- Sync points for container sync.
- Sharding state surfaced through broker info.

The controller also mutates the local sync-store symlink tree through `ContainerSyncStore` whenever metadata indicates sync should start or stop, and when containers are deleted.

Account-server state is updated through outgoing `PUT` requests in `account_update`, but account updates are deliberately retry-oriented: failures are logged and later repaired by `container-updater`.

Free-space checks happen before mutating requests and replication RPCs. DB preallocation and query logging flags are configured globally in `swift.common.db`.

## Dependencies and Integration Points

Major dependencies include:

- `swift.container.backend.ContainerBroker` and container DB constants.
- `swift.container.replicator.ContainerReplicatorRpc` for `REPLICATE`.
- `swift.container.sync_store.ContainerSyncStore` for sync daemon discovery.
- `swift.common.request_helpers` for path and query validation.
- `swift.common.utils` for hashing, timestamps, storage directories, sync validation, free-space config, shard ranges, and logging.
- `swift.common.middleware.listing_formats` for XML/JSON/text listings.
- `swift.common.storage_policy.POLICIES` for policy validation.
- `swift.common.bufferedhttp.http_connect` for account-server updates.

The server is called by:

- Proxy servers for user-facing container operations.
- Object updaters and object servers for object row updates.
- Container replicators for DB sync.
- Container sharders for shard range PUTs, shard listings, and shard container auto-creation.
- Container sync daemon indirectly through metadata and sync-store state.
- Account updater/account server flows through `account_update` and reported broker fields.

## Risks and Edge Cases

Object-update redirection must be opt-in because older object updaters do not understand shard redirects. `_redirect_to_shard` also refuses unsafe unquoted locations unless the caller supports quoted locations, intentionally letting the sharder later move misplaced rows.

Auto-create rules are security and correctness sensitive. Internal accounts may be auto-created, but shard accounts are blocked by default so ordinary updates do not accidentally create shard containers outside the sharder workflow.

Storage policy conflicts are rejected for live containers. Deleted containers may be recreated with a new policy, but object updates defaulting to policy 0 retain upgrade compatibility and can hide missing headers.

Shard listings have many compatibility paths: namespace vs full format, state aliases, fill-gaps, include-own for auditing, and override-deleted. Any change can affect proxy listing behavior or sharder audits.

During sharding, object listings read from `broker.get_brokers()[0]`, the retiring DB, so listing semantics depend on the backend broker exposing the right DB ordering.

`account_update` trusts the proxy-supplied account host/device/partition headers and only validates cardinality. Malformed or stale headers turn into retryable failures or `404` handling.

Metadata updates reset sync points when sync target changes; missing that reset would skip rows for the new destination.

## Test Signals

High-value tests should exercise:

- Header generation for live and deleted containers.
- Path validation helpers rejecting invalid internal account, container, and object names.
- Policy-index parsing, unknown policy rejection, and policy conflict response headers.
- Container create/recreate/delete flows and account update outcomes.
- Metadata persistence, sync-store updates, and sync-point reset on sync target changes.
- Object PUT/DELETE with and without auto-create, plus shard redirect behavior for quoted and unquoted locations.
- Shard PUT body validation and merge behavior.
- Object listings across JSON/XML/text, prefixes, delimiters, reverse order, reserved names, and sharding state.
- Shard listings with state aliases, namespace format, include-deleted, override-deleted, fill-gaps, and auditing include-own semantics.
- `REPLICATE` dispatch and bad JSON handling.
- `UPDATE` merge-items behavior and free-space failures.
- `__call__` handling of invalid UTF-8, disallowed methods, and request logging.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/container/server.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/container/sharder.py -->
# sources/object-store/openstack-swift/swift/container/sharder.py

## Purpose

`swift/container/sharder.py` implements Swift's container sharding daemon. It scans local container DBs, audits root and shard containers, identifies containers or shard ranges that should split or shrink, creates shard containers, cleaves object rows from retiring DBs into destination shard DBs, moves misplaced objects, reports shard state to root containers, and records sharding progress and recon data.

The file combines pure shard-range algorithms with daemon orchestration. It extends `ContainerReplicator` so it can reuse ring traversal, local handoff selection, replication, reclaim, and DB deletion behavior while replacing the normal post-replicate hook with sharding-specific work.

## Important APIs, Types, and Functions

Module constants:

- `CLEAVE_SUCCESS`, `CLEAVE_FAILED`, and `CLEAVE_EMPTY` classify a single shard-range cleave attempt.
- `DEFAULT_PERIODIC_WARNINGS_INTERVAL` controls duplicate warning suppression.

Pure and mostly pure helper functions:

- `sharding_enabled(broker)` checks sysmeta or existing shard ranges to decide whether a broker should be processed.
- `make_shard_ranges(broker, shard_data, shards_account_prefix)` converts scanner output into named `ShardRange` objects under the shards account namespace.
- `find_paths_with_gaps(shard_ranges, within_range=None)`, `_find_discontinuity`, `find_paths`, and `rank_paths` reason about shard-range namespace coverage.
- `find_overlapping_ranges(...)` finds overlapping shard ranges, optionally ignoring recent parent-child overlaps during a reclaim-age window.
- `is_sharding_candidate(...)` and `find_sharding_candidates(...)` detect large active ranges that should shard.
- `is_shrinking_candidate(...)`, `find_compactible_shard_sequences(...)`, `find_shrinking_candidates(...)`, `finalize_shrinking(...)`, and `process_compactible_shard_sequences(...)` detect and mark small neighboring shard ranges for compaction.
- `combine_shard_ranges(...)` merges new and existing shard ranges while respecting newest state and deletion markers.
- `update_own_shard_range_stats(broker, own_shard_range)` refreshes stats from broker info without persisting by itself.

`CleavingContext` persists progress for a retiring DB. It stores the DB-specific ref, namespace cursor, current max row, cleave-to row, previous cleave-to row, misplaced-done flag, cleaving-done flag, range counts, and accumulated replication time. Its `load`, `load_all`, `store`, `reset`, `start`, `range_done`, `done`, and `delete` methods serialize to broker sharding sysmeta keys named `Context-<db id>`.

`ContainerSharderConf` loads and validates sharder config. Important settings include:

- `shard_container_threshold`
- `max_shrinking` and `max_expanding`
- `shard_scanner_batch_size`
- `cleave_batch_size` and `cleave_row_batch_size`
- `broker_timeout`
- recon and sharding timeout settings
- `conn_timeout`
- `auto_shard`
- `shrink_threshold`, `expansion_limit`, `rows_per_shard`, and `minimum_shard_size`

`ContainerSharder(ContainerSharderConf, ContainerReplicator)` is the daemon. Important method groups:

- Stats and warnings: `periodic_warning`, `_zero_stats`, `_append_stat`, `_min_stat`, `_max_stat`, `_increment_stat`, `_update_stat`, `_make_stats_info`, `_report_stats`, `_periodic_report_stats`, `_record_sharding_progress`.
- Candidate detection: `_identify_sharding_candidate`, `_identify_shrinking_candidate`, `_find_and_enable_sharding_candidates`, `_find_and_enable_shrinking_candidates`.
- Remote/root communication: `_fetch_shard_ranges`, `_put_container`, `_send_shard_ranges`, `_update_root_container`.
- Broker and audit helpers: `_check_node`, `_get_shard_broker`, `_audit_root_container`, `_merge_shard_ranges_from_root`, `_delete_shard_container`, `_do_audit_shard_container`, `_audit_shard_container`, `_audit_cleave_contexts`, `_audit_container`.
- Object movement: `yield_objects`, `yield_objects_to_shard_range`, `_replicate_and_delete`, `_move_objects`, `_make_shard_range_fetcher`, `_make_default_misplaced_object_bounds`, `_make_misplaced_object_bounds`, `_move_misplaced_objects`.
- Sharding workflow: `_find_shard_ranges`, `_create_shard_containers`, `_cleave_shard_broker`, `_cleave_shard_range`, `_cleave`, `_complete_sharding`, `_process_broker`, `_one_shard_cycle`.
- Entrypoints and options: `_set_auto_shard_from_command_line`, `run_forever`, `run_once`, and `main`.

## Control Flow

A sharder run begins in `run_once` or `run_forever`. Both call `_one_shard_cycle`, optionally with device and partition filters and command-line auto-shard override.

`_one_shard_cycle`:

1. Resets stats and local-device tracking.
2. Discovers local ring devices with `_check_node`, populating `_local_device_ids` for later local shard broker placement.
3. Builds datadir/partition iterators, using inherited replicator directory traversal.
4. For each local container DB, creates a `ContainerBroker` with `broker_timeout`.
5. Records whether the DB is a sharding candidate.
6. If `sharding_enabled` is true, calls `_process_broker`; otherwise records a skip.
7. Records sharding progress for recon and periodically reports stats.

`_process_broker` is the central state machine:

1. It loads broker info, DB state, and delete state.
2. `_audit_container` validates root coverage/overlaps or shard root state, merges useful root shard-range data into shard DBs, cleans stale cleaving contexts, and may mark old empty shard DBs deleted.
3. `_move_misplaced_objects` finds object rows outside the broker's current responsibility and moves them to destination shard containers.
4. It decides whether this process is the leader: local primary index 0, auto-shard enabled, and DB not deleted.
5. For `UNSHARDED` or `COLLAPSED` DBs, the leader may bootstrap root sharding by marking its own shard range `SHARDING`. If the broker has cleaving-state own range and enough shard ranges, the DB is moved to `SHARDING`.
6. For `SHARDING` DBs, the leader scans for more shard ranges, the daemon creates shard containers for found ranges, replicates updated shard-range state when needed, cleaves pending ranges, and completes sharding when all required rows have moved.
7. For sharded root containers, it identifies and optionally enables shrinking and further sharding candidates, and sends `SHARDING` ranges to the affected shard containers.
8. For non-root containers, it reports own and child shard ranges back to the root until the own range is marked reported.

The cleaving path is the highest-risk control flow. `_cleave` loads a `CleavingContext`, first moves misplaced rows from the retiring DB, then iterates shard ranges after the context marker. It stops at gaps, unready shard states, failures, or `cleave_batch_size`. Each range is handled by `_cleave_shard_range`, which creates or opens a local shard broker, then `_cleave_shard_broker` copies rows by name range and row id, syncs source DB sync points into the shard broker, updates shard range state and metadata, replicates the shard DB to enough peers, advances the context cursor, and persists the context. Once the context says misplaced and cleaving work are done and no new rows appeared beyond `cleave_to_row`, `_complete_sharding` activates cleaved ranges, marks the own range `SHARDED` or `SHRUNK`, deletes non-root own ranges when appropriate, and calls `broker.set_sharded_state()`.

The misplaced-object flow is similar but destination-driven. `_make_misplaced_object_bounds` chooses source bounds based on DB state and cleaving cursor. `yield_objects_to_shard_range` partitions source rows across destination ranges from either the local root DB or a root GET. `_move_objects` merges rows into local destination shard brokers, then `_replicate_and_delete` replicates each destination DB and removes the source rows only if replication is sufficiently successful and the source DB id did not change.

## State and Persistence Behavior

The sharder persists most state in container DBs:

- DB state transitions: `UNSHARDED`, `COLLAPSED`, `SHARDING`, `SHARDED`.
- Own shard range state transitions: `FOUND`, `CREATED`, `CLEAVED`, `ACTIVE`, `SHARDING`, `SHARDED`, `SHRINKING`, `SHRUNK`, plus deleted and reported flags.
- Shard range rows for children, acceptors, donors, root ranges, and repair/fill ranges.
- Object rows copied or removed during cleaving and misplaced-object movement.
- Broker sync points copied to shard DBs so repeated cleaves can resume from the correct row.
- Sharding sysmeta, including quoted root path, sharding enabled flag, and serialized `CleavingContext` values.
- Tombstone counts and own shard range stats before root updates.

Shard container creation is persisted locally first via `ContainerBroker.create_broker`, then replicated with `_replicate_object`. Remote creation/updates happen through direct container `PUT` calls with `X-Backend-Record-Type: shard`, `X-Container-Sysmeta-Sharding`, `X-Container-Sysmeta-Shard-Quoted-Root`, storage-policy headers, and auto-create headers.

Recon state is written with `dump_recon_cache`, containing full sharding stats, candidate summaries, progress data, and elapsed cycle timing. Statsd metrics are emitted for many counters and timing points.

`CleavingContext` is deliberately tied to the retiring DB id so a fresh DB epoch or replaced DB gets its own progress record. Completed or stale contexts are later cleared by `_audit_cleave_contexts`.

## Dependencies and Integration Points

Important dependencies include:

- `ContainerReplicator` for scanning, ring data, local handoff selection, DB replication, reclaim, and deletion.
- `ContainerBroker` and backend constants for all DB state, shard range persistence, object movement, and broker lifecycle operations.
- `ShardRange`, `ShardRangeList`, `Timestamp`, and `NormalTimestamp` for namespace and state modeling.
- `internal_client.InternalClient` for root container shard range GETs.
- `direct_put_container` for shard range PUTs to specific container nodes.
- Ring utilities such as `is_local_device`, `quorum_size`, and `node_to_string`.
- `get_labeled_statsd_client` and `dump_recon_cache` for observability.

External integration points:

- Container server shard `GET` and shard `PUT` APIs, especially `states=auditing`, `states=updating`, namespace bounds, include-deleted, and auto-create headers.
- Container replicator, which must replicate shard DBs and avoid normal object replication after sharding begins.
- Proxy/object updater paths that may be redirected to shard containers after shard ranges enter update-capable states.
- `swift-manage-shard-ranges`, which can pre-create shard ranges and uses the same config validation expectations.
- Recon tooling that reads sharding stats and candidate lists.

## Risks and Edge Cases

Namespace correctness is the main risk. Gaps or overlaps in shard ranges can cause listing holes, duplicate listings, or misplaced object updates. The root audit checks overlaps and gaps, while shard audit only merges root-provided ranges when the combined set is gap- and overlap-free.

Cleaving must be resumable and conservative. The context tracks both namespace cursor and row boundaries because rows can arrive while cleaving is in progress. If `max_row` changes after a full pass, `_complete_sharding` resets context so another pass cleaves new rows instead of prematurely marking the DB sharded.

Replication quorum differs for new shard containers and existing shard containers. If the wrong quorum is used, the sharder may either stall or remove source rows before enough destination replicas exist.

Shrinking changes bounds and donor states in the root, then asks donors to cleave into acceptors asynchronously. Incorrect acceptor expansion or donor deletion can create temporary listing gaps or permanent namespace loss.

Root and shard views can be stale or inconsistent during rolling upgrades and replication lag. `_merge_shard_ranges_from_root` is intentionally selective: it merges own range updates, children before sharded state, and other ranges only when they are not unsafe ancestors and do not introduce bad coverage.

Misplaced object cleanup only removes source rows after destination replication and DB-id stability checks. If these checks are weakened, updates can be lost. If they are too strict, misplaced rows can accumulate.

Quoted root sysmeta is used instead of the older raw root sysmeta for paths with unsafe characters. Upgrade paths may temporarily see shards with incomplete root understanding.

Auto-shard leader selection depends on ring primary index 0. Handoffs and non-leaders can process already-enabled sharding but should not bootstrap new scans.

## Test Signals

High-value tests should cover:

- Pure range algorithms: path finding, gap detection, overlap detection with and without parent-child exclusions, path ranking, and shard-range combination.
- Candidate detection for sharding and shrinking, including row-count vs object-count thresholds and expansion limits.
- `CleavingContext` load/store/reset/start/range_done/done/delete behavior, including multiple DB ids and stale context cleanup.
- Config validation for threshold ordering and percent-based legacy options.
- Root audit warnings for gaps, overlaps, and own-shard-range epoch reset.
- Shard audit merging root state, handling missing own range, deleting old empty shard containers, and refusing unsafe merged ranges.
- `yield_objects` ordering of live rows before deleted rows, marker progression, since-row behavior, and empty-bound guards.
- Misplaced object movement success, unplaced ranges, DB-id changed protection, source row removal after quorum, and destination broker sync.
- Shard scanning, shard container creation, remote shard-range PUT headers, and break-on-first-create-failure behavior.
- Cleaving success/failure/empty outcomes, replication quorum decisions, sync-point copying, state transitions from `CREATED` to `CLEAVED` to `ACTIVE`, and context cursor updates.
- Completion of sharding for roots and shards, including own range deletion for non-root containers.
- Root update reporting latch and tombstone/stat refresh.
- Full `_process_broker` state-machine paths for unsharded, sharding, sharded root, shrinking donor, deleted shard, leader, non-leader, and handoff cases.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/container/sharder.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/container/sync.py -->
# sources/object-store/openstack-swift/swift/container/sync.py

## Purpose

`swift/container/sync.py` implements the container-sync daemon. It scans locally sync-enabled container DBs and mirrors object PUTs and DELETEs to a configured remote container. The daemon uses per-container sync points to divide work across local container replicas while still retrying older rows that may have been missed.

The file also contains a default internal-client configuration string used when `/etc/swift/internal-client.conf` is not present, so deployments can continue to run through upgrades.

## Important APIs, Types, and Functions

`ic_conf_body` is the fallback internal client pipeline. It includes catch_errors, proxy logging, cache, symlink, and proxy-server filters with account autocreation enabled.

`ContainerSync(Daemon)` is the daemon class. Important initialization fields include:

- `devices` and `mount_check` for local DB discovery.
- `interval` and `container_time` for scan cadence and per-container time budget.
- `realms_conf`, `allowed_sync_hosts`, and `http_proxies` for validating and routing remote sync requests.
- `sync_store`, a `ContainerSyncStore` that yields only local DBs with sync metadata.
- Global and per-container counters for syncs, deletes, puts, skips, failures, bytes, and report time.
- `container_ring`, `_myips`, and `_myport` for deciding which replica ordinal this local node owns.
- DB preallocation configuration.
- `swift`, an `InternalClient` used to read source objects through the proxy stack.

Core methods:

- `run_forever(...)` loops over sync-store entries, processing containers and reporting hourly.
- `run_once(...)` performs one scan and emits a final report.
- `report()` logs aggregate counters and resets them.
- `container_report(...)` logs per-container row and operation stats.
- `container_sync(path)` opens a broker, validates metadata and local ownership, manages sync points, and calls `container_sync_row`.
- `_update_sync_to_headers(...)` adds either realm-based `x-container-sync-auth` or legacy `x-container-sync-key`.
- `_object_in_remote_container(...)` performs a remote HEAD to skip unnecessary PUTs when the remote object timestamp is already current.
- `container_sync_row(...)` performs a remote DELETE or PUT for one container DB row.
- `select_http_proxy()` chooses a random configured sync proxy.

`main()` is the daemon entry point.

## Control Flow

The scan starts from `ContainerSyncStore.synced_containers_generator()`, so only DBs with local sync symlinks are visited. For each path, `container_sync`:

1. Opens a `ContainerBroker`.
2. Calls `get_info`; if the DB is missing behind a stale symlink, it removes the sync-store entry and re-raises.
3. Gets the container ring nodes for the account/container and finds this node's local ordinal. Non-local DBs are skipped.
4. Skips containers with object versioning sysmeta because versioned containers are not synced through this path.
5. Reads `X-Container-Sync-To`, `X-Container-Sync-Key`, and sync points from broker metadata/info.
6. Skips if sync target or key is absent; fails if `validate_sync_to` rejects the target.
7. Runs two sync stages inside the `container_time` budget.

The first stage handles rows between `sync_point2` and `sync_point1`. These are older rows for which all replicas should retry work to cover previous partial failures. For each row, it calls `container_sync_row`; if a row fails, `next_sync_point` records where to roll back point2. The broker's second sync point is advanced row by row, then rolled back to `next_sync_point` if needed.

The second stage handles rows newer than `sync_point1`. Each row is assigned to one replica by hashing account/container/object and taking modulo replica count. Only the matching ordinal sends the update. `sync_point1` advances for every observed row, regardless of whether this node sent it, so the next run can retry missed rows in the first stage.

`container_sync_row` decodes the row's composite timestamps. For deleted rows, it sends a remote DELETE using the tombstone data timestamp and treats remote `404` and `409` as acceptable. For live rows, it first HEADs the remote object with auth headers and skips if remote timestamp is not older. Otherwise it fetches the newest source object with the internal client, preserving symlink semantics through `params={'symlink': 'get'}`. It skips object-versioning symlinks, normalizes etag and content type, signs or keys the remote PUT, streams the object body via `FileLikeIter`, and updates counters.

## State and Persistence Behavior

Persistent state is mainly in the source container DB:

- `x_container_sync_point1` and `x_container_sync_point2` are updated throughout a run to track the newest row seen and the newest row for which all updates have been attempted.
- Container metadata controls whether sync is enabled and where it points.
- Object rows provide name, delete flag, timestamps, size, content type, etag, and policy context.

The sync-store symlink tree controls discovery but is maintained by the container server and replicator, not primarily by this daemon. This daemon removes stale symlinks when it discovers the pointed-to DB no longer exists.

Remote object state is mutated by `delete_object` and `put_object` helper calls. Authentication state is not persisted; realm signatures include per-request nonces.

Counters are in-memory and logged periodically. DB preallocation is configured globally in `swift.common.db`.

## Dependencies and Integration Points

Important dependencies include:

- `ContainerBroker` for source DB rows, metadata, sync points, and info.
- `ContainerSyncStore` for local sync-enabled DB discovery.
- `ContainerSyncRealms` and `validate_sync_to` for sync target validation and realm signatures.
- `Ring` and `is_local_device` for local ordinal selection.
- `InternalClient` for reading source objects through Swift's proxy path.
- `delete_object`, `put_object`, and `head_object` for remote sync I/O.
- Versioned writes sysmeta constants to skip object-versioning containers and symlinks.
- Timestamp helpers, `decode_timestamps`, `hash_path`, `quote`, and `FileLikeIter`.

Integration points include:

- Container server metadata updates, which reset sync points and refresh sync-store entries.
- Container replicator sync-store refreshes.
- The remote cluster/container, which must accept legacy sync-key or realm-auth headers.
- The symlink middleware in the internal-client pipeline to preserve symlink objects when syncing.

## Risks and Edge Cases

The two-sync-point algorithm is subtle. Advancing point1 too aggressively could skip rows; advancing point2 after failures could prevent retries. The current design retries older rows by all replicas while partitioning new rows by hash.

Stale sync-store symlinks are expected after races or crashes. The daemon removes them only when broker open fails with the specific missing-DB condition; other DB errors are treated as failures.

Local ordinal selection depends on ring device IP/port matching. If bind IPs, replication ports, or ring data are misconfigured, no node may sync or multiple nodes may sync the same new rows.

Remote HEAD optimization depends on timestamp comparison. Clock/timestamp encoding bugs can skip necessary PUTs or generate redundant PUTs.

Object versioning is explicitly skipped. If versioning metadata is stale, row-level symlink checks provide a second guard.

For live rows, the source object GET can return an older timestamp than the row metadata. The code raises the original exception if available or a generic error to avoid pushing stale data.

Failures are per-row and only return False from `container_sync_row`; the outer loops continue until time budget expires and persist conservative sync points.

## Test Signals

Useful tests should cover:

- Container discovery through sync-store symlinks and stale symlink removal.
- Local-node ordinal selection and non-local skip behavior.
- Missing sync metadata skip, invalid sync target failure, and object-versioning skip.
- Two-stage sync-point advancement, rollback on row failure, and hash partitioning of new rows.
- Realm-auth vs legacy sync-key header generation.
- Remote HEAD skip behavior for newer/equal/older timestamps and error propagation.
- DELETE handling of remote `404`, `409`, unauthorized, and generic failures.
- PUT behavior: newest source GET, symlink preservation, versioning symlink skip, etag/content-type normalization, body streaming, proxy selection, and byte/put counters.
- Time-budget exits and per-container report values.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/container/sync.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/container/sync_store.py -->
# sources/object-store/openstack-swift/swift/container/sync_store.py

## Purpose

`swift/container/sync_store.py` implements the local filesystem index used by the container-sync daemon. Instead of scanning every container DB on every pass, sync-enabled DBs are represented by symlinks under each device's `sync_containers` tree. The container server and replicator update this store when sync metadata changes; the container-sync daemon iterates it.

## Important APIs, Types, and Functions

`SYNC_DATADIR = 'sync_containers'` is the per-device directory name parallel to the normal container `DATADIR`.

`ContainerSyncStore` exposes:

- `__init__(devices, logger, mount_check)` normalizes the devices root and stores logging/mount behavior.
- `_container_to_synced_container_path(path)` converts a real container DB path such as `/srv/node/sdb/containers/.../hash.db` to `/srv/node/sdb/sync_containers/.../hash.db`.
- `_synced_container_to_container_path(path)` converts a sync-store symlink path back to the real container DB path.
- `add_synced_container(broker)` creates parent directories and a symlink from sync-store path to broker DB path.
- `remove_synced_container(broker)` unlinks the sync-store symlink and removes empty parent directories.
- `update_sync_store(broker)` decides whether to add or remove a symlink based on broker metadata and delete state.
- `synced_containers_generator()` scans `sync_containers` DB symlink locations and yields real container DB paths.

## Control Flow

Callers normally use `update_sync_store` after metadata or lifecycle changes:

1. If neither `X-Container-Sync-To` nor `X-Container-Sync-Key` has ever appeared in metadata, it returns without touching the filesystem. This avoids needless work during replicator passes over ordinary containers.
2. If the broker is deleted, it removes any sync symlink.
3. It reads current sync target and key values from metadata.
4. If both are non-empty, it calls `add_synced_container`.
5. Otherwise it calls `remove_synced_container`.

`add_synced_container` is idempotent. It stats the target symlink path, returns if present, creates parent directories, and tolerates an `EEXIST` symlink race. `remove_synced_container` is also idempotent for missing paths.

The daemon-side generator uses `audit_location_generator(self.devices, SYNC_DATADIR, '.db', ...)` to find sync-store DB entries. For each path it yields the corresponding real container DB path rather than the symlink path because `ContainerBroker` expects adjacent pending files and related DB artifacts in the real container directory.

## State and Persistence Behavior

The store persists no database records. Its durable state is the presence or absence of symlinks under:

`<devices>/<device>/sync_containers/<partition>/<suffix>/<hash>/<hash>.db`

The symlink target points at:

`<devices>/<device>/containers/<partition>/<suffix>/<hash>/<hash>.db`

Directory cleanup uses `os.removedirs`, so only empty parent directories are removed. Metadata values remain authoritative; the filesystem index is a derived local cache.

## Dependencies and Integration Points

Dependencies are intentionally small:

- `audit_location_generator` to scan mounted devices for `.db` paths.
- `mkdirs` for parent directory creation.
- `DATADIR` from `swift.container.backend`.
- Standard `os` and `errno`.

Integration points:

- `server.py` calls `_update_sync_store` after PUT/POST metadata changes and DELETE.
- `replicator.py` refreshes the store after replication and removes entries before DB deletion.
- `sync.py` consumes `synced_containers_generator` and removes stale links when DBs are missing.

## Risks and Edge Cases

The path conversion helpers assume the normal Swift container DB layout and locate `DATADIR`/`SYNC_DATADIR` using `rfind`. Unexpected device paths containing those directory names elsewhere could confuse conversion, although normal Swift storage paths are structured.

If metadata keys exist with empty values, the symlink is removed. If metadata keys never existed, the method does nothing; callers should not rely on it to clean arbitrary stale symlinks for never-synced containers.

Symlink creation races are tolerated only when the existing path is a symlink. A regular file at the sync path is treated as an error.

`os.removedirs` can raise errors other than `ENOENT` if parent directories are not empty or permissions are wrong; these propagate to callers and are usually logged by server/replicator wrappers.

Mount checking happens during generator scanning, not during add/remove operations.

## Test Signals

Useful tests should cover:

- Forward and reverse path conversion for normal device/container DB paths.
- Idempotent add when symlink already exists.
- Add failure when an existing non-symlink occupies the sync-store path.
- Remove behavior for existing and missing symlinks, including empty directory cleanup.
- `update_sync_store` no-op for never-synced metadata, add for both non-empty sync headers, remove for missing/empty values, and remove for deleted brokers.
- Generator yielding real container DB paths from sync-store locations and honoring mount-check behavior.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/container/sync_store.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/container/updater.py -->
# sources/object-store/openstack-swift/swift/container/updater.py

## Purpose

`swift/container/updater.py` implements the container-updater daemon. Its job is to scan local container DBs and report changed container statistics to account servers so account listings reflect container existence, object counts, bytes used, delete state, and storage policy. It is the retry path for account updates that failed during direct container-server requests.

## Important APIs, Types, and Functions

`ContainerUpdater(Daemon)` is the daemon. Initialization configures:

- `devices`, `mount_check`, and `swift_dir` for storage and ring discovery.
- `interval`, `concurrency`, and rate limiting.
- Account ring lazy loading through `get_account_ring`.
- `node_timeout` and `conn_timeout`.
- Per-run counters: `no_changes`, `successes`, `failures`.
- Account suppression maps and `account_suppression_time` to avoid repeatedly hammering failing accounts.
- DB preallocation, recon cache path, recon file path, and updater user agent.

Important methods:

- `get_account_ring()` lazily loads the account ring.
- `_listdir(path)` wraps `os.listdir` with logging and empty-list fallback.
- `get_paths()` discovers partition directories under mounted device `containers` dirs and shuffles them.
- `_load_suppressions(filename)` loads account suppression updates written by child processes.
- `run_forever(...)` performs repeated concurrent sweeps using one forked child per partition path up to configured concurrency.
- `run_once(...)` performs a single-threaded sweep.
- `container_sweep(path)` walks a partition path and calls `process_container` for every `.db`.
- `process_container(dbfile)` decides whether a container needs an account update and sends reports to all account replicas.
- `container_report(...)` sends one account-server `PUT` over the replication network.
- `main()` wires the daemon entry point.

## Control Flow

In long-running mode, `run_forever` sleeps for a randomized initial interval, then loops:

1. Expired account suppressions are removed.
2. The account ring is touched to refresh it.
3. Partition paths from `get_paths` are processed by forked children up to `concurrency`.
4. Each child resets counters, opens a temp file for new suppressions, monkey-patches eventlet after fork, processes one partition path with `container_sweep`, logs child stats, and exits.
5. The parent waits for children and calls `_load_suppressions` on each temp file.
6. The sweep time is logged and written to recon cache.
7. The daemon sleeps the remainder of the interval.

`run_once` avoids forking and processes every path in the current process, then writes the same recon sweep timing.

`process_container`:

1. Opens a `ContainerBroker` and reads `get_info`.
2. Skips on lock timeout.
3. Skips auto-created containers whose put timestamp is not positive, because their stats are not reliable yet.
4. Skips accounts currently suppressed.
5. If the broker is not a root container, zeroes object and byte stats so shard containers do not double-count at the account level.
6. Compares current put/delete/object/bytes fields against reported fields.
7. If unchanged, increments `no_changes`.
8. If changed, gets account partition and nodes, spawns one `container_report` green thread per account node, and counts statuses.
9. On majority success, calls `broker.reported(...)` to persist reported fields.
10. If every account replica returns `404`, quarantines the container DB because no account replicas exist.
11. Otherwise records failure and suppresses that account for a configured time, writing the suppression to the child temp file when running forked.

`container_report` sends a `PUT` to account server replication IP/port with container path and headers for put timestamp, delete timestamp, object count, bytes used, account override deleted, storage policy, and user agent. Connection and response phases have separate timeouts. Errors return `500` equivalent status for retry accounting.

## State and Persistence Behavior

Persistent local state includes:

- Broker `reported_put_timestamp`, `reported_delete_timestamp`, `reported_object_count`, and `reported_bytes_used`, updated only after majority account success.
- Container DB quarantine when all account replicas report `404`.
- Recon cache entry `container_updater_sweep`.

In-memory state includes counters and account suppressions. In `run_forever`, suppressions discovered by children are persisted only briefly through temp files passed back to the parent. The files are unlinked after `_load_suppressions`.

The account server receives durable account DB updates through replication-network `PUT` requests.

For shard containers, zeroing object_count and bytes_used before reporting prevents double counting. The root container and sharder are responsible for aggregating and reporting useful shard stats.

## Dependencies and Integration Points

Dependencies include:

- `ContainerBroker` for local DB info, reported markers, root-container detection, and quarantine.
- `Ring` for account partition/node lookup.
- `http_connect`, `ConnectionTimeout`, and `Timeout` for account server I/O.
- Eventlet `spawn` and `EventletRateLimiter` for concurrent request fan-out and scan throttling.
- `check_drive` and `DATADIR` for local path discovery.
- `dump_recon_cache` and recon constants for observability.
- `majority_size`, `Timestamp`, `node_to_string`, and config helpers.

Integration points:

- Container server writes initial account updates during user requests; updater retries later if those fail.
- Account servers consume the updater's `PUT` reports.
- Sharder/root-container semantics affect whether stats are zeroed for shard containers.
- Recon tooling reads updater sweep timing.

## Risks and Edge Cases

Forking plus eventlet requires monkey patching in children, not the parent path. The code deliberately calls `eventlet_monkey_patch()` in child and in `run_once`.

Suppression state is per account and shared from children through temp files. If temp file loading fails, failures may cause repeated account report attempts sooner than intended.

Majority success is required before reported fields advance. This prevents data loss but can cause repeated reports under partial outages.

All-account-404 handling quarantines the container DB. This is intentionally severe; false 404s from account-ring or network issues could quarantine good data if every response is misclassified.

Shard container reports zero object/byte stats to avoid double-counting. Any broker `is_root_container` error could make account stats too low or too high.

The updater skips containers with non-positive put timestamps. Auto-created containers therefore need later real updates before account stats are sent.

`get_paths` shuffles partition paths to distribute load, so tests should not assume deterministic processing order unless randomization is controlled.

## Test Signals

Useful tests should cover:

- Device and partition discovery with mounted, unmounted, and missing `containers` dirs.
- Lazy account-ring loading and refresh call in forever mode.
- `process_container` skip paths: lock timeout, auto-created timestamp, account suppression, and no changed fields.
- Majority success updating broker reported fields.
- Partial failures causing account suppression and retry behavior.
- All-404 responses quarantining the container DB.
- Non-root container stat zeroing before report.
- `container_report` headers, replication IP/port selection, timeout/error handling, response body drain, and connection close.
- Forked `run_forever` suppression file loading and recon cache updates.
- `run_once` single-threaded counters and rate limiter behavior.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/container/updater.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/obj/__init__.py -->
# sources/object-store/openstack-swift/swift/obj/__init__.py

## Purpose

`swift/obj/__init__.py` is an empty package marker for Swift's object-server package. Its purpose is to make `swift.obj` importable and to provide a stable package namespace for object-related modules elsewhere in the tree.

## Important APIs, Types, and Functions

This file defines no APIs, classes, functions, constants, or side effects. It has zero lines of executable code.

## Control Flow

There is no runtime control flow in this file. Importing `swift.obj` executes no package-level initialization beyond Python's normal package import mechanics.

## State and Persistence Behavior

The file persists no state and mutates no state. Its existence affects Python module resolution only.

## Dependencies and Integration Points

The integration point is the package namespace itself. Modules under `swift/obj/` can be imported as `swift.obj.<module>`, and external code may import the package as a namespace anchor. Because the file is empty, there are no dependency imports and no import-time coupling.

## Risks and Edge Cases

Adding imports or initialization logic here would affect every consumer that imports `swift.obj` or any submodule beneath it. Keeping the file empty avoids import cycles, startup overhead, and unintended side effects in daemons or tests.

Removing the file could break environments or tooling that still require explicit package markers, even if modern namespace-package behavior might work in some contexts.

## Test Signals

Test expectations are minimal:

- `import swift.obj` should succeed.
- Importing `swift.obj` should not import object-server submodules or trigger side effects.
- Packaging and source distribution checks should include the marker so the object package remains present.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/obj/__init__.py -->
