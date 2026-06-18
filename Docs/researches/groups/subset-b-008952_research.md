# Research Report: subset-b-008952

Work item `subset-b-008952` covers TiKV integration tests for raftstore v1/v2 compatibility, witness peers, resource metering, and server KV/debug/deadlock behavior. Each file section below preserves the source path in its title and is bounded for deterministic reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/raftstore/test_v1_v2_mixed.rs -->
# sources/storage-engines/tikv/tests/integrations/raftstore/test_v1_v2_mixed.rs

## Purpose

This integration test validates compatibility between the legacy raftstore simulator and the raftstore v2 tablet implementation. It proves that v1 can receive a tablet snapshot produced by v2, and that a v1 compatible learner can receive replicated writes forwarded from a v2 cluster.

## Important APIs, Types, and Functions

- `ForwardFactory` and `ForwardFilter` implement `test_raftstore::FilterFactory` and `Filter`. They drain outgoing `RaftMessage`s and forward messages targeting a chosen store through a captured router closure.
- `generate_snap<EK: KvEngine>` manually constructs a `raft::eraftpb::Snapshot` from v2 tablet state, writes a checkpoint using `Checkpointer::create_at`, wraps it in `RaftMessage`, and returns the matching `TabletSnapKey`.
- `random_long_vec` creates randomized 1 KiB values to enlarge v2 snapshots.
- `test_v1_receive_snap_from_v2` sends a v2 tablet snapshot to a v1 TiKV gRPC endpoint through `tikv::server::tablet_snap::send_snap`.
- `test_v1_simple_write` wires v1 and v2 simulators together through filters and checks learner replication.
- `check_key_in_engine` polls an engine until the expected key/value appears.

## Control Flow

`test_v1_receive_snap_from_v2` creates independent one-node v1 and v2 server clusters, enables `enable_v2_compatible_learner` on v1, writes either 20 or 5000 keys directly into the v2 tablet, builds a tablet snapshot, and sends it to the v1 address with an unrestricted `Limiter`. It then opens the received v1 snapshot RocksDB directory and verifies every expected default-CF key.

`test_v1_simple_write` starts two-node v1 and v2 node clusters, adds learners with matching logical peer identity, confirms baseline replication inside each cluster, and installs send/receive filters that redirect raft messages between v1 store 1 and v2 store 2. After filtering direct v1 receive traffic on store 2, a write through v2 is expected to materialize in the v1 learner engine.

## State and Persistence Behavior

The snapshot test persists a tablet checkpoint at the v2 snapshot manager path and validates the final v1 receive path using a RocksDB instance opened over the snapshot directory. The write test inspects persisted engine state on learner stores. The generated raft message embeds region epoch, snapshot metadata, conf state, and tablet snapshot version, so persisted compatibility depends on both raft metadata and tablet file layout.

## Dependencies and Integration Points

The file depends on `test_raftstore`, `test_raftstore_v2::WrapFactory`, `raftstore::store::{TabletSnapManager, TabletSnapKey}`, `engine_rocks`, `engine_traits`, `kvproto::tikvpb::TikvClient`, and `tikv::server::tablet_snap::send_snap`. It bridges direct storage APIs, raft message routing filters, gRPC snapshot transfer, and RocksDB snapshot inspection.

## Risks and Edge Cases

Snapshot construction is intentionally manual and may become stale if snapshot metadata or tablet snapshot versioning changes. The tests assume peer IDs/store IDs can be matched across independent clusters. The filter drains all messages it sees, so a routing or target-store mismatch can silently starve normal raft delivery. Polling in `check_key_in_engine` adds timing sensitivity.

## Test Signals

Strong signals include both small and large snapshot coverage, direct verification of received snapshot contents, and cross-simulator write propagation. Failures point to incompatibility in tablet snapshot format, v1 compatible learner handling, snapshot send/receive paths, or raft message forwarding semantics.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/raftstore/test_v1_v2_mixed.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/raftstore/test_witness.rs -->
# sources/storage-engines/tikv/tests/integrations/raftstore/test_witness.rs

## Purpose

This file exercises TiKV witness peer behavior in raftstore. Witness peers replicate raft metadata and logs without storing user data, so the tests focus on split/merge propagation, conf changes, leader restrictions, election behavior, raft log GC, replica reads, consistency checks, and snapshot recovery under network isolation.

## Important APIs, Types, and Functions

- `new_witness_peer`, `find_peer`, and `PdClient::must_switch_witnesses` drive witness peer topology changes.
- `must_get_error_is_witness` sends raft commands through the leader and asserts the response contains `errorpb::IsWitness`.
- `RaftApplyState` and `PeerState` are inspected to verify witness apply progress, truncation state, and tombstones.
- `RegionPacketFilter` and `IsolationFilterFactory` manipulate raft message flow for lag and snapshot tests.
- The test functions cover split/merge, conf changes, witness switching, leader/election constraints, raft log GC with lagged follower or witness, replica read rejection, leader-down behavior, consistency-check tolerance, and snapshot apply after isolation.

