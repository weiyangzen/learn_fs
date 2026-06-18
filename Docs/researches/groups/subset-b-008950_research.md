# Research Group: subset-b-008950

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/raftstore/test_life.rs -->
# sources/storage-engines/tikv/tests/integrations/raftstore/test_life.rs

## Purpose
This integration test file exercises raftstore peer lifecycle cleanup paths, especially garbage collection of removed peers, learner peers, and v2-compatible TiFlash-like learner behavior. It focuses on the correctness of tombstone/removed-record handling when peers are removed before creation, after learner creation, while isolated, or while their role changes through conf change.

## Important APIs, Types, and Functions
`ForwardFactory` and `ForwardFilter` implement `FilterFactory`/`Filter` to intercept `RaftMessage`s and optionally forward them into another cluster router. This is used to cross-wire v1 and v2 raftstore simulations in `test_gc_peer_tiflash_engine`.

The test functions are `test_gc_peer_tiflash_engine`, `test_gc_removed_peer`, and `test_gc_peer_with_conf_change`. They use `new_node_cluster`, `run_conf_change`, `new_peer`, `new_learner_peer`, `new_change_peer_request`, `new_admin_request`, `RegionPacketFilter`, `ExtraMessageType::MsgGcPeerRequest`, and `MsgGcPeerResponse`.

## Control Flow and Behavior
`test_gc_peer_tiflash_engine` boots v1 and v2 node clusters with matching learner state, forwards leader/learner traffic between the clusters, removes a learner from the v2 cluster, and waits for the v2 leader to clear removed records. `test_gc_removed_peer` synthesizes GC peer requests and verifies responses for a learner that never fully existed and for a learner that was added, tombstoned, and later collected. `test_gc_peer_with_conf_change` isolates an added learner, promotes/removes it through explicit admin conf-change requests, then sends a tombstone raft message addressed as a voter while the isolated local peer still sees itself as a learner.

## State and Persistence
The tests inspect raft local state, region local state, apply state, peer roles, `PeerState::Normal`/`Tombstone`, removed-record emptiness, and region epoch increments. They validate that lifecycle metadata persists enough to answer GC requests but is eventually cleaned after tombstone handling.

## Dependencies and Integration Points
The file depends on `kvproto` raft server metadata, raft message types, raftstore test transport filters, v1/v2 cluster simulators, PD conf-change helpers, and TiKV timing utilities. It integrates directly with raftstore message routing and peer cleanup paths rather than only using public KV operations.

## Risks
The tests are timing-sensitive because cleanup is tick-driven and message forwarding crosses simulated clusters. They also rely on exact peer IDs and region IDs. Regressions may appear as leaked removed records, peers stuck in learner/voter mismatch, or GC responses not emitted for tombstoned peers.

## Test Signals
Strong signals are successful `must_empty_region_removed_records`, expected `PeerState` transitions, equality of v1/v2 local raft/apply state before forwarding, and no errors from conf-change admin requests. Timeouts indicate lifecycle cleanup or forwarding regressions.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/raftstore/test_life.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/raftstore/test_merge.rs -->
# sources/storage-engines/tikv/tests/integrations/raftstore/test_merge.rs

## Purpose
This large integration test file is the main raftstore region-merge test suite. It validates normal split/merge behavior, merge prerequisites, stale peer cleanup, learner and target-peer edge cases, snapshot interaction, pessimistic lock transfer, approximate stats updates, max-ts synchronization, v1/v2 differences, and v2 removed/merged record GC.

## Important APIs, Types, and Functions
Core helpers come from `test_raftstore`: `configure_for_merge`, `ignore_merge_target_integrity`, `configure_for_snapshot`, `must_split`, `must_merge`, `try_merge`, `merge_region`, `must_transfer_leader`, `must_region_not_exist`, `wait_log_truncated`, `wait_tombstone`, and message filters such as `IsolationFilterFactory`, `RegionPacketFilter`, `DropMessageFilter`, and `CloneFilterFactory`.

