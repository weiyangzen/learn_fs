# subset-b-008492 Research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/MutationLogReaderCorrectness.cpp -->
## sources/storage-engines/foundationdb/fdbserver/workloads/MutationLogReaderCorrectness.cpp

`MutationLogReaderCorrectnessWorkload` is a single-client correctness workload for backup mutation-log reading. It synthesizes a private backup log UID, writes a deterministic sequence of records under `backupLogKeys.begin` using `getLogKey(version, uid)`, then constructs a `MutationLogReader` over `[beginVersion, endVersion)` and asserts that every returned key/value exactly matches the generated sequence.

Important APIs and types are `TestWorkload`, `MutationLogReader::Create`, `getLogKey`, `backupLogKeys`, `Transaction`, `FDBTransactionOptions::ACCESS_SYSTEM_KEYS`, `RangeResultRef`, and `error_code_end_of_stream`. `recordVersion`, `recordKey`, and `recordValue` encode the oracle: monotonically spaced versions, backup-log keys for the private UID, and formatted version strings as values.

Control flow is simple but sensitive to edge cases. The constructor chooses `records` in `[0, 500000)`, a random `beginVersion`, a very large version range, and `versionIncrement = versionRange / (records + 1)`. `start` runs only on client 0. `_start` writes records in 1000-key batches with system-key access and normal retry loops, then repeatedly calls `reader->getNext()` until `end_of_stream`. Every emitted record increments `nextExpectedRecord`; after stream termination the workload asserts that the count equals `records`.

State and persistence are limited to test-owned backup-log keys. The workload intentionally writes system keyspace data and does not clean it up, relying on simulation test isolation. A latent risk is the zero-record path: `endVersion = recordVersion(records - 1) + 1` calls `recordVersion(-1)`, which remains a computable version expression but is a semantic edge case worth watching. Other risks are integer overflow assumptions around `Version`, large record counts causing long setup, and pipeline depth fixed to 1 only covering serial reader behavior.

Dependencies and integration points are the backup agent log key schema, backup container reader plumbing, Flow actors, deterministic random generation, and tester workload registration through `WorkloadFactory<MutationLogReaderCorrectnessWorkload>`. Test signals are hard assertions on ordering/content and the final printed expected/found counts; `check` always returns true, so failures surface through asserts or unexpected reader errors.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/MutationLogReaderCorrectness.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/Performance.cpp -->
## sources/storage-engines/foundationdb/fdbserver/workloads/Performance.cpp

`PerformanceWorkload` is a tester-orchestrated saturation probe. It consumes the original workload options, saves them, and repeatedly launches another workload, defaulting to `ReadWrite`, through tester interfaces at increasing `transactionsPerSecond` targets. Its purpose is not simulation performance truth, but comparative discovery of the highest achieved transaction rate and latency metrics inside the tester framework.

The central APIs are `TestWorkload`, `TesterInterface`, `GetWorkersRequest::TESTER_CLASS_ONLY`, `runWorkload`, `TestSpec`, `DistributedTestResults`, and `PerfMetric`. `getOpts()` rebuilds one workload option vector with `testName`, `transactionsPerSecond`, and saved options. `getTesters()` discovers tester-class workers via the cluster interface. `getNamedMetric()` searches child workload metrics for `Transactions/sec` and `Median Latency (ms, averaged)`.

Setup runs only on client 0. `_setup` discovers testers and runs the target workload setup phase with a nominal 1000 TPS. `_start` calls `getSaturation`, which begins at 400 TPS, runs execution plus metrics, logs returned metrics, tracks best baseline latency, best achieved TPS, and corresponding saturation latency, and increases or backs off the requested rate. If achieved TPS is less than roughly 95% of target minus 100, it retries once, then either refines with multiplier 1.189 or returns.

State is in memory: saved options, discovered tester interfaces, best metric snapshots, and latency/TPS `PerfMetric` fields. It persists only whatever the child workload setup writes. Risks include reliance on exact child metric names, a typo in trace event names (`Performace...`), no use of testers recruited on workers despite the FIXME, and stopping on child `runWorkload` error without marking check failure. Saturation logic is heuristic and can miss unstable or multimodal throughput.

Integration points are distributed tester scheduling, worker discovery, and any probe workload that accepts `transactionsPerSecond`. Test signals are exported metrics: baseline latency, saturation transactions/sec, saturation median latency, and the metric set from the best achieved run. `check` always returns true, so correctness is measured through successful child execution and emitted metrics rather than explicit assertions.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/Performance.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/PerpetualWiggleStatsWorkload.cpp -->
## sources/storage-engines/foundationdb/fdbserver/workloads/PerpetualWiggleStatsWorkload.cpp

`PerpetualWiggleStatsWorkload` verifies storage wiggle metric restore/reset behavior when perpetual wiggle is enabled, disabled, and toggled while the data distributor is intentionally dead. It builds a `DDTeamCollectionTester` wrapper to reach protected `StorageWiggler` behavior, writes synthetic `StorageWiggleMetrics` to system metadata, and checks that `restoreStats()` and `finishWiggle()` honor configuration state.

Important APIs and types include `DDTeamCollection`, `StorageWiggler`, `StorageWiggleMetrics`, `StorageWiggleData::updateStorageWiggleMetrics`, `ManagementAPI::changeConfig`, `setDDMode`, `takeMoveKeysLock`, `DDTxnProcessor`, `ReadYourWritesTransaction`, and `BulkLoadTaskCollection`. `storageWiggleStatsEqual` compares finished counters and smoothed duration totals with a small floating tolerance.

