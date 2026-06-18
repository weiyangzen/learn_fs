# Research: subset-b-008851

Grouped source-tree-aligned research for TiKV raftstore store modules. Each section is delimited for reconciliation into the mapped per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/store/fsm/store.rs -->
## `sources/storage-engines/tikv/components/raftstore/src/store/fsm/store.rs`

### Purpose
This file is the store-level half of TiKV raftstore's batch-system runtime. It wires `PeerFsm` instances, the global `StoreFsm`, apply workers, asynchronous/synchronous raft log writers, PD/background workers, snapshot managers, transport, store metadata, and recurring store ticks into one `RaftBatchSystem`. It also owns the top-level raft message ingress path for messages whose target peer may not be registered yet.

### Important APIs, Types, and Functions
- `StoreRegionMeta` exposes store id, read delegates, region read progress, and range search for outside raftstore consumers.
- `StoreMeta` is the shared in-memory region map. It tracks `region_ranges`, `regions`, `readers`, pending raft messages, pending snapshots/merges, atomic snapshot destroy state, read progress, damaged file ranges/regions, and apply-catchup readiness counters.
- `RaftRouter<EK, ER>` wraps `BatchRouter<PeerFsm, StoreFsm>` and implements `ApplyNotifier`. It routes client raft commands, incoming raft messages, apply results, broadcasts, and control messages.
- `PollContext<EK, ER, T>` is the per-poller dependency bundle: config, store identity, routers, worker schedulers, engines, transport, metrics, snapshot manager, feature gate, store metadata, replication state, IO sender state, disk usage, latency inspectors, and GC safe point.
- `StoreFsm` is the singleton store control FSM with a loose-bounded receiver for `StoreMsg`.
- `StoreFsmDelegate` handles control messages and store ticks, including PD heartbeats, snapshot GC, compaction scheduling, imported SST cleanup, consistency checks, raft message rerouting/peer creation, replication-mode updates, unsafe recovery peer creation, and region wakeups.
- `RaftPoller` implements `PollHandler` for the batch system. It drains store and peer mailboxes, delegates peer work to `PeerFsmDelegate`, collects ready state, dispatches write work, flushes transports/metrics/tick batches, and updates busy signals.
- `RaftPollerBuilder::init` scans persisted region metadata from `CF_RAFT`, reconstructs peers, repairs applying snapshot state, clears tombstone metadata, registers meta/read-progress state, and deletes stale KV data ranges.
- `RaftBatchSystem::spawn`, `start_system`, and `shutdown` create, start, and stop raftstore workers and batch systems.
- `create_raft_batch_system` constructs the store and apply batch systems plus routers before full store bootstrap.

### Control Flow
Startup flows from `create_raft_batch_system` to `RaftBatchSystem::spawn`. `spawn` creates support workers, initializes the snapshot manager, region/snapshot/cleanup/PD/disk/fail-fast/write workers, then builds a `RaftPollerBuilder`. `RaftPollerBuilder::init` scans the KV engine's raft CF for `RegionLocalState`, drops tombstones, reconstructs normal/merging/unavailable peers, schedules applying snapshots, fills `StoreMeta`, and calls `clear_stale_data` for gaps outside known regions. `start_system` registers peer mailboxes, force-sends `PeerMsg::Start` to each peer, sends `StoreMsg::Start` to the store FSM, spawns raft and apply pollers, starts refresh-config and PD runners, and raises raftstore thread priority.

Runtime polling has three phases. `begin` refreshes dynamic config, buffer capacities, snapshot file limits, tick intervals, disk status, and write senders. `handle_control` drains bounded store messages and dispatches through `StoreFsmDelegate::handle_msgs`. `handle_normal` drains peer messages, delegates them to `PeerFsmDelegate`, collects ready state, and can skip expensive end processing when sync writes are enabled and no ready exists. `end` records latency-inspection timings, writes ready state synchronously or forwards inspectors to async write workers, marks the store busy if ready processing exceeds election timeout, and records process-ready metrics.

Incoming raft messages first try direct peer routing in `RaftRouter::send_raft_message`; if no peer route exists the message is sent to the store control mailbox as `StoreMsg::RaftMessage`. `StoreFsmDelegate::on_raft_message` retries direct routing, validates store id and epoch, handles tombstone/merge compatibility cases, calls `check_msg` against persisted `RegionLocalState`, possibly creates a peer through `maybe_create_peer`, or records a bounded pending first message for split races.