## Control Flow

Most tests start a three-node server cluster, disable PD default operators, write baseline keys, and switch one peer to witness. Split/merge tests verify witness flags on derived regions and reject merge when witness layouts differ. Conf-change tests reject witness conversion through ordinary conf change, add a new witness, wait for apply state, and remove it to tombstone. Leader tests keep the leader non-witness and block leader transfer to a witness.

Log GC tests lower `raft_log_gc_count_limit`, capture truncated states, stop either a normal follower or the witness, write many entries, restart the peer, and compare truncation advancement. Read-path tests build replica-read and leader-command requests that must produce `IsWitness` errors. Snapshot isolation tests add a witness peer, isolate it until snapshot is needed, drop append responses, then transfer leadership and write again to prove recovery.

## State and Persistence Behavior

Witness peers update raft apply state, region local state, region epoch, truncated state, and peer tombstone state but should not retain user KV data. The tests repeatedly assert `must_get_none` on witness engines while checking raft metadata advancement. Merge/split behavior must preserve witness flags in persisted region metadata.

## Dependencies and Integration Points

The file integrates PD scheduling APIs, raftstore test cluster utilities, raft conf change messages, region packet filters, raft apply metadata, and TiKV utility helpers. It relies on real raftstore simulation rather than isolated mocks.

## Risks and Edge Cases

The suite is timing-sensitive due to sleeps around witness conversion, log replication, consistency checks, and snapshot generation. It covers high-risk cases where witness peers could incorrectly store data, become leaders, allow stale reads, block log GC, or fail to recover from snapshot state. Merge rejection depends on exact error text containing `peers doesn't match`.

## Test Signals

Passing tests indicate witness peer invariants hold across topology changes and failure scenarios: witnesses do not serve data, cannot lead, maintain metadata, allow safe GC behavior, and recover from snapshot transfer after isolation.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/raftstore/test_witness.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/resource_metering/mod.rs -->
# sources/storage-engines/tikv/tests/integrations/resource_metering/mod.rs

## Purpose

This module wires the resource metering integration test suite into the broader TiKV integration test crate. It exposes common test support and conditionally includes platform-dependent tests.

## Important APIs, Types, and Functions

- Always exports `test_read_keys` and `test_suite`.
- On Linux and macOS, exports `test_dynamic_config`, `test_receiver`, `test_pubsub`, and `test_cpu`.
- Uses `#[cfg(any(target_os = "linux", target_os = "macos"))]` to gate tests that depend on platform-specific resource accounting or networking behavior.

## Control Flow

There is no runtime control flow beyond Rust module inclusion. Compilation decides which test modules are built for the target operating system.

## State and Persistence Behavior

The file holds no state and performs no persistence. Its state impact is indirect: gated modules create resource metering workers, mock servers, and temporary storage when compiled and run.

## Dependencies and Integration Points

It integrates with sibling modules under `tests/integrations/resource_metering` and the test harness module tree. The conditional gates prevent unsupported platforms from building resource metering tests that assume Linux/macOS behavior.

## Risks and Edge Cases

Changing module gates can either hide test coverage on supported platforms or introduce flaky/unsupported tests elsewhere. The always-included `test_read_keys` contains ignored tests, so its inclusion mostly provides code compilation and helper coverage.

## Test Signals

The module itself has no assertions. Its signal is successful compilation and discovery of the intended resource metering integration tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/resource_metering/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/resource_metering/test_cpu.rs -->
# sources/storage-engines/tikv/tests/integrations/resource_metering/test_cpu.rs

## Purpose

This file verifies that resource metering records non-zero CPU time for transactional and coprocessor workloads tagged by resource group. It injects artificial CPU load into selected execution paths and observes records through the resource metering pubsub stream.

## Important APIs, Types, and Functions

- `test_prewrite`, `test_commit`, `test_get`, `test_batch_get`, and `test_batch_get_command` exercise storage APIs.
- `test_reschedule_coprocessor` exercises DAG coprocessor execution with rescheduling.
- `setup_test_suite` creates `TestSuite`, `test_coprocessor::Store`, read pool, `Endpoint`, `ConcurrencyManager`, and `QuotaLimiter`.
- `prepare_insert` builds a product-table insert.
- `require_cpu_time_not_zero` subscribes to pubsub records and waits for one matching tag with summed `cpu_time_ms > 0`.
- `cpu_load` busy-loops for a requested duration and is installed through failpoints.