Setup on client 0 disables DD, takes the move-keys lock to force current DD shutdown, disables storage migration, and waits 30 seconds. `_start` constructs a synthetic primary `DDTeamCollectionTester`, sets minimal configuration fields, then runs three scenarios: restore followed by disabling perpetual wiggle resets metrics; disabling then enabling while DD is dead causes restored metrics to reset; and `finishWiggle()` after disabling does not overwrite reset stats. Each scenario calls `prepareTestEnv`, which enables perpetual wiggle and writes random metrics through a RYW transaction.

State persists in the cluster configuration and storage wiggle metadata. The workload also mutates DD mode and the move-keys lock, so cleanup is important; it re-enables DD at the end of `_start`. Risks include early `co_return` inside tester helper methods if `changeConfig` fails, which can skip some assertions; reliance on arbitrary delays for read windows and DD death; and constructing a DDTeamCollection outside a full DD lifecycle.

Integration points are DD internals, management configuration, system-key metadata, and perpetual storage wiggle persistence. Test signals are assertions comparing metrics before and after restore/reset, plus configuration-change success assertions in setup and preparation. `check` returns true, so failed invariants surface through asserts during execution.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/PerpetualWiggleStatsWorkload.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/PerpetualWiggleStorageMigrationWorkload.cpp -->
## sources/storage-engines/foundationdb/fdbserver/workloads/PerpetualWiggleStorageMigrationWorkload.cpp

`PerpetualWiggleStorageMigrationWorkload` verifies that perpetual storage wiggle can migrate a selected storage process to a configured storage engine without affecting an excluded-and-reincluded process that should continue using the base `storage_engine`. It is RocksDB-specific and exits immediately if the build lacks `WITH_ROCKSDB`.

Important APIs include `getStorageServers`, `ManagementAPI::changeConfig`, `excludeServers`, `includeServers`, `checkForExcludingServers`, `StorageServerInterface::getKeyValueStoreType`, `LocalityData`, simulator process lookup, and `AddressExclusion`. It disables all failure injection workloads because smooth exclude/include behavior is required.

On client 0, `startImpl` selects a reliable storage process to exclude/include and a distinct process to wiggle. It configures `perpetual_storage_wiggle_engine=ssd-rocksdb-v1`, enables perpetual wiggle, sets `storage_migration_type=gradual`, and restricts wiggle by `perpetual_storage_wiggle_locality` to the target process id. It excludes and includes the first process, then `validateDatabase` polls storage servers, asserting the excluded/reincluded process remains `ssd-2` and the wiggle target eventually reports the requested engine. With 50% probability it clears the wiggle engine to `none`, excludes/includes the wiggle target, and expects it to return to `ssd-2`.

State and persistence are cluster configuration changes, exclusion state, and storage server engine identity after recruitment. Validation tolerates the selected process never reappearing as a storage server by bounding missing-count loops and only requiring absence if the expected migrated engine is not observed. Risks include reliance on process reliability, build-time RocksDB availability, fixed storage engine names (`ssd-2`, `ssd-rocksdb-v1`), and probabilistic coverage of engine reset.

Integration points are data distribution, perpetual wiggle migration, storage process recruitment, simulator process metadata, and management exclusions. Test signals are trace events for selected processes, configuration success assertions, storage type assertions, and timeout-style loops that prevent indefinite waits. `check` returns true; execution assertions provide the pass/fail signal.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/PerpetualWiggleStorageMigrationWorkload.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/PhysicalShardMove.cpp -->
## sources/storage-engines/foundationdb/fdbserver/workloads/PhysicalShardMove.cpp

`PhysicalShardMoveWorkLoad` is a single-client simulation workload for explicit shard relocation and checkpoint restore behavior, especially physical shard IDs under sharded RocksDB. It disables DD, writes a small ordered key set, moves overlapping key ranges to selected single-server teams with logical or physical `DataMoveType`, validates storage server shard metadata, creates and fetches checkpoints, restores them into a local sharded RocksDB KV store, and finally validates database contents after DD is re-enabled.

Important APIs and types include `moveKeys`, `MoveKeysParams`, `newDataMoveId`, `DataMoveMetaData`, `StorageServerShard`, `getStorageServers`, `serverListKeyFor`, `GetShardStateRequest`, `createCheckpoint`, `getCheckpointMetaData`, `fetchCheckpointRanges`, `fetchCheckpoint`, `CheckpointMetaData`, `IKeyValueStore`, `keyValueStoreShardedRocksDB`, `ReadYourWritesTransaction`, `FlowLock`, and `DDEnabledState`.

The main `_start` sequence disables DD, populates keys `TestKeyA` through `TestKeyF`, moves `[TestKeyA, TestKeyF)` to an initial team, excludes that team from future random selection, and then moves subranges with three random shard IDs. It checks that `[TestKeyD, TestKeyF)` on the reused team has `id` and `desiredId` equal to `sh0`, that adjacent ranges expose distinct desired IDs, and that a subsequent move of `[TestKeyB, TestKeyC)` changes `desiredId` while preserving the old `id` until the move is complete. Between moves it calls `checkpointRestore` on selected ranges.

`checkpointRestore` writes checkpoint metadata under system keys, fetches metadata at the committed version, downloads checkpoint data into temporary directories, marks checkpoint records deleting, restores into a fresh local RocksDB store, reads `normalKeys`, and compares restored key/value pairs against the workload oracle for the requested restore ranges. `moveShard` takes the move-keys lock, cancels existing data moves with `cleanUpDataMove`, selects destination UIDs subject to include/exclude sets, and invokes `moveKeys` with separate parallelism locks.

