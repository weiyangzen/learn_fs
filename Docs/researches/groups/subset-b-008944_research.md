# subset-b-008944 research

This grouped report covers TiKV benchmark modules and failpoint cases. Each section preserves the original source path and is intended to be split into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/misc/serialization/bench_serialization.rs -->
# sources/storage-engines/tikv/tests/benches/misc/serialization/bench_serialization.rs

Purpose: benchmarks protobuf serialization overhead for Raft log entries containing one or two TiKV `Put` requests. It focuses on the hot path of wrapping `kvproto::raft_cmdpb::RaftCmdRequest` inside `raft::eraftpb::Entry` and decoding it back.

Important APIs and functions: `gen_rand_str` creates random byte keys/values; `generate_requests` converts a borrowed byte-slice map into `Request` protobufs with `CmdType::Put` and CF `"tikv"`; `encode` serializes requests into `RaftCmdRequest`, then stores the bytes as `Entry.data`; `decode` merges bytes into `Entry` and then into `RaftCmdRequest`. Bench functions are `bench_encode_one`, `bench_decode_one`, `bench_encode_two`, and `bench_decode_two`.

Control flow: each bench pre-generates random input, builds a small `HashMap<&[u8], &[u8]>`, and measures only repeated encode or decode work inside `Bencher::iter`. Decode cases precompute encoded data once.

State and persistence: no durable state is written. The simulated persisted object is a Raft `Entry` byte vector, exercising allocation and protobuf message layout.

Dependencies and integration: depends on `kvproto`, `protobuf::Message`, `raft`, `rand`, `collections::HashMap`, and Rust unstable `test` benches. It integrates with the misc serialization bench module.

Risks and test signals: map iteration order is non-deterministic, so this measures average serialization cost rather than stable wire ordering. `unwrap()` is acceptable in benchmarks but hides malformed data behavior. Signal is performance regression in request serialization size/count scenarios.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/misc/serialization/bench_serialization.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/misc/serialization/mod.rs -->
# sources/storage-engines/tikv/tests/benches/misc/serialization/mod.rs

Purpose: module shim for misc serialization benchmarks. It exposes `bench_serialization` to the bench harness.

Important APIs and functions: only `mod bench_serialization;` is declared.

Control flow: compile-time module inclusion only; benchmark discovery happens through `#[bench]` functions inside the child module.

State and persistence: none.

Dependencies and integration: integrates `bench_serialization.rs` under the misc benchmark tree.

Risks and test signals: risk is limited to accidental module removal causing all serialization benches to disappear from the suite.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/misc/serialization/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/misc/storage/incremental_get.rs -->
# sources/storage-engines/tikv/tests/benches/misc/storage/incremental_get.rs

Purpose: compares regular MVCC point reads through `SnapshotStore::get` with `SnapshotStore::incremental_get_entry` for table lookup patterns.

Important APIs and functions: `table_lookup_gen_data` builds a `SyncTestStorage`, prewrites and commits 30,000 row keys, compacts `write`, `default`, and `lock` CFs, opens a `SnapshotStore<Arc<RocksSnapshot>>`, and returns every 30th key. `bench_table_lookup_mvcc_get` loops over keys with a fresh `Statistics`; `bench_table_lookup_mvcc_incremental_get` loops over the same key set using incremental get.

Control flow: data setup is outside `Bencher::iter`; benchmark iterations scan a stable ordered key list. The incremental benchmark keeps a mutable `SnapshotStore` across iterations to exercise cursor reuse.

State and persistence: test storage writes MVCC data into RocksDB CFs, then compacts them to reduce setup artifacts. The snapshot is read-only during benchmarking.

Dependencies and integration: uses `test_storage::SyncTestStorageBuilder`, `tidb_query_datatype::codec::table`, `tikv::storage::{Engine, SnapshotStore, Store}`, and `txn_types::{Key, Mutation}`.

Risks and test signals: snapshot timestamp `10` and committed data at ts `2` model visible historical reads. Cursor state can bias results if key order changes. Signal is relative performance of incremental lookup optimization on table rows.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/misc/storage/incremental_get.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/misc/storage/key.rs -->
# sources/storage-engines/tikv/tests/benches/misc/storage/key.rs

Purpose: benchmarks `txn_types::Key::gen_hash` for common TiDB row and index key encodings.

Important APIs and functions: `gen_rand_str` creates random bytes; `bench_row_key_gen_hash` builds a row key with `table::encode_row_key`; `bench_index_key_gen_hash` encodes a 64-byte datum and builds an index seek key with `table::encode_index_seek_key`.

Control flow: each benchmark creates one key once and repeatedly calls `gen_hash` under `test::black_box`.