## Control Flow

Each test creates a resource metering suite with one-second precision and three-second report interval, installs a failpoint callback that burns CPU, spawns an async pubsub observer for a tag, runs a tagged workload, and asserts the observer reports non-zero CPU. Coprocessor coverage inserts and commits data, builds a DAG request with resource-group tag and request source, forces rescheduling, and validates the response is non-empty.

## State and Persistence Behavior

The tests use temporary RocksDB-backed storage through `TestSuite` and `Store`. Resource metering state is in recorder/reporter workers and pubsub streams. Transaction tests persist MVCC data before reading or committing; CPU accounting is emitted as `ResourceUsageRecord` items keyed by resource group tag.

## Dependencies and Integration Points

The file integrates resource metering with the scheduler, storage API, point getter, batch get command path, coprocessor endpoint, failpoints, read pools, resource control, and thread group properties. It depends on the shared `resource_metering::test_suite::TestSuite`.

## Risks and Edge Cases

The tests rely on failpoints such as `scheduler_process`, `scanner_next`, `point_getter_get`, and `copr_reschedule`. CPU timing and pubsub delivery can be flaky under heavily loaded CI. If thread registration or tag propagation changes, records may be missing even when storage operations succeed.

## Test Signals

Passing tests show resource tags propagate through prewrite, commit, point get, batch get, batch-get command, and coprocessor execution, and that the recorder attributes measurable CPU time to those tags.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/resource_metering/test_cpu.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/resource_metering/test_dynamic_config.rs -->
# sources/storage-engines/tikv/tests/integrations/resource_metering/test_dynamic_config.rs

## Purpose

This file validates live configuration changes for resource metering. It checks receiver address enable/disable, report interval changes, resource group aggregation limits, precision changes, and network I/O collection toggling.

## Important APIs, Types, and Functions

- `TestSuite::cfg_receiver_address`, `cfg_report_receiver_interval`, `cfg_max_resource_groups`, `cfg_precision`, and `cfg_enable_network_io_collection` drive dynamic config updates.
- `TestSuite::setup_workload`, `block_receive_one`, `nonblock_receiver_all`, and `flush_receiver` produce and observe records.
- `ENABLE_NETWORK_IO_COLLECTION` is checked directly after enabling network I/O collection.
- `alloc_port` provides receiver endpoints.

## Control Flow

`test_enable` starts with no receiver, confirms no records, configures a receiver address and expects tagged records, clears the address and expects silence, then restores it. `test_report_interval` changes interval from three seconds to one second and measures inter-arrival timing with retries. `test_max_resource_groups` generates skewed tags and reduces the max groups to three, expecting overflow to be grouped under the empty tag. `test_precision` verifies timestamp spacing before and after changing precision. `test_enable_network_io_collection` toggles the flag and asserts the global atomic is set.

## State and Persistence Behavior

State is in the resource metering config controller, recorder/reporter worker configuration, receiver connection state, in-memory usage aggregation, and the global network I/O collection flag. The suite uses temporary storage to generate get workloads but does not validate persisted KV data.

## Dependencies and Integration Points

The tests integrate TiKV dynamic config plumbing with resource metering `ConfigManager`, single-target reporting, receiver transport, aggregation policy, and global metrics collection switches. They use the shared mock receiver server.

## Risks and Edge Cases

Timing assertions around report interval and precision are sensitive to scheduling delays. `test_max_resource_groups` depends on deterministic enough workload skew despite shuffled tag order. Receiver address updates must tear down and reconnect cleanly or records can leak across phases.

## Test Signals

Passing tests show runtime config updates take effect without restarting workers, resource records are suppressed or emitted according to receiver configuration, aggregation respects group limits, precision changes reshape timestamps, and network I/O collection is enabled globally.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/resource_metering/test_dynamic_config.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/resource_metering/test_pubsub.rs -->
# sources/storage-engines/tikv/tests/integrations/resource_metering/test_pubsub.rs

## Purpose

This file tests the resource metering pubsub service exposed by the test suite. It verifies that subscribers receive resource usage records and that multiple subscribers can independently observe the same tagged workload stream.

## Important APIs, Types, and Functions

- `TestSuite::new` starts the recorder, reporter, and mock pubsub server.
- `TestSuite::setup_workload` creates repeated tagged storage gets.
- `TestSuite::subscribe` returns a `ResourceMeteringPubSubClient` and streaming receiver.
- `StreamExt::take`, `map`, and `collect` gather tags from `ResourceUsageRecord`s.

## Control Flow

`test_basic` starts a workload for `req-1` and `req-2`, subscribes once, takes four records, and asserts both tags appear. `test_multiple_subscribers` starts the same workload, creates three subscribers, spawns one async collection task per subscriber on the suite runtime, and asserts each subscriber receives both tags.

