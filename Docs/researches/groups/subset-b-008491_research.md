# subset-b-008491 research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/GetMappedRange.cpp -->
# sources/storage-engines/foundationdb/fdbserver/workloads/GetMappedRange.cpp

## Purpose
Tester workload for the client `getMappedRange` API. It builds a synthetic primary-record plus secondary-index layout and validates that mapped range reads return index entries together with the corresponding record lookups or record subranges, including byte-limit, continuation, conflict, and read-your-writes behavior.

## Important APIs, types, and functions
`GetMappedRangeWorkload` derives from `ApiWorkload` and chooses either native or read-your-writes transaction wrappers. Helpers generate tuple-encoded `recordKey`, split `recordKey(i, split)`, `indexEntryKey`, values, and mapper tuples. Core actors are `fillInRecords`, `scanMappedRangeWithLimits`, `scanMappedRange`, `testSerializableConflicts`, `testRYW`, `reportMetric`, and `_start`. Validation inspects `MappedRangeResult`, `MappedKeyValueRef`, `GetValueReqAndResultRef`, and `GetRangeReqAndResultRef`.

## Control flow
Only client 0 runs. Setup chooses transaction type, then `_start` inserts 500 records plus index entries. Native transactions use snapshot reads; read-your-writes transactions sometimes branch into explicit serializable-conflict or RYW-error checks. The happy path scans index entries from record 10 through 489 with randomized byte limits, checks every mapped record, advances with `firstGreaterThan(result.back().key)` while `more` is set, and runs a small-request stress loop while status metrics are checked.

## State and persistence behavior
The workload persists tuple keys under the user prefix `("prefix","RECORD",...)` and `("prefix","INDEX",...)`. It also mutates the server knob `STRICTLY_ENFORCE_BYTE_LIMIT` for the scan and restores it afterward. Conflict tests deliberately write either index keys or mapped record keys before commit. No cleanup is done, so test data remains in the simulated database.

## Dependencies and integration points
Depends on tuple encoding, `ApiWorkload` transaction factories, FoundationDB transaction wrapper APIs, commit proxy mapped-range implementation, `StatusClient::statusFetcher`, client/server knobs, and Flow coroutine utilities. It disables Attrition because queue and conflict expectations are sensitive to heavy failure injection.

## Risks and test signals
Risks include global `recordSize`/`indexSize` assumptions from record 0, continued reliance on split-record shape, transient mapped subrange `more` requiring retry, and expected fallback errors depending on quick-get knobs. Test signals are ASSERTs on result ordering and values, result size versus row and byte limits, expected `not_committed`/`get_mapped_range_reads_your_writes`/mapper errors, and storage `query_queue_max` remaining below `queueMaxLength`.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/GetMappedRange.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/GetRangeStream.cpp -->
# sources/storage-engines/foundationdb/fdbserver/workloads/GetRangeStream.cpp

## Purpose
Small performance and API comparison workload for reading a key range either through repeated `getRange` calls or through the streaming `getRangeStream` interface.

## Important APIs, types, and functions
`GetRangeStream` derives from `TestWorkload` and exposes options `useGetRange`, `begin`, `end`, and `printKVPairs`. It records `BytesRead`. `fdbClientGetRange` uses `Transaction::getRange` with `CLIENT_KNOBS->REPLY_BYTE_LIMIT`; `fdbClientStream` uses `Transaction::getRangeStream` into a `PromiseStream<Standalone<RangeResultRef>>`; `logThroughput` prints one-second byte rates.

## Control flow
Only client 0 runs. The workload starts a throughput logger and repeatedly reads from `begin` to `end`. The getRange mode advances `next` to `keyAfter(range.back().key)` while `range.more` is true. The stream mode consumes range batches from the promise stream until `end_of_stream`, updating `next` after non-empty chunks and retrying via `tx.onError` for other transaction errors.

## State and persistence behavior
The workload does not write database state. Runtime state is limited to the current continuation key and the byte counter. It reuses a single transaction object across retries, relying on `onError` reset semantics.

## Dependencies and integration points
Integrates with native API range reads, streaming range plumbing, Flow `PromiseStream`, tester workload registration, and normal key boundaries from tester helpers.

## Risks and test signals
Because `check` always returns true, this is primarily an operational metric workload. Risks are infinite streaming loops if stream termination changes, noisy stdout when `printKVPairs` is true, and stale transaction behavior around retries. The main signal is the `BytesRead` perf metric plus optional throughput prints.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/GetRangeStream.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/HTTPKeyValueStore.cpp -->
# sources/storage-engines/foundationdb/fdbserver/workloads/HTTPKeyValueStore.cpp

## Purpose
Simulation workload that tests the Flow HTTP client and simulated HTTP server path with a simple per-client key-value service. It exercises name resolution, connection reuse, request retries, header/content validation, and response integrity.

## Important APIs, types, and functions
`SimHTTPKVStore` stores string data and per-client sequence numbers. `httpKVRequestCallback`, `httpKVProcessPut`, and `httpKVProcessGet` implement the server contract. `KeyValueRequestHandler` adapts the store to `HTTP::IRequestHandler`. `HTTPKeyValueStoreWorkload` uses `INetworkConnections`, `HTTP::doRequest`, `PacketWriter`, `UnsentPacketQueue`, `IncomingResponse`, and counters for gets, puts, connects, and failed connects.

## Control flow
Client 0 registers a simulated server at `httpkvstore:80`; every client then preloads `nodeCount` keys through HTTP PUT. `doKVRequest` creates or reconnects a connection, optionally manually resolves endpoints, builds headers (`Key`, `ClientID`, `UID`, `SeqNo`), sends PUT or GET, validates echoed headers, and retries only timeout/connect/lookup failures. The start phase runs random GET/PUT traffic at a Poisson rate; check cancels the client and reads all keys back.

## State and persistence behavior
No FoundationDB keys are used. Persistent test state is the process-global `globalKVStore` map inside simulation and each workload instance's `myData` mirror plus `activePut`. Sequence numbers suppress out-of-order retransmits, and `activePut` permits a check to accept either the old local value or the in-flight PUT value if cancellation interrupted a write.

## Dependencies and integration points
Requires simulated networking and `g_simulator->registerSimHTTPServer`. It integrates with Flow HTTP serialization, connection handshake and close paths, DNS resolution, MD5 response headers, and tester workload metrics.

## Risks and test signals
Risks include strict header-count assertions, `opsPerSecond` accidentally reading the `nodeCount` option, process-global state coupling across handler clones, and no server-side missing-key handling beyond ASSERT. Signals are ASSERTs on HTTP codes, content length, echoed headers, MD5-bearing GET responses, local mirror consistency, and perf counters for request/connect behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/HTTPKeyValueStore.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/HealthMetricsApi.cpp -->
# sources/storage-engines/foundationdb/fdbserver/workloads/HealthMetricsApi.cpp

