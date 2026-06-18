# subset-b-008848 Research

Grouped source research for TiKV raftstore FSM lifetime helpers, store-level metrics aggregation, and the FSM module export surface. Each section is marker-delimited for reconciliation into the mapped source-tree-aligned research documents.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/store/fsm/life.rs -->
# sources/storage-engines/tikv/components/raftstore/src/store/fsm/life.rs

## Purpose

`sources/storage-engines/tikv/components/raftstore/src/store/fsm/life.rs` contains peer lifetime helper functions shared by the original raftstore FSM and raftstore v2 compatibility paths. Its scope is narrow but safety-critical: it constructs GC-peer response messages, forwards destroy checks from a merged target peer to a source peer, and lets compatible learners answer tombstone messages by inspecting persisted region state.

The file was read completely as a 98-line Rust module. It has no owned background tasks or structs; it is a helper module used by `store/fsm/store.rs` and `store/fsm/peer.rs`.

## Important APIs, Types, and Functions

`build_peer_destroyed_report(tombstone_msg: &mut RaftMessage) -> Option<RaftMessage>` builds an `ExtraMessageType::MsgGcPeerResponse` when a tombstone message proves that the addressed peer has been destroyed. If the incoming message already has an extra message, it asserts that the type is `MsgGcPeerRequest` and derives the destination region from `check_gc_peer.from_region_id`; otherwise it uses the message `region_id`. It refuses to build a response when the destination region id is zero or the original sender peer id is zero. The function consumes the incoming `to_peer` and `from_peer` via `take_to_peer` and `take_from_peer`, so callers should treat the input message as moved after calling it.

`forward_destroy_to_source_peer<T: FnOnce(RaftMessage)>(msg: &RaftMessage, forward: T)` converts a v2-style GC-peer request handled by a target peer into a tombstone raft message addressed to the merged source peer. It copies `check_region_id`, `check_peer`, `check_region_epoch`, and `from_region_id` from the request's `check_gc_peer` payload, sets `is_tombstone = true`, tags the extra message as `MsgGcPeerRequest`, and delegates transmission to the supplied closure.

`handle_tombstone_message_on_learner<EK: KvEngine>(engine: &EK, store_id: u64, mut msg: RaftMessage) -> Option<RaftMessage>` is the compatibility hook for learners such as TiFlash when `enable_v2_compatible_learner` is active. It reads `RegionLocalState` from the KV engine's raft column family under `keys::region_state_key(region_id)`. Missing or unreadable state is treated as a peer that may never have been created, and the function attempts to answer with `build_peer_destroyed_report`. If persisted state exists and is not `PeerState::Tombstone`, it returns `None`. If state is tombstone, it compares epochs and returns a destroyed report when the incoming epoch equals the local epoch or is stale relative to it.

## Control Flow

The store-level raft message handler in `store/fsm/store.rs` validates destination store id and region epoch first. When a message is tombstone and `enable_v2_compatible_learner` is true, it calls `handle_tombstone_message_on_learner`; any returned response is sent through the transport, and the original message is not routed to normal peer creation or peer FSM handling.

The peer-level extra message handler in `store/fsm/peer.rs` receives `MsgGcPeerRequest` only when v2 learner compatibility is enabled. `on_gc_peer_request` rejects malformed requests that lack `check_gc_peer` or have `extra_msg.index == 0`, waits until the local applied index reaches the request index, and then calls `forward_destroy_to_source_peer` to send a tombstone check to the source peer through `router.send_raft_message`.

`build_peer_destroyed_report` is the terminal response constructor for both direct tombstone handling and the missing-state path. Its output swaps sender and receiver peers, sets the response region, and attaches `MsgGcPeerResponse`.

## State and Persistence Behavior

The only persistent read in this module is `engine.get_msg_cf(CF_RAFT, &keys::region_state_key(region_id))`, decoded as `RegionLocalState`. No writes are performed. The persisted `PeerState::Tombstone` value and region epoch determine whether this local store can safely confirm destruction.

The module mutates in-memory `RaftMessage` values while building replies. That mutation is intentional but important: `take_to_peer` and `take_from_peer` empty those fields from the input. The forwarding helper builds a fresh tombstone message and does not mutate the original request.