## State and Persistence Behavior

State is held in active pubsub streams and resource metering worker buffers. Workload operations use temporary test storage, but the assertions focus on streamed usage records rather than persisted KV contents.

## Dependencies and Integration Points

The tests integrate `resource_metering::PubSubService`, gRPC streaming, the shared test suite workload generator, and the reporter data sink registry. They rely on the mock pubsub server created in `test_suite/mock_pubsub.rs`.

## Risks and Edge Cases

The tests assume four records are enough to observe both tags, which depends on workload scheduling and record batching. Multiple subscribers increase concurrency pressure on gRPC stream handling and data sink registration.

## Test Signals

Passing tests indicate pubsub delivery works for one and many subscribers, and tagged resource usage is visible through the external stream API.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/resource_metering/test_pubsub.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/resource_metering/test_read_keys.rs -->
# sources/storage-engines/tikv/tests/integrations/resource_metering/test_read_keys.rs

## Purpose

This file verifies resource metering `read_keys` accounting for KV point/scan reads and coprocessor reads. Both top-level tests are ignored as unstable, but they document expected integration behavior.

## Important APIs, Types, and Functions

- `test_read_keys` creates a real raftstore cluster with receiver reporting, writes ten keys, and checks point-get and scan `read_keys`.
- `new_cluster` configures resource metering receiver address, precision, and report interval.
- `must_recv_read_keys` and `recv_read_keys` drain `ResourceUsageRecord`s and sum `item.read_keys`.
- `test_read_keys_coprocessor` initializes recorder/reporter directly and registers `MockDataSink`.
- `init_coprocessor_with_data` builds a product-table `Endpoint`.
- `handle_select` executes a DAG request and decodes `SelectResponse`.
- `MockDataSink` implements `resource_metering::DataSink` and sends summed read keys through a channel.

## Control Flow

The KV test starts `MockReceiverServer`, configures a cluster, writes ten MVCC records, triggers a warm-up get, then asserts a point get reports one read key, a scan with limit five reports five, and a scan with high limit reports ten. The coprocessor test builds resource metering workers in-process, loads four product rows, executes a tagged DAG select once to register runtime threads, clears existing output, executes again, and expects four read keys.

## State and Persistence Behavior

The KV test persists MVCC data through raftstore and observes receiver-delivered usage records. The coprocessor test persists data in a test Rocks engine and captures reporter output via a registered mock sink. Accounting state is batched by recorder precision and report interval.

## Dependencies and Integration Points

The file integrates raftstore cluster setup, TiKV gRPC KV APIs, resource metering receiver protocol, coprocessor endpoint execution, protobuf decoding, `ResourceTagFactory`, and the shared mock receiver server.

## Risks and Edge Cases

Both tests are marked `#[ignore = "the case is unstable, ref #11765"]`, indicating known timing or accounting instability. Warm-up behavior, thread registration, report intervals, and channel timeouts are likely sources of flakiness.

## Test Signals

When run manually and passing, the tests show read-key counts propagate from point-get, scan, and coprocessor execution into resource metering records with expected cardinality.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/resource_metering/test_read_keys.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/resource_metering/test_receiver.rs -->
# sources/storage-engines/tikv/tests/integrations/resource_metering/test_receiver.rs

## Purpose

This file tests single-target receiver behavior for resource metering reports. It checks receiver address changes, receiver-side blocking, and receiver shutdown.

## Important APIs, Types, and Functions

- `TestSuite::start_receiver_at`, `shutdown_receiver`, `block_receiver`, and `unblock_receiver` manage the mock receiver.
- `cfg_receiver_address` changes the configured target endpoint.
- `setup_workload`, `cancel_workload`, `block_receive_one`, `flush_receiver`, and `nonblock_receiver_all` produce and inspect reports.

## Control Flow

`test_alter_receiver_address` starts with a valid receiver, confirms reports, switches to an invalid port and expects silence, then restores the valid address and expects reports again. `test_receiver_blocking` confirms normal reporting, makes the receiver block inside its report handler, verifies no records are delivered, unblocks it, flushes, and expects records again. `test_receiver_shutdown` confirms reports for one workload, changes workload tags, shuts down the receiver, and expects no subsequent records.

## State and Persistence Behavior

State lives in the reporter's receiver connection, the mock receiver server, and the test suite channel of received batches. The receiver can be blocked by an atomic flag, and shutdown removes the gRPC server. Storage state is only used to generate tagged workload.

## Dependencies and Integration Points

The tests integrate dynamic resource metering receiver config, gRPC client-streaming report delivery, mock receiver behavior, and reporter retry/suppression logic.