## Purpose
Attachable workload that polls `Database::getHealthMetrics` and validates that aggregate and optional detailed health metrics are populated and continue changing during a running simulation.

## Important APIs, types, and functions
`HealthMetricsApiWorkload` derives from `TestWorkload`. It tracks aggregate worst storage queue, durability lag, tlog queue, limiting values, and detailed per-storage/per-tlog queue, CPU, and disk usage. Key methods are `setup`, `start`, `check`, `getMetrics`, and `healthMetricsChecker`.

## Control flow
Setup optionally waits for detailed-health cache staleness and clears cached detailed stats when `sendDetailedHealthMetrics` is false. Start runs `healthMetricsChecker` until `testDuration`. The checker delays at `healthMetricsCheckInterval`, fetches health metrics, marks the workload failed if values repeat longer than `maxAllowedStaleness`, records maxima, emits trace events, and marks `gotMetrics` after both storage and tlog detailed maps appear.

## State and persistence behavior
The workload does not write database keys. It mutates client-side cached health metrics only in the non-detailed setup path. All lasting state is in workload counters/booleans used by `check`.

## Dependencies and integration points
Integrates with client health metrics aggregation, cached detailed metrics in `Database`, worker/storage/tlog metric producers, `CLIENT_KNOBS->DETAILED_HEALTH_METRICS_MAX_STALENESS`, and trace logging.

## Risks and test signals
The check tolerates receiving no full metric sample, but fails if received metrics stop changing or required values are zero/nonzero contrary to the detailed flag. It is timing-sensitive and can be noisy on idle clusters. Signals are trace events for metric values, `HealthMetricsStoppedUpdating`, `IncorrectHealthMetricsState`, and exported perf metrics for the maxima.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/HealthMetricsApi.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/HighContentionPrefixAllocatorWorkload.cpp -->
# sources/storage-engines/foundationdb/fdbserver/workloads/HighContentionPrefixAllocatorWorkload.cpp

## Purpose
Correctness workload for `HighContentionPrefixAllocator`, verifying that many concurrent allocator calls return unique, non-overlapping prefixes and write only inside the allocator subspace.

## Important APIs, types, and functions
`HighContentionPrefixAllocatorWorkload` owns a `Subspace("test_subspace")`, `HighContentionPrefixAllocator`, allocation counters, and a `std::set<Key>` of allocated prefixes. `runAllocationTransaction` issues multiple `allocator.allocate(tr)` calls in one `ReadYourWritesTransaction`; `runTest` runs randomized rounds of concurrent allocation transactions; `check` verifies counts and key bounds.

## Control flow
For each round, the workload starts a random number of allocation transactions. Each transaction chooses a random allocation count, waits for all allocation futures, commits, then checks the returned prefixes against previously allocated prefixes for exact duplicates or prefix containment in either direction. Check reads the first and last keys in the database to ensure all writes are within the allocator subspace.

## State and persistence behavior
The allocator persists its internal state beneath `allocatorSubspace`. The workload also maintains in-memory expected counts and the set of allocated prefixes. It does not clear the subspace.

## Dependencies and integration points
Depends on `fdbclient/HighContentionPrefixAllocator.h`, tuple/subspace key layout, `ReadYourWritesTransaction`, and tester concurrency primitives.

## Risks and test signals
The in-memory `expectedPrefixes` increments before transaction success but each transaction runs until commit, so cancellation or unexpected failure would skew counts. The key-bound check assumes the database contains no unrelated keys. Signals are ASSERTs and `HighContentionAllocationWorkloadFailure` traces for prefix collisions, wrong allocation count, or keys outside the subspace.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/HighContentionPrefixAllocatorWorkload.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/IDDTxnProcessorApiCorrectness.cpp -->
# sources/storage-engines/foundationdb/fdbserver/workloads/IDDTxnProcessorApiCorrectness.cpp

## Purpose
Simulation-only parity workload that compares real `DDTxnProcessor` behavior with `DDMockTxnProcessor` behavior for data-distribution movement APIs. It ensures the mock data distributor's transaction processor tracks the real cluster's shard/server mapping after raw and full move-key operations.

## Important APIs, types, and functions
Helper functions `describe`, `compareShardInfo`, and `verifyInitDataEqual` compare `InitialDataDistribution` and `DDShardInfo`. Tester subclasses expose protected `rawStartMovement` and `rawFinishMovement`. `IDDTxnProcessorApiWorkload` owns `DDSharedContext`, real/mock processors, `MockGlobalState`, current boundaries, and counters. Core methods include `readRealInitialDataDistribution`, `getRandomKeys`, `getRandomTeam`, `generateMoveKeysParams`, `testRawMovementApi`, `testMoveKeys`, and `worker`.

## Control flow
Client 0 disables DD mode, reads real initial distribution, initializes mock global state, verifies equality, then runs randomized movement tests until `testDuration`. Each test generates valid key ranges from current shard boundaries and destination teams from real servers, takes move-keys locks, invokes mock and real APIs, handles `movekeys_conflict` by retrying, re-reads real distribution, verifies mock parity, and refreshes mock global state for server changes. It restores DD mode after the run.

## State and persistence behavior
The workload mutates real data-distribution metadata by disabling/enabling DD and issuing move-key operations. Mock state lives in `MockGlobalState` and is rebuilt from real initial distribution. It also updates in-memory shard boundaries after each real read.

## Dependencies and integration points
Depends on DD shared context, `DDTxnProcessor`, `DDMockTxnProcessor`, `MoveKeysParams`, `MockGlobalState`, storage server interfaces, movement locks, shard location metadata mode, and database configuration. It disables `RandomMoveKeys` and Attrition due to direct DD-mode and movement interference.

## Risks and test signals
Risks are destructive movement side effects, race with server recruitment/removal, unsupported multi-region random teams, and strict equality over only fields the mock cares about. Signals are ASSERTs in init equality, destination checks, and post-movement equality plus perf counters `TestRawStart`, `TestRawFinish`, and `TestRawAll`.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/IDDTxnProcessorApiCorrectness.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/Increment.cpp -->
# sources/storage-engines/foundationdb/fdbserver/workloads/Increment.cpp

## Purpose
Atomic-operation throughput and consistency workload. It repeatedly increments one key in each half of a keyspace and verifies that the aggregate sums remain equal.

## Important APIs, types, and functions
`Increment` derives from `TestWorkload`, exposes `intToTestKey`, `incrementClient`, `incrementCheckData`, and `incrementCheck`, and tracks transactions, retries, transaction-too-old retries, commit-failed retries, and latency.

## Control flow
Each client starts `actorCount` Poisson-paced actors for `testDuration`. Each actor creates a transaction, performs two `MutationRef::AddValue` atomic ops with `"\x01"` against random keys in opposite halves of the configured range, commits with retry handling, and records latency. Check gathers client errors, enforces minimum throughput, and on client 0 reads the whole keyspace to validate sums.

