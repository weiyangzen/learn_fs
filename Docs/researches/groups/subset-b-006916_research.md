# Research: subset-b-006916

Grouped research for Ceph MDS metrics, migration, and mutation sources. Each section is bounded for deterministic splitting into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/MetricAggregator.cc -->
# sources/distributed-fs/ceph/src/mds/MetricAggregator.cc

## Purpose

`MetricAggregator.cc` implements the rank-0 MDS-side aggregator for metrics reported by every active MDS rank. It receives `MMDSMetrics` messages from peer ranks, validates that those reports correspond to its rank-ping sequence, converts client, subvolume, and rank telemetry into Ceph `PerfCounters`, and serves manager perf-query reports through `MgrClient`.

## Important APIs, Types, and Functions

- Local counter id enums define three counter families: aggregate client count, per-client metrics, and subvolume metrics.
- `MetricAggregator::init()` registers the rank-0 client-count perf counter, starts the `mds-ping` thread, installs manager query/report callbacks, and reads `subv_metrics_window_interval`.
- `shutdown()` stops the pinger thread and removes all owned `PerfCounters`.
- `ms_dispatch2()` handles `MSG_MDS_METRICS` from MDS peers only.
- `notify_mdsmap()` maintains `active_rank_addrs`, initializes `clients_by_rank`, culls vanished ranks, and resets ping state.
- `handle_mds_metrics()` is the main ingestion path. It checks `mds_pinger.pong_received(rank, seq)`, applies client refresh/remove updates, refreshes subvolume counters, and updates rank perf counters.
- `refresh_metrics_for_rank()` creates per-client labeled counters on first sight and updates both perf counters and `query_metrics_map`.
- `refresh_subvolume_metrics_for_rank()` maintains `SlidingWindowTracker<SubvolumeMetric>` per subvolume path, publishes averaged IOPS/throughput/latency/quota/usage counters, and removes stale trackers and query entries.
- `set_perf_queries()` and `get_perf_reports()` implement the mgr-facing dynamic perf-query contract.

## Control Flow

At startup rank 0 registers a low-cardinality `mds_client_metrics` counter and launches a periodic pinger. The pinger holds the aggregator lock while iterating `active_rank_addrs`, sends pings through `MDSPinger`, then sleeps outside the lock. MDS map updates add new active ranks and remove old ones. Removing a rank culls its clients, deletes its rank perf counters, and resets pinger state.

On `MMDSMetrics`, the aggregator locks, rejects stale or unordered reports via `MDSPinger`, then handles every client update. Refresh updates create or update `(client, rank)` perf counters; remove updates delete the per-client counters and query entries. Subvolume samples are accumulated into sliding windows and converted to per-second rates. Rank CPU/open-request telemetry is written into `mds_rank_perf` counters.

Manager perf queries are stored as `MDSPerfMetricQuery -> key -> counters`. Client keys are built from rank/client regex subkeys; subvolume keys are built from subvolume path and current MDS rank subkeys. `get_perf_reports()` serializes the current counters and marks lagging ranks as delayed.

## State and Persistence Behavior

This file is runtime state only, but it publishes persistent process telemetry through the perf-counter collection and mgr reports. State includes `clients_by_rank`, `client_perf_counters`, `subvolume_aggregated_metrics`, `subvolume_perf_counters`, `rank_perf_counters`, `active_rank_addrs`, and `query_metrics_map`. The journal is not touched. Shutdown is responsible for deleting all counters it created.

## Dependencies and Integration Points

Major dependencies are `MDSRank`, `MDSMap`, `MDSPinger`, `MgrClient`, `PerfCountersBuilder`, `MDSPerfMetricTypes`, `MMDSMetrics`, and Ceph messenger dispatch. It integrates with `MetricsHandler.cc`, which sends the `MMDSMetrics` reports, and with the manager daemon through `MgrClient::set_perf_metric_query_cb`.

## Risks