## Risks and Edge Cases

Sleep-based timing around failed addresses, blocked handlers, and shutdown may be flaky. A blocked report RPC can create backpressure; the test expects no channel records while the handler is blocked.

## Test Signals

Passing tests demonstrate that reports follow live receiver address changes, do not appear while the receiver is blocked or down, and resume when the receiver becomes usable again.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/resource_metering/test_receiver.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/resource_metering/test_suite/mock_pubsub.rs -->
# sources/storage-engines/tikv/tests/integrations/resource_metering/test_suite/mock_pubsub.rs

## Purpose

This helper builds a mock gRPC resource metering pubsub server for integration tests.

## Important APIs, Types, and Functions

- `MockPubSubServer::new(port, env, reg_handle) -> Server` constructs a `grpcio::Server`.
- `PubSubService::new(reg_handle)` is registered through `create_resource_metering_pub_sub`.
- Channel args set two concurrent streams and unlimited send/receive message sizes.

## Control Flow

The constructor builds channel args from the shared gRPC environment, creates a resource metering `PubSubService`, binds the server to `127.0.0.1:port`, registers the generated kvproto service, and returns an unstarted `Server`. The caller starts and shuts down the server.

## State and Persistence Behavior

The server holds a data sink registry handle and gRPC runtime state. It has no persistence and no independent mutable test state.

## Dependencies and Integration Points

It connects resource metering's `DataSinkRegHandle` and `PubSubService` to the kvproto `resource_usage_agent` pubsub gRPC service used by `TestSuite::subscribe`.

## Risks and Edge Cases

The helper assumes localhost binding and a preallocated free port. Stream limits are intentionally small, so tests with more concurrent subscribers may need adjustment.

## Test Signals

The helper has no assertions. Its signal is indirect: pubsub tests can connect and receive records from the server it builds.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/resource_metering/test_suite/mock_pubsub.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/resource_metering/test_suite/mock_receiver_server.rs -->
# sources/storage-engines/tikv/tests/integrations/resource_metering/test_suite/mock_receiver_server.rs

## Purpose

This helper implements a mock resource usage receiver server for tests that verify reporter delivery to a configured receiver address.

## Important APIs, Types, and Functions

- `MockReceiverServer` stores an `AtomicBool` block flag, a `Sender<Vec<ResourceUsageRecord>>`, and an optional `grpcio::Server`.
- `start_server` binds `ResourceUsageAgent` to localhost and starts the server.
- `block` and `unblock` control report handler progress.
- `shutdown_server` asynchronously stops the server.
- `MockReceiverService::report` implements the client-streaming resource usage report RPC.

## Control Flow

`start_server` builds channel args, registers `MockReceiverService`, starts the gRPC server, and stores it. The `report` handler spins while `should_block` is true, then asynchronously drains all streamed records into a vector, sends that vector to the crossbeam channel, and completes the RPC with `EmptyResponse`.

## State and Persistence Behavior

All state is in memory. The atomic block flag simulates a stuck receiver, the channel is the observation point for tests, and the optional server tracks lifecycle. There is no disk persistence.

## Dependencies and Integration Points

The mock implements kvproto's `ResourceUsageAgent`, integrates with `grpcio` client-streaming RPCs, and is controlled by the resource metering `TestSuite`.

## Risks and Edge Cases

The blocking loop sleeps on the RPC handling thread and can delay shutdown or consume test time. `tx.send(...).unwrap()` will panic if the receiver side is dropped. Tests rely on complete stream draining before an RPC success response.

## Test Signals

The helper enables receiver tests to distinguish delivered batches, blocked receivers, invalid addresses, and shutdown behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/resource_metering/test_suite/mock_receiver_server.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/resource_metering/test_suite/mod.rs -->
# sources/storage-engines/tikv/tests/integrations/resource_metering/test_suite/mod.rs

## Purpose

This file provides the shared resource metering integration test harness. It creates temporary TiKV storage, resource metering recorder/reporter workers, pubsub and receiver endpoints, dynamic config controls, workload generation, and record collection helpers.

## Important APIs, Types, and Functions

- `TestSuite` owns pubsub port, optional receiver server, storage, `ConfigController`, `ResourceTagFactory`, record channel, gRPC environment, Tokio runtime, workload cancellation channels, temp dir, and worker shutdown closure.
- `TestSuite::new` initializes recorder, reporter, single-target reporter, mock pubsub server, config manager, test storage, runtime, and cleanup closure.
- `subscribe` creates a `ResourceMeteringPubSubClient` and stream receiver.
- `cfg_*` methods update resource metering config through `ConfigController`.
- Receiver controls manage `MockReceiverServer`.
- `setup_workload` spawns a loop of tagged storage gets.
- `cancel_workload`, `nonblock_receiver_all`, `block_receive_one`, `merge_records`, and `flush_receiver` coordinate records.
- `Drop` stops pubsub, single-target, reporter, and recorder workers.

