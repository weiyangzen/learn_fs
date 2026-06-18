# subset-b-008490 Research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/ConsistencyCheckUrgent.cpp -->
# sources/storage-engines/foundationdb/fdbserver/workloads/ConsistencyCheckUrgent.cpp

Purpose: Implements the `ConsistencyCheckUrgent` tester workload, a distributed shard-by-shard replica consistency check for caller-supplied `rangesToCheck`. Unlike the broader single-threaded consistency workload, this one prioritizes complete coverage, retry reporting, and failure propagation for urgent consistency checker tasks.

Important APIs/types/functions: `ConsistencyCheckUrgentWorkload`, `getKeyLocationsForRangeList`, `getVersion`, `checkDataConsistencyUrgent`, and `_start` drive the workload. It uses `krmGetRanges`, `keyServersPrefix`, `decodeKeyServersValue`, `serverTagKeys`, `serverListKeyFor`, `StorageServerInterface::getKeyValues`, `GetKeyValuesRequest`, `KeyRangeMap<bool>`, `IRateControl`, and version-vector helpers such as `addSSIdTagMapping` and `getLatestCommitVersion`.

Control flow: `start` logs the checker id and calls `_start`; `_start` exits for empty assignments, may mimic tester failure in simulation, then calls `checkDataConsistencyUrgent` at epoch 0. The check resolves shards intersecting requested ranges, decodes source storage servers, fetches interfaces, reads each shard chunk at a fresh read version from all source replicas, compares data and `more` flags against the first valid replica, rate-limits by reply bytes, and advances by last key until the shard is exhausted.

State and persistence behavior: The workload does not write application data. It reads system metadata and direct storage-server data, tracks failed ranges in memory, and recursively retries coalesced failed ranges until `CONSISTENCY_CHECK_URGENT_RETRY_DEPTH_MAX`. Persistent effects are limited to trace events; version-vector mode mutates the client-side SSID/tag cache on the `Database` object.

Dependencies/integration: It integrates tester assignment state (`rangesToCheck`, `sharedRandomNumber`), key-server metadata, server list metadata, storage RPCs, simulator failure injection, client/server knobs, and Flow actor retry semantics. It disables no background workloads itself, so callers must consider interference.

Risks: Direct storage RPC reads are sensitive to server removal, failed machines, version-vector metadata, backward-read settings, and transient `getKeyValues` failures. Inconsistencies are traced but do not immediately stop the shard loop; unavailable replies cause retry epochs. Retry depth exhaustion converts to `consistency_check_urgent_task_failed`.

Test signals: Key signals are `ConsistencyCheckUrgent_TesterStartTask`, shard complete/failed events, `ConsistencyCheck_DataInconsistent` with uniqueness/mismatch counts, retry-depth events, and final tester exit reason. A successful workload reaches `CompleteCheck`; validation failure is propagated by throwing urgent-task-failed.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/ConsistencyCheckUrgent.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/CpuProfiler.cpp -->
# sources/storage-engines/foundationdb/fdbserver/workloads/CpuProfiler.cpp

Purpose: Defines `CpuProfiler`, a tester workload that turns Flow CPU profiling on and off across selected cluster workers for a configured window.

Important APIs/types/functions: `CpuProfilerWorkload`, `updateProfiler`, `getWorkers`, `WorkerInterface`, `ProfilerRequest`, worker `clientInterface.profiler`, `timeoutError`, and `PerfMetric` integration. Options include `initialDelay`, `duration`, and a list of process-class `roles`.

Control flow: `setup` is a no-op. `start` waits `initialDelay`, enables profiling on client 0, optionally delays for `duration`, and disables profiling. If `duration <= 0`, `check` disables profiling instead. `updateProfiler(true)` discovers workers, filters by role, records `profilingWorkers`, sends enable requests with output filenames based on worker address, and marks `success=false` if any enable reply is absent.

State and persistence behavior: Runtime state is the selected worker list and success flag. The workload causes worker-side profiler files named like `ip.port.profile.bin` to be written outside FDB key-value state. There are no database mutations.

Dependencies/integration: It depends on tester `dbInfo`, worker discovery from `TesterInterface`, the worker profiler RPC, trace logging, and Flow profiler support on target processes.

Risks: Only client 0 does work, so multi-client runs depend on that client surviving. Role strings must match process-class text. Disable replies are not used to update `success`, so failures during shutdown are mostly trace-level. A 60 second timeout bounds enable/disable RPC hangs.

Test signals: `SignalProfilerOn`, `SignalProfilerOff`, `DoneSignalingProfiler`, generated profile files, and final `check()` returning `success`.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/CpuProfiler.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/Cycle.cpp -->
# sources/storage-engines/foundationdb/fdbserver/workloads/Cycle.cpp

Purpose: Implements `Cycle`, a transactional integrity workload that maintains a single directed cycle over `nodeCount` keys while concurrent clients repeatedly reverse three links. It is a broad read/write conflict, clear-range, tracing, and final data-shape check.