- Counter lifetime is manual; missed remove paths can leak labeled `PerfCounters`.
- `clients_by_rank.at(rank)` assumes `notify_mdsmap()` established the rank before metrics arrive.
- `remove_metrics_for_rank()` decrements the aggregate client count even when called during rank culling with `remove=false`; this relies on culling being called once per known client.
- The per-client opened-inodes perf counter is set from `total_inodes` in one path, which looks easy to confuse with `opened_inodes` and should be covered by tests.
- Subvolume-cardinality is path based, so high churn in subvolume paths can create many labeled counters until the sliding window ages them out.
- All query-map updates occur under one mutex; complex regex queries and many subvolume paths can make the aggregator hot.

## Test Signals

Useful tests exercise rank add/remove through `notify_mdsmap()`, stale ping sequence rejection, client refresh/remove updates, dynamic perf-query regex matching, stale subvolume eviction, rank perf counter removal, and shutdown with non-empty client/subvolume/rank counter maps. Integration tests should include at least two MDS ranks plus client metrics to verify that rank 0 alone owns aggregated rank counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/MetricAggregator.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/MetricAggregator.h -->
# sources/distributed-fs/ceph/src/mds/MetricAggregator.h

## Purpose

`MetricAggregator.h` declares the rank-0 dispatcher and state container used to aggregate CephFS MDS metrics. The class receives MDS-to-MDS metric messages, pings active ranks to drive sequence validation, owns perf counters for client/subvolume/rank metrics, and exposes manager perf reports.

## Important APIs, Types, and Members

- `class MetricAggregator : public Dispatcher` makes the aggregator a messenger dispatcher.
- Public lifecycle methods are `MetricAggregator(CephContext*, MDSRank*, MgrClient*)`, `init()`, and `shutdown()`.
- `notify_mdsmap(const MDSMap&)` updates the active-rank membership tracked by the pinger and culls removed ranks.
- `ms_dispatch2()` is the only dispatch hook with behavior; connection reset/refusal hooks are no-ops.
- `lock` protects all maps and the `stopping` flag. The header explicitly warns not to hold it while calling `send_message_mds()`.
- `clients_by_rank` maps rank to client instances so rank removal can delete all client metrics for that rank.
- `query_metrics_map` stores manager-configured `MDSPerfMetricQuery` data.
- `mds_pinger` plus `pinger` thread manages rank pings and delayed-rank detection.
- Perf-counter ownership is split across `m_perf_counters`, `client_perf_counters`, `subvolume_perf_counters`, and `rank_perf_counters`.
- Private helpers cover message handling, client refresh/remove, subvolume refresh, rank perf updates, rank culling, pings, query setup, and report generation.

## Control Flow

The header exposes a compact external contract: construct with MDS and manager dependencies, call `init()`, feed MDS map updates, dispatch messenger messages, then call `shutdown()`. All detailed behavior is private, making callers interact only through Ceph dispatcher and MDS map hooks.

## State and Persistence Behavior

All stored state is process-local and mutex-protected. The class owns raw `PerfCounters*` pointers and must remove/delete them. No metadata journal, object store, or on-disk state is modified by the class itself. Query state persists only until the manager sends a new config payload or the MDS shuts down.

## Dependencies and Integration Points

The declaration depends on Ceph messenger types, `Dispatcher`, `ceph::mutex`, perf counters, mgr metric types, `MDSPerfMetricTypes`, `mdstypes`, and `MDSPinger`. It is tightly coupled to `MetricAggregator.cc`, `MetricsHandler.cc`, manager perf queries, and MDS map change notification from `MDSRank`.

## Risks

- The class has mixed ownership styles: `MDSPinger` by value, `std::thread` by value, and several raw perf-counter pointers.
- The lock-order warning is important because rank-to-rank sends can re-enter MDS code that may need MDS locks.
- `stopping` is protected by `lock`; any future helper that reads it lockless would need care.
- The public no-op connection handlers mean connection resets do not directly clear rank state; rank cleanup depends on MDS map updates and pinger/report logic.

## Test Signals