## State and persistence behavior
State is a set of numeric little-endian atomic-add values under decimal string keys. The workload never initializes or clears keys; absent keys count as zero. It reads all keys at check time and decodes values up to `uint64_t`.

## Dependencies and integration points
Uses native transactions, atomic add mutation semantics, tester timing helpers, and normal retry behavior through `Transaction::onError`.

## Risks and test signals
Risks include 32-bit `int` sum overflow if very high transaction counts are configured, reliance on atomic add byte encoding, and false failures under intentional fault injection if expected rate is too high. Signals are client future errors, minimum throughput warnings/failures, and equality of first-half and second-half sums.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/Increment.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/IncrementalBackup.cpp -->
# sources/storage-engines/foundationdb/fdbserver/workloads/IncrementalBackup.cpp

## Purpose
Backup-agent workload for submitting incremental backups, waiting for backup progress, optionally stopping backups, and restoring incremental backup data, including encrypted backup variants and system-key restore handling.

## Important APIs, types, and functions
`IncrementalBackupWorkload` owns backup URL/tag options, `FileBackupAgent`, mode flags (`submitOnly`, `restoreOnly`, `waitForBackup`, `stopBackup`, `checkBeginVersion`, `clearBackupAgentKeys`), optional blob manifest and encryption key file. It uses `addDefaultBackupRanges`, `IBackupContainer`, `BackupDescription`, `BackupContainerFileSystem`, `backupAgent.submitBackup`, `waitBackup`, `discontinueBackup`, and `restore`.

## Control flow
Only client 0 acts. `_start` computes backup ranges and configuration. Submit mode may create an encryption key file and submits an incremental-only backup, accepting duplicate-backup errors. Restore mode optionally clears file-backup system keys, waits for a backup container, optionally reads snapshot begin version from system keys, lists containers, splits restore ranges into normal and system ranges, restores system mutations first if needed, then restores normal ranges. `_check` can unpause backup agents, wait until contiguous log end reaches a read version, and discontinue the backup.

## State and persistence behavior
The workload writes backup-agent system metadata, backup container files under `backupDir`, optional encryption key files under `simfdb/`, and can clear `fileBackupPrefixRange`. Restore operations lock/unlock the database and may apply system mutation logs from `beginVersion`.

## Dependencies and integration points
Integrates with backup agent code, filesystem backup containers, encryption test utilities, management/system key ranges, database configuration, and restore locking.

## Risks and test signals
Risks include races while backup containers are being created, indefinite wait unless `waitRetries` bounds it, assumptions that `containers.front()` exists after listing, and destructive clearing/restoring of backup metadata. Signals are trace events for submit/wait/version-gate/restore phases, exceptions other than accepted duplicate or backup-unneeded errors, and successful completion of restore/check paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/IncrementalBackup.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/IndexScan.cpp -->
# sources/storage-engines/foundationdb/fdbserver/workloads/IndexScan.cpp

## Purpose
Range-read performance workload that repeatedly scans an index key range in bounded byte chunks and reports row/chunk/failure metrics.

## Important APIs, types, and functions
`IndexScanWorkload` derives from `KVWorkload`, using inherited `keyForIndex`, `allKeys`, and `nodeCount` helpers. It exposes `bytesPerRead`, `transactionDuration`, `singleProcess`, and `readYourWrites`, and tracks rows, chunks, scans, failed transactions, and total fetch time.

## Control flow
The start phase optionally limits execution to client 0, warms the location cache for `allKeys`, waits briefly, and runs `serialScans` for `testDuration`. Each `scanDatabase` starts at a random index in the first half of the database, reads until the end key using `GetRangeLimits(ROW_LIMIT_UNLIMITED, bytesPerRead)`, advances by `firstGreaterThan(last.key)`, and breaks a transaction after empty result, no `more`, or `transactionDuration`.

## State and persistence behavior
The workload does not set up or write data; comments state that data is prepared externally. It only accumulates in-memory metrics.

## Dependencies and integration points
Depends on `KVWorkload` key generation, `ReadYourWritesTransaction`, optional `READ_YOUR_WRITES_DISABLE`, location-cache warming, and standard range read retry behavior.

## Risks and test signals
`check` always returns true, so this is a measurement workload. Risks include repeated scans over missing externally populated data, byte-limit sensitivity, and false failure count inflation except for actor cancellation. Signals are metrics for failed transactions, rows, scans, chunks, elapsed fetch time, rows/sec, and rows/chunk.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/IndexScan.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/Inventory.cpp -->
# sources/storage-engines/foundationdb/fdbserver/workloads/Inventory.cpp

## Purpose
Transactional inventory counter workload that mixes point reads with multi-product read-modify-write increments and verifies final counts are within in-memory expected bounds.

## Important APIs, types, and functions
`InventoryTestWorkload` derives from `TestWorkload` and tracks per-key `minExpectedResults` and `maxExpectedResults`, actor and product counts, rates, clients, and counters. Key methods are `chooseProduct`, `inventoryTestWrite`, `inventoryTestClient`, `inventoryTestCheck`, `failures`, and metrics reporting.

## Control flow
Only client 0 runs actors. Each actor is Poisson-paced and randomly chooses write or read. Write transactions choose a set of products, pessimistically increment max bounds, read each product's current count, set count+1, retry on errors while adjusting max bounds, then increment min bounds after commit. Read transactions only read a random product with retry. Check reads the full product key range and compares actual counts to expected min/max bounds.

## State and persistence behavior
Database state is plain decimal count strings under `doubleToTestKey(product/nProducts)`. In-memory bounds account for transactions that may have been cancelled, retried, or committed. No cleanup occurs.

## Dependencies and integration points
Uses FoundationDB transactions, deterministic random key generation, tester Poisson pacing, and trace/perf metric utilities.

## Risks and test signals
The workload is single-client despite a multi-client note, and expected-bound bookkeeping is subtle around actor cancellation and retries. Count parsing uses `atoi` and assumes nonnegative bounded counts. Signals are client future errors, final actual count outside min/max, and latency/throughput perf metrics.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/Inventory.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/KRMCoalescingFragmentation.cpp -->
# sources/storage-engines/foundationdb/fdbserver/workloads/KRMCoalescingFragmentation.cpp

## Purpose
Regression workload for a `krmSetRangeCoalescing` fragmentation bug in `removeOldDestinations`. It exercises the real production KRM mutation path with a user-keyspace test prefix and verifies adjacent same-value entries are not left behind.

## Important APIs, types, and functions
`KRMCoalescingFragmentationWorkload` uses `krmSetRange`, `krmGetRanges`, `removeOldDestinations`, `serverKeysTrue`, `serverKeysFalse`, `allKeys`, and `ReadYourWritesTransaction`. Its state is `testPrefix` and `success`; the full test lives in `runTest`.