Important APIs/types/functions: `CycleWorkload`, `bulkSetup`, `cycleClient`, `cycleCheck`, `cycleCheckData`, `key`, `value`, `keyRange`, `badRead`, `PerfIntCounter`, `PerfDoubleCounter`, `Span`, `FDBTransactionOptions::SPAN_PARENT`, and simulator speed-up hooks.

Control flow: Setup optionally disables unseed checking and bulk-loads keys unless `skipSetup`. `start` launches `actorCount` timed `cycleClient` actors. Each client picks a random node, reads the next three links, clears a range around `r`, writes a reversed local segment, commits with retry accounting, and records latency. `check` detects client errors and client 0 scans the whole key range to verify the cycle length and key order.

State and persistence behavior: Persistent state is the cycle encoded as key/value pairs under `keyPrefix`, where values point to the next node. Runtime state is counters and client futures. The workload intentionally uses clear-range plus point writes to exercise mutation ordering and storage-engine point-delete conversion.

Dependencies/integration: It uses `BulkSetup.h`, Native API transactions, deterministic randomness, Flow tracing, simulator knobs for read-window recovery, and tester performance metrics.

Risks: Final validation requires reading `nodeCount + 1` keys and can suffer `transaction_too_old`; after many retries simulation is sped up. Missing values are traced but dereferenced, so true corruption can crash fast. Metrics divide by transaction count, which assumes at least one successful transaction.

Test signals: `TestFailure` reasons for node count, key changes, invalid values, shorter/longer cycles; retry counters by error type; approximate read/write rows per simulated second; and no client future errors.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/Cycle.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/DDBalance.cpp -->
# sources/storage-engines/foundationdb/fdbserver/workloads/DDBalance.cpp

Purpose: Defines `DDBalance`, a synthetic data-distribution stress workload that repeatedly moves many keys between logical bins to produce sustained key movement and latency metrics.

Important APIs/types/functions: `DDBalanceWorkload`, `ddbalanceSetup`, `ddbalanceSetupRange`, `ddBalanceMover`, `ddBalanceWorker`, `setKeyIfNotPresent`, `databaseWarmer`, `DDSketch<double>`, and counters for operations, retries, and bin shifts.

Control flow: Setup shuffles batched object ranges and writes initial keys into a random `currentbin`, optionally warming the database. `start` runs `moversPerClient` timed mover actors. Each mover picks a new destination bin, launches workers over slices of `nodesPerActor`, and each worker reads source keys, writes destination keys, clears sources, retries whole transaction chunks, and verifies it moved all expected keys.

State and persistence behavior: Persistent state is a set of formatted keys `(bin, object, mover, client)` with values derived from object number. Runtime state tracks current bin drift, measured latencies, and counters. Key-space drift can push future destination bins beyond the original `binCount` range to vary shard placement.

Dependencies/integration: It uses Native API transactions, `WorkloadUtils` database warming, deterministic random bin selection, Poisson pacing, and DDSketch percentile metrics.

Risks: `nodesPerActor = nodes / (actorsPerClient * clientCount)` can truncate coverage. The workload asserts on lost keys, so setup collisions or repeated failed reads become fatal. Edge-measurement discard changes metric denominators.

Test signals: `LostKeys` is the main correctness failure. Metrics include operations/sec, retries, bin shifts, and mean/median/p90/p98 latencies.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/DDBalance.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/DDMetrics.cpp -->
# sources/storage-engines/foundationdb/fdbserver/workloads/DDMetrics.cpp

Purpose: Implements `DDMetrics`, a small workload that measures how long high-priority data distribution relocations remain in flight after a start delay.

Important APIs/types/functions: `DDMetricsWorkload`, `getHighPriorityRelocationsInFlight`, `work`, `getMasterWorker`, `WorkerInterface::eventLogRequest`, `EventLogRequest("MovingData")`, and the `DDDuration` metric.

Control flow: Client 0 waits `beginPoll`, then polls every 2.5 seconds. Each poll contacts the current master worker, requests the latest `MovingData` event fields, parses `UnhealthyRelocations` via `sscanf`, and stops when the value reaches zero.

State and persistence behavior: No database state is changed. Runtime state is only `ddDone`, the elapsed time from polling start to zero high-priority relocations.

Dependencies/integration: It depends on master worker discovery, event-log field names emitted by data distribution, `QuietDatabase`/server info headers, and tester metrics.

Risks: The workload catches and traces errors without failing `check`, so missing event fields or transient master issues may silently leave `ddDone` at zero. The trace event name contains a spelling typo (`Reliocations`), which matters for log searches.

Test signals: `DDMetricsStarting`, `DDMetricsCheck` with `DIF`, `DDMetricsError`, and `DDDuration`.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/DDMetrics.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/DDMetricsExclude.cpp -->
# sources/storage-engines/foundationdb/fdbserver/workloads/DDMetricsExclude.cpp