Persistent cluster state includes test keys, data-move metadata, checkpoint metadata, DD mode, and local temporary checkpoint/RocksDB directories. Risks are broad: DD is disabled and must be restored, failures inside cleanup could leave mode or directories dirty, temporary path collisions are possible but randomized, physical/logical selection is probabilistic, and the workload assumes storage team size 1 and enough available storage servers. Some helper methods (`writeAndVerify`, `readAndVerify`) are present but unused in the main path.

Integration points are DD move orchestration, physical shard metadata, checkpoint fetch/restore, storage server shard-state RPCs, RocksDB KV-store restore, and simulator knobs such as `DD_PHYSICAL_SHARD_MOVE_PROBABILITY`. Test signals are dense `ASSERT` checks on shard metadata, checkpoint contents, and final data validation; `check` returns the `pass` flag, which is set false only by `validationFailed` in unused read helpers, so most failures are assertion-driven.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/PhysicalShardMove.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/Ping.cpp -->
## sources/storage-engines/foundationdb/fdbserver/workloads/Ping.cpp

`PingWorkload` measures request/reply latency and payload broadcast behavior between tester clients or workers. It defines a serializable `PingWorkloadInterface` containing a `RequestStream<LoadedPingRequest>`, optionally persists each client interface in the database, and runs pingers plus a local ponger for the configured duration.

Important APIs are `LoadedPingRequest`, `LoadedReply`, `RequestStream`, `BinaryWriter`/`BinaryReader`, `getWorkers`, `ActorCollection`, `poisson`, `PerfIntCounter`, and `PerfDoubleCounter`. Options select worker pings, registered tester-interface pings, broadcast mode, payload sizes, actor count, logging, and parallel broadcast behavior.

Setup persists the client interface under `Ping/Client/<clientId>` unless pinging workers or registration is disabled. Normal `pinger` fetches all persisted interfaces, starts `actorCount` poisson-paced actors, chooses random peer streams, sends `LoadedPingRequest`, optionally requests a payload reply, and records message count, total latency, and max latency. `workerPinger` uses worker `debugPing` streams instead. `payloadSender` periodically spawns a broadcast `payloadPinger` through an actor collection, sending the same ping ID to every endpoint and waiting for all replies. `ponger` continuously receives local requests and replies with optional payload.

State persists only interface records in normal keyspace. Runtime state is latency counters and payload buffers. Risks include divide-by-zero in average latency metrics if no messages complete, indefinite actors being stopped only by outer timeout, database-stored interfaces becoming stale if registration fails, and broadcast mode not counting messages in the same metric path. `registerInterface=false` with non-worker peer pinging would leave `fetchInterfaces` unable to find records.

Integration points are tester clients, worker debug ping endpoints, FDB serialization of interfaces, and simulation networking. Test signals are `Messages`, average latency, and max latency metrics; `check` always returns true, so workload failures surface through actor errors or missing interface assertions/retries rather than explicit validation.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/Ping.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/PrivateEndpoints.cpp -->
## sources/storage-engines/foundationdb/fdbserver/workloads/PrivateEndpoints.cpp

`PrivateEndpoints` is an untrusted-mode workload that verifies private proxy endpoints reject unauthorized client calls. It randomly chooses GRV or commit proxy request streams that should not be callable by ordinary clients, sends default requests through either `tryGetReply` or `getReply`, and treats `unauthorized_attempt` as success.

Important APIs are `ClientDBInfo`, `GrvProxyInterface`, `CommitProxyInterface`, `RequestStream<RT, false>`, `throwErrorOr`, `error_code_unauthorized_attempt`, and `error_code_request_maybe_delivered`. Template helpers `getInterface`, `assumeFailure`, and `addTestFor` build a vector of test functions for supported private channels.

At construction, the workload adds tests for GRV proxy `waitFailure` and `getHealthMetrics`, plus commit proxy `waitFailure` and `exclusionSafetyCheckReq`. `_start` waits `startAfter`, then loops for `runFor`, selecting a random test function, racing it against the end timer, incrementing `numSuccesses` for completed expected failures, and sleeping 0.2 seconds between attempts.

There is no durable state. Runtime state is `success`, `numSuccesses`, timing options, and the function vector. Risks include default-constructed request payloads not being valid for every possible private endpoint, empty proxy lists causing the test to wait on `clientInfo->onChange`, and treating `request_maybe_delivered` as success because connection failures can mask authorization. `success` is never set false; unexpected errors assert in `_start`.

Integration points are client DB info propagation, private endpoint authorization, proxy interfaces, and the untrusted workload factory (`UntrustedMode::True`). Test signals are the `Successes` metric and trace events for expected unauthorized or maybe-delivered outcomes. A wrong error code logs `WrongErrorCode` but does not directly set failure before `assumeFailure` returns, making trace review important.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/PrivateEndpoints.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/ProtocolVersion.cpp -->
## sources/storage-engines/foundationdb/fdbserver/workloads/ProtocolVersion.cpp

`ProtocolVersionWorkload` checks simulator support for querying protocol information from a process running a different protocol version. It finds any simulator process whose `protocolVersion` differs from `currentProtocolVersion()`, sends a well-known `ProtocolInfoRequest`, and asserts the reply version differs from the current network protocol version.

Important APIs are `g_simulator->getAllProcesses`, `ISimulator::ProcessInfo::protocolVersion`, `currentProtocolVersion`, `Endpoint::wellKnown`, `WLTOKEN_PROTOCOL_INFO`, `RequestStream<ProtocolInfoRequest>`, and `retryBrokenPromise`.