The file also uses `RegionLocalState`, `PeerState`, `ExtraMessageType`, `ConfChangeType`, `RAFT_ENABLE_UNPERSISTED_APPLY_GAUGE`, `LocksStatus`, `SnapshotExt`, `PessimisticLock`, `LastChange`, `CF_LOCK`, `CF_WRITE`, and API-version test helpers. Tests are split between `test_raftstore` and `test_raftstore_v2` via `#[test_case]`.

## Control Flow and Behavior
The base merge tests write data, split a region, verify key range enforcement, merge adjacent regions, assert epoch version increases by prepare+commit merge, confirm source peers become tombstones, and ensure post-merge writes succeed. Prerequisite tests intentionally create log gaps, admin entries, oversized log gaps, incomplete learner catch-up, reset `matched` indexes, and five-node snapshot states to ensure merge is rejected until a safe catch-up point exists.

Many scenarios isolate a store during merge and then recover it: slow learners, slow split, distributed isolation, brain split, cascade merge, target peer absent during isolation, stale learners removed before merge, and target peers removed before applying commit-merge. These tests use explicit leader placement and packet filters to create asymmetric progress, then check that recovered stores either catch up via logs/snapshot or destroy obsolete peers.

Snapshot and restart paths are covered by demotion during snapshot, empty-entry catch-up across restart, long-isolated target cleanup, stale raft messages after merge, and snapshot-based recovery of isolated stores. Transactional state is covered by transferring in-memory pessimistic locks from source to target, preserving target locks, keeping lock status in `MergingRegion` on repeated merge proposals, and allowing new writes when the log gap makes merge fail.

The v2-specific tail verifies source removed records and merged records are retained while peers are unreachable, forwarded either by target peer or by store-level GC responses, and cleaned once GC peer ticks can complete.

## State and Persistence
The tests inspect region epochs, raft/apply progress, tombstone region local state, raft log truncation, merged records, removed records, pending in-memory locks, lock CF writes, approximate size/key reports, max timestamp in the concurrency manager, and unpersisted-apply gauge state. Several cases intentionally restart the cluster or trigger snapshots to verify that merge decisions and cleanup survive persisted state boundaries.

## Dependencies and Integration Points
This suite integrates PD operators, raftstore admin commands, local reader/snapshot state, RocksDB/raft engine metadata, pessimistic transaction memory state, API version formatting, region heartbeat stats, and v1/v2 raftstore implementations. It is a high-blast-radius regression suite for region lifecycle, raft log safety, and distributed metadata cleanup.

## Risks
The file has heavy timing and topology assumptions. Failures may be flaky if leader transfer, tick intervals, snapshot generation, or filter timing changes. The riskiest behaviors are merge proceeding with unsafe log gaps, obsolete peers serving data after merge, pessimistic locks being lost or duplicated, max-ts not advancing after merge, and v2 removed/merged records leaking indefinitely.

## Test Signals
Signals include successful `must_merge`/expected `try_merge` errors, `PeerState::Tombstone`, `must_region_not_exist`, exact key presence/absence on isolated stores, lock bytes in `CF_LOCK`, `LocksStatus::MergingRegion`, changed approximate size/key metrics, advanced `max_ts`, cleaned merged/removed records, and preserved availability after network filters are cleared.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/raftstore/test_merge.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/raftstore/test_multi.rs -->
# sources/storage-engines/tikv/tests/integrations/raftstore/test_multi.rs

## Purpose
This file tests multi-node raftstore behavior under normal writes, deletes, leader crashes, restarts, lost majorities, message delay/drop, uncommitted logs, stale proposals, consistency checks, batch writes, catch-up, and pessimistic-lock cleanup on leader loss.

## Important APIs, Types, and Functions
Shared helpers include `test_multi_base`, `test_multi_base_after_bootstrap`, `test_multi_leader_crash`, `test_multi_cluster_restart`, `test_multi_lost_majority`, `test_multi_random_restart`, `test_leader_change_with_uncommitted_log`, `test_read_leader_with_unapplied_log`, `get_with_timeout`, `test_remove_leader_with_uncommitted_log`, `test_consistency_check`, and `test_batch_write`.