Purpose: Defines `DDMetricsExclude`, which excludes a configured storage-server address and measures moving-data volume and duration until data distribution drains the exclusion.

Important APIs/types/functions: `DDMetricsExcludeWorkload`, `excludeServers`, `StatusClient::statusFetcher`, `StatusObjectReader`, `getMovingDataAmount`, `AddressExclusion`, and metrics for peak moving data, queue bytes, in-flight bytes, duration, and throughput.

Control flow: `start` builds an exclusion from `excludeIp` and `excludePort`, calls `excludeServers`, then polls status every 2.5 seconds. It reads `cluster.data.moving_data.in_queue_bytes` and `in_flight_bytes`, updates peaks, and completes when the sum is exactly zero. `check` computes `movingDataPerSec`.

State and persistence behavior: Persistent cluster state is changed through the management exclusion keys. Runtime state records peak byte counts and completion time. There is no explicit include/cleanup in this workload.

Dependencies/integration: It integrates Management API exclusions, status JSON schema, data distribution movement accounting, and tester metrics.

Risks: The hard-coded default address may not exist in many simulations. If `ddDone` remains zero, `movingDataPerSec = peakMovingData / ddDone` risks invalid numeric output. Status schema changes or absent moving-data fields return `-1.0`, which can affect peak logic and liveness.

Test signals: `DDMetricsExcludeCheck`, `DDMetricsExcludeError`, and the five exported moving-data metrics.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/DDMetricsExclude.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/DataDistributionMetrics.cpp -->
# sources/storage-engines/foundationdb/fdbserver/workloads/DataDistributionMetrics.cpp

Purpose: Implements `DataDistributionMetrics`, a `KVWorkload` that stresses ordinary reads/writes while validating the raw data-distribution stats special range and key-selector semantics.

Important APIs/types/functions: `DataDistributionMetricsWorkload`, `ddRWClient`, `resultConsistencyCheckClient`, `_check`, `ddStatsRange`, `JSONSchemas::dataDistributionStatsSchema`, `schemaMatch`, `ReadYourWritesTransaction`, `RAW_ACCESS`, and timeout transaction options.

Control flow: `start` runs one stats-range consistency checker plus `actorCount` random read/write clients for `testDuration`, then waits five seconds. The checker repeatedly builds begin/end key selectors around random user-key intervals in `ddStatsRange`, reads with a large limit, and verifies the returned boundary keys match selector expectations. `check` on client 0 reads all DD stats, validates each JSON object against schema, counts shards, and computes average bytes.

State and persistence behavior: User data is randomly updated under `keyPrefix`-derived keys. System state is read through `ddStatsRange` with raw access. Runtime counters track commits and selector-result errors.

Dependencies/integration: Depends on `KVWorkload` node options, DD stats special keyspace, JSON schema definitions, Native API range behavior, and client timeout handling.

Risks: Timeouts are intentionally tolerated, but other special-range errors feed `onError`. The selector consistency assumptions can be broken by multi-RPC range reads, so the code guards only when `result.size() > 1`. Schema validation is strict and can fail on DD stats format changes.

Test signals: Any `errors` counter causes `TestFailure`. Other signals are `DataDistributionStatsSchemaValidationFailed`, `NumShards`, `AvgBytes`, and commit count.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/DataDistributionMetrics.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/DataLossRecovery.cpp -->
# sources/storage-engines/foundationdb/fdbserver/workloads/DataLossRecovery.cpp

Purpose: Tests recovery behavior after intentional data loss: a shard is manually moved to a single storage server, that process is killed, data distribution is re-enabled with the dead address excluded, and the key is expected to disappear before being writable again.

Important APIs/types/functions: `DataLossRecoveryWorkload`, `disableDDAndMoveShard`, `moveKeys`, `MoveKeysParams`, `MoveKeysLock`, `setDDMode`, `excludeServers`, `checkForExcludingServers`, `getStorageServers`, `GetStorageMetricsRequest`, `getAddressesForKey`, and simulator `killProcess`.

Control flow: Client 0 writes and verifies an initial key, disables DD, chooses a live unprotected storage server, locks and moves the shard to that single server, validates address placement, kills the process, verifies reads time out, enables DD, excludes the failed address, verifies the value is absent, and writes a new value.

State and persistence behavior: The workload mutates one user key and system DD/exclusion/move-keys metadata. It writes `moveKeysLockOwnerKey`, invokes logical or physical data movement depending on knobs, and relies on exclusion to drop unrecoverable shard data. Runtime `pass` is cleared on validation mismatch.

Dependencies/integration: It disables `RandomMoveKeys` and `Attrition`, uses MoveKeys internals, DD mode controls, management exclusions, storage-server metrics RPCs, simulator process state, and system-key transactions.