State and persistence: no storage state.

Dependencies and integration: uses TiDB datatype codec modules, `EvalContext`, `Datum`, and `txn_types::Key`. It belongs to the misc storage benchmark module.

Risks and test signals: random input means exact hash cost may vary slightly by run, but key shape is stable. Signal is CPU cost regression for hash generation used by storage and lock-management paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/misc/storage/key.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/misc/storage/mod.rs -->
# sources/storage-engines/tikv/tests/benches/misc/storage/mod.rs

Purpose: module aggregator for misc storage benchmarks.

Important APIs and functions: includes `incremental_get`, `key`, `mvcc_reader`, and `scan`.

Control flow: compile-time module wiring only.

State and persistence: none in this file; child modules create RocksDB-backed test storage as needed.

Dependencies and integration: connects storage microbenchmarks to the misc bench harness.

Risks and test signals: accidental omission disables the corresponding benchmark module.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/misc/storage/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/misc/storage/mvcc_reader.rs -->
# sources/storage-engines/tikv/tests/benches/misc/storage/mvcc_reader.rs

Purpose: measures `SnapshotReader::get_txn_commit_record` with short and long version chains.

Important APIs and functions: `prepare_mvcc_data` repeatedly prewrites and commits the same key for timestamps `1..=n`, then compacts RocksDB CFs. `bench_get_txn_commit_record` constructs a `SnapshotReader` for each iteration and calls `get_txn_commit_record(&key).unwrap().unwrap_single_record()`. Public bench entries cover `n=100` and `n=5`.

Control flow: setup writes MVCC history once; each iteration creates a snapshot reader over a fresh engine snapshot and resolves the transaction commit record.

State and persistence: durable test RocksDB state contains many versions for one logical key across write/default/lock CFs.

Dependencies and integration: uses API v1 test storage, `RocksEngine`, `SnapshotReader`, table row key encoding, and `txn_types::Mutation`.

Risks and test signals: repeatedly opening snapshots inside the benchmark is part of the measured cost. Signal is MVCC commit-record lookup behavior as version depth grows.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/misc/storage/mvcc_reader.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/misc/storage/scan.rs -->
# sources/storage-engines/tikv/tests/benches/misc/storage/scan.rs

Purpose: ignored benchmark for scanning through MVCC tombstones, documenting and measuring the cost of deleted-but-retained MVCC keys.

Important APIs and functions: `bench_tombstone_scan` uses `KvGenerator` to create 100,000 keys, then for each key writes a put and a delete at increasing timestamps. The benchmark repeatedly scans from generated keys and expects no visible rows.

Control flow: large setup alternates prewrite/commit for put and delete mutations. Iteration performs `store.scan(..., limit=1, key_only=false, version=next_ts)` and asserts empty results.

State and persistence: MVCC tombstones remain in test storage even though logical rows are deleted.

Dependencies and integration: uses `SyncTestStorageBuilder`, `test_util::KvGenerator`, `Context`, `Mutation`, and `txn_types::Key`.

Risks and test signals: marked `#[ignore]`, so it is opt-in and expensive. Signal is scan degradation caused by tombstone density.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/misc/storage/scan.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/misc/util/mod.rs -->
# sources/storage-engines/tikv/tests/benches/misc/util/mod.rs

Purpose: module shim for misc utility benchmarks.

Important APIs and functions: declares `mod slice_compare;`.

Control flow: compile-time inclusion only.

State and persistence: none.

Dependencies and integration: wires slice comparison microbenchmarks into the misc bench tree.

Risks and test signals: module removal silently drops utility benches.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/misc/util/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/misc/util/slice_compare.rs -->
# sources/storage-engines/tikv/tests/benches/misc/util/slice_compare.rs

Purpose: measures Rust byte-slice comparison performance for less-than, greater-than, and equality cases at common key lengths.

Important APIs and functions: `gen_rand_str` creates random byte vectors; helper benches compare two slices using `<` or `>`; concrete benches cover 32, 64, and 128 bytes plus equality at 128 bytes.

Control flow: random slices are generated once per benchmark and compared repeatedly in `Bencher::iter`.

State and persistence: none.

Dependencies and integration: uses `rand`, `test::Bencher`, and Rust slice ordering operators. Relevant to key comparator costs.

Risks and test signals: random pairs may differ early or late, so individual runs can vary. Equality bench intentionally exercises full-length comparison. Signal is low-level comparator regression.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/misc/util/slice_compare.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/misc/writebatch/bench_writebatch.rs -->
# sources/storage-engines/tikv/tests/benches/misc/writebatch/bench_writebatch.rs