It uses `new_node_cluster`, `new_server_cluster`, `must_put`, `must_get`, `must_delete`, `assert_quorum`, `RegionPacketFilter`, `DelayFilter`, `RandomLatencyFilter`, `DropPacketFilter`, `RaftStoreRouter`, callbacks, `MessageType`, `PessimisticLock`, and snapshot transaction extensions.

## Control Flow and Behavior
The baseline tests write/delete keys and assert quorum replication. Network tests wrap the same flow with fixed latency, random latency, or packet loss. Failure tests stop leaders or random nodes, verify new leader election and catch-up, restart whole clusters, and verify no leader exists after majority loss.

The uncommitted-log tests create followers with appended but unapplied entries, transfer leadership, and ensure the new leader does not serve stale reads or lose committed entries. Proposal cleanup tests make raft drop proposals during transfer-leader edge cases and require callbacks to be completed with errors. Batch write tests check atomicity when a batch crosses region ranges.

## State and Persistence
The tests assert data in each engine, raft leadership state, applied/unapplied log effects, callback cleanup, region-not-found behavior after removing the leader, and transaction extension memory state. Cluster restart tests verify data survives shutdown/start; catch-up tests verify a stopped peer receives missed logs after restart.

## Dependencies and Integration Points
The file integrates raftstore routing, simulated transports, PD membership updates, storage snapshots, local engine reads, raft callbacks, and pessimistic transaction lock memory. It covers both node and server cluster variants where applicable.

## Risks
Timing-sensitive leader election and packet filtering can make tests fragile. Key risks are stale reads from a new leader with unapplied logs, callbacks leaked after dropped proposals, writes accepted by a removed leader, batch partial application, and pessimistic locks surviving on a peer that lost leadership.

## Test Signals
Signals include exact key equality/nonexistence on individual engines, quorum predicates, leader identity changes, callback receipt within timeout, stale-command and region-not-found errors where expected, consistency-check survival, and empty pessimistic-lock memory after leadership returns.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/raftstore/test_multi.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/raftstore/test_prevote.rs -->
# sources/storage-engines/tikv/tests/integrations/raftstore/test_prevote.rs

## Purpose
This file validates raft prevote behavior after partitions, reboots, isolated followers, peer creation, and stale minority removal. It ensures prevote prevents disruptive term increases while still allowing legitimate elections and peer bootstrap traffic.

## Important APIs, Types, and Functions
`FailureType` models partition or reboot failures. `attach_prevote_notifiers` installs `MessageTypeNotifier`s for `MsgRequestPreVote` and `MsgRequestPreVoteResponse`. `test_prevote` is the shared scenario driver. Additional helpers are `test_pair_isolated`, `test_isolated_follower_leader_does_not_change`, and `test_create_peer_from_pre_vote`.

## Control Flow and Behavior
The shared prevote driver enables `prevote`, disables hibernate regions for observability, configures lease-read/election timing, transfers leadership, optionally attaches notifiers, applies a partition or reboot, checks whether prevote messages were observed, recovers the cluster, and verifies writes still succeed.

Other tests isolate a minority and let PD remove those peers, verify an isolated follower does not increase term or change the leader after reconnect, and verify a new peer can be created from prevote-triggered communication after isolation is cleared.

## State and Persistence
The file observes raft message traffic, leader identity, term stability through status requests, peer removal, and key persistence across failure/recovery. It does not directly inspect on-disk state, but it depends on raftstore persisting enough membership and term information to recover safely.

## Dependencies and Integration Points
It uses raft message filters, PD remove/add peer operations, `new_status_request`, leader commands, cluster partition/reboot controls, and `HandyRwLock` access to simulator internals.

## Risks
Prevote behavior is time-sensitive. Tests can miss messages if elections are slow or hibernation suppresses traffic, hence the explicit timing configuration. Regressions include unnecessary term bumps, leader churn after reconnect, isolated minority peers failing to remove themselves, or new peers not bootstrapping from prevote traffic.

## Test Signals
Signals are notifier channel delivery or timeout, stable leader and term after isolation, successful post-recovery writes, removed regions on isolated peers, and replicated data on newly added peers.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/raftstore/test_prevote.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/raftstore/test_region_change_observer.rs -->
# sources/storage-engines/tikv/tests/integrations/raftstore/test_region_change_observer.rs