## Dependencies and Integration Points

Direct dependencies include `engine_traits::{CF_RAFT, KvEngine}` for persisted region-local-state reads, `kvproto::raft_serverpb::{ExtraMessageType, PeerState, RaftMessage, RegionLocalState}` for raftstore wire messages and state, `keys::region_state_key` for the storage key, `crate::store::util::is_epoch_stale` for epoch safety checks, and `tikv_util::warn` for read failure diagnostics.

Primary integration points are the store FSM tombstone-message path, the peer FSM extra-message path, raftstore v2 GC-peer protocol compatibility, learner engines such as TiFlash, and merge cleanup flows where a target peer confirms source peer destruction. The behavior must remain consistent with raftstore v2's `Peer::on_gc_peer_request`, as noted by the caller.

## Risks and Edge Cases

The `assert_eq!` in `build_peer_destroyed_report` will panic if a caller passes a message with an unrelated extra message type. Current callers only pass tombstone or GC-peer request messages, but the helper is public within the module tree and relies on that contract.

The missing or unreadable `RegionLocalState` path sends a destroyed report. This is deliberate for skipped peer creation after snapshots, but a broad storage read failure can therefore be converted into a GC response. The warning includes store and region information, so operational logs are the main signal if this path is masking an engine problem.

Epoch handling is conservative: only equal or stale incoming epochs produce a response when tombstone state exists. Newer incoming epochs return `None`, avoiding acknowledgement against a local tombstone record that may not represent the requester's view.

Zero `from_region_id` or zero sender peer id suppresses the response. Corrupted GC-peer requests are also dropped earlier in `peer.rs` if required payload or index data is absent.

## Test Signals

Useful tests cover response construction for plain tombstone and `MsgGcPeerRequest` inputs, including sender/receiver peer swapping, `from_region_id` routing, and the `None` cases for zero ids.

Learner tombstone tests should exercise missing state, non-tombstone state, tombstone with equal epoch, tombstone with stale incoming epoch, and tombstone with newer incoming epoch. A mock `KvEngine` that returns read errors should verify that the warning path still attempts a destroyed report.

Integration tests should cover v1/v2 learner compatibility around merges: a peer receives `MsgGcPeerRequest`, waits for `applied_index >= extra_msg.index`, forwards a tombstone check to the source peer, and eventually emits `MsgGcPeerResponse`. Existing apply tests that enable `enable_v2_compatible_learner` are related signals, but this module benefits from direct unit coverage because the control flow is compact and protocol-sensitive.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/store/fsm/life.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/store/fsm/metrics.rs -->
# sources/storage-engines/tikv/components/raftstore/src/store/fsm/metrics.rs

## Purpose

`sources/storage-engines/tikv/components/raftstore/src/store/fsm/metrics.rs` defines a small set of raftstore FSM metrics and shared store-stat aggregation types. It bridges hot-path per-poller accounting with global atomics that the store heartbeat and maintenance ticks can consume without locking every write operation.

The file was read completely as a 122-line Rust module. It contains a Prometheus histogram for apply proposal batch size and the `StoreStat` / `GlobalStoreStat` / `LocalStoreStat` aggregation pattern.

## Important APIs, Types, and Functions

`APPLY_PROPOSAL` is a lazily registered Prometheus `Histogram` named `tikv_raftstore_apply_proposal`. It observes the count of proposals sent by a region at once using exponential buckets from 1 to 2^19. The apply FSM observes it after draining proposals into pending commands.

`StoreStat` is the global atomic storage for raftstore write-flow and busy-state metrics: `lock_cf_bytes_written`, `engine_total_bytes_written`, `engine_total_keys_written`, `engine_total_query_put`, `engine_total_query_delete`, `engine_total_query_delete_range`, and `is_busy`. All fields use atomics so multiple pollers or local flushes can update shared counters cheaply.

`GlobalStoreStat` wraps `Arc<StoreStat>` and exposes `local(&self) -> LocalStoreStat`, creating a zeroed local accumulator tied back to the same global stat object.