Header-level contract tests should verify lifecycle idempotence expectations, dispatcher message acceptance only for `MSG_MDS_METRICS` from MDS peers, and that MDS map changes are the supported source of active-rank membership. Static analysis should flag raw perf-counter ownership and thread shutdown paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/MetricAggregator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/MetricsHandler.cc -->
# sources/distributed-fs/ceph/src/mds/MetricsHandler.cc

## Purpose

`MetricsHandler.cc` implements the per-MDS-rank metrics collector. It accepts `MClientMetrics` messages from clients, stores per-session metric deltas, samples local rank CPU/open-request telemetry, aggregates subvolume metrics, and periodically sends `MMDSMetrics` updates to rank 0.

## Important APIs, Types, and Functions

- `MetricsHandler::MetricsHandler()` records `_SC_CLK_TCK` for CPU sampling.
- `init()` creates local `mds_rank_perf` counters for non-rank0 ranks, reads `subv_metrics_window_interval`, and starts the `mds-metrics` updater thread.
- `shutdown()` sets `stopping`, joins the updater, and removes local rank perf counters.
- `add_session()` creates a `client_metrics_map` entry with `UPDATE_TYPE_REFRESH`.
- `remove_session()` either erases unseen sessions locally or zeroes all metrics and marks `UPDATE_TYPE_REMOVE`.
- `handle_client_metrics()` validates active state, resolves a `Session`, and visits every payload variant.
- `handle_payload()` overloads update cap hits, latency, dentry leases, opened files/inodes, pinned icaps, IO sizes, and subvolume samples.
- `update_rank0()` samples rank telemetry, packages client and subvolume updates, increments sequence state, and sends `MMDSMetrics` to rank 0.
- `aggregate_subvolume_metrics()` folds client subvolume reports into a single path-level `SubvolumeMetric`.
- `maybe_update_subvolume_quota()` records quota/used bytes learned from quota broadcasts.
- `sample_cpu_usage()` and `sample_open_requests()` fill `RankPerfMetrics`.

## Control Flow

The updater thread sleeps for `mds_metrics_update_interval`, wakes under the metrics lock, then calls `update_rank0()`. Client metric messages update in-memory deltas under the same lock. Subvolume payloads are special: the handler temporarily releases the metrics lock while resolving inode ids to paths through `MDSRank::get_path()`, then reacquires it to append samples.

MDS ping messages from rank 0 set `next_seq`; outbound `MMDSMetrics` include that sequence. `last_updated_seq` increments only after rank 0 has assigned a nonzero sequence, which lets session removal collapse locally if rank 0 never saw the session.

`update_rank0()` samples CPU/open requests, skips if rank0 address is not known, copies and resets/removes client metric entries, resolves subvolume used bytes outside the metrics lock, aggregates subvolume path metrics, evicts stale quota entries, then sends the message without holding the metrics lock.

## State and Persistence Behavior

The class maintains runtime state only. `client_metrics_map` stores per-client deltas and sequence bookkeeping. `subvolume_metrics_map` buffers per-path aggregated IO samples between periodic sends. `subvolume_quota` caches quota and used bytes with activity timestamps. `rank_telemetry` stores the previous process CPU sample and latest rank metrics. Non-rank0 local rank perf counters are registered in the perf-counter collection.

## Dependencies and Integration Points

Dependencies include client metric payload types from `include/cephfs/metrics/Types.h`, `MClientMetrics`, `MMDSMetrics`, `MMDSPing`, `MDSRank`, `MDCache`, `CInode`, `SessionMap`, perf counters, `ceph::read_process_cpu_ticks`, and `op_tracker`. It integrates with `MetricAggregator.cc` by sending rank/client/subvolume metrics to rank 0.

## Risks

- The updater uses `sleep()`, so shutdown can wait for the current interval.
- Correctness depends on the lock being released around MDS operations that may take `mds_lock`; future code must preserve that ordering.
- `remove_session()` relies on `last_updated_seq` to avoid sending removes for sessions rank 0 never saw.
- Subvolume `used_bytes == 0` is both a valid value and a cache-miss signal for fallback lookup.
- Payload handlers silently ignore metrics for unknown sessions.
- Rank0 does not create local rank perf counters here; `MetricAggregator` creates counters for all ranks, so startup ordering matters.