## Purpose
This file tests the raftstore coprocessor `RegionChangeObserver` event stream for create, update, split, merge, destroy, removal, and re-addition of a region on a node.

## Important APIs, Types, and Functions
`TestObserver` implements `Coprocessor` and `RegionChangeObserver`, sending `(Region, RegionChangeEvent)` pairs through a synchronous channel from `on_region_changed`. `test_region_change_observer_impl` drives the scenario. It uses `BoxRegionChangeObserver`, `ObserverContext`, `RegionChangeReason`, `StateRole`, `post_create_coprocessor_host`, `find_peer`, and PD split/merge/conf-change helpers.

## Control Flow and Behavior
The test registers an observer only on node 1, starts a cluster, and verifies one initial `Create` event. It adds a peer and expects an `Update(ChangePeer)`, splits and accepts either order of `Update(Split)` and `Create`, merges and expects `Update(PrepareMerge)`, then `Update(CommitMerge)` plus `Destroy`. Finally it removes the node's peer, expecting update then destroy, re-adds the peer with a new peer ID, and expects create.

## State and Persistence
The observed region snapshots carry region IDs, key ranges, peer lists, and epochs. The test checks epochs change after update events and that destroy/create events reflect local membership changes.

## Dependencies and Integration Points
This is a coprocessor host integration test. It relies on raftstore event emission, PD operators, split/merge execution, local node observer registration, and `StateRole` delivery to the observer callback.

## Risks
Event ordering is intentionally flexible for split and commit-merge update/destroy pairs, but event cardinality is strict. Regressions include missing updates, stale epoch snapshots, duplicate observer registrations, and failing to destroy/recreate local observer state after peer removal.

## Test Signals
Signals are channel-received event variants, no extra channel messages after each phase, correct region IDs and range boundaries, expected peer counts, and the re-added peer ID `2333`.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/raftstore/test_region_change_observer.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/raftstore/test_region_heartbeat.rs -->
# sources/storage-engines/tikv/tests/integrations/raftstore/test_region_heartbeat.rs

## Purpose
This file tests raftstore region heartbeat reporting to PD: down peers, pending peers, heartbeat timestamps, heartbeat terms, and approximate-size behavior across leader changes.

## Important APIs, Types, and Functions
The `test_down_peers!` macro drives down-peer detection. `test_pending_peers` drives snapshot-blocked peer addition. Test functions include hibernate/non-hibernate down-peer variants, node/server pending-peer variants, `test_region_heartbeat_timestamp`, `test_region_heartbeat_term`, and `test_region_heartbeat_leader_change`.

It uses `ReadableDuration`, `ReadableSize`, `DropSnapshotFilter`, PD heartbeat inspection methods such as `get_down_peers`, `get_pending_peers`, `get_region_last_report_ts`, `get_region_last_report_term`, and approximate-size getters.

## Control Flow and Behavior
Down-peer tests stop nodes, wait for PD to report them down, restart nodes, transfer leadership, and verify stale down-peer seconds are reset instead of reused. Pending-peer tests block snapshots to a new peer, require PD to report the peer pending, then unblock and require pending state to disappear.

Timestamp and term tests transfer leaders and poll PD metadata until report timestamp or term advances. The leader-change stats test forces split-check/heartbeat behavior, grows approximate region size, transfers leadership, grows again, adds peers to trigger heartbeats, and confirms approximate size is not reset to stale lower values after transferring back.

## State and Persistence
The file observes PD-side heartbeat state rather than local disk directly: down-peer maps, pending-peer maps, last report timestamp, last report term, and approximate size. It also relies on raftstore local apply/snapshot progress to clear pending peers.

## Dependencies and Integration Points
The tests integrate cluster node lifecycle, hibernate-region configuration, PD client state, snapshot transport filters, split-check ticks, leader transfer, and heartbeat tick intervals.

## Risks
Heartbeat tests are timing-heavy. Regressions include hibernated regions delaying down-peer reports unexpectedly, stale down-peer seconds surviving leader transfer, pending peers not clearing after snapshot delivery, heartbeat term/timestamp not advancing, and approximate stats regressing after leadership changes.