### State and Persistence Behavior
`StoreMeta` is in-memory but mirrors persisted region state. Region local state and raft state live in the KV engine raft CF and raft engine; startup reads them, writes cleanup batches for tombstones, recovers applying snapshot state through `peer_storage::recover_from_applying_state`, and consumes raft log batches synchronously where needed. `clear_stale_data` deletes KV data ranges not covered by any recovered region. Peer creation for replication registers memory metadata before mailbox registration, while unsafe recovery creation deletes stale data by key range, writes `PeerState::Normal` with sync write options, and then registers the peer.

Raft message memory is tracked through `MEMTRACE_RAFT_MESSAGES`; messages decrement trace on drop unless successfully forwarded. Router alive/leak counts are pushed to memory trace when peers are registered or closed. Periodic entry-cache eviction is configured here but actual eviction is handled in peer tick logic.

The file persists no user data directly outside repair, cleanup, unsafe recovery, and raft/write-worker setup paths. Most normal writes are batched through `StoreWriters` or sync write worker. Snapshot files are managed by `SnapManager` and cleanup/import SST workers, with stale import SST deletion governed by region epoch/version rules and an old-protocol one-week fallback.

### Dependencies and Integration Points
The file integrates `batch_system`, `engine_traits`, `kvproto`, `pd_client`, raft, resource control/metering, health controller latency inspection, failpoints, TiKV worker pools, snapshot/import subsystems, coprocessor region-change hooks, replication mode, fail-fast monitoring, async IO write/read routers, and PD reporting. It exports `RaftRouter` and `create_raft_batch_system` through `store/mod.rs`.

Store ticks depend on labels from `metrics.rs` and tick definitions from `msg.rs`. Hibernation and peer behavior are mostly delegated to `PeerFsmDelegate` and peer modules, but this file can broadcast unreachable/replication-mode/resolved-store events and awaken regions through raft messages.

### Risks and Edge Cases
- Lock ordering matters: comments require `store_meta` before `pending_create_peers` and before `global_replication_state`. Violating this can deadlock raftstore.
- `StoreMeta::set_region` panics if previous metadata is inconsistent while holding the meta lock.
- Peer creation must handle split, merge, overlapping ranges, damaged ranges, tombstones, and local-first races. Wrong ordering can register overlapping peers or lose first raft messages.
- `clear_stale_data` deletes gaps outside recovered regions at startup. Incorrect `region_ranges` reconstruction would make this destructive.
- The `pending_msgs` ring intentionally stores only bounded first messages; capacity pressure can discard old first messages.
- Unsafe recovery peer creation panics on write/delete failures after meta insertion, so partial failure handling depends on process abort/restart semantics.
- Metrics flushing is intentionally throttled; short test runs may not expose metric increments until flush.

### Test Signals
The file has one local unit test, `test_calc_region_declined_bytes`, validating compaction-range declined-byte attribution. Most important behavior is covered indirectly by raftstore integration tests elsewhere. Useful future test signals include startup recovery with applying/tombstone/merging states, local-first peer creation races, damaged range rejection, store heartbeat busy-on-apply transitions, and unsafe recovery peer creation persistence ordering.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/store/fsm/store.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/store/hibernate_state.rs -->
## `sources/storage-engines/tikv/components/raftstore/src/store/hibernate_state.rs`

### Purpose
This file models raft group hibernation state. It lets a leader negotiate whether a region can move from active replication into an idle hibernated state, while preserving compatibility with older TiKV versions through PD feature gating.

### Important APIs, Types, and Functions
- `NEGOTIATION_HIBERNATE` requires feature version 5.0.0 before broadcasting the negotiation protocol.
- `GroupState` is the serialized group-level state: `Ordered`, `Chaos`, `PreChaos`, or `Idle`.
- `LeaderState` tracks local leader negotiation state: `Awaken`, `Poll(Vec<u64>)`, or `Hibernated`.
- `HibernateState` combines group and leader state.
- `HibernateState::ordered` creates an active ordered state.
- `reset` changes group state, updates `HIBERNATED_PEER_STATE_GAUGE`, and wakes leader state unless the new group state is `Idle`.
- `count_vote` records one peer's hibernate vote during polling, deduplicated by peer id.
- `should_bcast` checks whether the feature gate allows hibernate negotiation.
- `maybe_hibernate` performs the leader-side vote/quorum/down-peer decision and returns `(hibernated, vote_peer_ids)`.