Purpose: benchmarks RocksDB write batch throughput by batch size and allocation strategy.

Important APIs and functions: `writebatch` creates a new engine write batch for each round, inserts formatted keys, and writes it. `bench_writebatch_impl` opens a temp RocksDB with default CF and selected write options, then measures a fixed total key count across batch sizes 1 through 1024. `fill_writebatch` appends repeated puts until `data_size >= target_size`; capacity benches compare `write_batch()` versus `write_batch_with_cap(4096)`.

Control flow: setup constructs a temp engine; each iteration writes batches to the same database path. Batch-size benches set `round = 8192 / batch_keys`.

State and persistence: benchmark writes persistent RocksDB data in a `tempfile` directory. Data accumulates across iterations until the tempdir is dropped.

Dependencies and integration: uses `engine_rocks`, `engine_traits::{Mutable, WriteBatch, WriteBatchExt}`, `CF_DEFAULT`, and Rust benches.

Risks and test signals: accumulated keys may affect later iterations through RocksDB state. Signal covers write batch construction, serialization, and write path behavior under multi-batch write.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/misc/writebatch/bench_writebatch.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/misc/writebatch/mod.rs -->
# sources/storage-engines/tikv/tests/benches/misc/writebatch/mod.rs

Purpose: module shim for write batch benchmarks.

Important APIs and functions: declares `mod bench_writebatch;`.

Control flow: compile-time module inclusion only.

State and persistence: none in this file; child benchmarks create temp RocksDB instances.

Dependencies and integration: links writebatch benchmarks to the misc bench harness.

Risks and test signals: removing this file’s module declaration drops the write batch benchmark family.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/misc/writebatch/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/raftstore/mod.rs -->
# sources/storage-engines/tikv/tests/benches/raftstore/mod.rs

Purpose: Criterion benchmark binary for raftstore set/get/delete operations over node and server cluster simulators.

Important APIs and functions: `enc_write_kvs` directly writes data keys into RocksDB. `prepare_cluster` runs the cluster, seeds initial data into all KV engines, and resolves the leader. `bench_set`, `bench_get`, and `bench_delete` build clusters and measure `must_put`, `get`, and `must_delete`. `bench_raft_cluster` sweeps node counts `1,3,5` and value sizes `8,128,1024,4096`. `ClusterFactory` abstracts `NodeClusterFactory` and `ServerClusterFactory`. `main` checks file descriptors and runs Criterion sample size 10.

Control flow: each benchmark input builds a fresh cluster; get/delete cases preload 100,000 KVs and then mix existing and generated keys.

State and persistence: clusters write to test RocksDB engines. Direct preload bypasses raft for setup; measured operations go through raftstore APIs.

Dependencies and integration: uses Criterion, `test_raftstore`, `test_util::KvGenerator`, Rocks engine traits, and TiKV config fd checking.

Risks and test signals: setup cost is outside timing but cluster lifecycle may still be heavy. Signals raftstore API latency under simulator variants and replica counts.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/benches/raftstore/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/failpoints/cases/mod.rs -->
# sources/storage-engines/tikv/tests/failpoints/cases/mod.rs

Purpose: central module manifest for failpoint integration tests.

Important APIs and functions: declares all failpoint case modules, including the subset files researched here and many additional cases such as local read, merge, rawkv, storage, titan, transaction, ttl, unsafe recovery, and witness.

Control flow: compile-time test module registration only. The Rust test harness discovers `#[test]` and `#[test_case]` functions in children.

State and persistence: none directly.

Dependencies and integration: this file is the integration point between `tests/failpoints` and individual failure-injection scenarios.

Risks and test signals: missing a `mod` declaration disables an entire failpoint file. Additions here can increase failpoint suite runtime and global failpoint interactions.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/failpoints/cases/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/failpoints/cases/test_async_fetch.rs -->
# sources/storage-engines/tikv/tests/failpoints/cases/test_async_fetch.rs

Purpose: tests raft log async fetch, entry cache retention, and log compaction coordination when peers lag, restart, change leadership, or are removed.

Important APIs and functions: tests include `test_node_async_fetch`, `test_persist_delay_block_log_compaction`, `test_node_async_fetch_remove_peer`, `test_node_async_fetch_leader_change`, and `test_node_compact_entry_cache`. They use `new_node_cluster`, PD peer operations, `RaftApplyState` from `CF_RAFT`, `check_compacted`, and failpoints such as `on_async_fetch_return`, `worker_async_fetch_raft_log`, `worker_gc_raft_log`, `apply_pending_snapshot`, and `before_region_gen_snap`.