## Test Signals
Signals are PD map contents, increasing timestamp/term values, eventual approximate size thresholds, exact pending peer identity, and successful data writes that force heartbeat state refresh.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/raftstore/test_region_heartbeat.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/raftstore/test_region_info_accessor.rs -->
# sources/storage-engines/tikv/tests/integrations/raftstore/test_region_info_accessor.rs

## Purpose
This file tests `RegionInfoAccessor` and raft engine region scanning. It verifies region range ordering, role reporting, split/merge updates, peer add/remove updates, leader transfer role changes, and `seek_region` behavior for raft engine backed stores.

## Important APIs, Types, and Functions
`dump` calls `RegionInfoAccessor::debug_dump` and checks the range index matches region metadata through `RangeKey::from_end_key`. `check_region_ranges` asserts ordered ranges. `test_region_info_accessor_impl` drives mutations. `test_node_cluster_region_info_accessor` registers an accessor through the coprocessor host. `test_raft_engine_seek_region` calls `raft_engine.seek_region`.

## Control Flow and Behavior
The accessor test writes keys, verifies the initial full-range region, splits at `k1`, `k4`, `k2`, and `k3`, checks ordered ranges, merges left-to-right and right-to-left, adds a peer, transfers leadership away from node 1, waits for `StateRole::Follower`, removes node 1's peer, and waits for the accessor to drop the removed region.

The raft-engine test splits at several keys, distributes leaders across stores, then seeks from key `b` on store 0's raft engine and expects regions `b`, `c`, and `d` with roles follower/leader/follower according to leader placement.

## State and Persistence
The test checks in-memory accessor state built from raftstore coprocessor updates and raft-engine persisted region metadata. It validates key ranges, peer lists, region epochs, and roles.

## Dependencies and Integration Points
It integrates `RegionInfoAccessor`, coprocessor host construction, PD split/merge/leader transfer, `tikv_kv::Engine`, and raft engine region iteration callbacks.

## Risks
Accessor updates are slightly asynchronous, so waits are needed after removal and leader transfer. Regressions include range index mismatch, stale role reporting, removed regions lingering, missing split/merge updates, and raft-engine `seek_region` returning wrong ordering or role data.

## Test Signals
Signals are exact ordered ranges, role transitions from leader to follower, expected peer membership, region count decrease after peer removal, and exact `seek_region` output from a start key.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/raftstore/test_region_info_accessor.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/raftstore/test_replica_read.rs -->
# sources/storage-engines/tikv/tests/integrations/raftstore/test_replica_read.rs

## Purpose
This file tests replica read and read-index correctness under unapplied logs, hibernation, stale peers, out-of-order read-index responses, lock checking retries, split isolation, snapshot peer replacement, malformed read-index messages, and pending peers.

## Important APIs, Types, and Functions
`CommitToFilter` records commit indexes per peer and clears commit fields in outgoing raft messages. Tests use `async_read_on_peer`, `async_read_index_on_peer`, `ReadIndexContext`, `block_on_timeout`, `RegionPacketFilter`, `DropSnapshotFilter`, `IsolationFilterFactory`, `configure_for_lease_read`, `configure_for_hibernate`, `Lock`, `LockType`, and concurrency-manager lock guards.

## Control Flow and Behavior
The not-applied test blocks followers from seeing commits, transfers leadership to a follower with an uncommitted first entry, verifies follower reads block instead of returning old values, releases append responses, and checks retry completion. Hibernation tests block read-index traffic, observe pre-vote wakeups, and verify hibernated leaders can be woken by extra messages after PD leader info loss.

Stale and out-of-order tests block appends or heartbeat responses to ensure reads time out or later resolve after peer removal. Lock retry tests insert an in-memory lock on one key and confirm delayed read-index responses report locked only for the affected key. Split isolation and snapshot replacement tests ensure local reader delegates are updated after split/snapshot and peer ID replacement. Malformed read-index sends an entry with `request: None` and verifies the read queue still serves a subsequent valid request. Pending-peer tests return `read_index_not_ready`.

