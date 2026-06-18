# subset-b-006917 research

Grouped research report for Ceph MDS files in `sources/distributed-fs/ceph/src/mds`. Each section is delimited for reconciliation into the source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/OpenFileTable.cc -->
## sources/distributed-fs/ceph/src/mds/OpenFileTable.cc

Purpose: implements `OpenFileTable`, the MDS rank component that records open file inodes and tracked directory fragments in metadata-pool omap objects named `mds<rank>_openfiles.<idx>`. It keeps enough anchor/backpointer data to reconstruct open files during replay/rejoin and to prefetch recovered inodes before recovery decisions.

Important APIs and control flow: public add/remove APIs delegate to `get_ref()` and `put_ref()`, which maintain `anchor_map`, inherited parent references, `CInode::STATE_TRACKEDBYOFT`, and `CDir::STATE_TRACKEDBYOFT`. `notify_link()` and `notify_unlink()` update stored parent dentry coordinates when an open inode is linked or unlinked. `commit()` converts `dirty_items` into omap updates/removals, assigns objects up to `MAX_OBJECTS`, splits large writes at `mdcache->max_dir_commit_size`, and chooses either a direct write or a two-phase journaled update. `_load_finish()` decodes omap headers and values, handles legacy headers, scans more keys/objects, and replays `_journal.*` records. `prefetch_inodes()` and `_open_ino_finish()` stage recovery through directory inode load, optional dirfrag fetch, then file inode load.

State and persistence: persistent state is `omap_version`, `omap_num_objs`, per-object counts, anchor records, and a header journal state (`JOURNAL_NONE`, `JOURNAL_START`, `JOURNAL_FINISH`). Multi-object or multi-request commits first write `_journal.<n>` records containing intended updates/removes, then apply real omap changes and remove journal keys. Load replays complete journals and discards/reset state on malformed headers or I/O failure. Runtime state includes commit waiters, load waiters, prefetch waiters, pending open counts, destroyed inode filters by log segment, and perf counters for object/key/update/remove totals.

Dependencies and integration: depends on `MDSRank`, `MDCache`, `CInode`, `CDir`, `Anchor`, `Objecter`, `ObjectOperation`, Ceph buffer encoding, and MDS finisher contexts. `MDCache` owns an `OpenFileTable`, uses its committed log sequence and prefetch behavior during recovery, and calls tracking methods when open-file or dirfrag references change.

Risks and test signals: correctness relies on strict assert-heavy invariants: dirty state must match omap placement, total omap item count must equal `anchor_map.size()`, and only one commit may be pending. Journal recovery, legacy header decoding, destroyed-inode filtering, and multi-object object-count shrink/expand are high-risk areas. Test signals include MDS recovery/rejoin tests that open files across failover, omap corruption/journal replay tests, and perf counters `oft.omap_total_*`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/OpenFileTable.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/OpenFileTable.h -->
## sources/distributed-fs/ceph/src/mds/OpenFileTable.h

Purpose: declares the `OpenFileTable` class and its public contract for tracking open inodes/dirfrags, persisting their anchors, loading/prefetching state after failover, and coordinating journal-log sequence durability.

Important APIs and types: callers use `add_inode()`, `remove_inode()`, `add_dirfrag()`, `remove_dirfrag()`, `notify_link()`, `notify_unlink()`, `commit()`, `load()`, `prefetch_inodes()`, `should_log_open()`, `wait_for_load()`, `wait_for_prefetch()`, and `wait_for_commit()`. Protected helpers expose object naming, header encoding, omap read/load/recover, ancestor reconstruction, and reference accounting. Constants include dynamic `MAX_ITEMS_PER_OBJ`, fixed `MAX_OBJECTS`, dirty sentinels, and prefetch/journal state enums.

State and persistence: the header shows the full persistent model: `omap_version`, `omap_num_objs`, `omap_num_items`, `anchor_map`, `dirty_items`, and `loaded_anchor_map`. It also declares transient coordination state for pending commits, committed/committing log sequences, loaded journals, load/prefetch waiters, destroyed inode tracking, perf counters, and commit waiters.