Risks: This is highly simulation- and timing-sensitive. Selecting a dead server before DD cleanup would hang without the metrics probe. Move-key conflicts and finish retries are expected transient errors. Assertions assume a single-address placement after the move.

Test signals: Phase traces, `TestKeyMoved`, `TestTeamKilled`, `ExcludedFailedServer`, read timeout verification, absent value verification, and final `check()` returning `pass`.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/DataLossRecovery.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/DcLag.cpp -->
# sources/storage-engines/foundationdb/fdbserver/workloads/DcLag.cpp

Purpose: Defines `DcLag`, a gray-failure simulation workload that clogs a primary satellite TLog's outbound communication to remote data-center processes and verifies log routers can detect and recover from data-center lag.

Important APIs/types/functions: `DcLagWorkload`, `clogTlog`, `unclogAll`, `fetchDatacenterLag`, `clogClient`, `StatusClient::statusFetcher`, `RecoveryState`, `fdbSimulationPolicyState().remoteDcId`, and simulator `clogPair`/`unclogPair`.

Control flow: After `startDelay`, client 0 waits for full recovery, finds remote process IPs and primary satellite TLogs, clogs one satellite TLog to each remote IP for the test duration, polls status every five seconds, marks lag detected when seconds approach `LOG_ROUTER_PEEK_SWITCH_DC_TIME`, and unclogs once lag later falls below five seconds.

State and persistence behavior: No database data is written. Runtime state is the list of clogged IP pairs and `lagged` flag. Simulator network state is modified and should be cleaned by `unclogAll` only on the normal recovered path.

Dependencies/integration: It disables `Attrition`, relies on multi-region/satellite log configuration, status JSON `cluster.datacenter_lag`, recovery state updates, and simulator networking.

Risks: If no satellite TLogs exist, the test skips. If the actor times out before recovery, clogged pairs may remain because there is no destructor cleanup. Status field absence causes polling to continue with empty optionals.

Test signals: `DcLagDetected`, `DcLagRecovered`, `DcLagNo*` status traces, and timeout/error wrapping under `DcLagError`.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/DcLag.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/DifferentClustersSameRV.cpp -->
# sources/storage-engines/foundationdb/fdbserver/workloads/DifferentClustersSameRV.cpp

Purpose: Implements a multi-cluster simulation workload that probes behavior when two different clusters are read at the same read version and when a connection record switches from one cluster to another.

Important APIs/types/functions: `DifferentClustersSameRVWorkload`, `Database::createSimulatedExtraDatabase`, `_setup`, `advanceVersion`, `doSwitch`, `readerClientSeparateDBs`, `writerClient`, `ClusterConnectionMemoryRecord`, `lockDatabase`, `unlockDatabase`, `runRYWTransaction`, and `minRequiredCommitVersionKey`.

Control flow: Setup advances both original and extra cluster versions to a common high floor. Start launches concurrent separate-cluster readers, a delayed switch actor, and writers on both clusters. `doSwitch` sets a watch, locks both DBs, reads a value/version from the original, copies it to the extra DB, advances the extra DB past that version, switches the connection record, verifies a read at the old version returns the same value or a retryable error, unlocks the extra DB, writes the watched key, waits for the watch, and finally unlocks the original.

State and persistence behavior: Both clusters mutate `keyToRead`; the extra cluster also gets `keyToWatch`. System state is touched through database locks and `minRequiredCommitVersionKey`. Runtime state records `switchComplete`.

Dependencies/integration: Requires exactly one simulated extra database, lock-aware transactions, connection-record switching, watches, and Flow error tracing.

Risks: The workload assumes simulated extra database configuration. Watch completion and old-version reads are timing-sensitive. Errors are generally passed through `onError`, but failure to complete the switch fails `check`.

Test signals: `DifferentClusters_*` trace milestones, reader code probe for different values at same version across clusters, watch completion, and absence of `DifferentClustersSwitchNotComplete`.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/DifferentClustersSameRV.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/DiskDurability.cpp -->
# sources/storage-engines/foundationdb/fdbserver/workloads/DiskDurability.cpp

Purpose: Defines an `AsyncFileWorkload` that repeatedly writes and verifies unbuffered file pages to catch non-durable or torn disk writes.

Important APIs/types/functions: `DiskDurabilityWorkload`, nested `FileBlock`, `FileBlock::test_impl`, `IAsyncFileSystem::open`, `AsyncFileHandle`, `AsyncFileBuffer`, `FlowLock`, `worker`, `syncLoop`, and `_PAGE_SIZE`.

Control flow: Setup opens/creates the configured file with read-write, unbuffered, and uncached flags. Start constructs one `FileBlock` per page, launches a randomized sync loop plus writer actors, and runs them for `testDuration`. Each worker chooses skewed random blocks, serializes access through the block lock, reads previous contents when expected, verifies all int64 words equal the last value, writes a new value across the block, and updates `lastData`.