## State and Persistence
The tests inspect applied values on each engine, read response errors, read-index lock fields, local reader delegate freshness, hibernation wakeup messages, and snapshot-created peer state. They rely on raft log commit/applied indexes and transaction lock memory.

## Dependencies and Integration Points
The file integrates raftstore local reads, raft read-index protocol, hibernate-region wakeup messages, PD membership updates, snapshots, concurrency manager locks, UUID-encoded read contexts, and v1/v2 node cluster variants.

## Risks
Risks include stale local reads, blocked reads never retrying, malformed read-index corrupting the queue, local reader caching an obsolete peer ID after snapshot replacement, hibernated leaders not waking, and pending peers serving reads before they are safe.

## Test Signals
Signals are timeout vs success boundaries, expected `v1`/`v2` values, `not_leader`, `read_index_not_ready`, locked read-index fields, captured wakeup extra messages, absence of mismatch-peer-id errors, and successful reads after filters clear.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/raftstore/test_replica_read.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/raftstore/test_replication_mode.rs -->
# sources/storage-engines/tikv/tests/integrations/raftstore/test_replication_mode.rs

## Purpose
This file tests DR Auto Sync and majority replication mode behavior: label-aware commit safety, sync-recover, async switching, conf-change checks, group-id assignment, hibernate interaction, migration between replication modes, rolling label loading, and commit-group deadlock avoidance.

## Important APIs, Types, and Functions
Helper functions `prepare_cluster`, `configure_for_snapshot`, `run_cluster`, and `prepare_labels` configure labeled server clusters. Tests use PD APIs `configure_dr_auto_sync`, `switch_replication_mode`, `region_replication_status`, `must_joint_confchange`, `must_leave_joint`, `transfer_leader`, and conf-change helpers with `ConfChangeType`.

The file uses `RegionReplicationState::{IntegrityOverLabel, SimpleMajority}`, `DrAutoSyncState::{Async, SyncRecover}`, isolation filters, snapshot-forcing raft log GC settings, and async command callbacks.

## Control Flow and Behavior
Tests isolate stores in specific zones to verify writes commit only when label integrity can be satisfied. Switching tests move from sync to async to sync-recover and assert write blocking/unblocking and replication status IDs. Snapshot tests force log truncation, switch modes, restore an isolated store by snapshot, and verify the status returns to label integrity after apply.

Conf-change tests validate promotion decisions under DR label constraints. Migration tests configure DR mode at runtime, switch to majority and back, split regions created under majority, and verify both old and new regions report updated DR status. Rolling-start tests add labels before each node start to confirm labels are loaded into store metadata. The commit-group migration test uses failpoints around snapshot/apply peer creation to ensure assigning commit groups while regions migrate does not deadlock.

## State and Persistence
The tests observe PD replication status state IDs, replication state values, committed key visibility, snapshot catch-up, group IDs implied by commit behavior, label metadata loaded during rolling starts, and liveness of peer creation under failpoint stalls.

## Dependencies and Integration Points
This suite integrates PD replication mode configuration, store labels, raft conf change including joint consensus, snapshot/log GC, async write callbacks, hibernation, and raftstore-v2 commit group assignment.

## Risks
Regressions include writes committing without required label durability, writes blocking after async mode should unblock, sync-recover incorrectly blocking, label metadata missing after rolling starts, unsafe peer promotion, stale replication status after split/migration, and deadlocks while assigning commit groups during snapshot application.

## Test Signals
Signals are callback timeout/success, exact replication state and state_id assertions, key presence on specific engines, successful leave-joint operations, successful leader transfers after group-id updates, and both migrated regions reporting `IntegrityOverLabel`.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/raftstore/test_replication_mode.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/raftstore/test_scale_pool.rs -->
# sources/storage-engines/tikv/tests/integrations/raftstore/test_scale_pool.rs

## Purpose
This file tests runtime resizing of raftstore execution resources: store/apply batch pools, raftstore-v2 pools, store IO pool, RocksDB high-priority background threads, and snapshot generator pool size.