### Control Flow
The leader starts in `LeaderState::Awaken`. The first `maybe_hibernate` call moves it to `Poll` and returns false so peers can be asked to vote. Later calls include votes via `count_vote`. `maybe_hibernate` builds a vote set including the leader, checks for alive peers that have not voted and are not listed as down, allows quorum-based progress when non-voters are down, and finally enters `LeaderState::Hibernated` only if every peer is either leader, voted, or down.

### State and Persistence Behavior
`GroupState` derives `Serialize` and `Deserialize`, so it can cross message/config/storage boundaries where higher-level raftstore code chooses to persist or transmit it. This file itself performs no disk IO. State changes are in memory and reflected through `HIBERNATED_PEER_STATE_GAUGE`; `Idle` and `PreChaos` count as hibernated for the gauge, while `Ordered` and `Chaos` count as awaken.

### Dependencies and Integration Points
The code depends on `kvproto::metapb::Region` for peer lists, `pd_client::FeatureGate` for compatibility, `collections::HashSet` for vote/quorum sets, and raftstore metrics. It is re-exported by `store/mod.rs` as `GroupState` and `HibernateState`, then used by peer logic to negotiate quiet raft groups.

### Risks and Edge Cases
- The feature gate is important because older binaries cannot recognize the negotiation protocol and may reset connections.
- Down-peer handling allows hibernation with quorum even without every peer vote; correctness depends on the caller's `down_peer_ids` and quorum predicate being accurate.
- `reset` ignores same-state transitions, so gauge initialization depends on callers accounting for initial states elsewhere.
- `vote_peer_ids` is built from a hash set, so its order is intentionally unstable and should not be used as an ordered protocol.

### Test Signals
There are no local tests. Valuable coverage would include first-call polling transition, duplicate votes, all-voted hibernation, quorum-with-down-peers hibernation, alive-non-voter rejection, `reset` metric transitions, and feature-gate behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/store/hibernate_state.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/store/local_metrics.rs -->
## `sources/storage-engines/tikv/components/raftstore/src/store/local_metrics.rs`

### Purpose
This file defines buffered, thread-local raftstore metrics used on the performance-critical path. It converts raftstore events into local Prometheus counters/histograms and flushes them periodically to global collectors, reducing contention in raft pollers and write workers.

### Important APIs, Types, and Functions
- `RaftSendMessageMetrics` wraps `RaftSentMessageCounterVec` and maps raft `MessageType` values to accept/drop counters.
- `HealthStatistics` stores average disk and network latency samples for health inspection. It is backed by private `LocalHealthStatistics`.
- `IoType` distinguishes disk from network health samples.
- `RaftMetrics` owns local counters/histograms for ready handling, message sends/drops, proposals, invalid proposals, raft log GC skips, store/proposal/message timings, peer message size, commit log duration, write-block wait, IO read/write reasons, waterfall metrics, stale-peer checks, and leader-missing tracking.
- `RaftMetrics::new` binds all local metric handles to global metrics from `metrics.rs`.
- `RaftMetrics::maybe_flush` flushes every 10 seconds and updates `LEADER_MISSING`.
- `StoreWriteMetrics` buffers write-worker task wait and waterfall timings.
- `TimeTracker` bridges local histograms with request-level `tracker` TLS metrics and records write-stage timings.

### Control Flow
Pollers create `RaftMetrics::new` with the current waterfall-metrics config. Hot paths increment local handles directly. `maybe_flush` returns early until `METRICS_FLUSH_INTERVAL` has elapsed, then flushes all counters and histograms and drains the `leader_missing` set into a gauge. `RaftSendMessageMetrics::add` explicitly matches raft message types so new raft variants require an instrumentation decision.

`TimeTracker::default` captures the TLS tracker token and records `write_instant` if a tracker is active. `observe` records elapsed duration into the provided local histogram and fills the selected tracker field only once. `reset` moves the local start instant without changing the tracker token.

### State and Persistence Behavior
The file has only in-memory metric buffers. It does not persist raftstore data. The main state risk is observability freshness: local values are not visible globally until a flush interval elapses or an owning component calls flush.

### Dependencies and Integration Points
It depends on Prometheus local metric types, raft `MessageType`, tracker TLS/global trackers, TiKV time utilities, and metric definitions from `metrics.rs`. `RaftMetrics` is embedded in `PollContext` from `fsm/store.rs` and used throughout peer/store FSM code. `StoreWriteMetrics` is used by the async write path. `HealthStatistics` feeds health-controller latency inspectors.