## Test Signals

Tests should cover session add/remove before and after `last_updated_seq` advances, client payload visitation, subvolume path resolution with missing paths, quota update with `force_zero`, stale quota eviction, rank0 address changes in `notify_mdsmap()`, CPU sampling on first sample and counter reset, and send-without-lock behavior. Multi-rank tests should verify that rank 0 receives messages only after ping sequence setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/MetricsHandler.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/MetricsHandler.h -->
# sources/distributed-fs/ceph/src/mds/MetricsHandler.h

## Purpose

`MetricsHandler.h` declares the per-rank metrics dispatcher for CephFS MDS. It is responsible for receiving client metrics, periodically forwarding aggregated updates to rank 0, tracking rank0 sequencing, and exposing quota and rank telemetry helpers.

## Important APIs, Types, and Members

- `class MetricsHandler : public Dispatcher` accepts client and MDS ping messages.
- Public methods are lifecycle (`init()`, `shutdown()`), session hooks (`add_session()`, `remove_session()`), MDS map hook (`notify_mdsmap()`), and `maybe_update_subvolume_quota()`.
- `HandlePayloadVisitor` dispatches boost/static-visitor style payload handling but intentionally aborts for `SubvolumeMetricsPayload`, because subvolume handling needs an unlock/relock pattern.
- `create_subv_perf_counter()` is declared for subvolume perf-counter creation.
- `lock` protects sequence state, client metric maps, subvolume buffers, quota cache, rank0 address, stopping flag, and rank telemetry.
- `next_seq` is assigned by rank0 pings; `last_updated_seq` tracks local update rounds.
- `client_metrics_map` maps client entity instance to `(last_update_seq, Metrics)`.
- `subvolume_metrics_map` maps subvolume path to client-reported aggregated IO metrics.
- `SubvolumeQuotaInfo` caches quota, used bytes, and activity time by subvolume inode number.
- `UnlockGuard` is an RAII helper for temporarily dropping the metrics lock during MDS operations.
- `RankTelemetry` holds `RankPerfMetrics` plus CPU sampling state.

## Control Flow

The header defines a collector with two inbound paths: `MClientMetrics` from clients and `MMDSPing` from rank 0. The periodic updater thread is private and feeds rank0 through `update_rank0()`. MDS map changes control `addr_rank0`; sequence reset is part of the public map-notification contract.

## State and Persistence Behavior

State is transient and process-local. The class publishes rank perf counters, but does not journal metadata or persist metrics. Its cached quota data is intentionally evicted when inactive. The sequence fields are local coordination state with rank 0 and are reset when rank0 disappears or changes address.

## Dependencies and Integration Points

The header depends on Ceph messenger dispatch, mutexes, `MDSPerfMetricTypes`, CephFS metric payload types, boost variant visitation, and MDS/session forward declarations. It integrates with session lifecycle code, client message dispatch, MDS map notifications, quota broadcast code in `MDCache`, and rank0 aggregation.

## Risks

- The explicit unlock guard is necessary but risky if callers assume the lock remains held across helper calls.
- The comment near `addr_rank0` contains a stray non-ASCII character, which is harmless for build behavior but can trip strict text tooling.
- `rank_perf_counters` is a raw pointer with lifecycle split between `init()` and `shutdown()`.
- The visitor pattern has a hard abort for subvolume payloads; future payload additions must choose the correct dispatch path.

## Test Signals

Contract tests should assert accepted message types, sequence reset on rank0 address changes, session lifecycle transitions, thread shutdown cleanup, and quota cache behavior. Concurrency-oriented tests should focus on paths that temporarily unlock around MDS calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/MetricsHandler.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/Migrator.cc -->
# sources/distributed-fs/ceph/src/mds/Migrator.cc