Dependencies and integration: includes CephFS inode/object/frag types, `mdstypes.h`, config access for the omap threshold, and forward declarations for MDS cache objects. Friend context classes in the `.cc` complete asynchronous objecter reads/writes on the MDS finisher.

Risks and test signals: consumers must not call `wait_for_load()` or `wait_for_prefetch()` after the corresponding state is done because the methods assert the opposite. The API assumes callers serialize through normal MDS locking and only call `commit()` when no other commit is pending. The most useful tests exercise load-before-prefetch, wait-for-commit ordering, and the `should_log_open()` suppression rules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/OpenFileTable.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/PurgeQueue.cc -->
## sources/distributed-fs/ceph/src/mds/PurgeQueue.cc

Purpose: implements a durable per-MDS purge work queue. It journals `PurgeItem`s, consumes them under configurable throttles, removes or zeroes file/dir objects through `Filer` and `Objecter`, and advances the journal expire position only after operations complete.

Important APIs and control flow: `PurgeItem::encode()`/`decode()` preserve purge payloads and support a v1 decoding workaround for a historical bad encoding. `open()` recovers the Journaler and trims partial entries through `_recover()` before enabling writes. `create()` initializes a resilient journal. `push()` appends a purge item, waits for flush, and attempts immediate consumption, scheduling delayed flush if throttled. `_consume()` loops while `_can_consume()` permits, waits for readable entries, decodes items, and calls `_execute_item()`. `_execute_item()` expands high-level actions into `PurgeItemCommitOp`s: file data range purge, backtrace removes, old pool backtrace removes, directory fragment object removes, or truncate range plus first-object zero. `_commit_ops()` submits the actual I/O gather and completes via `_execute_item_complete()`.

State and persistence: durable state is the Journaler stream identified by `MDS_INO_PURGE_QUEUE + rank`; read/write/expire positions are the queue cursor. Runtime state includes `in_flight` entries keyed by journal offset, `pending_expire` for out-of-order completions, `ops_in_flight`, `max_purge_ops`, delayed flush timer, recovery waiters, readonly flag, and high-water/perf counters. On internal I/O error, `_go_readonly()` marks the queue readonly, calls the error context, stops accepting pushes, and completes recovery waiters with an error.

Dependencies and integration: depends on `Journaler`, `Filer`, `Objecter`, `Striper`, `MDSMap`, `CInode::get_object_name()`, `SnapContext`, and MDS config knobs such as `mds_max_purge_files`, `mds_max_purge_ops`, and `mds_purge_queue_busy_flush_period`. `StrayManager` feeds items into this queue after metadata has been unlinked.

Risks and test signals: high-risk behavior includes partial journal recovery, v1 decode compatibility, out-of-order purge completion and expire-position advancement, readonly transition, and throttle updates from data-pool PG counts. Test signals include `PurgeItem::generate_test_instances()`, perf counters `pq_*`, failover/upgrade tests with non-empty purge journals, and operations that delete files with snapshots, old pools, directory fragments, or truncation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/PurgeQueue.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/PurgeQueue.h -->
## sources/distributed-fs/ceph/src/mds/PurgeQueue.h

Purpose: declares `PurgeItem`, `PurgeItemCommitOp`, perf counter IDs, and `PurgeQueue`, the durable asynchronous deletion engine for strays and truncations.

Important APIs and types: `PurgeItem` contains `Action` (`NONE`, `PURGE_FILE`, `TRUNCATE_FILE`, `PURGE_DIR`), inode number, size, file layout, old pools, snap context, fragment tree, timestamp, and padding for journal splicing. `PurgeItemCommitOp` captures concrete `Filer` or `Objecter` operations. `PurgeQueue` exposes lifecycle (`init`, `activate`, `shutdown`, `create`, `open`), recovery waiters, `push()`, `drain()`, idle check, and config/map update hooks.

State and persistence: the class owns its own `Finisher`, `SafeTimer`, `Filer`, and `Journaler`, explicitly avoiding `MDSDaemon::mds_lock`. Persistent queue entries live in the Journaler; in-memory state tracks in-flight offsets, pending expiration offsets, throttle counters, delayed flushes, recovery completion, readonly mode, and journal item sizing.