Control flow: each test configures raft log GC thresholds and entry cache lifetime, creates lagging peers by stopping nodes or isolating traffic, writes enough entries to trigger async fetch or compaction, pauses internal workers, then resumes and validates catch-up.

State and persistence: reads persisted raft apply truncated state from the raft CF and validates KV replication after restarts/removals. Compaction is expected to wait when persist is delayed.

Dependencies and integration: integrates raftstore cluster simulation, PD client peer management, engine traits, and fail-rs.

Risks and test signals: timing sleeps and failpoint ordering are sensitive. Signals include successful lagging-peer recovery, no premature log GC, and retained cache for learners.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/failpoints/cases/test_async_fetch.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/failpoints/cases/test_async_io.rs -->
# sources/storage-engines/tikv/tests/failpoints/cases/test_async_io.rs

Purpose: verifies raftstore async IO semantics when leader or follower persistence is paused, snapshots are persisting, peers are removed, and unstable entry buffers shrink.

Important APIs and functions: test cases cover commit without leader persist, apply without leader persist, conf change while leader persist is skipped, delayed destroy after self-removal, snapshot-persist destroy/ready exclusion, and unstable entry shrink. Uses `#[test_case]` over v1/v2 clusters for several cases.

Control flow: tests pause or return from `raft_before_save_on_store_*`, `raft_before_persist_on_store_*`, or `raft_before_save_kv_on_store_*`, issue async puts/conf changes, and assert which stores can observe values before persistence resumes. Snapshot tests isolate a peer, wait for `MsgSnapshot`, then assert tombstone/ready processing is blocked until snapshot persistence completes.

State and persistence: explicitly distinguishes committed/applied data from persisted raft logs and persisted snapshot KV data. Uses engine reads and `unstable_entries_stat`.

Dependencies and integration: uses `test_raftstore`, packet filters, `MessageTypeNotifier`, PD client, and `tikv_util::HandyRwLock`.

Risks and test signals: strong timing dependence around snapshot delivery. Signals protect against data loss, premature destroy, and unbounded unstable entry buffers.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/failpoints/cases/test_async_io.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/failpoints/cases/test_auto_compaction.rs -->
# sources/storage-engines/tikv/tests/failpoints/cases/test_auto_compaction.rs

Purpose: validates GC worker auto-compaction candidate detection and MVCC-read-aware prioritization.

Important APIs and functions: `test_gc_worker_auto_compaction_with_failpoints` creates multiple split regions with different redundant MVCC/tombstone patterns and observes failpoint callbacks for candidate ranges. `test_mvcc_aware_compaction_prioritization` records reads in `MVCC_READ_TRACKER` and checks `FIRST_COMPACTION_CANDIDATE_REGION`.

Control flow: configures low thresholds, disables RocksDB auto compactions, writes version/delete patterns via KV prewrite/commit, flushes `CF_WRITE`, waits for auto compaction thread failpoints, and asserts expected regions are selected.

State and persistence: persists MVCC histories in write CF and uses PD/cluster GC safe points. Candidate selection is based on flushed table properties and tracker state.

Dependencies and integration: uses `test_raftstore`, `kvproto::kvrpcpb`, `engine_traits::MiscExt`, `ReadableDuration`, GC auto-compaction internals, and failpoint callbacks.

Risks and test signals: one branch tolerates environments where the thread cannot start. The second test contains an apparent duplicate assignment to `mvcc_scan_threshold`, with the latter disabling age factor. Signals candidate scoring and read-aware priority regressions.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/failpoints/cases/test_auto_compaction.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/failpoints/cases/test_backup.rs -->
# sources/storage-engines/tikv/tests/failpoints/cases/test_backup.rs

Purpose: tests backup behavior when an async prewrite holds a memory lock.

Important APIs and functions: `backup_blocked_by_memory_lock` uses `TestSuite`, `kv_prewrite`, `suite.backup`, and checks `brpb::Error_oneof_detail::KvError`.

Control flow: pauses `raftkv_async_write_finish`, starts a prewrite with async commit in another thread, sleeps to let the in-memory lock exist, runs backup over `a..z` at backup ts 21, and expects a locked key error. It then removes the failpoint, joins the thread, and stops the suite.

State and persistence: the important state is an in-memory lock not yet fully written through the async write path. Backup observes this lock and refuses to silently skip it.

Dependencies and integration: uses backup test harness, futures stream collection, temp storage path, and KV RPC protobufs.

Risks and test signals: uses fixed sleep to wait for the lock. Signal is correctness of backup conflict detection against transient memory locks.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/failpoints/cases/test_backup.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/failpoints/cases/test_bootstrap.rs -->
# sources/storage-engines/tikv/tests/failpoints/cases/test_bootstrap.rs