## Purpose

`Migrator.cc` implements Ceph MDS subtree and capability migration. It coordinates exporting authority and cached metadata from one MDS rank to another, importing that data on the destination, notifying bystander ranks of authority changes, handling failure/reversal, and moving client capabilities.

## Important APIs, Types, and Functions

- `export_state_t` tracks exporter state, peer, transaction id, waiting bystanders, imported cap acknowledgements, mutation locks, approximate export size, freeze diagnostics, and parent split-export coordination.
- `import_state_t` tracks importer state, peer, transaction id, bystanders, bounds, updated scatterlocks, forced sessions, peer cap exports, and mutation locks.
- `dispatch()` routes all migration message types: discover/prep/export/finish/cancel, notify/notifyack, cap export/ack, and gather caps.
- Export entry points are `export_dir()`, `export_dir_nicely()`, `maybe_do_queued_export()`, `dispatch_export_dir()`, `export_frozen()`, `export_go()`, `export_go_synced()`, and `export_finish()`.
- Import entry points are `handle_export_discover()`, `handle_export_prep()`, `handle_export_dir()`, `import_logged_start()`, `handle_export_finish()`, and `import_finish()`.
- Reversal and failure paths include `export_try_cancel()`, `export_reverse()`, `import_reverse()`, `import_reverse_unfreeze()`, and `handle_mds_failure_or_stop()`.
- Serialization helpers include `encode_export_prep_trace()`, `decode_export_prep_trace()`, `encode_export_inode()`, `encode_export_dir()`, `decode_import_inode()`, and `decode_import_dir()`.
- Capability-only migration is handled by `export_caps()`, `handle_export_caps()`, `logged_import_caps()`, `handle_export_caps_ack()`, and `handle_gather_caps()`.

## Control Flow

An export starts only if the source dir is auth, active, exportable, not frozen, not quiesced, not system/root-ineligible, and the destination rank is active. The exporter auth-pins and marks the dir exporting, starts an internal `CEPH_MDS_OP_EXPORTDIR` request, then acquires locks. Large subtrees can be split by `maybe_split_export()` into child exports governed by a shared parent record.

For a whole-subtree export, the exporter sends `MExportDirDiscover`, freezes the tree, receives discover ack, releases request locks, then waits for the freeze. Once frozen, it grabs required locks, encodes export bounds/traces in `MExportDirPrep`, flushes affected client sessions, waits for prep ack and bystander warnings, syncs the log, adjusts subtree auth to ambiguous, subtracts balancer popularity, encodes the full subtree into `MExportDir`, and sends it to the importer.

The importer creates `IMPORT_DISCOVERING` state, discovers/pins the root inode, decodes the prep root and traces, opens and pins bounds, adjusts bounded subtree auth to ambiguous, freezes the import region, and acks prep. On actual export data it logs `EImportStart`, force-opens sessions, decodes dirs/dentries/inodes/caps into cache, records peer cap exports, and then sends `MExportDirAck` with imported cap ids after `import_logged_start()`.

After exporter receives ack it logs `EExport`, notifies bystanders, sends final finish to importer, locally transitions exported objects to replica state, clears bounds, unfreezes, drops locks/pins, and trims cache. Importer finalizes caps, logs `EImportFinish(true)`, processes delayed expires, unfreezes, evaluates imported caps, and may re-export empty imports.

## State and Persistence Behavior

Migration state is held in `export_state` and `import_state`. Persistent recovery points are journal entries: `EExport`, `EImportStart`, `EImportFinish`, and `ESessions`. The code carefully orders auth changes, journaling, and finish messages so recovery can disambiguate ambiguous imports and exports. Runtime pins include auth pins, `PIN_EXPORTBOUND`, `PIN_IMPORTING`, `PIN_IMPORTBOUND`, `PIN_IMPORTINGCAPS`, and `PIN_EXPORTINGCAPS`.

## Dependencies and Integration Points