The workload has no setup and no persistent state. `start` is the entire test: find the mixed-version process, assert one exists, build a request stream from that process address set, await the protocol info reply, and assert version mismatch. `check` returns true.

Risks are environmental: the workload requires a mixed-protocol simulation and will assert if none is present. It does not check process liveness beyond using `retryBrokenPromise`, and it validates only version inequality, not exact compatibility metadata. Integration is with simulator process metadata and the RPC well-known protocol-info endpoint. Test signals are the two assertions in `start`.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/ProtocolVersion.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/PubSubMultiples.cpp -->
## sources/storage-engines/foundationdb/fdbserver/workloads/PubSubMultiples.cpp

`PubSubMultiplesWorkload` appears to be a scaffold for exercising many pub/sub feeds and inboxes per actor, but only node creation is implemented. It creates `inboxesPerActor` feeds and inboxes for each actor and stores their numeric IDs under deterministic `/PSM/feeds/<offset>` and `/PSM/inbox/<offset>` keys.

Important APIs are `PubSub::createFeed`, `PubSub::createInbox`, `Transaction`, `PerfIntCounter`, and tester actor scheduling. `keyForFeed`, `keyForInbox`, and `valueForUInt` define the persisted mapping from actor/client offsets to pub/sub object IDs.

Setup calls `createNodes`, which starts one `createNodeSwath` per actor on cloned databases. Each swath creates feed/inbox pairs and commits their IDs in a retry loop. `start` launches `startTests` in a local future and returns `delay(testDuration)`. `startTests` waits for `createSubscriptions` futures and starts `messageSender`, but both are stubs returning `Void`; no subscriptions or messages are actually created.

Persistent state is the created pub/sub metadata plus the `/PSM` mapping keys. Runtime message metrics are defined but never incremented. Risks are mostly incompleteness: offset calculation uses `clientId * clientCount * actorCount * inboxesPerActor`, which looks suspicious for multi-client uniqueness, and the workload reports success despite no validation. It may still serve as a setup stressor for pub/sub object creation.

Integration points are the `pubsub.h` helper layer and FDB transactions. Test signals are limited to successful setup and the `PSMNodesCreated` trace; `check` returns true and `Messages` remains zero unless future code fills in sender/subscriber behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/PubSubMultiples.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/QueuePush.cpp -->
## sources/storage-engines/foundationdb/fdbserver/workloads/QueuePush.cpp

`QueuePushWorkload` is a write-throughput workload that repeatedly finds one end of a synthetic key queue and inserts a new key beyond it. It can push forward from `0000000000000001` toward `9999999900000001` or backward from the end toward the start, measuring GRV and commit latency with `DDSketch`.

Important APIs are `Transaction`, `getReadVersion`, `getKey(lastLessThan/firstGreaterThan)`, snapshot reads, `PerfIntCounter`, `DDSketch`, and key formatting/parsing helpers. `keyForIndex(base, offset)` produces fixed 16-byte hex keys. `valuesForKey` parses the two 8-hex-digit components back into integers.

`start` launches `actorCount` write clients and times them out after `testDuration`. Each `writeClient` obtains a read version, snapshot-reads the current queue edge, defaults to the configured boundary if none exists, parses the edge key, and writes a new key whose base is adjusted by the parsed offset and whose offset is random in `[1,1000)`. It then commits, records commit latency, and increments transaction counters; retry loops call `tr.onError` and increment retries.

State persists generated queue keys and fixed-size random values in normal keyspace. Risks include hot contention on the queue edge, `valuesForKey` throwing if non-conforming keys appear near the selected boundaries, no setup clearing pre-existing keys, and possible integer movement beyond intended boundaries over long runs. Metrics divide by configured duration rather than observed runtime.

Integration points are key selector semantics, snapshot reads, commit path, and latency sketches. Test signals are throughput, bytes/sec, transaction/retry counts, and GRV/commit latency percentiles. `check` always returns true, so it is performance-oriented rather than correctness-validating.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/QueuePush.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/RYWDisable.cpp -->
## sources/storage-engines/foundationdb/fdbserver/workloads/RYWDisable.cpp

`RYWDisableWorkload` verifies that `READ_YOUR_WRITES_DISABLE` cannot be set after a `ReadYourWritesTransaction` has performed operations that require the RYW layer. It runs on client 0 for `testDuration`, choosing random operation prefixes before attempting to disable RYW and checking whether that should succeed.

Important APIs are `ReadYourWritesTransaction`, `FDBTransactionOptions::READ_YOUR_WRITES_DISABLE`, `error_code_client_invalid_operation`, Flow retry handling, and the workload's `keyForIndex` generator. The generated keys are fixed length and ordered by embedding a double-derived index.

The `_start` loop creates a RYW transaction, randomly performs one of: `set`, asynchronous `get` without waiting, awaited `get`, or no-op. For the first three cases it expects setting `READ_YOUR_WRITES_DISABLE` to throw `client_invalid_operation`; for no-op it expects success. It then delays, checks duration, optionally resets the transaction, and continues.

No data is committed, so persistence is minimal. Runtime state is only timing and generated transaction operations. Risks include the no-wait get case depending on client-side state being marked immediately after issuing the future, and the workload not tracking the `clients` vector it checks. It deliberately does not validate database contents.

Integration points are NativeAPI transaction option validation and RYW transaction internal state. Test signals are assertions around expected option-setting behavior; `check` returns false only if any stored client future is in error, but the main path returns directly from `_start`.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/RYWDisable.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/RYWPerformance.cpp -->
## sources/storage-engines/foundationdb/fdbserver/workloads/RYWPerformance.cpp