Dependencies and integration: depends on Ceph context/config, `MDSMap`, `Objecter`, metadata pool id, `Journaler`, and the caller-provided `on_error` context. The header documents that there is one queue per MDS rank and that persistence completion is reported to submitters, not eventual deletion completion.

Risks and test signals: public callers must wait for recovery before pushing and must tolerate `-EROFS` after internal I/O failure. `drain()` intentionally raises `max_purge_ops` to finish quickly, so drain tests should check progress accounting and no lost expire positions. Encoding tests should include `PurgeItem` v1/v2, `NONE` padding, and all action variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/PurgeQueue.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/QuiesceAgent.cc -->
## sources/distributed-fs/ceph/src/mds/QuiesceAgent.cc

Purpose: implements the worker-side quiesce agent that receives root state maps from the quiesce DB manager, starts or cancels local quiesce requests, and asynchronously acknowledges observed state back to the manager.

Important APIs and control flow: `db_update()` reconciles an incoming `QuiesceMap` with current tracked roots, removes failed roots from the response, reuses existing `TrackedRoot`s where possible, computes actual state, and arms pending roots for the agent thread. `agent_thread_main()` swaps pending roots into current, performs upkeep outside the mutex, issues `submit_request()` for roots that should quiesce, calls `cancel_request()` for roots that should release, builds an ack for state changes, sends `agent_ack()`, then waits for pending work or callback-triggered upkeep. `set_pending_roots()` arms a new version; `set_upkeep_needed()` wakes the thread when request completion changes state. `TrackedRoot::~TrackedRoot()` cancels an abandoned active quiesce request.

State and persistence: all state is in-memory. `current` and `pending` hold versioned root maps; each `TrackedRoot` stores request handle, cancel function, quiesce/cancel results, committed DB state, and expiry. No disk persistence is done here; durable/replicated state lives in the quiesce DB manager/listings.

Dependencies and integration: depends on `QuiesceDb.h`, Ceph `Thread`, `Context`, and callbacks supplied by MDS quiesce integration (`submit_request`, `cancel_request`, `agent_ack`). It avoids synchronous ack races by always returning false from `db_update()`.

Risks and test signals: risks center on threading and lifetimes: callback captures `this`, tracked roots use a spin lock, destructors can synchronously cancel, and reset warns about deadlock if called while holding the MDS lock. Tests should cover repeated DB versions, rollback logging, quiesce completion followed by release, cancellation failures, shutdown while callbacks are pending, and asynchronous ack ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/QuiesceAgent.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/QuiesceAgent.h -->
## sources/distributed-fs/ceph/src/mds/QuiesceAgent.h

Purpose: declares `QuiesceAgent`, the asynchronous bridge between replicated quiesce database state and local MDS quiesce mechanics.

Important APIs and types: `ControlInterface` supplies `submit_request`, `cancel_request`, and `agent_ack`. Public operations include construction/start, `shutdown()`, `reset()`, `reset_async()`, `db_update()`, `tracked_roots()`, `get_tracked_root()`, and `get_current_version()`. `TrackedRoot` records per-root request state and exposes `should_quiesce()`, `should_release()`, `update_committed()`, `get_ttl()`, `get_actual_state()`, and a small spin lock.

State and persistence: `TrackedRootsVersion` stores roots plus `QuiesceDbVersion` and an `armed` bit for pending/current handoff. The agent keeps mutex/condition-variable state, `stop_agent_thread`, and `upkeep_needed`. It does not persist anything; expiry is represented by absolute local time derived from received TTLs.

Dependencies and integration: depends on `QuiesceDb.h` types and Ceph `Thread`. The class is designed for subclass hooks `_agent_thread_will_work()` and `_agent_thread_did_work()` used by tests or integration instrumentation.