The file integrates with `MDSRank`, `MDCache`, `CDir`, `CInode`, `CDentry`, `Locker`, `Server`, `MDBalancer`, `MDLog`, `MDSMap`, `Mutation`, capability classes, migration message classes, and journal event classes. It also uses config options such as `mds_max_export_size`, `mds_inject_migrator_session_race`, and `mds_kill_export_at`/`mds_kill_import_at` failure-injection gates.

## Risks

- This is a distributed state machine with many legal intermediate states; missing one cleanup path can leave frozen trees, stale auth, or leaked pins.
- Lock ordering is critical around frozen trees, quiesce, scatter locks, and remote auth pins.
- Export splitting depends on size estimates and parent restart bookkeeping.
- Failure handling must distinguish failed peer, failed bystander, and local recovery states.
- Wire encoding is versioned in many nested buffers; incompatible decode changes can break migration.
- Forced session open/close and cap handoff must remain journaled and ordered with client notifications.

## Test Signals

High-value tests include successful export/import, export cancellation at every state, importer cancellation at every state, destination failure before ack, bystander failure during warning/notify, split export retry, stale freeze detection, cap-only export, ambiguous import recovery, forced-session race injection, and all `mds_kill_export_at`/`mds_kill_import_at` gates. Assertions in `audit()` and `dump_export_states()` provide useful invariant probes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/Migrator.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/Migrator.h -->
# sources/distributed-fs/ceph/src/mds/Migrator.h

## Purpose

`Migrator.h` declares the Ceph MDS migration coordinator. It exposes the API used by `MDCache`, `MDSRank`, balancer, locker, and message dispatch code to move subtree authority and capability ownership between MDS ranks.

## Important APIs, Types, and Members

- Export states range from `EXPORT_LOCKING` through `EXPORT_NOTIFYING`, with explicit cancel states.
- Import states range from `IMPORT_DISCOVERING` through `IMPORT_ABORTING`.
- `get_export_statename()` and `get_import_statename()` provide string names for diagnostics and dump output.
- Public status/query methods include `is_exporting()`, `is_importing()`, `is_ambiguous_import()`, `get_import_state()`, `get_import_peer()`, `get_export_state()`, `export_has_warned()`, and `export_has_notified()`.
- Public control methods include `dispatch()`, `handle_mds_failure_or_stop()`, `audit()`, `quiesce_overdrive_export()`, `export_dir()`, `export_empty_import()`, `export_dir_nicely()`, `maybe_do_queued_export()`, `clear_export_queue()`, and `maybe_split_export()`.
- Public encode/decode helpers are available for export/import inode, caps, and directory data.
- Protected methods are grouped by exporter, importer, cap migration, and bystander notification roles.
- Persistent state maps are `export_state` keyed by `CDir*` and `import_state` keyed by `dirfrag_t`.
- Private config-backed state includes `max_export_size` and `inject_session_race`.

## Control Flow

The header defines an event-driven object. External callers initiate exports, feed messenger messages to `dispatch()`, notify failures, and ask status questions. Most transitions are hidden behind protected helpers and friend context classes used as asynchronous continuations from locks, journal commits, waiters, and gather completions.

## State and Persistence Behavior

The header does not directly persist data but declares the state maps used by the implementation to coordinate journaled export/import events. `export_queue` and `export_queue_gen` model deferred exports and invalidate stale parent restarts. `total_exporting_size` and `num_locking_exports` throttle concurrent export size.

## Dependencies and Integration Points

The declaration depends on `Capability`, `Mutation` for `MDRequestRef`, `LogSegmentRef`, MDS message forward declarations, cache object forward declarations, and common Ceph types. It is central to MDS cache balancing, failure recovery, client cap transfer, and journal replay semantics.

## Risks

- The public helper surface is broad, so call sites can couple to migration internals.
- State constants are numeric and used in persisted diagnostics and many switch statements; adding a state requires updating transition logic, dumps, and failure handling.
- `export_state` keyed by raw `CDir*` assumes cache object lifetime is pinned correctly by the implementation.
- Friend context classes imply asynchronous callbacks can reach protected internals after partial state changes.