Purpose: verifies node bootstrap recovery after injected failures at different bootstrap phases.

Important APIs and functions: helper `test_bootstrap_half_way_failure` drives `NodeCluster` startup with failpoints `node_after_bootstrap_store`, `node_after_prepare_bootstrap_cluster`, and `node_after_bootstrap_cluster`. It inspects `STORE_IDENT_KEY`, calls `set_bootstrapped`, restarts, checks `PREPARE_BOOTSTRAP_KEY`, and validates replication.

Control flow: first `cluster.start()` must fail after partial persistent state. The test then marks the discovered store bootstrapped in PD, removes the failpoint, starts successfully, and writes `k1`.

State and persistence: persistent store identity and prepare-bootstrap keys are the core state. The test asserts stale prepare-bootstrap metadata is cleared.

Dependencies and integration: uses `TestPdClient`, raftstore cluster APIs, engine `Peekable`, and protobuf metapb/raft_serverpb messages.

Risks and test signals: directly manipulates PD bootstrap state, so helper behavior must match production bootstrap contracts. Signal is idempotent restart after partial bootstrap.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/failpoints/cases/test_bootstrap.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/failpoints/cases/test_cmd_epoch_checker.rs -->
# sources/storage-engines/tikv/tests/failpoints/cases/test_cmd_epoch_checker.rs

Purpose: tests raft command proposal epoch checking and callback behavior across split, merge, rollback merge, leader transfer, conf change, partition, and delayed propose windows.

Important APIs and functions: `CbReceivers` asserts proposed/committed/applied callback states. `make_cb` builds callbacks with proposed and committed hooks. `make_write_req` creates a region-epoch write request for a key. Tests cover rejecting proposals during split/merge/rollback/leader-transfer, accepting during conf change, not invoking committed callback on failure to commit, and proposals delayed before transfer/split/merge.

Control flow: tests pause apply stages with failpoints such as `apply_before_split`, `apply_before_prepare_merge`, `apply_before_commit_merge`, `apply_before_rollback_merge`, and `force_delay_propose_batch_raft_command`; submit async commands directly to node routers; then resume operations and assert callback ordering and errors.

State and persistence: region epoch, merge state, split state, and raft commit/apply progression are central. KV reads verify successful applied commands.

Dependencies and integration: uses raftstore message APIs, `RocksSnapshot`, `block_on_timeout`, and `test_raftstore`.

Risks and test signals: callback timing can be delicate; the test intentionally covers alternate proposed-callback code paths. Signals prevent stale epoch proposals and incorrect callback invocation.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/failpoints/cases/test_cmd_epoch_checker.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/failpoints/cases/test_conf_change.rs -->
# sources/storage-engines/tikv/tests/failpoints/cases/test_conf_change.rs

Purpose: exercises edge cases around peer removal, local reader cleanup, writes racing destruction, stale peer cache, redundant conf changes via snapshots, and apply FSM pending-state recovery.

Important APIs and functions: tests include `test_destroy_local_reader`, `test_write_after_destroy`, `test_tick_after_destroy`, `test_stale_peer_cache`, `test_redundant_conf_change_by_snapshot`, and `test_handle_conf_change_when_apply_fsm_resume_pending_state`.

Control flow: cluster setup adds/removes peers through PD, transfers leaders, installs packet filters, pauses apply or destroy failpoints, and checks engine visibility/region cleanup after resuming.

State and persistence: key state includes region local data removal, local reader delegates, peer cache contents, on-disk versus in-memory conf state after snapshot restore, and pending apply state during conf change.

Dependencies and integration: uses node/server clusters including v2 variants, PD client, raft message filters, conf-change admin requests, and lease-read helpers.

Risks and test signals: several tests rely on sleeps around async destroy/apply. Signals guard against stale local reads, writes landing on destroyed peers, and inconsistent membership state.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/failpoints/cases/test_conf_change.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/failpoints/cases/test_coprocessor.rs -->
# sources/storage-engines/tikv/tests/failpoints/cases/test_coprocessor.rs

Purpose: tests coprocessor error handling, deadline handling, paging scan ranges, follower read-index lock checking, bucket version propagation, and default-CF-not-found reporting.

Important APIs and functions: early tests inject `deadline_check_fail`, `coprocessor_parse_request`, `future_pool_spawn_full`, `rockskv_async_snapshot`, `kv_cursor_seek`, and `region_snapshot_seek`. Paging tests build `DagSelect` requests and parse `SelectResponse`. Later tests use grpc `TikvClient`, follower replica read context, in-memory locks, `Bucket`, and failpoints around stale-read safety and default CF loading.