Risks and test signals: `reset()` can call cancel outside the mutex and warns about MDS-lock deadlocks; `reset_async()` uses an empty pending version to let the thread release roots. Tests should inspect `get_actual_state()` transitions for successful quiesce, failed quiesce, successful/failed cancel, expiry after committed release, and correct TTL saturation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/QuiesceAgent.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/QuiesceDb.h -->
## sources/distributed-fs/ceph/src/mds/QuiesceDb.h

Purpose: defines the core quiesce database model: lifecycle states, relative-time versioning, client requests, replicated listings, root maps, peer acks, and callback interfaces used by the manager and agents.

Important APIs and types: `QuiesceState` is ordered intentionally so min/max aggregation reflects lifecycle. `QuiesceDbVersion` pairs membership epoch and set version. `QuiesceSet` holds members, state, timeout, expiration, and methods for requested/effective member state and next set state. `QuiesceDbRequest` encodes include/query, exclude/cancel, reset/release, optional conditional version, timeout/expiration changes, await, flags, and roots. `QuiesceDbListing` is the replicated set-centric DB update. `QuiesceMap` is the root-centric request/ack map used by agents. `QuiesceInterface` defines transport/control callbacks.

State and persistence: no manager storage is implemented here, but all persistent/replicated fields are defined here. Times are represented as database ages rather than absolute timestamps because MDS clocks are not synchronized. `RecordedQuiesceState` records both state and relative age of state transition.

Dependencies and integration: uses Ceph coarse real clock, CephFS types, `mdstypes.h`, STL containers, and generic callback types. `QuiesceDbManager`, `QuiesceAgent`, and MDS message wrappers include these types.

Risks and test signals: enum ordering is a semantic dependency; inserting states in the wrong place would break min/max aggregation. Request validity has subtle wildcard rules, and `Control` uses a union with `raw` for encoding. Tests should cover request validity, root include/exclude/reset semantics, state aggregation under release/quiesced rollback, TTL saturation, and database-age calculations across replicated listings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/QuiesceDb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/QuiesceDbEncoding.h -->
## sources/distributed-fs/ceph/src/mds/QuiesceDbEncoding.h

Purpose: provides Ceph bufferlist `encode()` and `decode()` functions for all quiesce DB wire/persistence structures.

Important APIs and behavior: each structure uses `ENCODE_START(1, 1)` / `DECODE_START(1)` for versioned encoding. Encoded types include `QuiesceDbVersion`, `QuiesceState`, `QuiesceTimeInterval`, `RecordedQuiesceState`, `QuiesceSet::MemberInfo`, `QuiesceSet`, `QuiesceDbRequest`, `QuiesceDbListing`, `QuiesceDbPeerListing`, `QuiesceMap::RootInfo`, `QuiesceMap`, and `QuiesceDbPeerAck`. `QuiesceState` is stored as `uint8_t`, guarded by a static assertion; durations are stored as raw clock counts.

State and persistence: this header defines the wire compatibility surface for quiesce manager messages and any persisted bufferlists. Field order is the compatibility contract: changing it requires a new encoding version and compatibility decode path.

Dependencies and integration: depends on `QuiesceDb.h` and Ceph `include/encoding.h`. Message classes such as quiesce DB listing/ack wrappers depend on these overloads to serialize peer replication and acks.

Risks and test signals: the decode for `RecordedQuiesceState` calls `decode(rstate.at_age, p)` while encode writes `rstate.at_age.count()`, relying on the overload for `QuiesceTimeInterval`. Tests should round-trip all quiesce structures, include optional request fields, empty/non-empty maps, unknown state byte handling expectations, and cross-version compatibility if versions are raised.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/QuiesceDbEncoding.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/QuiesceDbManager.cc -->
## sources/distributed-fs/ceph/src/mds/QuiesceDbManager.cc

Purpose: implements the replicated quiesce DB manager thread. It handles membership changes, leader bootstrap, replica updates, client requests, peer acks, set state progression, await completion, and agent notification.