## Control flow
Client 0 initializes a KRM map to `true`, clears `["d","j")`, verifies the four-entry setup, then calls `removeOldDestinations` for current keys `["a","m")` while preserving shards `["a","c")`, `["e","g")`, and `["k","m")`. It reads the KRM back, traces all entries, detects adjacent same-value fragmentation, and asserts the exact expected transitions at empty, `"c"`, and `"k"`.

## State and persistence behavior
The workload writes KRM metadata under `KRMFragTest/` in user keyspace. It does not mutate system metadata, but it does not clean up the test prefix.

## Dependencies and integration points
Integrates directly with `KeyRangeMap` helper functions and `MoveKeys.cpp`'s `removeOldDestinations`, making it a narrow regression test for DD range-map coalescing behavior.

## Risks and test signals
Risks are hard-coded key examples and exact result-size expectations. Signals are `success`, ASSERTs on KRM entries, and `KRMFragTestFragmentationDetected`/`KRMFragTestFailed` traces when adjacent equal-value records remain.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/KRMCoalescingFragmentation.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/KVStoreTest.cpp -->
# sources/storage-engines/foundationdb/fdbserver/workloads/KVStoreTest.cpp

## Purpose
Standalone storage-engine workload for exercising `IKeyValueStore` implementations outside normal transaction layers. It measures read/commit latency and checks basic read-committed/causal consistency against an in-memory version history.

## Important APIs, types, and functions
`TestHistogram` samples latency distributions. `KVTest` wraps an `IKeyValueStore`, version counters, and `allSets` history. Actors `testKVRead`, `testKVReadSaturation`, and `testKVCommit` validate and measure operations. `KVStoreTestWorkload` selects store type and options, while `testKVStoreMain` and `testKVStore` drive setup, load, random operations, optional counting, clearing, and store lifecycle.

## Control flow
Client 0 creates a key-value store by type (`SQLite`, Redwood, RocksDB, sharded RocksDB, memory, radix tree), initializes it, optionally counts existing rows, bulk-loads keys, then runs either saturation or scheduled operations. Scheduled operations choose commit, set, or read according to configured fractions. Commits are issued through an `ActorCollectionNoErrors`; reads verify returned versions relative to durable and committed version trackers. Optional clear deletes chunks at the end.

## State and persistence behavior
Database state is in the selected local KV store file or in-memory store, not FoundationDB. Values encode a `Version` plus padding. `KVTest::allSets` tracks expected version history, and close either disposes unnamed stores or closes named stores for preservation.

## Dependencies and integration points
Depends on `IKeyValueStore`, storage-engine factory functions, Flow actors, binary serialization, `IndexedSet`, deterministic random keys, and trace/perf metrics.

## Risks and test signals
Risks include high memory use from `allSets`, file lifecycle differences between named and random stores, broad ASSERT on store errors, and concurrency through asynchronous commits. Signals are consistency ASSERTs in reads, store `getError`, setup/count traces, operation counters, and latency histogram metrics.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/KVStoreTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/KillRegion.cpp -->
# sources/storage-engines/foundationdb/fdbserver/workloads/KillRegion.cpp

## Purpose
Simulation-only force-recovery workload that disables regions, kills data centers, and verifies recovery into a usable single-region configuration.

## Important APIs, types, and functions
`KillRegionWorkload` derives from `TestWorkload`, sets `fdbSimulationPolicyState().usableRegions = 1`, disables all other failure injection, and uses `_setup`, `waitForStorageRecovered`, and `killRegion`. It calls `ManagementAPI::changeConfig`, `waitForPrimaryDC`, `forceRecovery`, `getDatabaseConfiguration`, and simulator data-center kill APIs.

## Control flow
Client 0 first disables the primary and waits for remote DC `"1"` to become primary. During start, it may disable remote and restore original region settings, waits a random fraction of `testDuration`, kills data centers `"0"`, `"2"`, and `"4"` with random destructive kill types, then force-recovers using DC `"1"`. If the configuration still has multiple usable regions, it repeatedly configures primary disablement and anti-quorum until storage recovers, then sets `usable_regions=1`.

## State and persistence behavior
The workload mutates cluster configuration and simulated process liveness. It does not write user keys, but it can delete/reboot simulated data-center processes and changes recovery/region metadata.

## Dependencies and integration points
Depends on simulated networking, simulation policy state, management API config changes, recovery state from `dbInfo`, connection-record based force recovery, and database configuration reads.

## Risks and test signals
This is intentionally disruptive and incompatible with other failure injectors. Risks include hard-coded DC IDs, force-kill requirements, and long waits for storage recovery. `check` always returns true, so signals are successful actor completion and trace events through force-recovery phases.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/KillRegion.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/LocalRatekeeper.cpp -->
# sources/storage-engines/foundationdb/fdbserver/workloads/LocalRatekeeper.cpp

## Purpose
Simulation workload that validates storage-server local ratekeeper behavior when durability lag rises. It checks both reported `localRateLimit` and whether reads to a lagging storage server are rejected as future versions.

## Important APIs, types, and functions
The file-local `getRandomStorage` reads `serverListKeys` and decodes a `StorageServerInterface`. `LocalRatekeeperWorkload` exposes `startAfter`, `blockWritesFor`, `testFailed`, `testStorage`, and `_start`. It uses `StorageQueuingMetricsRequest`, `GetValueRequest`, `SERVER_KNOBS->STORAGE_DURABILITY_LAG_SOFT_MAX/HARD_MAX`, and simulator `disableFor`.

## Control flow
Client 0 in simulation waits `startAfter`, picks a random storage server, disables its `updateStorage` actor for `blockWritesFor`, waits roughly until soft lag should be reached, then races `testStorage` with the block duration. `testStorage` repeatedly fetches queuing metrics, computes the expected local rate limit linearly from durability lag, sends 100 direct `getValue` requests at a current read version, and counts `future_version` rejections.

## State and persistence behavior
No user data is written. Runtime state is the disabled simulator role and `testFailed`. System key reads require `ACCESS_SYSTEM_KEYS`.

## Dependencies and integration points
Integrates with storage server interfaces, local ratekeeper metrics, simulator role disabling, transaction read versions, and direct storage-server read requests.

## Risks and test signals
Risks are timing sensitivity around lag accumulation, selecting a storage server whose state changes, and treating any direct request error as workload failure. Signals are `StorageRateLimitTooFarOff`, `LoadBalancedResponseReturnedError`, `RejectedVersions` traces, and `check` returning `!testFailed`.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/LocalRatekeeper.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/LockDatabase.cpp -->
# sources/storage-engines/foundationdb/fdbserver/workloads/LockDatabase.cpp

## Purpose
Database-lock correctness workload. It locks the database, verifies normal read-version requests fail while locked, then unlocks and checks user data did not change during the locked interval.