## Important APIs, Types, and Functions
Tests use config controllers from simulators via `get_cfg_controller`, update keys such as `raftstore.store-pool-size`, `raftstore.apply-pool-size`, `raftstore.store-io-pool-size`, and `raftstore.snap-generator-pool-size`, and inspect current configs. Thread helpers `get_poller_thread_ids`, `get_raft_poller_thread_ids`, and `get_async_writers_tids` read OS thread names using `tikv_util::sys::thread`.

Failpoints include `poll`, `before_handle_tasks`, `on_flush_completed`, and `before_region_gen_snap`. The file also uses `ConfigurableDb::set_high_priority_background_threads`, engine `flush_cf`, and snapshot filters.

## Control Flow and Behavior
Pool-increase tests pause all existing pollers, show writes time out, increase pool size, and verify writes succeed. Decrease tests record thread IDs before and after shrinking and verify expected threads are removed while remaining threads are from the original set. v2 variants separately test store and apply pool resizing.

Store IO tests verify increasing async writers creates more writer threads, decreasing does not release existing writer threads, and switching between sync/async IO modes is rejected. High-priority RocksDB thread tests pause flush completion, reduce flush threads so flush blocks, then increase threads and unblock. Snapshot generator tests resize generation pools while snapshot generation is paused and verify only expected snapshots can proceed.

## State and Persistence
The file observes runtime config state, OS thread counts, key writes on engines, RocksDB flush progress, and snapshot delivery to lagging stores. It is mostly runtime behavior, but data writes verify resized pools still process persisted KV operations.

## Dependencies and Integration Points
It integrates raftstore batch systems, raftstore-v2 thread naming, YATP/snapshot generation, RocksDB thread configuration, failpoints, simulator config controllers, and engine reads.

## Risks
Risks include runtime config updates not taking effect, shrinking killing the wrong poller threads, writes remaining blocked after scaling up, invalid IO mode transitions being accepted, snapshot generation pool allowing unsafe zero size, and background flush thread changes not unblocking stalled flushes.

## Test Signals
Signals are write timeout vs success, current config values, thread ID count differences, preserved thread IDs after shrink, error results for invalid resize, blocked/unblocked flush channels, and expected key visibility or absence on lagging engines.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/raftstore/test_scale_pool.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/raftstore/test_single.rs -->
# sources/storage-engines/tikv/tests/integrations/raftstore/test_single.rs

## Purpose
This file tests basic single-region/single-node raftstore commands across node/server and v1/v2 cluster variants: put, delete, delete range, wrong store ID rejection, large entry rejection, and initial no-op apply.

## Important APIs, Types, and Functions
Tests use `new_put_cmd`, `new_request`, `batch_put`, `must_delete`, `test_delete_range`, `call_command_on_node`, `ReadableSize`, `RAFT_INIT_LOG_INDEX`, random data selection, and `#[test_case]` to run against multiple cluster constructors.

## Control Flow and Behavior
`test_put` writes 999 keys in batches, samples random keys, overwrites all values, and samples again. `test_delete` writes batches and deletes sampled keys. Delete-range tests toggle `use_delete_range` and exercise default/write CF cleanup. `test_wrong_store_id` mutates the request header peer store ID and expects a non-empty error. `test_put_large_entry` sets `raft_entry_max_size` and expects `raft_entry_too_large`. `test_node_apply_no_op` waits until applied index advances beyond `RAFT_INIT_LOG_INDEX`.

## State and Persistence
The tests validate values read through the cluster API and delete-range effects in underlying CFs. The no-op test directly checks apply state progress.

## Dependencies and Integration Points
The file is a low-level integration smoke suite for raftstore request building, command validation, storage CF deletion, size checks, and apply-worker progress. It covers both legacy and v2 cluster constructors where supported.

## Risks
Regressions include batched puts not applying atomically, overwrites not replacing values, delete range leaving CF data behind, request peer validation accepting wrong store IDs, oversize entries entering raft, or a bootstrapped node failing to apply the no-op log.

## Test Signals
Signals are sampled value equality, deleted keys returning `None`, non-empty command error for wrong store ID, `has_raft_entry_too_large`, and applied index exceeding `RAFT_INIT_LOG_INDEX` within the timeout.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/raftstore/test_single.rs -->