### Risks and Edge Cases
- Message-type matching intentionally ignores internal raft messages; adding a new important raft message without updating this map can hide traffic.
- `HealthStatistics::avg` uses integer microseconds and returns default duration when empty, so zero can mean no samples or truly low latency.
- `leader_missing` uses a mutex-protected set inside `RaftMetrics`; high churn could contend, although it is flushed and cleared periodically.
- Waterfall metrics are conditional, so code must keep config refresh and metric flushing in sync.
- `TimeTracker` only sets tracker fields if they are currently zero, preserving first observation semantics.

### Test Signals
There are no local unit tests. Useful tests would validate `RaftSendMessageMetrics` mapping, flush interval behavior with mocked time, `HealthStatistics` averaging/reset, and `TimeTracker` behavior with and without a TLS tracker token.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/store/local_metrics.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/store/memory.rs -->
## `sources/storage-engines/tikv/components/raftstore/src/store/memory.rs`

### Purpose
This file defines raftstore memory tracing roots and helpers for entry-cache eviction decisions. It lets raftstore account memory for peers, apply FSMs, entry cache, router state, raft messages, and raft entries, then uses process high-water detection to decide when the entry cache should be evicted.

### Important APIs, Types, and Functions
- `MEMTRACE_ROOT` defines the raftstore memory trace tree.
- `MEMTRACE_PEERS`, `MEMTRACE_APPLYS`, `MEMTRACE_ENTRY_CACHE`, `MEMTRACE_RAFT_ROUTER_ALIVE`, `MEMTRACE_RAFT_ROUTER_LEAK`, `MEMTRACE_APPLY_ROUTER_ALIVE`, `MEMTRACE_APPLY_ROUTER_LEAK`, `MEMTRACE_RAFT_MESSAGES`, and `MEMTRACE_RAFT_ENTRIES` expose subtraces used by FSM/router/message code.
- `get_memory_usage_entry_cache` returns the summed entry-cache trace, with a failpoint override.
- `needs_evict_entry_cache` returns true when entry-cache usage exceeds a configured ratio of near-high-water process memory, with a failpoint override and zero-ratio disable behavior.

### Control Flow
The trace tree is initialized lazily. Code elsewhere records trace events against the relevant subtrace. `needs_evict_entry_cache` first honors a failpoint, returns false if the configured ratio is effectively zero, asks `memory_usage_reaches_near_high_water` whether process memory is near the high-water mark, and compares entry-cache traced bytes against `usage * ratio`.

### State and Persistence Behavior
All state is process-local memory accounting. There is no disk persistence. Correctness depends on callers adding and subtracting trace events reliably; for example `RaftRouter::send_raft_message` subtracts message heap size on failed forwarding.

### Dependencies and Integration Points
The file depends on `tikv_alloc::mem_trace`, failpoints, and `tikv_util::sys::memory_usage_reaches_near_high_water`. It is re-exported via `store/mod.rs` and consumed by raftstore FSM, entry cache, router, and apply paths.

### Risks and Edge Cases
- If trace increments/decrements are unbalanced elsewhere, eviction decisions become inaccurate.
- `needs_evict_entry_cache` only considers eviction when the process is near high-water memory; large entry cache below that threshold will not trigger eviction.
- A ratio below `f64::EPSILON` disables eviction, which is intentional but can surprise config validation.
- Failpoints can force mock usage or eviction behavior in tests.

### Test Signals
There are no local tests in this file. Useful tests would cover disabled ratio, mocked entry-cache usage, mocked high-water status, and trace balance in router/entry-cache callers.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/store/memory.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/store/metrics.rs -->
## `sources/storage-engines/tikv/components/raftstore/src/store/metrics.rs`

### Purpose
This file is the central Prometheus metric registry for raftstore store, peer, apply, snapshot, compaction, split, hibernation, write, IO, and slow-store observability. It defines static metric label enums and registers the global counters, gauges, histogram vectors, and local-auto-flush wrappers consumed by raftstore runtime code.

### Important APIs, Types, and Functions
- `make_auto_flush_static_metric!` declares label enums and typed local wrappers for perf context, write/admin commands, snapshot validation, region hash, CF names, raft entry fetches, warmup, snapshot CF metrics, and compaction guard actions.
- `make_static_metric!` declares typed vectors for raft ready, sent/dropped messages, proposals, invalid proposals, store event durations, raft log GC skip reasons, load-based split events, snapshot BR events, hibernated state, busy-on-apply gauges, CPU pool gauges, and snapshot generate-byte counters.
- `lazy_static!` registers global Prometheus metrics such as `STORE_TIME_HISTOGRAM`, `APPLY_TIME_HISTOGRAM`, store write histograms, waterfall histograms, IO duration histograms, proposal/admin/write counters, snapshot metrics, raft ready/message counters, read-index metrics, load split metrics, entry-cache metrics, slow trend gauges, snapshot BR metrics, and busy/CPU gauges.