## Important APIs, types, and functions
`LockDatabaseWorkload` uses options `lockAfter`, `unlockAfter`, and `onlyCheckLocked`. Key actors are `lockAndSave`, `unlockAndCheck`, `checkLocked`, and `lockWorker`. It calls `lockDatabase`, `unlockDatabase`, reads `databaseLockedKey`, and uses transaction options `ACCESS_SYSTEM_KEYS`, `LOCK_AWARE`, and `READ_SYSTEM_KEYS`.

## Control flow
Client 0 either runs `checkLocked` for a bounded period or delays until `lockAfter`, locks using a random UID while reading all normal keys into a snapshot, starts a concurrent locked-state checker, waits until `unlockAfter`, cancels the checker, unlocks with the same UID, reads normal keys again, and compares both range results.

## State and persistence behavior
The workload writes database lock system state and reads normal key data for comparison. It does not change normal data itself. Unlock is skipped if the lock key is already absent.

## Dependencies and integration points
Depends on FoundationDB management lock helpers, system key permissions, normal-key range reads, lock-aware transactions, and read-version behavior while locked.

## Risks and test signals
Risks include assuming normal data fits in 50,000 rows, exact `RangeResult` comparison under concurrent workloads that may legitimately write unless coordinated, and cancellation of `checkLocked`. Signals are `GotVersionWhileLocked`, `DataChangedWhileLocked`, and final `ok`.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/LockDatabase.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/LockDatabaseFrequently.cpp -->
# sources/storage-engines/foundationdb/fdbserver/workloads/LockDatabaseFrequently.cpp

## Purpose
Stress workload that repeatedly locks and unlocks the database to exercise lock system-key paths under frequent transitions.

## Important APIs, types, and functions
`LockDatabaseFrequentlyWorkload` has options `delayBetweenLocks` and `testDuration`, a `LockCount` counter, and actors `worker` and `lockAndUnlock`. It uses management helpers `lockDatabase(cx, uid)` and `unlockDatabase(cx, uid)`.

## Control flow
Only client 0 runs. The worker tracks Poisson schedules for lock and unlock phases, repeatedly creates a random UID, races lock completion with the next lock schedule, then races unlock completion with the next unlock schedule. It increments `lockCount` after each full cycle and returns once the duration timer is ready.

## State and persistence behavior
The workload continuously mutates the database lock system key state. It does not read or write user data and performs no explicit cleanup beyond each unlock operation.

## Dependencies and integration points
Depends on FoundationDB database lock management APIs, Flow Poisson pacing, and workload metrics.

## Risks and test signals
`check` always succeeds, so the workload is primarily a fault/exercise generator. Risks include overlapping lock timing semantics, disruption to unrelated workloads, and lock UID mismatch if helpers change. The signal is successful completion and the `LockCount` metric.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/LockDatabaseFrequently.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/LogMetrics.cpp -->
# sources/storage-engines/foundationdb/fdbserver/workloads/LogMetrics.cpp

## Purpose
Workload that temporarily increases system metric logging frequency and runs `systemMonitor` at that rate, then restores the default metric rate.

## Important APIs, types, and functions
`LogMetricsWorkload` uses options `logAt`, `logDuration`, `logsPerSecond`, and `dataFolder`. `setSystemRate` sends `SetMetricsLogRateRequest` to all workers returned by `getWorkers(dbInfo)` and writes the `fastLoggingEnabled` system key. `_start` controls the timing.

## Control flow
Client 0 waits `logAt`, sets worker and storage metric rates to `logsPerSecond`, runs `recurring(&systemMonitor, 1.0 / logsPerSecond)` for `logDuration`, then calls `setSystemRate` with `1.0` to restore normal logging.

## State and persistence behavior
The workload writes the `fastLoggingEnabled` system key in a self-conflicting transaction and sends in-memory rate changes to worker interfaces. It does not write user data.

## Dependencies and integration points
Depends on worker interface discovery, metrics log-rate RPCs, system monitor infrastructure, `ServerDBInfo`, `QuietDatabase` headers, system key access, and transaction retry semantics.

## Risks and test signals
`check` always returns true and no metrics are exported. Risks are increased trace/log volume, partial worker delivery because sends are fire-and-forget, and restoring with a floating value converted to `uint32_t`. Signals are trace events around rate changes and absence of actor errors.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/LogMetrics.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/LowLatency.cpp -->
# sources/storage-engines/foundationdb/fdbserver/workloads/LowLatency.cpp

## Purpose
Latency guard workload for high-priority read-version and commit operations. It periodically runs a system-immediate, lock-aware transaction and fails if latency exceeds configured thresholds.

## Important APIs, types, and functions
`LowLatencyWorkload` tracks `testDuration`, `maxGRVLatency`, `maxCommitLatency`, `checkDelay`, `testWrites`, `testKey`, `operations`, `retries`, and `ok`. `setup` adjusts worst-fit candidacy delay knobs in simulation; `_start` performs the latency checks.

## Control flow
Client 0 loops until `testDuration`, sleeping `checkDelay` between attempts. Each operation randomly chooses commit or GRV when writes are enabled, sets transaction options `PRIORITY_SYSTEM_IMMEDIATE` and `LOCK_AWARE`, either writes `testKey` and commits or calls `getReadVersion`, retries on errors, and compares elapsed time to the matching maximum.

## State and persistence behavior
When write testing is enabled, the workload repeatedly writes an empty value to `testKey`. It also changes simulated server knobs for candidacy delay. Runtime state is the `ok` flag and counters.

## Dependencies and integration points
Integrates with transaction priority options, database locks, GRV path, commit path, server knob plumbing, and tester failure-injection coordination. It disables Attrition.

## Risks and test signals
Thresholds are wall-clock simulation sensitive, and retry loops can hide transient errors while still causing latency failures. Signals are `LatencyTooLarge`, unsuppressed transaction failure traces, and metrics for operations/sec, operations, and retries.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/LowLatency.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/MachineAttrition.cpp -->
# sources/storage-engines/foundationdb/fdbserver/workloads/MachineAttrition.cpp

## Purpose
Primary FoundationDB failure-injection workload for killing, rebooting, replacing, or faulting simulated or real workers/machines/regions during tests.

## Important APIs, types, and functions
`MachineAttritionWorkload` derives from `FailureInjectionWorkload` and is registered both as a workload and failure injector. It defines attrition options for machine/worker counts, leave counts, durations, reboot/delete/fault modes, target locality IDs, replacement, wait-for-version, and fault injection. Helpers include `normalAttritionErrors`, `ignoreSSFailuresForDuration`, `shouldInject`, `initializeForInjection`, `getServers`, `sendRebootRequests`, `noSimMachineKillWorker`, and `machineKillWorker`.

## Control flow
In simulation, enabled client 0 collects server zone localities, shuffles them, and runs `machineKillWorker` until `testDuration`. The worker can kill an entire DC, data hall, all switch clusters, or selected zones/machines with random kill types, optional healthy-zone marking, optional DD storage-failure suppression, replacement reshuffling, and iterative backoff. Outside simulation, it sends reboot requests to matching workers or randomly selected non-tester workers. `killSelf` can throw `please_reboot`.