`LocalStoreStat` stores non-atomic local counters for one poll context: lock CF bytes, total written bytes, total written keys, `tikv_util::store::QueryStats`, and an `is_busy` flag. Its custom `Clone` does not duplicate accumulated values; it returns a fresh zeroed local accumulator for the same global object.

`LocalStoreStat::flush(&mut self)` transfers non-zero local counters into the global atomics with relaxed ordering, clears the local counters, and sets the global `is_busy` flag to true if the local poller observed busy state.

## Control Flow

`RaftPoller::end` in `store/fsm/store.rs` calls `self.poll_ctx.store_stat.flush()`, so local metrics accumulated during raft processing are periodically folded into `GlobalStoreStat`. Peer execution updates write counters after command execution results have fully completed, avoiding double counting around commit-merge waits.

The store heartbeat path in `store/fsm/store.rs` consumes global counters with atomic `swap(0, Ordering::Relaxed)` for bytes, keys, query stats, and busy state, then writes those values into `pdpb::StoreStats` for PD. The lock-CF compaction tick reads `lock_cf_bytes_written` with `SeqCst` and subtracts the observed total when scheduling a full lock CF compaction.

`APPLY_PROPOSAL` is observed in `store/fsm/apply.rs` after proposals have been converted into pending commands. The metric is intentionally independent from `StoreStat`; it is an immediate Prometheus histogram, not part of PD store heartbeat stats.

## State and Persistence Behavior

This module owns no persistent state and performs no engine I/O. Its state is process-local telemetry. Local accumulators live inside raftstore poll contexts; global atomics live behind an `Arc` shared by the raftstore system.

Most flush operations use `Ordering::Relaxed` because the counters are telemetry and do not guard correctness-critical memory. `lock_cf_bytes_written` uses stronger ordering in the consuming compaction path, but local flush still uses relaxed `fetch_add`. The busy flag is level-like between heartbeats: any local busy observation stores true globally, and the heartbeat consumes it with `swap(false, Relaxed)`.

## Dependencies and Integration Points

Direct dependencies are `std::sync::{Arc, atomic::*}`, `lazy_static`, `prometheus::{Histogram, exponential_buckets, register_histogram}`, and `tikv_util::store::QueryStats`.

The module is re-exported by `store/fsm/mod.rs` as `GlobalStoreStat` and `LocalStoreStat`. `RaftPollerBuilder` initializes `GlobalStoreStat::default()`, `PollContext` carries both global and local stats, peer FSM command execution increments local write counters, raft poller shutdown/end-of-iteration flushes them, and store heartbeat reports the global values to PD. Lock CF compaction uses the lock-CF byte counter to schedule cleanup work.

## Risks and Edge Cases

Because `LocalStoreStat::clone` drops local accumulated values and returns a fresh zeroed accumulator, callers must not clone it expecting a snapshot. In this codebase it is used as a context-local accumulator, and the custom clone avoids accidental double counting.

Counters can be temporarily underreported if a poller exits or stalls before `flush`. The design accepts eventual telemetry accuracy in exchange for avoiding atomics on every hot-path mutation.

`flush` only clears the `put`, `delete`, and `delete_range` fields of `QueryStats`; if `QueryStats` grows additional fields, this code must be updated or new query counters will never reach PD stats.

The lock-CF compaction path subtracts the loaded total after scheduling. Concurrent relaxed additions can race with the load/subtract window; as telemetry-driven thresholding this is acceptable, but changes here should avoid making compaction scheduling depend on exact accounting.

## Test Signals

Unit tests should verify that `GlobalStoreStat::local` starts at zero, `LocalStoreStat::flush` adds each counter to the matching global atomic, clears local fields, and sets/clears busy state as expected. A focused test should assert that cloning a `LocalStoreStat` does not carry over accumulated counters.

Integration signals include store heartbeat tests that confirm bytes, keys, query stats, and busy state are swapped into `StoreStats`, peer execution tests that update `ctx.store_stat` only after command results complete, and lock-CF compaction tests that schedule cleanup only after the threshold is exceeded.

Metrics smoke tests can validate that `APPLY_PROPOSAL` registration succeeds and observations from apply proposal draining appear in the histogram without panics or duplicate registration.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/store/fsm/metrics.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/store/fsm/mod.rs -->
# sources/storage-engines/tikv/components/raftstore/src/store/fsm/mod.rs