### Control Flow
There is no runtime algorithm beyond lazy registration. Consumers import typed metrics or raw Prometheus handles, create local handles when needed, increment/observe on hot paths, and flush via local metrics code. The static metric macros provide compile-time field names for label combinations, which reduces label typo risk and keeps call sites ergonomic.

### State and Persistence Behavior
All state is Prometheus process memory. No raftstore data is persisted. Metric cardinality is mostly bounded by static labels, except a few vector labels such as store id, output level, target, type/window strings, and read-QPS order.

### Dependencies and Integration Points
The file depends on `lazy_static`, `prometheus`, and `prometheus_static_metric`. It is imported by `local_metrics.rs`, store/peer/apply/snapshot/worker modules, and re-exported in part by `store/mod.rs` (`RAFT_ENTRY_FETCHES_VEC`). Metric labels must remain aligned with `StoreTick::tag`, `PeerTick` handling, raft message mappings, proposal classification, snapshot validation, and worker code.

### Risks and Edge Cases
- Metric registration uses `unwrap`; duplicate metric names or incompatible label sets will panic during lazy initialization.
- Changing static label enums can break call sites and dashboards.
- High-cardinality dynamic labels must be treated carefully; `MESSAGE_RECV_BY_STORE` labels by store id and can grow with cluster membership.
- Local metrics can hide recent events until flushed by `local_metrics.rs`.
- Histogram bucket choices encode operational assumptions; changing them impacts alerting and dashboard comparability.

### Test Signals
There are no local tests. Compilation is the main guard for static metric field names. Runtime test signals should include metric registration smoke tests, dashboard/alert compatibility checks, and code review for new labels or metric names.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/store/metrics.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/store/mod.rs -->
## `sources/storage-engines/tikv/components/raftstore/src/store/mod.rs`

### Purpose
This file is the raftstore store module facade. It declares public and private submodules and re-exports the primary types, functions, routers, worker tasks, metrics, snapshot utilities, unsafe recovery handles, and helper APIs that other TiKV components use.

### Important APIs, Types, and Functions
- Public modules include `cmd_resp`, `config`, `entry_storage`, `fsm`, `local_metrics`, `memory`, `metrics`, `msg`, `region_meta`, `snapshot_backup`, `transport`, `util`, `simple_write`, and `snap`.
- Private modules include async IO, bootstrap, compaction guard, disk probe, fail-fast, hibernate state, peer storage, region snapshot, replication mode, peer/read queue internals, transaction extensions, unsafe recovery, and worker internals.
- Re-exports include bootstrap functions, config, entry storage, `RaftRouter`, `check_sst_for_ingestion`, hibernation types, memory helpers, message/callback types, peer/request helpers, peer storage constants/functions, read queue types, region snapshots, replication state, snapshot managers/utilities, transport traits, transaction extension types, unsafe recovery types/functions, region read progress utilities, and many worker task/controller/stat types.
- `PeerInternalStat` is only re-exported for tests or `testexport`.

### Control Flow
There is no executable control flow beyond module loading and export resolution. The file shapes the public API boundary for `crate::store::*` and controls which internals remain private.

### State and Persistence Behavior
This file owns no state and performs no persistence. Its persistence impact is indirect: it exposes peer storage functions, snapshot managers, bootstrap helpers, and unsafe recovery tools to other modules.

### Dependencies and Integration Points
Every major raftstore subsystem flows through this facade. API consumers can import from `crate::store` instead of deep module paths. The facade is especially important for `fsm/store.rs`, peer modules, server bootstrap, tests, PD workers, transport implementations, and snapshot/unsafe recovery integrations.

### Risks and Edge Cases
- Re-export churn can become a hidden public API break inside the crate.
- Publicly re-exporting too many worker/internal types increases coupling and makes refactors harder.
- Private modules such as `hibernate_state` are still partially exposed through selected re-exports.
- Feature-gated exports must stay aligned with test-only code to avoid build failures under different feature sets.