## Control Flow

Construction starts all resource metering components and registers the dynamic config manager. Workload setup spawns a runtime task that repeatedly issues one storage `get` per tag, each with `Context.resource_group_tag`; a oneshot cancellation path breaks the loop. Receiver and pubsub helpers expose either direct stream subscription or receiver channel batches. Record merging groups timestamps and CPU times by resource group tag.

## State and Persistence Behavior

The harness uses a temporary TiKV config directory and temporary Rocks storage. Recorder/reporter workers maintain in-memory usage state and periodically emit `ResourceUsageRecord`s. The config controller mutates live module settings. The temp dir and workers are cleaned up on drop.

## Dependencies and Integration Points

The suite integrates `resource_metering::{init_recorder, init_reporter, init_single_target, ConfigManager}`, TiKV `ConfigController`, `TestStorageBuilderApiV1`, `MockLockManager`, gRPC pubsub/receiver services, crossbeam channels, futures oneshot cancellation, and Tokio runtime execution.

## Risks and Edge Cases

Drop assumes `stop_workers` is present and unwraps it. Workload loops can run indefinitely if cancellation is not called before drop, though runtime teardown handles task shutdown. `flush_receiver` uses a timing heuristic based on configured report interval plus 500 ms, which can be flaky on slow systems.

## Test Signals

This harness is the foundation for the resource metering integration tests. Correct behavior is signaled by reliable dynamic config updates, record delivery through pubsub or receiver channels, and clean worker shutdown.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/resource_metering/test_suite/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/server/debugger.rs -->
# sources/storage-engines/tikv/tests/integrations/server/debugger.rs

## Purpose

This file tests debugger functionality specific to compaction and flashback-to-version operations, mainly for raftstore v2 tablet-backed storage plus debug-client flashback RPC behavior.

## Important APIs, Types, and Functions

- `gen_mvcc_put_kv` encodes a data key at commit timestamp and serializes a `WriteType::Put`.
- `gen_delete_k` encodes a timestamped data key for deletion.
- `test_compact` builds three regions, writes and deletes MVCC write-CF data, calls `DebuggerImplV2::compact`, and compares approximate sizes.
- `test_flashback_to_version`, `test_flashback_to_version_without_prepare`, and `test_flashback_to_version_with_mismatch_ts` use debug gRPC clients.
- `flashback_to_version` iterates region IDs, fetches region ranges, and issues `FlashbackToVersionRequest`s.

## Control Flow

Compaction setup splits a v2 node cluster into three regions, writes 30 MVCC put records in `CF_WRITE`, flushes tablets, deletes those records, flushes again, records approximate tablet sizes, runs debugger compaction over a requested key range, and verifies only the expected region tablets shrink to zero. Flashback tests write many versions, fetch all region IDs from the debug service, and call flashback in prepare/finish phases, including error cases for missing prepare and mismatched timestamps.

## State and Persistence Behavior

The compaction test manipulates persisted tablet RocksDB state and uses approximate sizes to confirm physical compaction after deletions. Flashback tests mutate MVCC history through KV writes and debug flashback state, then verify historical reads or error responses.

## Dependencies and Integration Points

The file integrates `DebuggerImplV2`, `ConfigController`, tablet caches, RocksDB approximate range sizes, debugpb/debug gRPC APIs, transaction write encoding, and raftstore cluster utilities.

## Risks and Edge Cases

Approximate size checks can be sensitive to RocksDB behavior and flush/compaction semantics. Flashback tests depend on region enumeration and strict debug error messages such as `not in flashback state`. Key range encoding must use data-key boundaries correctly.

## Test Signals

Passing tests show debugger compaction targets only tablets overlapping the requested range and debug flashback enforces prepare/finish state and timestamp matching while restoring older MVCC versions.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/server/debugger.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/server/gc_worker.rs -->
# sources/storage-engines/tikv/tests/integrations/server/gc_worker.rs

## Purpose

This file tests that TiKV's GC worker can bypass Raft and directly remove MVCC data and write records from local engines for both raftstore v1 and v2 clusters.

## Important APIs, Types, and Functions

- `test_gc_bypass_raft` is parameterized with `test_raftstore::must_new_cluster_mul` and `test_raftstore_v2::must_new_cluster_mul`.
- Uses `must_kv_prewrite`, `must_kv_commit`, and `sync_gc`.
- Inspects `CF_WRITE` and default data keys through `engine_traits::Peekable`.
- Encodes keys with `txn_types::Key::append_ts` and `keys::data_key`.