State and persistence behavior: Persistent state is the test file. Runtime state is per-page `lastData` and locks; it is not persisted across workload restarts. Syncs happen at random intervals up to `syncInterval`.

Dependencies/integration: It relies on Flow async file APIs, `AsyncFileWorkload` options/path handling, deterministic randomness, and OS support for unbuffered/uncached file modes.

Risks: The code increments `newData` from zero rather than from `lastData`, so after the first write later writes use value 1 unless `lastData` is zero; the verification still catches durability mismatch for the previous value. Lock release occurs after successful write, so exceptions can leave a block lock held.

Test signals: `WriteWasNotDurable` with filename, offset, expected/found values is the primary failure; otherwise the workload exports no metrics.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/DiskDurability.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/DiskDurabilityTest.cpp -->
# sources/storage-engines/foundationdb/fdbserver/workloads/DiskDurabilityTest.cpp

Purpose: Implements `DiskDurabilityTest`, a database-backed durability ledger for a raw file. It verifies recorded pages, writes new pages, syncs the file, then records page values in FoundationDB.

Important APIs/types/functions: `DiskDurabilityTest`, `encodeValue`, `encodeKey`, `decodeValue`, `decodeKey`, `encodePage`, `decodePage`, `IAsyncFileSystem::open`, `IAsyncFile::sync`, and transaction range reads under a configurable prefix.

Control flow: Client 0 opens a locked unbuffered/uncached file, aligns a page buffer, reads all stored page ledger entries from `range`, validates on-disk pages against expected encoded values, then loops forever. Each loop chooses existing and appended pages, clears their ledger keys, increments a `syncs` metric key after the first cycle, commits, writes page buffers to disk, waits for writes, syncs, and commits new ledger entries.

State and persistence behavior: Persistent state is split between the file and FDB keys under `/DiskDurabilityTest/` by default. Clearing ledger entries before file writes models in-flight pages as unverifiable until sync and second commit complete.

Dependencies/integration: Uses Native API transactions, Flow file I/O, `fmt::print`, and tester single-client execution.

Risks: A crash between file sync and ledger commit leaves durable data untracked but safe; a crash after ledger commit with bad disk contents is detected next run. The unused read-version future hides latency but is not awaited. The loop has no duration timeout inside this file and relies on tester cancellation.

Test signals: `ValidationError` trace or thrown `operation_failed` on mismatch, `Verified` trace with page counts, and the `syncs` metric key.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/DiskDurabilityTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/DiskFailureInjection.cpp -->
# sources/storage-engines/foundationdb/fdbserver/workloads/DiskFailureInjection.cpp

Purpose: Implements a failure-injection workload and failure-injector factory that sends disk delay and/or bit-flip chaos commands to randomly selected storage workers, then verifies chaos metrics appear.

Important APIs/types/functions: `DiskFailureInjectionWorkload`, `injectDiskDelays`, `injectBitFlips`, templated `diskFailureInjectionClient`, `reSendChaos`, `chaosGetStatus`, `periodicEventBroadcast`, `SetFailureInjection`, `latestEventOnWorkers`, and `FailureInjectorFactory`.

Control flow: Client 0 optionally waits `startDelay`, repeatedly fetches storage workers, chooses unchosen addresses, and sends throttle/corrupt commands until configured counts are met. A parallel broadcaster periodically re-sends commands to chosen workers after restarts and fetches `ChaosMetrics`; verification mode runs until non-zero metrics are found, otherwise execution is bounded by `testDuration`.

State and persistence behavior: No FDB keyspace writes occur. Runtime state is `chosenWorkers`; simulator state may mark `corruptWorkerMap[address]=true`. Worker-side failure injection settings are volatile and are re-broadcast to survive worker restarts.

Dependencies/integration: It extends `FailureInjectionWorkload`, disables `Attrition`, uses worker `setFailureInjection` RPCs, storage worker discovery, worker event logs, simulator policy state, and chaos metrics fields `DiskDelays` and `BitFlips`.

Risks: It currently targets storage workers only. Command futures inside `diskFailureInjectionClient` are not awaited by the caller, so errors are traced asynchronously. If a complete storage list cannot be fetched, chaos selection is skipped. Metric lookup tolerates missing attributes but rethrows other errors.

Test signals: `ChaosDisabled`, `DiskFailureInjectionFailed`, `ResendChaos`, `FoundChaos`, `ChaosCouldNotGetStorages`, and non-zero chaos metric counts.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/DiskFailureInjection.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/ExcludeIncludeStorageServersWorkload.cpp -->
# sources/storage-engines/foundationdb/fdbserver/workloads/ExcludeIncludeStorageServersWorkload.cpp

Purpose: Creates repeated storage-server exclude/include churn in simulation to exercise RateKeeper bookkeeping when many storage servers leave and rejoin.