Important APIs and control flow: `quiesce_db_thread_main()` waits on submitted work or timed DB events, runs `membership_upkeep()`, then chooses leader or replica upkeep. Replicas keep only the latest listing, respond to discovery listings with local DB, adjust `time_zero` from listing age, and merge leader updates. A leader bootstraps by discovering all peers, choosing the highest peer set version if needed, and incrementing to force fresh acks. `leader_upkeep()` records acks, processes requests, advances DB sets, and checks awaits. `leader_process_request()` validates and sanitizes roots, creates sets, handles cancel-all, applies updates, and enqueues awaits. `leader_update_set()` applies include/exclude/reset/release/timeout/expiration changes. `leader_upkeep_set()` folds peer reports into member/set states and handles quiesce timeout and expiration. `calculate_quiesce_map()` builds root-centric agent commands from active sets.

State and persistence: the manager stores in-memory replicated DB state (`epoch`, `set_version`, `sets`, `time_zero`) and peer state (`diff_map`, activity, last sent version). Persistence is via repeated peer replication messages, not local disk. Await state and done request completion are local to the active leader. Database age is derived from `time_zero` so replicated listings preserve relative deadlines.

Dependencies and integration: uses `QuiesceDb.h`, `QuiesceDbManager.h`, `boost::url` for root normalization, `fmt`, MDS membership/courier callbacks, and agent callbacks. `MDSRankQuiesce.cc` wires manager requests, peer messages, and agent callbacks.

Risks and test signals: high-risk areas include membership transitions while awaits are pending, bootstrap from a peer with newer DB, repeated peer update throttling, root URI normalization/authority checks, request result sign conventions, fallthrough in release/await switch handling, and expiration/timeout boundary conditions. Tests should simulate leader changes, stale/future acks, missing peers, concurrent release plus await, duplicate roots after normalization, and agent callback absence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/QuiesceDbManager.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/QuiesceDbManager.h -->
## sources/distributed-fs/ceph/src/mds/QuiesceDbManager.h

Purpose: declares `QuiesceDbManager`, the threaded coordinator for quiesce DB leadership, replication, client request submission, peer acknowledgments, peer listings, and agent callback notification.

Important APIs and types: `QuiesceClusterMembership` describes epoch, filesystem identity, local/leader peer ids, members, and courier callbacks. `RequestContext` carries a `QuiesceDbRequest` and `QuiesceDbListing` response. Public APIs include `update_membership()`, `submit_request()`, `submit_peer_ack()`, `submit_peer_listing()`, `submit_agent_ack()`, and `reset_agent_callback()` overloads. Protected structures model the thread-owned DB, peer info, await contexts, and request completion map.

State and persistence: all manager state is in-memory and protected by `submit_mutex`/`agent_mutex`. The authoritative DB is reset on membership loss and versioned by epoch/set version. Peer state records last known root diff maps and last sent versions; awaits are local and complete when DB state changes or timeouts fire.

Dependencies and integration: depends on `QuiesceDb.h`, Ceph `Context`, `Thread`, filesystem id types, STL queues/deques/maps, and callback-based message transport. Only the leader accepts client requests and peer acks; replicas accept peer listings and forward agent acks to the leader.

Risks and test signals: public methods return `-ENOTTY`, `-EPERM`, or `-ESTALE` for role/epoch mismatches, so callers must not treat all failures as retryable. `shutdown()` first clears membership then joins the thread. Tests should verify role gating, epoch checks, local-vs-remote agent ack paths, callback reset version filtering, and clean thread exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/QuiesceDbManager.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/RecoveryQueue.cc -->
## sources/distributed-fs/ceph/src/mds/RecoveryQueue.cc

Purpose: implements an in-memory MDS file recovery queue that probes object sizes/mtimes for authoritative inodes needing max-size recovery after client writes or failover.

Important APIs and control flow: `enqueue()` clears `STATE_NEEDSRECOVER`, sets `STATE_RECOVERING`, auth-pins the inode, increments counters, and puts it on the normal queue if not already queued. `prioritize()` moves a queued inode to the front queue. `advance()` starts work from the priority queue first while below `mds_max_file_recover`. `_start()` checks projected inode client ranges and max size, starts `Filer::probe()` for new work, or marks active work for restart. `_recovered()` handles probe result, respawns on blocklist, marks MDS damaged on other OSD read errors, clears/restarts state, updates max size through `Locker::check_inode_max_size()`, evaluates the file lock, unpins, and advances more work.