## Test Signals

Header-level review should verify every declared state has a name and switch coverage in the implementation, every public entry point has an invariant in `Migrator.cc`, and config changes update `max_export_size` and `inject_session_race`. API users should be tested against both normal and degraded MDS maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/Migrator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/Mutation.cc -->
# sources/distributed-fs/ceph/src/mds/Mutation.cc

## Purpose

`Mutation.cc` implements request/mutation lifetime helpers for Ceph MDS operations. It manages cache pins, auth pins, held lock descriptors, projected dirty metadata, request-specific extension state, diagnostics, and lock-cache attachment.

## Important APIs, Types, and Functions

- `MutationImpl::pin()`, `unpin()`, `drop_pins()` manage `MDSCacheObject::PIN_REQUEST`.
- `set_stickydirs()` and `put_stickydirs()` protect directory-fragment state on an inode.
- `start_locking()` and `finish_locking()` track the current lock acquisition attempt.
- `is_rdlocked()` and `is_wrlocked()` also consult an attached `MDLockCache`.
- `LockOp::print()`, `LockOpVec::erase_rdlock()`, and `sort_and_merge()` normalize lock acquisition vectors.
- Auth pin helpers are `auth_pin()`, `auth_unpin()`, `drop_local_auth_pins()`, `set_remote_auth_pinned()`, and `_clear_remote_auth_pinned()`.
- `add_updated_lock()`, `add_cow_inode()`, `add_cow_dentry()`, `apply()`, and `cleanup()` commit projected metadata state and release local pins.
- `MDRequestImpl` implements lazy `More` allocation, freeze/ambiguous-auth helpers, path helpers, batching checks, peer/client request reset/release, printing, and formatter dump output.
- `MDLockCache` attaches cached lock and dirfrag references to locks/caps for create/unlink style operations.

## Control Flow

Mutation users pin cache objects before operations that must keep them alive, auth-pin objects before mutating authority-owned state, and collect locks in `locks`. When metadata projections are ready, `apply()` pops projected inode/fnode state, marks copy-on-write inodes/dentries dirty, and marks scatter locks dirty. `cleanup()` releases local auth pins and normal pins; the destructor asserts that no locks, lock cache, pins, or auth pins remain.

`MDRequestImpl::more()` lazily allocates a large optional state block for uncommon peer, rename, snap, flock, export, and internal lookup data. Freeze auth pin paths set `rename_inode`, auth-pin it, freeze the inode, then convert to a frozen auth pin. Drop-local-auth-pins unfreezes when needed before delegating to `MutationImpl`.

`can_batch()` allows only simple root `GETATTR` and one-component non-snap `LOOKUP` requests with no auth pins, remote pins, lock cache, or locks. `MDLockCache` attaches itself to cached locks and auth-pinned dirfrags, then detaches symmetrically.

## State and Persistence Behavior

This file does not journal by itself, but it controls which metadata becomes dirty and associated with a `LogSegmentRef`. `apply()` uses `ls` while popping projected state and marking dirty objects. Request state includes `reqid`, attempt, peer target, `object_states`, lock sets, updated locks, dirty COW lists, and optional `More` fields.

## Dependencies and Integration Points

Dependencies include `ScatterLock`, `SimpleLock`, `BatchOp`, `CDentry`, `CInode`, `CDir`, `MClientRequest`, `MMDSPeerRequest`, `TrackedOp`, and formatter/dump infrastructure. It is a foundational type for `Migrator`, `MDCache`, locker paths, server request handling, and op tracking.

## Risks

- Destructor assertions make cleanup bugs fatal, which is desirable but means every error path must release pins/locks.
- `LockOpVec::sort_and_merge()` assumes same-object grouping and non-empty vectors in its iterator logic.
- Remote auth pins are counted separately and must be cleared by the distributed request protocol.
- Freeze auth pin state lives in optional `More`, so callers must not bypass the specialized drop/unfreeze path.
- `release_client_request()` and `reset_peer_request()` use the inherited tracked-op mutex; ownership changes should be reviewed carefully.
- `MDLockCache::get_cap_bit_for_lock_cache()` aborts for unsupported opcodes.