Control flow: most tests initialize product-table data, build a coprocessor request, inject a failure or small batch size, call `handle_request`, and assert region/other errors or page ranges.

State and persistence: MVCC table data is written into test engines or raft engines; memory locks in concurrency manager must be observed by follower read-index checking. Bucket metadata is refreshed and then validated through response versions.

Dependencies and integration: integrates test coprocessor/table helpers, storage test engines, grpc clients, PD TSO, raftstore clusters, and TiDB datatype encoding.

Risks and test signals: paging range assertions are key-boundary sensitive. Signals cover user-visible coprocessor errors and resumable scan correctness.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/failpoints/cases/test_coprocessor.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/failpoints/cases/test_debugger.rs -->
# sources/storage-engines/tikv/tests/failpoints/cases/test_debugger.rs

Purpose: validates debug MVCC scanning across tablet-backed region metadata where region ranges and RocksDB key ranges intentionally differ.

Important APIs and functions: `prepare_data_on_disk` builds a TiKV config, tablet registry, raft log engine, six region states, and tablet RocksDB data using `must_prewrite_put`. Region 4 is tombstoned and region 6 has mismatched start/end metadata. `extract_key` maps stored `zkNN` keys to logical `kNN`. `test_scan_mvcc` uses `new_debugger(...).scan_mvcc`.

Control flow: create on-disk raft/tablet metadata, enable `unlimited_range_compaction_filter`, instantiate debugger, reject invalid scans, and verify full and partial scans skip tombstoned or nonmatching regions.

State and persistence: persists raft region local states and per-region tablets on disk. The debugger reads existing files, not a running cluster.

Dependencies and integration: uses `RaftLogEngine`, `TabletRegistry`, `KvEngineFactoryBuilder`, `Debugger`, and storage transaction test helpers.

Risks and test signals: synthetic key mapping is narrow but deliberate. Signal is debug tooling resilience to tombstones, gaps, limits, and bad ranges.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/failpoints/cases/test_debugger.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/failpoints/cases/test_disk_full.rs -->
# sources/storage-engines/tikv/tests/failpoints/cases/test_disk_full.rs

Purpose: comprehensive disk usage behavior tests for raft proposals, transactions, follower reads, hibernation, merges, down peers, and majority-full decisions.

Important APIs and functions: helpers `assert_disk_full`, `disk_full_stores`, `get_fp`, `assert_region_leader_changed!`, and `ensure_disk_usage_is_reported!`. Tests cover leader/follower behavior, txn operations with `DiskFullOpt`, majority full, hibernated followers, merge under majority full, mixed almost/already full stores, down nodes, and follower read-index rejection.

Control flow: failpoints `disk_almost_full_peer_N` and `disk_already_full_peer_N` simulate store status; tests force reports through read-index, issue raft commands or KV RPCs, and assert accepted/rejected paths and leader movement.

State and persistence: raft local state indexes verify whether entries were appended; engines verify value replication or absence. PD down-peer and disk status reports affect scheduling decisions.

Dependencies and integration: uses node/server clusters with v2 variants, `kvproto::disk_usage`, raft command options, transaction client helpers, and raft packet filters.

Risks and test signals: many scenarios depend on disk usage report propagation and sleeps. Signals are exact store IDs in errors, safe admission of special operations, and blocked unsafe writes.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/failpoints/cases/test_disk_full.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/failpoints/cases/test_disk_snap_br.rs -->
# sources/storage-engines/tikv/tests/failpoints/cases/test_disk_snap_br.rs

Purpose: ignored regression test for backup disk snapshot behavior during region merge scheduling.

Important APIs and functions: `test_merge` uses `test_backup::disk_snap::Suite`, `assert_success`, `prepare_backup`, `wait_apply`, and failpoint `on_schedule_merge`.

Control flow: split a region, pause merge scheduling, issue merge, prepare backup, resume scheduling, manually advance source epoch to simulate prepare merge application, wait for backup apply awareness, then assert eventual merge.

State and persistence: region epochs and backup rejector state are central. It models a merge command interaction with backup prepare state.

Dependencies and integration: depends on backup disk-snapshot test harness and raftstore merge operations.

Risks and test signals: marked ignored with comment explaining current behavior intentionally does not reject `CommitMerge`, so this is documentation/regression scaffolding rather than active CI signal.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/failpoints/cases/test_disk_snap_br.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/failpoints/cases/test_early_apply.rs -->
# sources/storage-engines/tikv/tests/failpoints/cases/test_early_apply.rs

Purpose: validates early-apply restrictions and correctness around unpersisted logs, merge catch-up, and leader demotion with overlapping entry cache contents.