State and persistence: no durable queue exists; recovery state is represented by inode state bits, auth pins, elist membership, and `file_recovering` restart flags. If the MDS dies, recovery candidates must be rediscovered from metadata/open-file state.

Dependencies and integration: depends on `CInode`, `MDCache`, `MDSRank`, `Locker`, `Filer`, perf counters, and config `mds_max_file_recover`. It is owned by `MDCache` and invoked when inodes require file size recovery.

Risks and test signals: risks include dangling queue list membership, double enqueue/prioritize, restart while a probe is in flight, and correctly clearing auth pins on skip/error paths. Tests should cover priority ordering, max concurrency, no max-size skip, restart flag behavior, blocklist respawn, and logger counter updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/RecoveryQueue.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/RecoveryQueue.h -->
## sources/distributed-fs/ceph/src/mds/RecoveryQueue.h

Purpose: declares `RecoveryQueue`, the MDCache helper that schedules file size recovery probes for authoritative inodes.

Important APIs and types: public methods are `enqueue(CInode*)`, `advance()`, `prioritize(CInode*)`, and `set_logger()`. Private callbacks `_start()` and `_recovered()` are used by the `C_MDC_Recover` I/O context in the implementation.

State and persistence: the class owns two intrusive `elist<CInode*>` queues, normal and priority, size counters, a map of active recoveries to restart flags, an `MDSRank*`, optional perf counter logger, and a `Filer`. There is no persistent journal or disk state.

Dependencies and integration: depends on `include/elist.h`, `Filer`, `CInode`, `MDSRank`, and perf counters. It relies on `CInode` list items `item_dirty_dirfrag_dir` and `item_dirty_dirfrag_nest` as queue hooks.

Risks and test signals: correctness depends on each inode being on at most one queue and on active recoveries being represented in `file_recovering`. Tests should assert list membership transitions, logger initialization before enqueue, and `prioritize()` behavior when the inode is already active or not queued.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/RecoveryQueue.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/RetryMessage.h -->
## sources/distributed-fs/ceph/src/mds/RetryMessage.h

Purpose: provides small MDS context helpers that redispatch an MDS message after an asynchronous wait condition resolves.

Important APIs and types: `C_MDS_RetryMessage` derives from `MDSInternalContext`, stores a `cref_t<Message>`, and on `finish()` calls `get_mds()->retry_dispatch(m)`. `CF_MDS_RetryMessageFactory` captures `MDSRank*` and a message and builds new retry contexts on demand.

State and persistence: state is only the retained message reference and target MDS pointer. No persistence or external state is modified until the context finishes.

Dependencies and integration: includes `MDSContext.h`, `MDSRank.h`, and `msg/Message.h`. `ScrubStack` uses `C_MDS_RetryMessage` when remote scrub handling must wait for dirfrag unfreeze before retrying the same message.

Risks and test signals: retrying preserves the original message, so callers must ensure the wait condition eventually changes and that redispatch is idempotent. Tests should cover waits that retry scrub messages without losing source identity or causing duplicate side effects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/RetryMessage.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/RetryRequest.h -->
## sources/distributed-fs/ceph/src/mds/RetryRequest.h

Purpose: declares request-retry contexts for `MDRequestRef` operations that need to be rescheduled after locks or cache conditions change.

Important APIs and types: `C_MDS_RetryRequest` stores an `MDCache*` and `MDRequestRef` and implements `finish()` in the corresponding source file elsewhere. `CF_MDS_RetryRequestFactory` stores the same request plus a `drop_locks` flag and builds retry contexts.

State and persistence: the header defines only in-memory retry state. It does not persist request state; it relies on `MDRequestRef` lifetime and MDCache request machinery.

Dependencies and integration: includes `MDCache.h` and `MDSContext.h`. Comments in nearby `CDir.cc` indicate retry requests can drive damage-table paths after blocked operations resume.