`RYWPerformanceWorkload` is a microbenchmark for `ReadYourWritesTransaction` cache behavior. It loads `nodes` keys with `"bar"`, then prints operations/sec for repeated gets, sequential gets, range reads, and interleaved set/get patterns after filling the RYW cache in fourteen different ways.

Important APIs are `ReadYourWritesTransaction`, single-key `get`, `getRange`, `set`, `clear`, range clear, `waitForAll`, and the same monotonic `keyForIndex` style used by other tester workloads. `fillCache(type)` is the core matrix: pure sets, parallel gets, get-then-set combinations, full range reads followed by sets/clears, and many overlapping range reads followed by mutations.

Setup runs on client 0 and writes the baseline keys in one transaction. `_start` then serially executes `test_get_single` for cache types 0-13, `test_get_many_sequential` for 0-13, `test_get_range_basic` for 4-13, and `test_interleaved_sets_gets` for 0-13. Each test creates a RYW transaction, fills its cache, times the repeated operation loop with `timer()`, prints a throughput value to stderr, and returns without committing.

Persistent state is only the setup keyspace. The benchmark mutates local RYW state heavily but does not commit benchmark changes. Risks include printing rather than exporting structured metrics, very large `nodes` causing huge in-memory future vectors, no validation of results, and retrying an entire cache fill on error without resetting all local timing context. Because `check` returns true and metrics are empty, this file is useful mainly for ad hoc performance output.

Integration points are RYW cache algorithms, key-range read merging, mutation overlay behavior, and tester setup. Test signals are stderr rows of throughput values and assertion failures only from lower-level APIs.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/RYWPerformance.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/RandomClogging.cpp -->
## sources/storage-engines/foundationdb/fdbserver/workloads/RandomClogging.cpp

`RandomCloggingWorkload` is a simulation-only failure injection workload that intermittently clogs network interfaces and pairs of simulator processes. It can run once or iteratively, either with simple random clogs or a "swizzle" mode that clogs a random half of machines with staggered start/end times.

Important APIs are `FailureInjectionWorkload`, `ISimulator::clogInterface`, `ISimulator::clogPair`, `g_simulator->getAllProcesses`, `poisson`, `reportErrors`, and failure-injector registration. `shouldInject` gives eligible database workloads a decreasing random chance of receiving this injection; `initFailureInjectionMode` randomizes scale, clogginess, swizzle mode, and iteration.

`startImpl` runs until `maxRunDuration` or a single `testDuration` depending on `iterate`. `clogClient` repeatedly chooses a random process, computes exponentially distributed clog durations scaled by `scale`, clamps them to remaining workload time, and schedules interface and pair clogs. `swizzleClogClient` chooses many processes, assigns random starts and ends within a clog window, adds extra pair clogs, and schedules delayed interface clogs.

No FDB state is persisted. Runtime state is simulator network impairment. Risks include asynchronous `doClog` futures being launched without awaiting inside the loops, short or zero clogs near workload end, and broad interactions with other failure workloads. It only runs on client 0 in simulation.

Integration points are the simulator fault model and the failure injection factory. Test signals are indirect: the workload returns true from `check`, so value comes from whether the primary workload survives under injected network stalls and whether `reportErrors` catches actor errors.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/RandomClogging.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/RandomMoveKeys.cpp -->
## sources/storage-engines/foundationdb/fdbserver/workloads/RandomMoveKeys.cpp

`MoveKeysWorkload` (`NAME = "RandomMoveKeys"`) is a simulation failure injection workload that disables DD and repeatedly issues random `moveKeys` operations over random key ranges to random storage teams. It stresses relocation, cancellation of overlapping relocations, and data distribution recovery after manual damage.

Important APIs and types include `FailureInjectionWorkload`, `DatabaseConfiguration`, `configKeys`, `setDDMode`, `takeMoveKeysLock`, `getStorageServers`, `MoveKeysParams`, `moveKeys`, `KeyRangeMap`, `KeyRangeActorMap`, `newDataMoveId`, `DataMoveType`, `DataMovementReason`, and locality fields on `StorageServerInterface`.

`start` reads configuration from system keys to learn storage team size, disables DD, runs `worker` for `testDuration`, and restores the old DD mode. `worker` takes the move-keys lock, filters duplicate-address and TSS storage servers, then loops at a poisson rate. For each random range it selects a random team with unique zones/data halls, cancels in-flight actors affected by the inserted range, updates an in-flight range map, and starts `doMoveKeys` for every affected range. `doMoveKeys` builds logical or physical data movement parameters depending on `SHARD_ENCODE_LOCATION_METADATA` and the physical move probability knob.

State and persistence include data-move metadata, shard location changes, and DD mode. The workload intentionally perturbs real shard placement and relies on restoring DD and a delayed `check` to let the database heal. Risks include no support for multi-region usable regions, operation failures when too few unique machines exist, broad overlap cancellation, and DD mode restoration being skipped if an unexpected error escapes before the final set mode.

Integration points are DD locking, storage team selection, physical/logical shard movement, failure injection selection, and simulator-only operation. Test signals are relocation trace intervals and downstream workload/database health after the delayed `check`, which returns true after `testDuration / 2`.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/RandomMoveKeys.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/RandomRangeLock.cpp -->
## sources/storage-engines/foundationdb/fdbserver/workloads/RandomRangeLock.cpp

`RandomRangeLockWorkload` is a failure injection workload for exclusive read locks on random ranges. It registers randomly duplicated owner names, attempts to lock arbitrary byte ranges after random delays, holds successful locks briefly, unlocks them, and finally asserts that no locks remain for the workload's owner prefix.