Important APIs and functions: tests include singleton no-early-apply, multi-region early apply, yield followed by many entries, and leader demote by append. Uses failpoints `raft_before_save_on_store_1`, `before_handle_normal_3`, `after_handle_catch_up_logs_for_merge_1003`, and `pause_on_peer_collect_message`.

Control flow: tests pause raft persistence or apply handling, issue writes across singleton/multi-peer regions, merge regions with large entries, restart clusters, and inject modified `MsgAppend` messages directly through `PeerMsg`.

State and persistence: distinguishes committed, applied, and persisted logs. It validates KV visibility before/after persist and restart, and entry cache consistency under demotion.

Dependencies and integration: uses node clusters plus v2 variants, raft message filters, PD merges, and `block_on_timeout`.

Risks and test signals: direct message mutation is artificial but targets a documented corner case. Signals protect against applying singleton unpersisted logs, restart inconsistency, and entry cache panics.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/failpoints/cases/test_early_apply.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/failpoints/cases/test_encryption.rs -->
# sources/storage-engines/tikv/tests/failpoints/cases/test_encryption.rs

Purpose: tests encryption metadata recovery and KMS temporary-unavailable retry behavior.

Important APIs and functions: `test_file_dict_file_record_corrupted` uses `FileDictionaryFile`, `create_file_info`, and failpoint `file_dict_log_append_incomplete`. `test_kms_provider_temporary_unavailable` uses fake KMS helpers and failpoints `kms_api_timeout_encrypt` and `kms_api_timeout_decrypt`.

Control flow: first test truncates an intermediate log record and expects recovery failure, then truncates the final record and expects recovery to keep prior entries. Second test injects one timeout on encrypt and decrypt and expects retry success.

State and persistence: file dictionary log records are persisted in tempdir; recovery must distinguish unrecoverable middle corruption from discardable tail corruption. KMS backend state is cleared between encrypt/decrypt phases.

Dependencies and integration: uses encryption crate, encryption protobufs, tempfile, and fail-rs.

Risks and test signals: corruption byte count assumes record header layout. Signals protect encrypted file metadata durability and transient KMS tolerance.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/failpoints/cases/test_encryption.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/failpoints/cases/test_engine.rs -->
# sources/storage-engines/tikv/tests/failpoints/cases/test_engine.rs

Purpose: tests RocksDB engine memory/flush listener behavior in raftstore v2.

Important APIs and functions: `dummy_string` creates zero-filled strings. `test_write_buffer_manager` sets per-CF and global write buffer limits, injects `on_memtable_sealed`, and writes to `CF_WRITE`, `CF_LOCK`, and `CF_DEFAULT`. Ignored `test_rocksdb_listener` models historical memtable sealed/flush ordering around `on_flush_begin`, `on_memtable_sealed`, and `on_flush_completed`.

Control flow: active test lowers write buffer sizes to force memtable sealing and cycles the failpoint return value by CF while writing dummy data. Ignored test splits tablets, starts concurrent flushes, pauses callbacks, and checks no deadlock/panic after RocksDB listener order changes.

State and persistence: writes CF data into tablet/RocksDB engines; listener state tracks memtable flush/seal sequence.

Dependencies and integration: uses `test_raftstore_v2`, `engine_traits::MiscExt`, CF constants, and `ReadableSize`.

Risks and test signals: ignored listener test is scenario documentation. Active signal is write buffer manager interaction with CF-level sealing.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/failpoints/cases/test_engine.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/failpoints/cases/test_gc_metrics.rs -->
# sources/storage-engines/tikv/tests/failpoints/cases/test_gc_metrics.rs

Purpose: validates GC compaction-filter metrics and scheduling for transactional and raw key modes.

Important APIs and functions: tests cover creating txn compaction filters, filtering MVCC versions, handling txn GC keys, filtering raw MVCC versions, and handling raw GC keys. Metrics include `GC_COMPACTION_FILTER_PERFORM`, `SKIP`, `FILTERED`, `GC_COMPACTION_FILTER_MVCC_DELETION_MET`, `HANDLED`, and `MVCC_VERSIONS_HISTOGRAM`.

Control flow: builds test engines with compaction settings, writes MVCC/raw version data, runs `TestGcRunner` or starts `GcWorker` auto GC with mock safe point/region info providers, flushes CFs, compacts ranges, sleeps for async scheduling, then asserts metric counters.

State and persistence: RocksDB write/default CFs hold encoded MVCC or API v2 raw versions. Region metadata is synthesized for auto GC.

Dependencies and integration: uses GC worker internals, Rocks flush/compact APIs, API v2 raw encoding, coprocessor region info accessors, and transaction test helpers.