## Test Signals

Tests should cover pin/auth-pin reference counts, apply/cleanup ordering, lock vector merge semantics, lazy `More` allocation, freeze/unfreeze auth pin paths, batching eligibility, formatter dump for client/peer/internal ops, and `MDLockCache` attach/detach symmetry. Fault tests should verify cleanup after aborted requests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/Mutation.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/Mutation.h -->
# sources/distributed-fs/ceph/src/mds/Mutation.h

## Purpose

`Mutation.h` declares the common mutation and metadata request state used throughout Ceph MDS. It models cache object pinning, auth pinning, lock ownership, projected metadata updates, peer/client/internal request context, and lock-cache reuse.

## Important APIs, Types, and Members

- `MutationImpl : public TrackedOp` is the base mutation state.
- `ObjectState` tracks per-cache-object request pin, local auth pin, and remote auth pin owner.
- `LockOp` models rdlock, wrlock, xlock, remote wrlock, and state pin flags for a `SimpleLock`.
- `LockOpVec` accumulates ordered lock requests and can sort/merge them.
- `lock_set locks` holds acquired locks; `lock_cache` can contribute cached read/write locks.
- Request lifetime state includes `reqid`, optional `result`, `attempt`, `ls`, `peer_to_mds`, object states, pin counters, sticky dirs, current `locking`, and flags such as `committing`, `aborted`, `killed`, and `dead`.
- Dirty/projected state includes `projected_nodes`, `updated_locks`, `dirty_cow_inodes`, and `dirty_cow_dentries`.
- `MDRequestImpl` extends `MutationImpl` for client, peer, and internal MDS requests.
- `MDRequestImpl::More` stores uncommon fields: peers, witnesses, rename/auth-freeze state, imported sessions/caps, flock/snap data, waiting contexts, export/fragment data, and internal lookup paths.
- `Params` carries construction metadata and message refs.
- `MDPeerUpdate` models peer rollback/waiter cleanup.
- `MDLockCache` caches lock/auth-pin state associated with a client capability and opcode.

## Control Flow

Callers construct `MDRequestImpl` from `Params`, then progressively fill path, lock, pin, peer, and optional `More` fields as request processing advances. Mutation cleanup is explicit; the destructor only verifies that cleanup already happened. The lazy `More` split keeps common request memory smaller while still supporting complex rename, peer update, export, and snap operations.

## State and Persistence Behavior

The header declares state that is later used to mark projected metadata dirty against a log segment. It also stores request identity and op timestamps for tracking/dumps. No persistence occurs in the header itself, but `ls`, projected nodes, COW lists, peer rollback buffers, and imported cap/session maps are central to journaled metadata mutation and replay behavior.

## Dependencies and Integration Points

Dependencies include `TrackedOp`, `Context`, `interval_set`, `elist`, `filepath`, `Capability`, `LogSegmentRef`, `mdstypes`, and `MMDSPeerRequest`. The types are shared by locker code, MDCache request processing, server ops, migrator export/import, batching, and diagnostics.

## Risks

- This is a high-fanout shared header; layout or semantic changes can affect many MDS paths.
- Raw pointers dominate because the cache owns objects; correct pin/auth-pin discipline is mandatory.
- Optional `More` fields require `has_more()` checks before const access.
- The destructor asserts no outstanding locks or pins, so request lifecycle tests must cover every abort path.
- `MDLockCache` ties cached lock validity to cap lifetime and opcode-specific cap bits.

## Test Signals

Useful tests include construction from `Params`, client/peer/internal descriptor output, lock-flag predicates, lock cache eligibility, optional `More` lifecycle, auth pin count invariants, and memory/lifetime behavior for aborted or killed requests. Compile-time users should be checked for direct field access that bypasses helper invariants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/Mutation.h -->