## State and persistence behavior
The workload mutates process liveness, simulated disks, global switch cluster state, healthy-zone system keys, and possibly suppresses DD reactions to storage failures. It does not write normal user data.

## Dependencies and integration points
Deeply integrates with simulator process info, `FDBSimulationPolicyState`, worker client reboot interfaces, management API healthy-zone keys, fault-injection activation, locality data, and recovery retry behavior.

## Risks and test signals
Risks are intentionally broad: destructive process failure, interaction with extra databases, timing around healthy-zone cleanup, and different semantics in simulation versus no-simulation mode. Expected normal errors are `please_reboot` and `please_reboot_delete`. `check` returns the result of the ignore-SS-failures cleanup future, and traces such as `Assassination`, `WorkerKill`, and `AddingFailureInjection` are the main signals.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/MachineAttrition.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/Mako.cpp -->
# sources/storage-engines/foundationdb/fdbserver/workloads/Mako.cpp

## Purpose
Configurable benchmark workload for mixed FoundationDB operations. It can bulk-populate key/value data, run user-specified transaction mixes, record per-operation latency and throughput, optionally maintain checksum keys for consistency validation, and clean up benchmark data.

## Important APIs, types, and functions
`MakoWorkload` parses an operation spec into `operations[MAX_OP][2]` across GRV, get, range get, snapshot get, update, insert, insert range, clear, set-clear, clear range, set-clear-range, and commit. It uses `bulkSetup`, `ReadYourWritesTransaction`, `DDSketch`, `PerfIntCounter`, Zipf generators, CRC32C helpers, checksum keys, and operation counters. Key methods include `keyForIndex`, `randomValue`, `parseOperationsSpec`, `_setup`, `_runBenchmark`, `makoClient`, checksum calculation/update/verification, `tracePeriodically`, and `cleanup`.

## Control flow
Setup optionally bulk-loads rows and, on client 0, generates checksum keys. Start runs `actorCountPerClient` Poisson-paced clients for `testDuration`, optionally with periodic trace logging. Each client loops through configured operation counts, chooses random or Zipf-distributed keys, performs reads/writes/ranges, marks checksum partitions affected by mutations, commits when required, updates per-op counters and latency sketches, and retries on transaction errors while counting conflicts. Check verifies all configured checksum keys by recomputing CRC32C over sampled rows.

## State and persistence behavior
Benchmark data is stored under the configurable key prefix with fixed-length keys and random values. Optional checksum keys are named from the prefix and row count and are updated in the same transactions as mutations. Cleanup clears the prefix range if `preserveData` is false.

## Dependencies and integration points
Depends on bulk setup, RYW transactions, snapshot reads, key encoding helpers, Zipf distribution support, CRC32C, Flow timing, and tester perf metrics.

## Risks and test signals
Risks include complex operation-spec parsing, checksum coverage gaps when row counts do not divide evenly, generated insert keys outside checksum index space, possible bug from bitwise `|` in checksum mutation condition, and very high default TPS. Signals are operation/transaction/conflict/retry metrics, latency sketches, periodic traces, and checksum verification failures or missing checksum keys.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/Mako.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/MaxGrvQueueDelay.cpp -->
# sources/storage-engines/foundationdb/fdbserver/workloads/MaxGrvQueueDelay.cpp

## Purpose
End-to-end validation for the `MAX_GRV_QUEUE_DELAY` transaction option. It verifies that normal and permissive GRV requests succeed while a burst of zero-delay uncached GRV requests is rejected by proxy GRV queue throttling.

## Important APIs, types, and functions
`MaxGrvQueueDelayWorkload` exposes request counts, required rejection count, strict and permissive delay thresholds, warmup controls, start delay, timeout, completion/failure flags, and counters. It uses `FDBTransactionOptions::SKIP_GRV_CACHE`, `MAX_GRV_QUEUE_DELAY`, `errorOr`, `waitForAll`, and `transaction_grv_queue_rejected`.

## Control flow
Only client 0 runs in simulation when general buggify is disabled, and all failure injection is disabled. `run` waits `startAfter`, calls `verifyBaseline` with retries for a no-option request and a permissive option request, optionally launches warmup GRVs, then launches `requestCount` strict-option GRVs in parallel. It counts successes, expected rejections, and unexpected errors, then fails if fewer than `minRejected` requests were rejected.

## State and persistence behavior
The workload does not write keys. It only exercises transaction read-version requests with specific options and records in-memory counters.

## Dependencies and integration points
Depends on client transaction option encoding, proxy GRV queue ratekeeper configuration from test files, simulation environment, Flow buggify status, and error propagation.

## Risks and test signals
The workload is sensitive to external ratekeeper knob configuration and recovery backlog. Baseline retry reduces but does not eliminate startup flakiness. Signals are counters for requests/successes/rejected/unexpected errors, `MaxGrvQueueDelayTooFewRejections`, and completion/failure flags checked after timeout.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/MaxGrvQueueDelay.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/MemoryKeyValueStore.cpp -->
# sources/storage-engines/foundationdb/fdbserver/workloads/MemoryKeyValueStore.cpp

## Purpose
Implementation of a simple ordered in-memory key-value store used by tester code as a model or helper store.

## Important APIs, types, and functions
Defines `MemoryKeyValueStore` methods declared in the header: `get`, `getKey`, `getRange`, `set`, `clear(key)`, `clear(range)`, `size`, `startKey`, `endKey`, and `printContents`. The backing data structure is `std::map<Key, Value>`.

## Control flow
Point reads lookup `store.find`. `getKey` starts from `lower_bound(selector.getKey())`, adjusts for `orEqual` and selector offset direction, walks the map up to the absolute offset, and returns `startKey` or `endKey` when the selector falls outside the stored range. Forward `getRange` iterates from `lower_bound(range.begin)` until range end or limit. Reverse `getRange` starts before `range.end` and walks backward.

## State and persistence behavior
All data is process-local memory. `set` copies keys and values into the map; clear erases one key or a half-open range. `startKey` returns empty key and `endKey` returns `\xff`.

## Dependencies and integration points
Uses FoundationDB `Key`, `Value`, `KeySelectorRef`, `RangeResult`, and `Reverse` types. It is paired with `MemoryKeyValueStore.h` and tester workloads that need a local store abstraction.

## Risks and test signals
Reverse range support is explicitly noted as untested, and the loop compares unsigned key ordering while decrementing iterators carefully. Selector offset edge cases are the highest-risk behavior. There are no direct tests in this file; signals come from workloads using this model store.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/MemoryKeyValueStore.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/MemoryKeyValueStore.h -->
# sources/storage-engines/foundationdb/fdbserver/workloads/MemoryKeyValueStore.h

## Purpose
Header for an in-memory ordered key-value store that mirrors a subset of FoundationDB key-value operations for tester workloads.