Risks and test signals: the main risk is lock ownership: retry factories that drop locks must match the wait condition that caused the retry. Tests should verify that retried metadata requests do not retain invalid locks, do not double-complete, and re-enter MDCache through the expected dispatch path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/RetryRequest.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/ScatterLock.h -->
## sources/distributed-fs/ceph/src/mds/ScatterLock.h

Purpose: defines `ScatterLock`, a `SimpleLock` specialization for distributed/scattered metadata values that can be dirtied, flushed, and rejoined across MDS ranks.

Important APIs and control flow: state queries include `is_scatterlock()`, `is_sync_and_unlocked()`, `can_scatter_pin()`, dirty/flushing/flushed checks, and scatter/unscatter wanted flags. Mutation APIs include `mark_dirty()`, `start_flush()`, `finish_flush()`, `remove_dirty()`, and update-stamp/list tracking. Rejoin APIs include `infer_state_from_strong_rejoin()`, `encode_state_for_rejoin()`, `decode_state_rejoin()`, and `remove_replica()`.

State and persistence: dirty/flushing/flushed/scatter flags live in `state_flags`. Dirty scatterlocks pin the parent with `PIN_DIRTYSCATTERED`; flush completion drops the pin and clears parent dirty-scattered state. Extra state is lazily allocated in `_more` to hold an updated-list item and timestamp, and is released when dirty is cleared.

Dependencies and integration: depends on `SimpleLock`, `MDSCacheObject`, `xlist`, and MDS context waiters. `Locker` and `CInode` use scatter locks for file and directory metadata scatter/gather behavior.

Risks and test signals: rejoin behavior is delicate: MIX states mark recovery need, flushing is converted back to dirty on decode, and replica removal is blocked during rejoin for several MIX sub-states. Tests should cover dirty pin lifetime, writebehind flush transitions, rejoin encode/decode of gathering states, and delayed rdlock behavior during recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/ScatterLock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/ScrubHeader.h -->
## sources/distributed-fs/ceph/src/mds/ScrubHeader.h

Purpose: defines `ScrubHeader`, the shared parameter and accounting object carried by recursive MDS scrub operations.

Important APIs and types: constructor captures tag, internal-tag flag, force, recursive, repair, and scrub-mdsdir options. Accessors expose origin inode, options, tag, repaired bit, forwarding epoch, and pending count. It also records uninline failures by errno/inode/path and counters for uninline started/passed/failed/skipped. `ScrubHeaderRef` and `ScrubHeaderRefConst` are shared pointer aliases.

State and persistence: state is in-memory for the lifetime of one scrub tag. It tracks global completion through pending count and `epoch_last_forwarded`; final failure/counter data is later collected by `ScrubStack` into scrub stats and the damage table.

Dependencies and integration: depends on inode number types and Ceph assertions. `ScrubStack`, `CInode`, and `CDir` attach and read headers while queueing, forwarding, validating, and completing scrub work.

Risks and test signals: pending count asserts on underflow, so all forwarded or async work must balance increments/decrements in code outside this header. Tests should cover multi-MDS forwarding epochs, uninline failure aggregation, repair flag propagation, and status reporting for force/recursive/repair/scrub_mdsdir options.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/ScrubHeader.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/ScrubStack.cc -->
## sources/distributed-fs/ceph/src/mds/ScrubStack.cc

Purpose: implements the MDS scrub scheduler, recursive traversal, remote scrub forwarding, pause/resume/abort control, status reporting, scrub stats exchange, and data-uninline integration.

Important APIs and control flow: `enqueue()` registers a tag, sets origin, optionally queues the local mdsdir, initializes counters, queues the root, logs status, and calls `kick_off_scrubs()`. `_enqueue()` initializes inode/dirfrag scrub state, skips purging objects, pins queue entries, and pushes top/bottom. `kick_off_scrubs()` respects `mds_max_scrub_ops_in_progress`, state transitions, waiting list, and recursively processes inodes or dirfrags. `validate_inode_auth()` either proceeds locally, waits for auth stability/recovery, or forwards to the authoritative rank. `scrub_dir_inode()` queues local dirfrags, forwards remote fragsets, waits for fetch/unfreeze, or final-validates. `scrub_dirfrag()` walks dentries, queues child inodes, identifies remote-link damage, scrubs local dirfrag state, and maybe fragments. `scrub_file_inode()` and `scrub_dir_inode_final()` call `validate_disk_state()`; `_validate_inode_done()` reports damage/repair and updates damage tables.