## Control Flow

The test creates a two-node cluster, disables default PD operators, writes four committed versions of one key, and verifies both default-CF and write-CF records exist for each version. It then iterates all stores, gets each store's GC scheduler, constructs a region range covering the key, runs `sync_gc` with safe point 200, and verifies old start/commit timestamp records are gone from every engine.

## State and Persistence Behavior

The test writes persisted MVCC records and then validates local deletion from engines. GC bypasses Raft, so each store's local GC worker must independently remove data under `keys::DATA_PREFIX`.

## Dependencies and Integration Points

It integrates KV gRPC transaction helpers, raftstore simulation, GC worker scheduler, MVCC key encoding, and direct engine reads.

## Risks and Edge Cases

The test assumes the manually adjusted region range fully covers the encoded key. It checks only old versions and not preservation of the newest version. Because GC bypasses Raft, per-store scheduler access must be correct for both raftstore engines.

## Test Signals

Passing tests show bypass-Raft GC removes obsolete default and write CF records on every store in both raftstore implementations.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/server/gc_worker.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/server/kv_service.rs -->
# sources/storage-engines/tikv/tests/integrations/server/kv_service.rs

## Purpose

This large integration suite validates TiKV KV, raw KV, debug, batch command, forwarding, health, transaction, quota, execution-detail, lock, pipelined DML, API-version, cluster-id, and commit-ts RPC behavior. Most tests are parameterized across raftstore v1 and raftstore v2 cluster constructors.

## Important APIs, Types, and Functions

- Raw KV APIs: compare-and-swap, get, put, scan, delete, TTL, get-key-TTL.
- Transaction APIs: prewrite, commit, get, scan, batch get, scan lock, rollback, cleanup, resolve lock, delete range, MVCC debug lookups, flashback, pessimistic lock, resumable lock, check txn status, heartbeat.
- Debug APIs: cluster/store info, metrics, region properties, range properties, debug get, raft log, region info, region size, failpoint injection, scan MVCC.
- Transport APIs: batch commands, health feedback, forwarding options, gRPC health check.
- Internal helpers/macros: `test_func!`, `test_func_init!`, `test_with_memory_lock_cluster`, and many `test_raftstore` helper functions.
- Storage/engine integration: `ConcurrencyManager`, `QuotaConfig`, `CollectorRegHandle`, `LazyWorker`, `StoreMeta`, `SstImporter`, raft engines, and CF constants.

## Control Flow

The suite starts clusters and gRPC clients through test constructors, runs RPCs, and asserts response bodies, region errors, key errors, execution details, or persisted engine state. Early tests cover raw KV and raw TTL semantics, basic MVCC read/write paths, rollback/cleanup, resolve lock, GC, delete range, and flashback prepare/finish/retry behavior. Split-region tests validate API v1/v2 key encoding and raw/non-raw split keys.

Debug tests write direct engine state or raft-engine logs and call debug RPCs to verify retrieval and not-found errors. Batch tests stress duplex `batch_commands`, empty requests, health feedback throttling, explicit health feedback, and wall-time details. Forwarding tests send many unary and batch RPC types first without a forwarding header and then with `server::build_forward_option`, proving proxy routing and reconnect behavior.

Transaction tests cover pessimistic lock error modes, resumable waits, async commit check status, max commit timestamp fallback, transaction heartbeat not-found, in-memory lock visibility for reads, lock wait info API, API version validation, quota limiter delay, write/detail metrics, scan lock over memory and CF locks, pessimistic rollback with read-first scan, and `need_commit_ts` response fields. Pipelined DML tests use `kv_flush` and `kv_buffer_batch_get` to validate buffered data, conflicts, min-commit-ts push, and unordered/duplicated key handling.

## State and Persistence Behavior

The file exercises both persisted RocksDB/raft-engine state and in-memory concurrency-manager lock state. It writes MVCC default/write/lock CF records, raw KV TTL records, raft logs, raft apply/region states, buffered pipelined DML locks, and direct debug data. It also verifies state transitions: flashback state blocks newer reads/writes and scheduling, GC removes old versions, quota limits delay writes, and cluster ID validation must not advance max timestamp on invalid requests.

## Dependencies and Integration Points

This suite is a broad integration point for `kvproto::tikvpb::TikvClient`, raftstore v1/v2 test harnesses, gRPC streaming, debugpb clients, health checking, storage scheduler, concurrency manager, API-version encoding, raft engines, resource metering collector handles, quota limiter config, failpoints, and TiKV server forwarding.

## Risks and Edge Cases