Important APIs/types/functions: `ExcludeIncludeStorageServersWorkload`, `workloadMain`, `includeServers`, `excludeServers`, `checkForExcludingServers`, `NativeAPI::getServerListAndProcessClasses`, `logsKey`, `decodeLogsValue`, `dbInfo->logSystemConfig`, `AddressExclusion`, and simulator protected-address checks.

Control flow: Client 0 only, simulation only. Each round first includes everything, then reads storage servers with system-priority lock-aware access, removes protected addresses, TLogs, and log routers from the candidate set, randomly excludes one remaining storage server, and waits up to 100 seconds for exclusion completion. The loop runs 10 to 79 rounds unless too many timeouts or no eligible server exists.

State and persistence behavior: Persistent cluster management state changes through exclusion keys; the workload clears exclusions at the start of each round and at the end to avoid leaving DD stuck. It also sets `allowLogSetKills=false` in simulator policy.

Dependencies/integration: It disables all other failure-injection workloads, depends on server-list and log metadata, data distribution exclusion machinery, and RateKeeper side effects checked by broader simulation validation.

Risks: It can quit early by design when all SS are colocated with TLogs/log routers or exclusions do not finish. It assumes excluding candidates without TLog/log-router roles preserves availability.

Test signals: `WorkloadStart`, `QuitEarlyNoEligibleSSToExclude`, `QuitEarlyNotCompleteServerExclude`, and `WorkloadFinish` with timeout count.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/ExcludeIncludeStorageServersWorkload.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/ExternalWorkload.cpp -->
# sources/storage-engines/foundationdb/fdbserver/workloads/ExternalWorkload.cpp

Purpose: Provides the `External` workload adapter that dynamically loads a shared library and runs a C++ or C workload implementation through FoundationDB's workload plugin interfaces.

Important APIs/types/functions: `ExternalWorkload`, `FDBWorkloadContext`, `FDBWorkload`, `FDBLoggerImpl`, `FDBPromiseImpl`, C API translators for metrics, promises, and context, `loadLibrary`, `loadFunction`, `ThreadSafeDatabase`, `ThreadSafeTransaction`, `workloadFactory`, and `workloadCFactory`.

Control flow: The constructor resolves `libraryPath/lib<name>`, loads it, then either obtains a C `workloadCFactory` or C++ `workloadFactory`, creates the named workload, and calls `init`. `setup`, `start`, and `check` wrap the tester `Database` as a `ThreadSafeDatabase`, pass a generic promise into the external workload, and await the result. Metrics are converted from `FDBPerfMetric` to tester `PerfMetric`.

State and persistence behavior: Persistent state is owned by the external workload. This adapter owns the dynamic library handle, external workload instance, and success flag. It closes the library in the destructor. C promise/context wrappers allocate memory that external code must free through provided vtables.

Dependencies/integration: It bridges Flow main-thread scheduling, thread futures, platform dynamic loading, trace logging, workload API versioning, and simulator process identity.

Risks: ABI/API mismatches, missing symbols, and external workload bugs become runtime failures. `keepAlive` futures are called but not retained, so database lifetime depends on external promise completion behavior. The factory variable is named `CycleWorkloadFactory` despite registering `ExternalWorkload`, which is confusing but local symbol naming only.

Test signals: `ExternalWorkloadLoad`, `ExternalWorkloadLoadError`, `ExternalCFactoryNotFound`, `ExternalFactoryNotFound`, `WorkloadNotFound`, `ExternalWorkloadFailure`, external trace events, and external metric output.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/ExternalWorkload.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/FailoverWithSSLag.cpp -->
# sources/storage-engines/foundationdb/fdbserver/workloads/FailoverWithSSLag.cpp

Purpose: Tests that regional failover does not complete while remote storage servers lag behind primary, even if remote TLogs are in sync.

Important APIs/types/functions: `FailoverWithSSLagWorkload`, `findAndClogRemoteStorages`, `clogUnclogRemoteStorages`, `fetchStorageServerLag`, `waitForRemoteDataCenterToLag`, `failover`, `doFailover`, `ManagementAPI::changeConfig`, `waitForPrimaryDC`, `StatusClient`, and simulator `clogPair`.

Control flow: In simulation, client 0 sets usable regions to two, waits for full recovery, finds remote TLog IPs and remote storage process IPs, clogs TLog/storage communication both ways, waits until storage lag exceeds `MAX_VERSION_DIFFERENCE`, starts failover by disabling the primary, and races failover completion against a 100 second delay. If failover completes while clogged, the test fails; otherwise it unclogs and expects failover to complete with lag below threshold.

State and persistence behavior: No user data is written. Cluster configuration changes via `changeConfig` and simulator network clogs are the main state changes. Runtime `testSuccess` records failure.

Dependencies/integration: Disables all failure injection, depends on multi-region simulation, status JSON lag fields, recovery state, log-system config, remote DC locality, and management config strings from simulation policy.