Risks and test signals: metric resets are required to avoid cross-test contamination. Signals enforce both filtering behavior and observability counters.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/failpoints/cases/test_gc_metrics.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/failpoints/cases/test_gc_worker.rs -->
# sources/storage-engines/tikv/tests/failpoints/cases/test_gc_worker.rs

Purpose: tests GC worker handling of orphan versions emitted by write-CF compaction filters.

Important APIs and functions: `test_error_in_compaction_filter` injects `write_compaction_filter_flush_write_batch` and inspects `GcTask::OrphanVersions`. `test_orphan_versions_from_compaction_filter` starts auto GC in a raft cluster with mock safe point and region providers, then runs `sync_gc`.

Control flow: writes several versions and a delete, triggers compaction-filter GC, forces write-batch flushing failure, and verifies orphan default-CF versions are cleaned by the GC worker path.

State and persistence: MVCC write CF can be filtered before default CF cleanup, creating orphan default values. Tests check encoded `data_key` entries disappear.

Dependencies and integration: uses `TestGcRunner`, `GcWorker`, grpc KV client, raftstore clusters, `keys::data_key`, and transaction helpers.

Risks and test signals: polling loop waits for async cleanup. Signals protect cleanup handoff between compaction filter and GC worker.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/failpoints/cases/test_gc_worker.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/failpoints/cases/test_hibernate.rs -->
# sources/storage-engines/tikv/tests/failpoints/cases/test_hibernate.rs

Purpose: tests raftstore hibernation behavior around restart, busy-on-apply, unstable entry buffers, forced wakeup, store disconnect, and long-uncommitted proposal ticks.

Important APIs and functions: tests include `test_break_leadership_on_restart`, `test_restart_peer_busy_on_apply`, `test_hibernate_region_releases_unstable_entry_buffer`, `test_forcely_awaken_hibenrate_regions`, `test_store_disconnect_with_hibernate`, and `test_check_long_uncommitted_proposals_while_hibernate`. They use `GroupState`, `PeerTick`, `ExtraMessageType`, store heartbeats, and failpoints around raft ticks/apply checks.

Control flow: each test configures short raft ticks, enables hibernate, waits for idle state, injects messages or node restarts, then checks election suppression, busy flags, buffer release, wakeup callbacks, or tick suppression/resumption.

State and persistence: raft group hibernate state, unstable entry buffers, leader committed index, store stats `is_busy`, and KV replication are core state.

Dependencies and integration: uses node/server clusters, PD client, raft message filters, and `ReadableDuration`.

Risks and test signals: timing-heavy by design. Signals prevent false elections after restart, stuck busy state, memory retention after hibernation, and missed wakeups.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/failpoints/cases/test_hibernate.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/failpoints/cases/test_import_service.rs -->
# sources/storage-engines/tikv/tests/failpoints/cases/test_import_service.rs

Purpose: exercises SST import service concurrency, resource limits, ingestion idempotency/conflicts, encryption cleanup, v2 cleanup, bucket/split metadata, applied-index flushing, and duplicate detection stream behavior.

Important APIs and functions: uses import grpc client methods `download`, `ingest`, `ingest_async`, `switch_mode`, `duplicate_detect`, helpers from `test_sst_importer` and integrations import util, and `sst_file_count`. Tests include concurrent download success/failure, blocking SST writer, download under disk/memory pressure, reentrant ingest, key-manager delete failure, ingest conflicts, stale-epoch cleanup, applied-SST cleanup, bucket update after ingest, flushed applied index after ingest, and duplicate detect client-stop handling.

Control flow: tests generate SST files in temp dirs, upload or download them through import service, inject failpoints such as `create_local_storage_yield`, `on_open_sst_writer`, `mock_memory_usage`, `key_manager_fails_before_delete_file`, `before_sst_service_ingest_check_file_exist`, `on_cleanup_import_sst_schedule`, `on_flush_completed`, `on_update_region_keys`, `on_apply_ingest`, and `failed_to_async_snapshot`, then ingest or stream and assert data or error messages.

State and persistence: import-sst files, encrypted file keys, region epoch metadata, applied-index flush state, bucket metadata, and duplicate-detect SST contents are persisted or tracked. Several tests restart clusters to validate cleanup durability.

Dependencies and integration: integrates `kvproto::import_sstpb`, TiKV config, local external storage, grpc, disk usage status, raftstore simulator, TDE import setup, and raw KV client writes.

Risks and test signals: high concurrency and fixed timeouts can be flaky under slow IO. Signals include no deadlocks on duplicate downloads, correct resource errors, idempotent ingest, no stale file resurrection, and robust streaming cancellation.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/failpoints/cases/test_import_service.rs -->