The file contains high timing and concurrency risk: sleeps, timeouts, blocked lock waits, gRPC stream collection, quota-delay assertions, and failpoint-driven flashback partial failures. It asserts exact behavior for many protocol edge cases, including API version mismatch strings, cluster ID invalid-argument errors, health feedback sequence increments, and `need_commit_ts` lock handling. Broad coverage also means failures can originate from setup utilities rather than a single RPC implementation.

## Test Signals

Passing tests provide strong end-to-end confidence that TiKV's public KV service behaves consistently across raftstore v1 and v2. The suite signals correctness for raw and transactional APIs, debug endpoints, proxy forwarding, batch streaming, resource and execution accounting, lock management, flashback, pipelined DML, API compatibility, and request validation.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/server/kv_service.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/server/lock_manager.rs -->
# sources/storage-engines/tikv/tests/integrations/server/lock_manager.rs

## Purpose

This file tests TiKV lock manager and deadlock detector behavior, including detector leadership changes across region topology updates and deadlock handling for ordinary and shared pessimistic locks.

## Important APIs, Types, and Functions

- `deadlock` constructs a two-transaction cycle and validates returned deadlock wait-chain metadata, including resource group tags.
- `kv_shared_pessimistic_lock`, `must_kv_shared_pessimistic_lock`, and `force_shared_lock_shrink_only` exercise shared pessimistic locks and shrink-only tracking.
- `async_pessimistic_lock_resumable` runs blocking lock requests in threads and returns channels.
- `build_leader_client`, `must_detect_deadlock`, `deadlock_detector_leader_must_be`, and topology helpers manage cluster clients and detector placement.
- Tests cover leader transfer, region split, region transfer, region merge, waiter updates, partial edge cleanup, and shared-lock waiter updates.

## Control Flow

`new_cluster_for_deadlock_test` creates a three-peer region, disables default PD operators, sets lock wait timeout, disables pipelined pessimistic txn behavior, transfers leadership, and confirms basic deadlock detection. Subsequent tests mutate region topology and then ensure deadlock detection still works from the correct detector leader. Shared-lock tests create shared lock owners, force shrink-only mode with conflicting exclusive lock attempts, spawn waiters, and assert deadlocks are detected or cleaned up as expected.

## State and Persistence Behavior

The tests manipulate in-memory lock wait graphs, pessimistic locks, shared lock ownership, region leadership metadata, and raftstore region membership. Cleanup uses pessimistic rollback to remove locks and unblock waiters. Resource group tags are stored in request contexts and expected in deadlock wait-chain entries.

## Dependencies and Integration Points

The file integrates gRPC `TikvClient`, raftstore cluster topology operations, pessimistic transaction APIs, deadlock detector leader tracking through PD region metadata, and TiKV shared-lock behavior.

## Risks and Edge Cases

Concurrency and timing are central: tests use spawned threads, short sleeps, receive timeouts, and resumable lock waits. Region merge/transfer cases can be sensitive to leader election timing. Shared-lock tests target subtle graph cleanup bugs where partial deadlock detection edges could poison later waiters.

## Test Signals

Passing tests show deadlock detection remains correct across leadership and region topology changes, wait-chain metadata is accurate, and shared pessimistic lock deadlock tracking cleans up and updates waiters safely.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/server/lock_manager.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/server/mod.rs -->
# sources/storage-engines/tikv/tests/integrations/server/mod.rs

## Purpose

This module wires server integration test submodules and provides a helper for constructing a TiKV gRPC server from a `Tikv` service implementation.

## Important APIs, Types, and Functions

- Declares submodules: `debugger`, `gc_worker`, `kv_service`, `lock_manager`, `raft_client`, `security`, `server`, and `status_server`.
- `tikv_service<T>(kv, ip, port) -> grpcio::Result<Server>` accepts any `Tikv + Clone + Send + 'static`.
- Uses `SecurityManager::new(SecurityConfig::default())`, `create_tikv(kv)`, and `ServerBuilder`.

## Control Flow

`tikv_service` creates a two-thread gRPC environment, builds a default security manager, configures channel args with two concurrent streams and unlimited message sizes, registers the TiKV service, binds through the security manager, and returns the built server.

## State and Persistence Behavior

The module has no persistence. The helper creates runtime gRPC server state and security binding state for tests that need an in-process TiKV service.

## Dependencies and Integration Points

It integrates generated kvproto TiKV gRPC services, TiKV security configuration, and `grpcio` server construction. The module declarations connect the server integration suite to Rust's test harness.

## Risks and Edge Cases

The helper uses default security config and localhost-style binding passed by callers; tests requiring custom TLS/security behavior must use other helpers. The low concurrent stream limit may constrain tests if reused outside its intended scope.

## Test Signals

The file itself has no tests, but compilation and downstream server tests confirm module wiring and service construction remain valid.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/server/mod.rs -->