Risks: Missing remote TLogs or storages marks failure. Clogged connections are not cleaned in a destructor. Status lag fields are required; absence causes indefinite waiting.

Test signals: `SSLag`, `LagInfo`, `FailoverBegin`, `FailoverComplete`, failure by `testSuccess=false`, and `FailoverWithSSLagError`.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/FailoverWithSSLag.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/FastTriggeredWatches.cpp -->
# sources/storage-engines/foundationdb/fdbserver/workloads/FastTriggeredWatches.cpp

Purpose: Exercises watch trigger latency by setting watches on random keys, changing those keys, and asserting the watch-trigger-to-visible-read version lag remains bounded.

Important APIs/types/functions: `FastTriggeredWatchesWorkload`, `_setup`, `_start`, `setter`, `keyForIndex`, `ReadYourWritesTransaction`, `watch`, `getCommittedVersion`, `SERVER_KNOBS->VERSIONS_PER_SECOND`, and `MAX_VERSIONS_IN_FLIGHT`.

Control flow: Client 0 initializes every other key to a default value. During start, it repeatedly chooses a key and optional random value/clear, starts a delayed setter transaction, then loops reading the key. If the desired value is not visible, it creates a watch, commits it with a dummy conflict range, waits for the watch, then reads again. After the setter completes, it computes version delta and asserts it is below the allowed threshold unless versions in flight are already high.

State and persistence behavior: Persistent state is a fixed key set generated from encoded doubles in fixed-width byte strings. Values are set or cleared. Runtime state includes last read version, watch commit version, and counters, though operation/retry counters are not incremented in the current code.

Dependencies/integration: Disables `Attrition`, uses watches, RYW transactions, server knobs, deterministic key generation, and tester metrics.

Risks: Recoveries can bump versions enough to violate the assertion, hence attrition is disabled. The `clients` vector is unused for the main actor, so `check` mostly returns true unless future code adds clients. Version-delta assertion is timing-sensitive.

Test signals: Assertion failure in `_start`, `FastWatchError`, and latency/counter metrics, though counters may remain zero.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/FastTriggeredWatches.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/FileSystem.cpp -->
# sources/storage-engines/foundationdb/fdbserver/workloads/FileSystem.cpp

Purpose: Models a file metadata workload with indexed paths, users, servers, deletion state, modification queries, deletion-count queries, and optional concurrent writes.

Important APIs/types/functions: `FileSystemWorkload`, `FileSystemOp`, `RecentModificationQuery`, `ServerDeletionCountQuery`, `initializeFile`, `nodeSetup`, `operationClient`, `writeClient`, `modificationQuery`, `deletionQuery`, `DDSketch`, and formatted key helpers.

Control flow: Setup partitions file IDs across clients, shuffles batches, and initializes metadata plus secondary indexes. Start warms the selected query briefly, resets counters, optionally launches write actors, then launches query actors paced by Poisson delays. Query mode is either recent modifications by user using reverse key selectors or deletion counts by server scanning index pages. Writers randomly toggle deletion state or update file size and last-updated time.

State and persistence behavior: Persistent keys include `/files/id/<id>` metadata, `/size`, `/server`, `/deleted`, `/created`, `/lastupdated`, `/userid`, user updated/path indexes, server deleted index, and global path index. Runtime state tracks query/write counters and latency sketches. Deletion toggles maintain server deleted index entries.

Dependencies/integration: Uses Native API transactions, deterministic random metadata generation, key-selector range reads, Poisson pacing, and DDSketch percentile metrics.

Risks: Some metadata writes duplicate `/server` intentionally/accidentally. User modification indexes are only created during initialization; write updates change `lastupdated` but do not update the user updated index, limiting realism. Query operation object is shared by concurrent actors but stateless.

Test signals: `FileSetupOK`, optional query traces, operations/sec, writes/sec, read latency percentiles, and median write latency.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/FileSystem.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/FuzzApiCorrectness.cpp -->
# sources/storage-engines/foundationdb/fdbserver/workloads/FuzzApiCorrectness.cpp

Purpose: Defines `FuzzApiCorrectness`, a brittle but broad random API fuzzer for thread-safe transactions, key/value limits, special keys, system-key access, conflict ranges, watches, atomic ops, transaction options, and error contracts.

Important APIs/types/functions: `ExceptionContract`, `FuzzApiCorrectnessWorkload`, `BaseTest`, `BaseTestCallback`, test cases `TestSetVersion`, `TestGet`, `TestGetKey`, `TestGetRange0..3`, `TestGetAddressesForKey`, `TestAddReadConflictRange`, `TestAtomicOp`, `TestSet`, `TestClear0..2`, `TestWatch`, `TestAddWriteConflictRange`, `TestSetOption`, and `TestOnError`.