State and persistence: scrub queue state is in-memory: `scrub_stack`, `scrub_waiting`, `scrubs_in_progress`, `remote_scrubs`, `scrubbing_map`, state enum, `clear_stack`, control contexts, and per-rank scrub stats. Persistent side effects are indirect: damage table notifications, cluster log messages, possible metadata repair/log trim, and internal uninline metadata requests.

Dependencies and integration: depends on `MDCache`, `MDSRank`, `CInode`, `CDir`, `MMDSScrub`, `MMDSScrubStats`, `RetryMessage`, `SnapRealm`, Objecter/Filer-facing inode validation, and MDS lock discipline. Rank 0 coordinates scrub state messages and stats epochs.

Risks and test signals: risks include duplicate scrub tags, queue pin leaks, remote ACK loss, rank failure during remote scrub, abort/pause races while work is in progress, dirty remote dirfrag reporting, damaged dirfrag skip semantics, and uninline request lifetime. Tests should cover recursive multi-rank scrub, pause/resume/abort propagation, forced vs incremental scrub, remote dentry damage, stats epoch convergence, and repair-triggered log trimming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/ScrubStack.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/ScrubStack.h -->
## sources/distributed-fs/ceph/src/mds/ScrubStack.h

Purpose: declares `ScrubStack`, the MDCache-owned scrub work stack and distributed scrub coordination object.

Important APIs and types: public APIs include `enqueue()`, `scrub_abort()`, `scrub_pause()`, `scrub_resume()`, `scrub_status()`, `scrub_summary()`, `advance_scrub_status()`, `handle_mds_failure()`, `dispatch()`, `remove_inode_if_stacked()`, uninline failure/counter helpers, and config-change handling. Protected/private helpers manage queueing, waiting, auth validation, inode/dirfrag scrub, final validation callbacks, state messages, pending aborts, path summaries, message handlers, and uninline.

State and persistence: the header declares intrusive stack/waiting lists, in-progress counts, remote scrub gather sets, scrub epochs, abort flags, per-rank stats and counters, active tag map, state enum, clear-stack flag, and control contexts. The object is expected to be empty and idle at destruction.

Dependencies and integration: depends on `CInode`, `ScrubHeader`, cluster log, `Cond`, `elist`, `Finisher`, `CDir`, and MDS message types. It is tightly coupled to `MDCache` and MDS locking.

Risks and test signals: state transitions are asynchronous: abort and pause can be delayed until in-progress work completes, while resume cancels pending pause contexts. Tests should validate stack/waiting list accounting, summary/status output, rank 0 peer coordination, config refresh of `mds_scrub_stats_review_period`, and destructor invariants after completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/ScrubStack.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/SegmentBoundary.h -->
## sources/distributed-fs/ceph/src/mds/SegmentBoundary.h

Purpose: defines a small base class marking metadata log events that create or represent log segment boundaries.

Important APIs and types: `SegmentBoundary` stores a `LogSegment::seq_t`, exposes `get_seq()` and `set_seq()`, and provides virtual `is_major_segment_boundary()` defaulting to false. It has a virtual destructor so log events can derive from it safely.

State and persistence: only the segment sequence number is stored. Persistence is provided by derived log event types and `MDLog`; this base class does not encode or write anything itself.

Dependencies and integration: depends on `LogSegment.h`. `MDLog` uses `dynamic_cast<SegmentBoundary*>` when starting new segments and trimming by boundary sequence.

Risks and test signals: because behavior is type-identified through inheritance/dynamic cast, derived log events must inherit correctly and set sequence numbers consistently. Tests should cover MDLog segment creation/trimming around boundary events and major-boundary overrides in derived classes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/SegmentBoundary.h -->