### Test Signals
There are no local tests. The main signal is whole-crate compilation across normal, test, and `testexport` feature sets. API cleanup should be validated by downstream imports rather than this file alone.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/store/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/store/msg.rs -->
## `sources/storage-engines/tikv/components/raftstore/src/store/msg.rs`

### Purpose
This file defines raftstore's message and callback contracts. It is the shared vocabulary for client raft commands, read/write responses, peer ticks, store ticks, significant peer events, casual peer notifications, inspected raft network messages, and store-level control messages.

### Important APIs, Types, and Functions
- `ReadResponse<S>` and `WriteResponse` wrap raft command responses; reads may include a `RegionSnapshot` and transaction extra operation.
- `PeerClearMetaStat` records raft and KV metadata cleanup durations.
- `Callback<S>` represents no-op, read, write, and test callbacks. Write callbacks can include proposed and committed early callbacks plus `TimeTracker` entries.
- `ReadCallback`, `WriteCallback`, and `ErrorCallback` abstract callback completion/error paths; `Vec<C>` implementations fan out errors and write notifications.
- `PeerTick` enumerates periodic peer tasks and provides stable tags/all-tick ordering.
- `StoreTick` enumerates store-level periodic tasks and maps to `RaftEventDurationType`.
- `MergeResultKind`, `SignificantMsg`, `CampaignType`, and `CasualMessage<EK>` model high-level peer events ranging from snapshot status and merge results to unsafe recovery, split, bucket refresh, force compaction, snapshot applied, and in-memory-engine load triggers.
- `RaftCmdExtraOpts` and `RaftCommand<S>` wrap user raft command requests with callback, send time, deadline, and disk-full behavior.
- `InspectedRaftMessage` carries a raft network message plus precomputed heap size for memory accounting.
- `PeerMsg<EK>` is the per-region FSM mailbox message enum.
- `StoreMsg<EK>` is the singleton store FSM control mailbox message enum.

### Control Flow
Callbacks are invoked by consuming the callback object: read callbacks receive `ReadResponse`, write callbacks receive `WriteResponse` or raft response, and error callbacks reuse normal response delivery. Write callbacks can notify proposed/committed stages before final result, and can expose mutable tracker lists for write-stage timing.

Peer/store pollers use `discriminant` methods to build slow-log distributions in parallel with `strum` variant names. `PeerMsg::is_send_failure_ignorable` identifies the rare significant message that can fail to send without treating it as fatal. Debug implementations intentionally summarize large or callback-bearing messages to avoid expensive or unsafe formatting.

### State and Persistence Behavior
The file defines message state but performs no IO. Persistence semantics are encoded in message meaning: `PeerMsg::ApplyRes`, `PeerMsg::Persisted`, `SignificantMsg::RaftLogGcFlushed`, snapshot/merge/unsafe recovery variants, and `StoreMsg::UnsafeRecoveryCreatePeer` are consumed by other modules to advance durable raft/KV state. `RaftCommand` includes deadline and disk-full options that influence proposal handling.

### Dependencies and Integration Points
The definitions depend on `engine_traits`, `kvproto`, raft, resource-control metering, health-controller latency inspection, futures channels, tracker, region snapshots, apply task results, unsafe recovery syncers, snapshot backup requests, worker bucket types, and metrics labels. `fsm/store.rs`, peer FSMs, apply FSMs, workers, transport, snapshot backup, unsafe recovery, tests, and external request routers all use these types.

### Risks and Edge Cases
- `Callback::invoke_read` panics if called on a non-read callback; callers must keep request classification correct.
- `PeerMsg` size is performance-sensitive and locally tested.
- Discriminant values must remain aligned with slow-log distribution arrays and `EnumCount`; test-only `StoreMsg::Validate` must stay last.
- Some messages are explicitly lossy (`CasualMessage`) while others must not be lost (`ApplyRes`, `SignificantMsg`). Wrong send path selection can cause correctness bugs.
- `RaftCommand::new_ext` copies only known extra option fields, so adding fields to `RaftCmdExtraOpts` requires updating construction logic.
- Debug formatting must avoid exposing huge payloads or consuming callbacks.

### Test Signals
Local tests assert `PeerMsg<RocksEngine>` remains 32 bytes and validate `StoreMsg` discriminant/variant-name slow-log alignment for selected variants. Additional useful tests would cover callback fanout/error behavior, proposed/committed callback one-shot behavior, `PeerTick::VARIANT_COUNT` alignment, and new message variant discriminants.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/store/msg.rs -->