Control flow: Constructor randomizes key layout, system/special-key modes, density, clear sizes, and registers test cases once. Setup creates a `ThreadSafeDatabase`. `loadAndRun` initializes random data batches, then repeatedly runs `randomTransaction`. Each random transaction creates many asynchronous operations, waits for random subsets, waits for all, and commits; operation-specific classes create futures or callbacks and validate expected/possible/forbidden errors.

State and persistence behavior: Persistent data is randomized user/system key data, with protected system ranges avoided for writes. Runtime state includes operation id, created tenant placeholders, key prefix map, and success. `writeBarrier` clears `normalKeys` with a system-key conflict to prevent cancelled write-only reordering.

Dependencies/integration: It uses thread-safe Native API wrappers, transaction options, special key modules, client/server knobs, mutation option metadata, protected system key definitions, deterministic randomness, and Flow futures.

Risks: The file itself documents tenant-era brittleness. Some generated operations intentionally exceed limits. Expected error contracts must track evolving API semantics; otherwise valid behavior can be reported as failure. Large random values/keys can produce large packet traces, remapped to info.

Test signals: Unexpected errors are emitted as severity error from each `Test*` contract; required-but-missing errors are also traced. `FuzzLoadAndRunError`, ignored operation warnings, and final `check()` success are the main guard outputs.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/FuzzApiCorrectness.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/GcGenerations.cpp -->
# sources/storage-engines/foundationdb/fdbserver/workloads/GcGenerations.cpp

Purpose: Tests that with TLog recovery tracking enabled, old TLog generations can be garbage-collected during recovery before the database reaches fully recovered.

Important APIs/types/functions: `GcGenerationsWorkload`, `clogRemoteDc`, `unclogAll`, `dbAvailable`, `generateMultipleTxnGenerations`, `gcGenerationsTestClient`, simulator connection failures, `disableTLogRecoveryFinish`, `logSystemConfig.oldTLogs`, `RecoveryState`, and `getConnectionString`.

Control flow: Client 0 waits `startDelay` and database availability, disables TLog recovery finish, partitions the remote DC from non-remote processes except coordinators, repeatedly enables connection failures, waits for accepting commits, ensures the master is in the primary DC, reboots it to generate old TLog generations, and verifies generation count grows. Then it unclogs, disables connection failures, re-enables recovery finish, repeatedly reboots the master until old generations shrink to at most one, and finally waits for full recovery.

State and persistence behavior: No user key writes occur. Simulator network partition state, connection-failure state, process reboot state, and global simulation policy are mutated. Destructor cleanup unclogs, disables connection failures, and resets `disableTLogRecoveryFinish`.

Dependencies/integration: Disables `Attrition` and `RandomClogging`, relies on remote DC locality, log-system recovery state, coordinator resolution, master election behavior, and TLog generation GC internals.

Risks: Highly timing-sensitive and simulation-only. Remote masters are rebooted while partitioned to force primary-DC coordination; after unclogging the guard is intentionally relaxed. Failure to clean simulator state would damage later workloads, hence explicit destructor cleanup.

Test signals: `PartitionRemoteDc`, `CurrentGenerations`, `AfterMultipleRecovery`, `RebootMasterForGC`, `GcGenerationsWaitingForReduction`, and `GcGenerationsWorkloadFinish`.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/GcGenerations.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/GetEstimatedRangeSize.cpp -->
# sources/storage-engines/foundationdb/fdbserver/workloads/GetEstimatedRangeSize.cpp

Purpose: Implements a focused workload that verifies `getEstimatedRangeSizeBytes(normalKeys)` returns a plausible estimate after optional bulk setup.

Important APIs/types/functions: `GetEstimatedRangeSizeWorkload`, `bulkSetup`, `checkSize`, `sizeIsAsExpected`, `getSize`, `ReadYourWritesTransaction::getEstimatedRangeSizeBytes`, `doubleToTestKey`, and `normalKeys`.

Control flow: Setup bulk-loads `nodeCount` deterministic keys unless `checkOnly` is true. Client 0 start calls `checkSize`, which repeatedly calls `getSize`. `getSize` reads the estimated normal-key range size, traces it, and if outside the broad expected window waits five seconds and retries for up to 300 seconds before returning the last estimate. `checkSize` asserts the estimate is within range.

State and persistence behavior: Persistent state is the optional bulk-loaded cycle-style key/value set under `keyPrefix`. Runtime state is limited to retry delay accumulation.

Dependencies/integration: Uses `BulkSetup.h`, Native API range-size estimation, client knobs, deterministic key/value encoding, simulator tracing, and workload client gating.

Risks: The expected window is intentionally wide because the API is approximate. If `checkOnly` is used without preloaded data, the assertion will fail. Estimation may lag data distribution/storage metrics enough to consume the full 300 second retry window.

Test signals: `GetSizeResult`, `GetSizeError`, and the final `ASSERT(sizeIsAsExpected(size))`.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/workloads/GetEstimatedRangeSize.cpp -->