## Important APIs, types, and functions
Declares class `MemoryKeyValueStore` with public APIs for `get`, key-selector resolution via `getKey`, bounded `getRange`, point and range `clear`, `set`, `size`, `startKey`, `endKey`, and `printContents`. It stores data in a private `std::map<Key, Value>`.

## Control flow
The header has no runtime control flow; it defines the contract implemented by `MemoryKeyValueStore.cpp`. Consumers can treat the class as a synchronous model store with FoundationDB key/value and range types.

## State and persistence behavior
State is entirely in-memory and scoped to the object lifetime. There is no persistence, versioning, transaction isolation, or concurrency control in the class contract.

## Dependencies and integration points
Includes `fdbrpc/fdbrpc.h` and tester workload headers for FoundationDB value/range types and pulls in `<map>`. It is intended for workload code rather than production storage.

## Risks and test signals
The API is intentionally minimal and synchronous, so consumers must not assume database semantics such as conflict ranges or snapshots. Test signal comes indirectly from workloads that compare database behavior to this local model.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/MemoryKeyValueStore.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/MemoryLifetime.cpp -->
# sources/storage-engines/foundationdb/fdbserver/workloads/MemoryLifetime.cpp

## Purpose
Workload that checks returned memory from transaction read APIs remains valid across transaction object replacement and short delays. It repeatedly performs equivalent reads and compares the retained results.

## Important APIs, types, and functions
`MemoryLifetime` derives from `KVWorkload`, uses `bulkSetup`, random keys/selectors, `ReadYourWritesTransaction`, `getRange`, `get`, `getKey`, and `getAddressesForKey`. It overrides `operator()` for bulk setup and runs all checks in `start`.

## Control flow
Setup bulk-loads `nodeCount` random key/value pairs. Start loops until `testDuration`, randomly choosing one of four operations. For range/get/key-selector checks, it may add a local write in the transaction, performs the read with random snapshot/reverse options, replaces the transaction, waits 0.01 seconds, repeats the same local write and read, then asserts both results match. For address lookups, it validates retained address strings parse successfully.

## State and persistence behavior
Setup writes normal test data through `bulkSetup`; the repeated local transaction writes are not committed. Runtime state is only local comparisons.

## Dependencies and integration points
Depends on RYW transaction memory ownership, snapshot and reverse range APIs, address-for-key lookup, deterministic random workload helpers, and bulk setup.

## Risks and test signals
The workload is designed to catch lifetime/arena bugs rather than data-model bugs. It can be sensitive to real data changes between paired reads, but local uncommitted mutations are replayed. Signals are ASSERTs and detailed `MemoryLifetimeCheckKeyError`/`MemoryLifetimeCheckValueError` traces.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/MemoryLifetime.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/MetricLogging.cpp -->
# sources/storage-engines/foundationdb/fdbserver/workloads/MetricLogging.cpp

## Purpose
Workload that exercises the `TDMetric` logging infrastructure by rapidly toggling boolean metrics or updating int64 metrics.

## Important APIs, types, and functions
`MetricLoggingWorkload` owns actor and metric counts, `testBool`, `enabled`, `changes`, `BoolMetricHandle` vector, and `Int64MetricHandle` vector. `setup` enables metric configs, `MetricLoggingClient` mutates metrics in batches, and metrics reporting exports changes and changes/sec.

## Control flow
Construction creates the requested metric handles. Setup waits two seconds then enables each metric's config. Start launches `actorCount` clients for `testDuration`. Each client loops forever, performing 100 metric updates per yield: boolean mode toggles the next metric modulo `metricCount`; int64 mode assigns the current change count.

## State and persistence behavior
No database state is used. State is in the process-wide metric subsystem and workload counters. `check` clears client futures and always succeeds.

## Dependencies and integration points
Depends on `flow/TDMetric.h`, tester workload scheduling, metric handle configuration, and perf counter export.

## Risks and test signals
The `enabled` option is read but not used to gate execution. High actor/metric counts can create high metric churn. Signals are absence of actor errors and the `Changes`/`Changes/sec` metrics.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/MetricLogging.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/MiniCycle.cpp -->
# sources/storage-engines/foundationdb/fdbserver/workloads/MiniCycle.cpp

## Purpose
Transactional cycle-integrity workload. It partitions the keyspace into per-client mini-cycles, runs transactions that reverse links among three adjacent cycle nodes, and repeatedly verifies each cycle remains a single valid cycle.

## Important APIs, types, and functions
`MiniCycleWorkload` derives from `TestWorkload` and uses `bulkSetup`, key/value helpers with optional `keyPrefix`, `FlowLock` for serialized checks, retry counters, and latency metrics. Core methods are `cycleSize`, `beginKey`, `endKey`, `operator()` for initial links, `cycleClient`, `_check`, `_checkCycle`, `cycleCheckClient`, and `cycleCheckData`.

## Control flow
Setup bulk-loads the current client's mini-cycle. The start phase does nothing; check launches transaction clients for all client partitions for `testDuration` while periodically running full cycle checks. A cycle client picks a random node, reads three links, writes a reversal of the next links across those nodes, and commits with retry handling. Checkers read each partition range and walk values as pointers to ensure exactly one complete cycle with no missing, invalid, shorter, or longer loop.

## State and persistence behavior
State is normal key/value data where each key's value encodes the next node in the cycle. Transactions mutate three links atomically. No cleanup is performed.

## Dependencies and integration points
Uses bulk setup, normal transactions, optional span parent transaction option, deterministic key encoding, Flow locks, and tester metrics.

## Risks and test signals
Risks include the typo-like option name `"traceParentProbability "` with trailing space, check methods using `clientId` in places where `clientID` is passed, and high contention producing rate failures. Signals are cycle structural failures, bad reads, client/checker errors, minimum throughput checks, and retry/latency metrics.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/MiniCycle.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/MinimumThroughput.cpp -->
# sources/storage-engines/foundationdb/fdbserver/workloads/MinimumThroughput.cpp

## Purpose
Simple throughput floor workload for error-free conditions. It verifies the cluster can sustain a configured rate of basic point reads and optional writes.

## Important APIs, types, and functions
`MinimumThroughputWorkload` tracks actors, node count, duration, per-client target TPS, minimum expected TPS, read fraction, client futures, transaction/retry counters, and latency. `keyForIndex` uses `MTP/%08d`; `client` performs the workload loop.

## Control flow
Every client starts `actorCount` Poisson-paced actors for `testDuration`. Each operation picks a random key, chooses read-only versus read-write, reads the key, optionally writes `"x"` and commits, then records transaction count and latency. Check reports client errors and fails if achieved transactions are below `testDuration * minExpectedTransactionsPerSecond`.

## State and persistence behavior
Writes are simple point sets under `MTP/` keys. There is no setup or cleanup, and absent keys are valid for read-only operations.