Important APIs are `registerRangeLockOwner`, `getRangeLockOwner`, `takeExclusiveReadLockOnRange`, `releaseExclusiveReadLockOnRange`, `findExclusiveReadLockOnRange`, `RangeLockState`, and failure-injector hooks. The no-options constructor only enables injection when read range locks are enabled and incompatible version-vector/private mutation features are off; the options constructor enables in simulation on client 0.

Each `lockActor` chooses a duration and start delay, constructs an owner name from a prefix plus a random actor index, registers that owner, delays, generates a random range from random byte strings, and attempts to lock. `range_lock_failed` is expected for ranges beyond `normalKeys.end`; `range_lock_reject` is acceptable for conflicts. It then waits, attempts unlock, and accepts corresponding failed/rejected errors. `start` runs `lockActorCount` actors concurrently and verifies every owner prefix slot has no remaining locks in `normalKeys`.

State persists range lock owner and lock metadata in system keys. Runtime state includes randomized owners and lock ranges. Risks include duplicate owner names intentionally racing, random ranges outside normal keyspace, feature gating differing between constructors, and the workload's final cleanup only checking owner names in the configured prefix range. Failed registration or actor cancellation propagates.

Integration points are the range lock subsystem, system metadata, failure injection scheduler, and simulator. Test signals are assertions on owner presence, expected error codes, range bounds for failed locks, and final empty lock searches. `check` returns true after execution.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/RandomRangeLock.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/RandomSelector.cpp -->
## sources/storage-engines/foundationdb/fdbserver/workloads/RandomSelector.cpp

`RandomSelectorWorkload` is a RYW correctness workload comparing a `ReadYourWritesTransaction` view against a regular transaction-maintained mirror. For each client it keeps two key prefixes: `b/` is mutated through RYW and `d/` is mutated through committed regular transactions. Reads and selector-based range reads from the RYW transaction are compared to reads from the mirror prefix.

Important APIs are `ReadYourWritesTransaction`, `Transaction`, `KeySelectorRef`, `getRange` with forward/reverse selectors and limits, single-key get/set/clear, range clear, many atomic mutation types (`AddValue`, `AppendIfFits`, `And`, `Or`, `Xor`, `Max`, `Min`, `ByteMin`, `ByteMax`), and commit-unknown-result handling via random marker keys under `z/`.

Setup seeds guard keys under `a/`, `c/`, and `e/` for each client. The main client loop first clears and repopulates both mutable prefixes with identical random values. It then runs a random number of operations against the RYW transaction while applying equivalent committed operations to the mirror. Operation types include sets, clears, range clears, gets, atomic ops, and random selector range reads with random equality flags, offsets, limits, byte-limit variable preparation, and direction. Mismatches log detailed `RanSelTestFailure` events and set `fail`. After committing the RYW transaction, it reads both prefixes and compares final values.

State persists per-client prefixed test data. The mirror side commits throughout the operation sequence, while RYW changes are local until final commit, so commit errors and unknown results require careful handling. Risks include an apparent option typo where `maxOperationsPerTransaction` reads `"minOperationsPerTransaction"` instead of its own key, unused `randomByteLimit` in `getRange`, retries incrementing on successful transactions as written at the loop tail, and final key comparison focusing values rather than transformed key prefixes.

Integration points are the RYW mutation overlay, key selectors, atomic mutation semantics, conflict/retry behavior, and transaction error handling. Test signals are the `fail` flag returned by `check`, transaction/retry metrics, and detailed trace logs for mismatched reads or final contents.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/RandomSelector.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/RangeLock.cpp -->
## sources/storage-engines/foundationdb/fdbserver/workloads/RangeLock.cpp

`RangeLocking` is a deterministic client workload for the range lock subsystem. It registers a test owner, performs random lock/unlock and key-value operations, maintains in-memory models of locked ranges and visible KVS state, compares both models against database state, then tests releasing locks by owner across many owners.

Important APIs and types include `registerRangeLockOwner`, `takeExclusiveReadLockOnRange`, `releaseExclusiveReadLockOnRange`, `releaseExclusiveReadLockByUser`, `findExclusiveReadLockOnRange`, `RangeLockState`, `KeyRangeMap<bool>`, `coalesceRangeList`, and `FDBTransactionOptions::LOCK_AWARE`. `KVOperation` and `LockRangeOperation` record the random operations applied during each iteration.

The workload disables `RandomRangeLock` because both would race on lock state. `complexTest` loops up to 100 iterations, randomly updating locks and then DB keys. `updateLockMapWithRandomOperation` applies lock/unlock requests and records only accepted operations. `updateDBWithRandomOperations` tries random sets or range clears and accepts `transaction_rejected_range_locked` as expected. The memory model applies KV operations only if they do not intersect a locked range. `checkLockCorrectness` compares coalesced DB locks to the in-memory lock map; `checkKVCorrectness` reads normal keys with `LOCK_AWARE` and compares to the in-memory map. At the end it releases all locks for the main owner and asserts none remain.

`testUnlockByUser` registers 100 owners, tries to lock up to two random ranges each, randomly chooses users to unlock, calls `releaseExclusiveReadLockByUser`, and verifies unlocked users have no locks while other users still have exactly their coalesced lock ranges.

Persistent state includes lock owner metadata, lock records, and test keys in the small digit keyspace. Risks include `check` returning true regardless of the `pass`/`shouldExit` model flags, random lock conflicts causing skipped operations, reliance on normal keyspace filtering, and broad cleanup only for owners created in the workload. The workload intentionally uses `LOCK_AWARE` reads for validation so locks do not block model inspection.