## Purpose

`sources/storage-engines/tikv/components/raftstore/src/store/fsm/mod.rs` is the module root and public facade for the raftstore finite state machine implementation. It defines the FSM submodules and re-exports the primary types and constructors used by the rest of the raftstore crate.

The file was read completely as a 25-line Rust module. Its documentation explains the current architecture: peers are state machines representing region replicas, while the store is also a special state machine for store-wide requests; the two are still mixed but expected to separate in the future.

## Important APIs, Types, and Functions

Declared submodules are `apply`, `life`, `metrics`, `peer`, and `store`. `apply`, `life`, and `store` are public modules; `metrics` and `peer` are private modules with selected public re-exports.

The apply facade re-exports `Apply`, `ApplyBatchSystem`, `ApplyMetrics`, `ApplyRes`, `ApplyRouter`, `ApplyPollerBuilder`, `CatchUpLogs`, `ChangeObserver`, `ChangePeer`, `ExecResult`, `GenSnapTask`, `ApplyTask`, `ApplyNotifier`, `Proposal`, `Registration`, `SwitchWitness`, `ApplyTaskRes`, `check_sst_for_ingestion`, and `create_apply_batch_system`.

The metrics facade re-exports `GlobalStoreStat` and `LocalStoreStat`.

The peer facade re-exports `DestroyPeerJob`, `MAX_PROPOSAL_SIZE_RATIO`, `PeerFsm`, `new_admin_request`, and `new_read_index_request`.

The store facade re-exports `RaftBatchSystem`, `RaftPollerBuilder`, `RaftRouter`, `StoreMeta`, and `create_raft_batch_system`.

## Control Flow

There is no runtime control flow in this file. Its effect is compile-time namespace wiring: external modules import raftstore FSM capabilities through `crate::store::fsm::*` or selected nested modules instead of depending directly on every implementation file.

The facade matters operationally because it shapes construction flow elsewhere. Store startup uses `RaftPollerBuilder` and `create_raft_batch_system`; apply startup uses `ApplyPollerBuilder` and `create_apply_batch_system`; routers and task/result types cross the boundaries between store FSM, peer FSM, apply FSM, workers, and transport.

## State and Persistence Behavior

`mod.rs` owns no state and performs no persistence. It exposes state-bearing types from submodules, especially `StoreMeta`, `PeerFsm`, `Apply`, `GlobalStoreStat`, and `LocalStoreStat`. Persistence behavior remains in the re-exported implementation modules, particularly apply, peer storage, and store FSM code.

## Dependencies and Integration Points

The direct dependencies are its sibling modules. Broader integration points include `store/mod.rs`, `router.rs`, async I/O write routing, peer storage, workers, unsafe recovery, read queues, split checks, and tests that import the public raftstore FSM surface.

Because `life` is public as a module while `metrics` and `peer` are private with curated re-exports, this file also encodes intended API boundaries. Compatibility helpers in `life.rs` can be used by both raftstore variants, while peer internals remain mostly hidden.

## Risks and Edge Cases

Re-export changes are source-compatibility changes for the rest of the crate and potentially downstream crates if this module is part of a public crate API. Removing or renaming an item here can break imports far from the implementation file.

The facade can hide ownership boundaries: many high-level types are exported from one place even though they belong to different subsystems. That matches current raftstore architecture, but broadening this file further can increase coupling between apply, peer, and store FSMs.

Module visibility is intentional. Making `metrics` or `peer` public wholesale would expose implementation details; hiding `life` would break shared lifetime-management use cases.

## Test Signals

Compile tests are the primary signal: imports through `crate::store::fsm` should continue to resolve for store startup, apply batch systems, routers, unsafe recovery, and worker integrations.

Refactors to this file should run raftstore unit tests or at least targeted checks covering creation of raft and apply batch systems, peer/admin/read-index request constructors, and code paths importing `GlobalStoreStat` / `LocalStoreStat`.

A useful review signal is import churn: if many callers need to switch from facade imports to deep module paths, the facade may no longer be serving its stabilizing role.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/store/fsm/mod.rs -->