## Dependencies and integration points
Depends on normal transaction get/set/commit paths, retry handling, tester pacing, and perf metrics. It disables all failure injection to keep the throughput assertion meaningful.

## Risks and test signals
The workload is sensitive to configured expected rate and environment capacity. Division by zero is possible in average latency metric if no transactions complete. Signals are client errors, throughput-below-minimum trace details, transaction/retry counters, and average latency.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/MinimumThroughput.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/MockDDReadWrite.cpp -->
# sources/storage-engines/foundationdb/fdbserver/workloads/MockDDReadWrite.cpp

## Purpose
Mock data-distributor workload that runs mock storage servers and a `MockDataDistributor` over a populated `MockGlobalState`, intended to exercise mock DD read/write behavior.

## Important APIs, types, and functions
`MockDDReadWriteWorkload` derives from `MockDDTestWorkload`. It owns a `Reference<DDSharedContext>`, `Reference<DDMockTxnProcessor>`, `MockDataDistributor`, and `ActorCollection`. It uses inherited `populateMgs` and `sharedMgs`.

## Control flow
Setup runs only when enabled, calls the base setup to create `MockGlobalState`, populates mock data, and constructs a `DDMockTxnProcessor`. Start launches all mock servers through `sharedMgs->runAllMockServers()`, starts `dataDistributor.run(ddcx, mock)`, and then delays for `testDuration`. Check currently returns true.

## State and persistence behavior
All state is in the simulated mock DD universe, not FoundationDB user keys. `sharedMgs` contains cluster layout, mock server state, shard sizes, and populated data.

## Dependencies and integration points
Depends on `MockDDTest.h`, `MockDataDistributor`, `DDTxnProcessor` abstractions, `DDSharedContext`, mock servers, and Flow actor collection lifecycle.

## Risks and test signals
Because `check` always returns true and metrics are empty, this workload is mostly a smoke/exercise harness. Risks include actor errors being hidden if not surfaced through `ActorCollection`, incomplete validation of read/write results, and dependency on base mock population. Signal is successful run without actor failure traces.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/MockDDReadWrite.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/MockDDTest.cpp -->
# sources/storage-engines/foundationdb/fdbserver/workloads/MockDDTest.cpp

## Purpose
Implementation of the common base class for mock data-distribution workloads. It builds a mock cluster/global state and provides data population strategies for derived mock DD tests.

## Important APIs, types, and functions
`MockDDTestWorkload` implements `getRandomRange`, constructor option parsing, `populateRandomStrategy`, `populateLinearStrategy`, `populateFixedStrategy`, `populateMgs`, and `setup`. It owns `sharedMgs`, mock DB size accounting, keyspace strategy parameters, byte-size limits, and simulation configuration knobs.

## Control flow
Construction enables the workload only for client 0 in simulation and reads options. `setup` builds a `BasicSimulationConfig`, creates `MockGlobalState`, initializes cluster layout and an empty mock database. Derived classes call `populateMgs`, which chooses fixed, linear, or random population, inserts synthetic keys into mock global state, computes estimated size, and traces reported total size.

## State and persistence behavior
State is fully in `MockGlobalState`; no real database keys are written. Population strategies create keys from integer keyspace offsets with value sizes determined by strategy and configured bounds.

## Dependencies and integration points
Depends on mock data-distribution classes, `BasicSimulationConfig`, deterministic random key generation, and derived mock DD workloads in the same folder.

## Risks and test signals
Risks include approximate size accounting, strategy string matching with `Value`, and a loop in total-size reporting that overwrites rather than accumulates per-server size. Signals are population traces and derived workload checks.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/MockDDTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/MockDDTest.h -->
# sources/storage-engines/foundationdb/fdbserver/workloads/MockDDTest.h

## Purpose
Shared declaration for mock data-distribution tester workloads. It centralizes common options, mock global state ownership, and population hooks.

## Important APIs, types, and functions
Declares `MockDDTestWorkload : TestWorkload` with public state `enabled`, `simpleConfig`, `testDuration`, `meanDelay`, byte-size/keyspace options, `sharedMgs`, `getRandomRange`, and `setup`. Protected members include `mockDbSize`, `keySize`, strategy controls, and virtual `populateRandomStrategy`, `populateLinearStrategy`, `populateFixedStrategy`, and `populateMgs`.

## Control flow
The header has no executable control flow, but defines the template method shape: derived workloads call base `setup`, optionally override or reuse population methods, and use the populated `sharedMgs`.

## State and persistence behavior
The base contract owns only in-memory mock data-distribution state through `std::shared_ptr<MockGlobalState>`. It does not expose real database persistence behavior.

## Dependencies and integration points
Includes tester workload infrastructure, `DDSharedContext`, `DDTxnProcessor`, move-keys types, and storage server interfaces. It is used by `MockDDReadWrite.cpp` and `MockDDTrackerShardEvaluator.cpp`.

## Risks and test signals
Derived classes depend on base fields remaining consistent with `MockDDTest.cpp` defaults. There are no direct signals in the header; tests come from derived workload checks and mock global state traces.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/MockDDTest.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/MockDDTrackerShardEvaluator.cpp -->
# sources/storage-engines/foundationdb/fdbserver/workloads/MockDDTrackerShardEvaluator.cpp

## Purpose
Mock DD workload that runs `DataDistributionTracker` over synthetic mock shard data and records relocation reasons produced by shard evaluation, especially size and write splits.

## Important APIs, types, and functions
`MockDDTrackerShardEvaluatorWorkload` derives from `MockDDTestWorkload`. It owns `DDSharedContext`, `DDMockTxnProcessor`, relocation output and metrics promise streams, `KeyRangeMap<ShardTrackedData>`, actor collection, reason counts, and `DataDistributionTracker`. Key actors are `setup`, `relocateShardReporter`, `start`, and `check`.

## Control flow
Setup builds and populates mock global state and constructs a mock transaction processor. Start launches mock servers, starts a reporter that consumes `RelocateShard` messages and increments `rsReasonCounts`, obtains initial data distribution from the mock processor, builds physical shard and bulk-load collections, constructs a tracker with mock streams and shard map, and runs the tracker for `testDuration`. Check asserts minimum shard count and minimum relocation reason counts, prints counts, clears actors, and returns true.

## State and persistence behavior
All state is mock/in-memory: shard map, mock servers, mock data distribution, and relocation counters. No real database writes occur.

## Dependencies and integration points
Depends on `MockDDTest`, `DDMockTxnProcessor`, `DataDistributionTracker`, physical shard and bulk-load collections, relocation streams, and mock storage metrics APIs.

## Risks and test signals
Risks include tracker behavior depending on synthetic population distributions, wrong-shard-server retries in the reporter, and minimal validation beyond count thresholds. Signals are ASSERTs on shard count and relocation reason counts plus perf metrics named by `RelocateReason`.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/MockDDTrackerShardEvaluator.cpp -->