Integration points are range lock metadata, transaction rejection for locked ranges, audit utilities, and management/system data. Test signals are assertions, `shouldExit` being set on mismatches, detailed `RangeLockWorkLoadHistory` trace events, and final empty-lock assertions.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/RangeLock.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/ReadAfterWrite.cpp -->
## sources/storage-engines/foundationdb/fdbserver/workloads/ReadAfterWrite.cpp

`ReadAfterWriteWorkload` measures storage propagation delay: the extra time for a committed version to become readable from storage compared with reading an already-established read version. It is a `KVWorkload`, so it uses the common random keyspace helpers without mutating logical state.

Important APIs are `KVWorkload::getRandomKey`, `Transaction::getReadVersion`, `Transaction::setVersion`, `commit`, `DDSketch`, and `error_code_future_version`. The helper `latencyOfRead` retries `future_version` until the storage server can serve the requested version, but rethrows other errors.

Each benchmark iteration chooses a random key, gets a read version in `writeTr`, reads the key to ensure the read version is present on a storage server, writes back the same value or clears the absent key, and commits. It then reads the same key concurrently at the original read version and at the commit version, subtracts baseline read latency from after-write latency, clamps at zero, and records the propagation sample.

State persistence is intentionally neutral: committing the same value or clear should not change user-visible contents, allowing pairing with other workloads. Risks include the write transaction still creating conflict/commit work, repeated `future_version` retry spinning without delay, and metrics depending on the baseline and after-write reads being comparable. The `benchmark` future is not awaited directly; `start` keeps it alive by local future until `delay(testDuration)` returns and cancellation occurs.

Integration points are storage read-version availability, log-to-storage propagation, and KV workload key generation. Test signals are latency metrics: mean, median, 90%, 99%, and max propagation latency. `check` returns true.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/ReadAfterWrite.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/ReadHotDetection.cpp -->
## sources/storage-engines/foundationdb/fdbserver/workloads/ReadHotDetection.cpp

`ReadHotDetectionWorkload` creates a small keyset with one selected large hot key, drives read traffic toward that key, and checks whether `Database::getReadHotRanges` eventually reports a hot range containing it. It is a user-visible validation of read-hot metrics and storage metrics plumbing.

Important APIs are `ReadYourWritesTransaction`, `Database::getStorageMetrics`, `Database::getReadHotRanges`, `ReadHotRangeWithMetrics`, `DDSketch` include support, `poisson`, and random value generation. Options set duration, transactions per second, actors per client, and key count.

Setup writes `keyCount` keys named `testkey%08x`; the selected `readKey` always gets a 100 KB value and other keys get either large or small random values. `start` launches poisson-paced readers, with roughly 60% of actors reading the hot key and others reading random keys, and on client 0 starts `_check`. `_check` repeatedly retrieves storage metrics for the whole keyspace, calls `getReadHotRanges`, and sets `passed=true` once any returned range contains `readKey`; otherwise it sets `passed=false` and retries on transaction errors.

Persistent state is the test key range and large values. Runtime state includes reader futures, the checker future, `wholeRange`, and `passed`. A significant risk is that `passed` is not initialized in the constructor; if client 0 reaches `check` before `_check` sets it, result is undefined. The checker also uses `tr.onError(err)` even though its main calls are on `cx`, so invalid error handling paths should be reviewed.

Integration points are storage metrics, read-hot range detection, RYW read path, and workload traffic shaping. Test signals are `passed` on client 0 and trace comments left in the code for debugging; no metrics are exported.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/ReadHotDetection.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/ReadWrite.cpp -->
## sources/storage-engines/foundationdb/fdbserver/workloads/ReadWrite.cpp

`ReadWrite.cpp` implements the common setup/metrics declared in `ReadWriteWorkload.h` and the concrete `ReadWriteWorkload`, FoundationDB's configurable mixed read/write performance workload. It can bulk-load data, run many actors at a target transaction rate, vary read/write mix, use normal or RYW transactions, apply transaction tags and read priorities, exercise hot-key patterns, and report detailed latency/throughput metrics.

Important APIs and types include `bulkSetup`, `DDSketch`, `TDMetric` handles, `TraceBatchDumpRequest`, `ReadYourWritesTransaction`, `Transaction`, `FDBTransactionOptions` for priority, read cache, tags, and read priority, `ReadType`, poisson scheduling, and `PerfMetric`. Static helpers `getNextRV` and `getInconsistentReadVersion` implement optional stale/inconsistent read-version reuse.

`ReadWriteCommonImpl::setup` calls `bulkSetup` unless disabled and records load time plus optional insertion rates. `tracePeriodically` emits rolling trace events and appends periodic metrics when the interval is inside the configured measurement window. `ReadWriteCommon::check` clears clients, adjusts metrics duration when workers are not cancelled at duration, dumps local trace batches, and on client 0 asks workers to dump trace batches too. `getMetrics` exports measured duration, transaction/operation rates, row and byte rates, load time, retries, periodic metrics, and insertion-rate checkpoints.

`ReadWriteWorkload` extends the common class with transaction-shape options. `_start` warms key server caches with one read and `warmRange`, optionally starts periodic logging, records `clientBegin`, and launches actors using either `Transaction` or `ReadYourWritesTransaction`. Each actor uses poisson pacing, optional ramp-up/ramp-down concurrency, optional transaction-type sweeps, random or adjacent read/write keys, optional range reads or dependent reads, optional extra conflict ranges, and optional hot-key forcing. It records GRV, row-read, full-read, commit, and total transaction latencies, logs success/failure TD metrics, handles `tag_throttled`, retries through `onError`, and increments A/B transaction counters inside the measurement window.

State persists the bulk-loaded KV dataset and any writes generated during the run. In-memory state includes sketches, counters, periodic metrics, global static read-version cache for inconsistent reads, and optional worker futures left alive until `check`. Risks include very broad configuration surface, global `nextRV/lastRV` shared across workload instances, subtle A/B naming inversion (`aTransaction` selected with `random01() > alpha`), metrics cleared periodically when logging is enabled, and correctness being assumed rather than checked for read values. `cancelWorkersAtDuration=false` requires `check` to clean up.

Integration points are bulk setup, NativeAPI read/write paths, server-side read cache, transaction tagging/throttling, trace batching, worker interfaces, and KVWorkload key/value generation. Test signals are extensive performance metrics plus TDMetric events for successful transactions, failed transactions, and reads; `check` mainly validates worker trace dump completion.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/ReadWrite.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/ReadWriteWorkload.h -->
## sources/storage-engines/foundationdb/fdbserver/workloads/ReadWriteWorkload.h

`ReadWriteWorkload.h` declares the metric descriptors and shared `ReadWriteCommon` base used by `ReadWrite.cpp`. It centralizes option parsing, metric state, key/value generation hooks from `KVWorkload`, setup/check/metrics declarations, and helper methods for latency logging and measurement-window filtering.

Important APIs and types are `KVWorkload`, `DDSketch`, `TDMetric` descriptors/handles, `PerfIntCounter`, `PerfMetric`, `boost::lexical_cast`, `Standalone<StringRef>`, and Flow futures. The descriptors define structured TD metrics for successful transactions (`totalLatency`, `startLatency`, `commitLatency`, `retries`), failed transactions (`startLatency`, `errorCode`), and individual reads (`readLatency`).

The constructor parses common options: duration, target TPS, allowed latency-derived actor count, reads/writes per A/B transaction, alpha, node-prefix key widening, measurement start/duration, edge-discard behavior, warming and insert throttles, debug trace windows, read latency logging, periodic interval, cancellation behavior, RYW mode, setup enablement, and insertion-count checkpoints. It also validates that `keyForIndex` remains monotonic for random key pairs.

State is mostly runtime metric state and workload configuration. Persistent behavior is delegated to `setup`, implemented in `ReadWrite.cpp` through `bulkSetup`; `operator()(uint64_t)` produces `KeyValueRef` pairs for bulk loading. Risks include the header's broad mutable public state, dependence on implementation in the `.cpp`, and option parsing that can silently ignore invalid insertion-count strings.

Integration points are concrete read/write workloads, bulk setup, Flow metric descriptors, and tester metric collection. Test signals are not emitted directly by the header, but it defines the counters, sketches, event metrics, and `shouldRecord` window used by the implementation.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/ReadWriteWorkload.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/RemoveServersSafely.cpp -->
## sources/storage-engines/foundationdb/fdbserver/workloads/RemoveServersSafely.cpp

`RemoveServersSafelyWorkload` is a simulation-only workload that exercises safe exclusion and removal of random processes or machines. It chooses two kill sets, filters them to what the simulator says can be safely killed, excludes them through management APIs or locality exclusions, optionally marks some exclusions as failed, changes coordinators, then kills or clears the corresponding simulator processes/machines and includes everything again.

Important APIs and types include `AddressExclusion`, `includeServers`, `excludeServers`, `includeLocalities`, `excludeLocalities`, `checkSafeExclusions`, `checkForExcludingServers`, `changeQuorum`, `autoQuorumChange`, `getConnectionString`, simulator `ProcessInfo`, `killZone`, `rebootProcess`, `canKillProcesses`, `fdbSimulationPolicyState`, and `getWorkers`.

Setup runs only on client 0 in simulation. It enumerates available server processes, maps machine IPs to process addresses and locality zone IDs, randomly chooses two process-address sets, optionally expands selections to whole machines, disables swap to selected machines, and prevents log set kills in simulation policy. `start` waits a random delay and calls `workloadMain`.

`workloadMain` updates process IDs from worker localities, filters `toKill1` through `protectServers`, excludes it, attempts `removeAndKill` with a short timeout, reincludes on failure or buggify, then filters and processes `toKill2` with a longer timeout and expected success. `removeAndKill` first includes all, optionally chooses a coordinator to include in failed exclusions under buggify, repeatedly runs safety checks for random failed subsets, swaps coordinator membership to keep kill-set size bounded, applies failed and non-failed exclusions either by server or by locality, waits for exclusion completion while monitoring locality changes, adjusts coordinator quorum, and calls `killAddresses`. `killAddresses` either reboots/deletes individual processes or kills/clears whole zones depending on `killProcesses` and buggify.

State and persistence span management exclusion metadata, locality exclusion metadata, coordinator configuration, simulator process flags, disabled swap targets, and process locality process IDs. Risks include high complexity, long timeouts, interactions with protected addresses, reliance on simulator availability calculations, locality changes during process reboot requiring a background monitor, and `check` returning true regardless of whether cleanup fully restored all simulator-side flags. The constructor mutates global simulation policy by disabling log set kills.

Integration points are management exclusion safety, locality exclusion, coordinator changes, simulator kill/reboot/delete behavior, worker locality process IDs, and recovery after removals. Test signals are extensive `RemoveAndKill` trace events and `reportErrors(timeoutError(...), "RemoveServersSafelyError")` for the second kill set; the first kill set may time out without failing by design.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/RemoveServersSafely.cpp -->
