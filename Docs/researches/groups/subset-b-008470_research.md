# subset-b-008470 Research

Grouped research report for the requested FoundationDB source files. Each section is source-tree-aligned and bounded with the exact reconciliation markers.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/fdbserver.cpp -->
# sources/storage-engines/foundationdb/fdbserver/fdbserver.cpp

## Purpose
This is the main `fdbserver` executable entrypoint. It owns process-wide initialization, command-line parsing, network/simulator selection, trace/log setup, knob initialization, role dispatch, and final exit handling for normal server, simulation, tests, maintenance roles, and utility roles.

## Important APIs, Types, and Functions
- `g_rgOptions` defines the SimpleOpt option table for public address, cluster files, roles, memory limits, TLS, tracing, test controls, filesystem validation, blob credentials, MockS3 persistence, authorization keys, and future protocol toggles.
- `ServerRole` enumerates dispatch targets including `FDBD`, `Simulation`, `Test`, `MultiTester`, `UnitTests`, network test roles, KV file utilities, consistency checks, cluster-key change, and `MockS3Server`.
- `CLIOptions` is the parsed runtime configuration object. It stores command line text, data/log paths, memory limits, role, network addresses, TLS config, knobs, localities, blob credentials, profiler config, allowlist, and role-specific fields.
- `CLIOptions::parseArgs`, `parseArgsInternal`, and `parseEnvInternal` populate `CLIOptions`, validate conflicting options, read environment knob/proxy/blob credential settings, seed deterministic randomness, and create or load the cluster connection file as needed.
- `CLIOptions::buildNetwork` and `buildNetworkAddresses` parse/validate public/listen addresses, auto-address selection, TLS consistency with coordinators, secondary address TLS separation, and synthetic consistency-check addresses.
- `getSharedMemoryMachineId` derives a machine/zone identifier shared across server processes via boost shared memory, with platform-specific permissions and deterministic-debug bypass.
- `validateSimulationDataFiles` protects simulation runs from accidental reuse of dirty folders and validates restart expectations.
- `main` runs platform initialization, crash handler setup, buffering, profiling registration, knob setup, network/simulator construction, tracing, role dispatch, network run loop, elapsed-time tracing, and error translation to FDB exit codes.

## Control Flow
Startup begins with platform and crash-handler initialization, standard stream line buffering, profiling registration, and argument parsing. The parser handles immediate-exit commands such as help, version, build flags, and code-probe printing, then validates role requirements and command-line combinations.

`main` resets and initializes server knobs before network creation. Simulation and template roles start the deterministic simulator and install the simulation policy; other roles construct Net2, FlowTransport, TLS, tracing, filesystem, metrics, and address bindings. After common `ProgramStart` tracing and memory monitor setup, execution dispatches by `ServerRole`. `FDBD` starts the real server actor via `fdbd(...)` plus histogram and metrics reporters. Test and consistency roles call `runTests(...)`; network test roles call `networkTestClient` or `networkTestServer`; KV roles call `KVFileCheck`, `GenerateIOLogChecksumFile`, or `KVFileDump`; cluster-key change calls `coordChangeClusterKey`; MockS3 starts the real mock S3 server.

Simulation has a larger pre-run branch: it logs test config early, traces all knob sets, validates allowed directories and files, deletes/creates the simulation data folder for fresh runs, handles restart restore metadata from `restartInfo.ini`, restores snapshotted role files, applies persisted encryption/shard-location knobs, then calls `simulationSetupAndRun` and `g_simulator->run()`.

## State and Persistence Behavior
Persistent state includes cluster connection files, process data directories, tlog spill directories, trace logs, metrics destinations, simulation restart metadata, snapshot/restore files, MockS3 persistence directories, blob credential files, authorization public keys, and optional shared-memory machine IDs. The entrypoint does not implement storage protocols itself but chooses the folders, memory budgets, filesystems, and per-role persistent inputs that downstream actors use.

The parser may synthesize a `ClusterConnectionFile` from a seed file or seed connection string when the target cluster file is absent. Simulation cleanup can recursively erase the simulation data folder for fresh tests, and restart/restore logic selectively deletes non-snapshot files or moves snapshotted files back into role directories. Trace rotation is configured from `rollsize` and max-log-size options, with simulation-specific defaults.

## Dependencies and Integration Points
This file integrates nearly every high-level server subsystem: Flow/Net2, FlowTransport, TLS, simulator, worker process roles, data distributor test harnesses, KV file utilities, MockS3, coordination server utilities, backup blob credential plumbing, metrics, tracing, actor lineage profiling, fault injection, buggify, Swift concurrency hooks, and platform filesystem helpers. It is the executable-level integration point between command-line flags and lower-level server actors.

## Risks and Edge Cases
- Address validation is security- and availability-sensitive: public/listen counts must match, TLS state must match coordinators, and dual addresses must not use the same TLS state.
- Simulation folder cleanup is intentionally destructive for fresh runs; validation must catch non-FDB files before erasing anything.
- Seed cluster file/string handling must avoid conflicting sources and malformed cluster descriptions.
- Memory and cache limits are validated early; bad combinations can cause process exit before network setup.
- Role dispatch depends on options validated earlier. Missing public address for server-like roles, missing `--testservers`, missing target key, or invalid new cluster key are hard failures.
- Shared memory machine ID creation has cross-user/platform permission subtleties.
- The function is large and highly conditional; build flags (`WITH_ROCKSDB`, `FLOW_GRPC_ENABLED`, Swift support, platform macros) materially change behavior.

## Test Signals
This file directly supports `simulation`, `test`, `multitest`, `unittests`, network tests, KV file checks, and consistency checks. Simulation emits `SevError` counts as failure signals and prints random unseed/elapsed times. It also exposes dev flags for unit test parameters, buggify/fault-injection overrides from test files, future protocol version testing, and network implementation selection.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/fdbserver.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/grvproxy/CMakeLists.txt -->
# sources/storage-engines/foundationdb/fdbserver/grvproxy/CMakeLists.txt

## Purpose
This CMake file defines the GRV proxy server component as a static library and wires it into link and unit-test targets.

## Important APIs, Types, and Functions
- `fdb_find_sources(FDBSERVER_GRVPROXY_SRCS)` discovers source files in this directory.
- `add_flow_target(STATIC_LIBRARY NAME fdbserver_grvproxy ...)` builds the static library.
- `add_fdbserver_link_test(fdbserver_grvproxylinktest ...)` validates linkability with `fdbserver_logsystem` and `fdbserver_core`.
- `add_fdbserver_unit_test(fdbserver_grvproxy_test grvproxy ...)` registers GRV proxy unit tests.
- `configure_fdbserver_common_includes`, `target_include_directories`, and `target_link_libraries` set public/private include paths and dependencies.

## Control Flow
CMake discovers the directory sources, builds them into `fdbserver_grvproxy`, creates a link test and unit-test executable, exposes `include/` as a public include directory, keeps the source directory private, and links core/logsystem dependencies.

## State and Persistence Behavior
No runtime state is created. The file affects build graph state only.

## Dependencies and Integration Points
The library depends on `fdbserver_core` and `fdbserver_logsystem`, which matches the runtime GRV proxy dependency on server knobs, worker interfaces, and log-system committed-version confirmation.

## Risks and Edge Cases
Because sources are discovered automatically, new files under the directory can enter the target without explicit listing. Include visibility is significant: only `include/` is public, so private headers such as `GrvQueueDelay.h` remain internal to this component.

## Test Signals
The build file registers both a link test and a `grvproxy` unit-test target. `GrvQueueDelayTests.cpp` and `GrvTransactionRateInfo.cpp` unit tests are pulled in through source discovery.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/grvproxy/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/grvproxy/GrvProxyServer.cpp -->
# sources/storage-engines/foundationdb/fdbserver/grvproxy/GrvProxyServer.cpp

## Purpose
This file implements the GRV proxy role. GRV proxies accept `GetReadVersionRequest`s from clients, queue them by priority, enforce ratekeeper transaction-rate limits, ask the master/log system for committed read versions, attach health/throttle/version-vector metadata, and serve global configuration and health metrics.

## Important APIs, Types, and Functions
- `GrvProxyStats` owns counters, queue-size gauges, rate/limit gauges, latency samples, latency bands, recent-request buckets, and histograms for committed-version and epoch-confirmation timing.
- `GrvProxyData` holds the proxy interface, master interface, request stream, DB info, log system, global config DB handle, latency-band config, version-vector cache, and committed-version tracking fields.
- `globalConfigMigrate`, `globalConfigRefresh`, and `globalConfigRequestServer` migrate legacy client-info keys and serve cached global configuration through the GRV proxy interface.
- `getRate` polls ratekeeper with released transaction counts, local version, tag counters, and detailed-metric cadence; it updates `GrvTransactionRateInfo`, health metrics, client tag throttles, and lease state.
- `queueGetReadVersionRequests` is the intake actor. It accepts GRV requests, applies queue memory pressure rules, applies `maxGrvQueueDelayMS` rejection, updates counters, and appends requests to system/default/batch queues.
- `rejectIncomingForMaxGrvQueueDelay`, `rejectForMaxGrvQueueDelay`, `dropRequestFromQueue`, and `proxyGRVThresholdExceeded` implement queue-delay rejection and queue-overflow drop/error paths.
- `transactionStarter` is the queue-drain actor. It wakes on the GRV timer, chooses requests by priority, checks normal and batch rate budgets, sends committed-version RPCs, and schedules reply actors.
- `getLiveCommittedVersion` confirms epoch liveness unless the request is causal-read-risky, asks the master for a raw committed version, updates version-vector cache and committed-version state, and returns a `GetReadVersionReply`.
- `sendGrvReplies` sends a shared read-version reply to each batched request, applies minimum-known-committed-version flag behavior, version-vector deltas, tag throttle info, process busy time, mid-shard size, and sustained ratekeeper throttle flags.
- `monitorDDMetricsChanges` periodically asks the data distributor for `midShardSize` to include in GRV replies.
- `grvProxyServerCore`, `checkRemoved`, and `grvProxyServer` compose the role actors, handle DB-info/log-system changes, and translate expected termination errors.

## Control Flow
`grvProxyServer` races `grvProxyServerCore` against `checkRemoved`. Core waits until the master lifetime and recovery state are usable, constructs the log system, applies latency-band config, and starts actors for wait-failure service, role tracing, transaction starting, health metrics, global config, and optional last-commit updating.

Incoming GRV requests are received by `queueGetReadVersionRequests`. Under queue pressure, lower-priority queued work may be dropped to admit higher-priority work. Requests carrying `maxGrvQueueDelayMS` are estimated before queue insertion and can be rejected immediately. Otherwise they are counted and enqueued by priority; an idle queue schedules the GRV timer.

When the timer fires, `transactionStarter` starts a release window in normal and batch `GrvTransactionRateInfo` objects. It repeatedly selects the next request from system, default, then batch queues, subject to max requests per batch and rate budgets. Selected requests are split into causal-risky and non-risky vectors based on the low flag bit. For each non-empty vector it calls `getLiveCommittedVersion` and sends replies asynchronously. It then updates budgets, throttling flags, queue processed percentages, and timer rescheduling.

Ratekeeper polling runs independently through `getRate`. It reacts to DB-info changes, sends `GetRateInfoRequest`s, handles detailed health metric cadence, updates local rate limiters, replaces client tag throttle maps, and expires leases by disabling rate limiters and marking `GrvRateLeaseState::Expired`.

## State and Persistence Behavior
Most state is in memory: request queues, queue transaction counts, smoothed rate budgets, ratekeeper lease state, client tag counters/throttles, health metric snapshots, latency histograms, version-vector cache, global config cache, and committed-version tracking. Persistent reads/writes are limited to the global-config migration/refresh transaction paths and log-system/master committed-version confirmation. The GRV proxy does not persist its queues; request state lives in actor memory and replies or errors are sent before removal.

## Dependencies and Integration Points
The file integrates with `GrvProxyInterface`, `CommitProxyInterface` request types, master committed-version RPCs, `LogSystem::confirmEpochLive`, ratekeeper `getRateInfo`, data distributor metrics, `HealthMetricsRequestServer`, `GrvQueueDelay`, `GrvTransactionRateInfo`, global configuration keys, version-vector support, Flow actors/futures, tracing, histograms, latency metrics, and worker failure services.

## Risks and Edge Cases
- Queue pressure drops lower-priority requests to admit higher priority; accounting must keep `txnRequestOut`, queue sizes, and `GrvQueueTransactionCounts` synchronized.
- `maxGrvQueueDelayMS` rejection depends on estimated remaining delay, elapsed request time, and ratekeeper lease state. Expired leases reject bounded requests immediately.
- Ratekeeper lease expiry disables rate info smoothly but may lead to zero/infinite delay estimates depending on caller path.
- Version-vector cache deltas and reply metadata are conditional on `ENABLE_VERSION_VECTOR`; misuse can inflate reply size or send stale deltas.
- Causal-read-risky requests skip epoch confirmation, while non-risky requests transform log/master failures; incorrect flag grouping could affect read safety.
- `GetReadVersionRequest::FLAG_CAUSAL_READ_RISKY == 1` is assumed with a `static_assert`, so bit layout changes require code review.
- Global config refresh serves only cached data at or above the client's last-known version; otherwise it returns `future_version`.
- `getRecentRequests` divides by remaining bucket-window time; bucket timing assumptions matter for load balancing signals.

## Test Signals
The build target includes GRV proxy unit tests. `GrvQueueDelayTests.cpp` exercises queue-delay helper behavior used by this file. `GrvTransactionRateInfo.cpp` contains a unit test for throttling to a target rate. Runtime test probes and trace events cover ratekeeper lease expiry, queue delay rejection, queue memory pressure, tag throttling, master/tlog failure handling, and latency metrics.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/grvproxy/GrvProxyServer.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/grvproxy/GrvQueueDelay.cpp -->
# sources/storage-engines/foundationdb/fdbserver/grvproxy/GrvQueueDelay.cpp

## Purpose
This file implements queue accounting and delay-estimation helpers for GRV proxy `maxGrvQueueDelayMS` rejection. It separates system/default/batch transaction counts and uses normal and batch rate limiters to estimate remaining queue delay.

## Important APIs, Types, and Functions
- `GrvQueueTransactionCounts::add/remove(TransactionPriority, int64_t)` updates per-priority queued transaction counts with nonnegative assertions.
- `add/remove(GetReadVersionRequest const&)` adapts request priority and transaction count into the accounting methods.
- `normalRateQueuedTransactions()` returns system plus default queued work.
- `batchRateQueuedTransactions()` returns system plus default plus batch queued work.
- `estimateRemainingGrvQueueDelay(...)` calls `GrvTransactionRateInfo::estimateDelay` for normal work and, for batch-priority requests, additionally for the batch limiter.
- `shouldRejectForMaxGrvQueueDelay(...)` implements the final threshold decision using request option presence, expired lease override, elapsed queue delay, and remaining delay.

## Control Flow
Priority accounting treats `IMMEDIATE` and above as system, `DEFAULT` through below immediate as default, and below default as batch. Delay estimation always computes normal-rate delay from normal queued transactions. For batch requests it also computes a batch-rate delay from all queued transactions. Rejection first ignores requests without `maxGrvQueueDelayMS`, then rejects immediately if the rate lease is expired, otherwise compares clamped elapsed queue delay plus remaining delay to the request's millisecond threshold.

## State and Persistence Behavior
State is caller-owned and in-memory only. This file mutates `GrvQueueTransactionCounts` fields and reads request timestamps/options. It persists nothing.

## Dependencies and Integration Points
It depends on `GetReadVersionRequest`, `TransactionPriority`, `GrvTransactionRateInfo`, Flow time via `now()`, and server assertions. `GrvProxyServer.cpp` uses these helpers during queue insertion and queue removal.

## Risks and Edge Cases
- Remove operations assert counts remain nonnegative, so any queue-accounting mismatch becomes a hard assertion failure.
- Batch-priority delay has two dimensions: normal-rate and batch-rate. Callers must check both estimates.
- If ratekeeper lease is expired, bounded-delay requests are rejected independent of numeric delay.
- Future request timestamps are clamped by `std::max(0.0, elapsedQueueDelay)` to avoid negative elapsed time reducing the estimate.

## Test Signals
`GrvQueueDelayTests.cpp` covers transaction-count aggregation, normal/batch delay estimates, disabled rate-info behavior, and rejection decisions including expired lease and elapsed-time contribution.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/grvproxy/GrvQueueDelay.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/grvproxy/GrvQueueDelay.h -->
# sources/storage-engines/foundationdb/fdbserver/grvproxy/GrvQueueDelay.h

## Purpose
This header declares GRV queue-delay accounting and rejection interfaces used by the GRV proxy to enforce client-specified maximum queue delay.

## Important APIs, Types, and Functions
- `GrvQueueTransactionCounts` stores queued transaction counts split into `systemPriority`, `defaultPriority`, and `batchPriority`; it exposes add/remove overloads and aggregate normal/batch count queries.
- `GrvQueueDelayEstimate` returns a required `normalRateDelay` and optional `batchRateDelay`.
- `GrvRateLeaseState` models ratekeeper lease knowledge as `Unknown`, `Active`, or `Expired`.
- `estimateRemainingGrvQueueDelay(...)` estimates delay for a request with a given priority and transaction count against current queue counts and rate info objects.
- `shouldRejectForMaxGrvQueueDelay(...)` decides whether a request should be rejected for its `maxGrvQueueDelayMS` bound.

## Control Flow
The header defines the contract: callers maintain queue counts, estimate remaining delay before or during queue handling, then call the rejection helper with request metadata and optional lease state.

## State and Persistence Behavior
The declared structures are in-memory only and contain primitive counters or delay values. There is no ownership of queues, requests, or persistent storage.

## Dependencies and Integration Points
It includes `CommitProxyInterface.h`, `GrvProxyInterface.h`, `GrvTransactionRateInfo.h`, and Flow. The main integration point is `GrvProxyServer.cpp`, where bounded-delay GRV requests are rejected before queue insertion and queue counts are updated on enqueue/drop/start.

## Risks and Edge Cases
The API accepts raw pointers to rate info objects, so callers must provide valid normal and batch rate limiters. The distinction between normal-rate and batch-rate queued work is central; misclassifying priority changes admission behavior.

## Test Signals
The matching test file covers every public helper and the exposed fields of `GrvQueueTransactionCounts`.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/grvproxy/GrvQueueDelay.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/grvproxy/GrvQueueDelayTests.cpp -->
# sources/storage-engines/foundationdb/fdbserver/grvproxy/GrvQueueDelayTests.cpp

## Purpose
This file contains Flow unit tests for GRV proxy maximum queue-delay logic. It verifies queue count aggregation, delay estimation, disabled rate limiter behavior, and rejection threshold semantics.

## Important APIs, Types, and Functions
- `forceLinkGrvQueueDelayTests()` is a link anchor for the unit tests.
- `makeRateInfo()` builds a `GrvTransactionRateInfo` with a 1-second window, zero empty-queue budget, rate 10, and an active release window.
- `expectedEstimateDelay(...)` mirrors the expected deficit/rate calculation using `START_TRANSACTION_MAX_TRANSACTIONS_TO_START`.
- `expectedShouldReject(...)` mirrors rejection semantics for option absence, expired lease, elapsed queue delay, and threshold comparison.
- Test cases cover `/queueTransactionCounts`, `/remainingDelayEstimate/table`, `/remainingDelayEstimate/disabledRateInfo`, and `/rejectDecision/table`.

## Control Flow
The count test constructs immediate/default/batch `GetReadVersionRequest`s, adds/removes them, and checks direct fields plus aggregate normal/batch counts. The estimate table builds normal and batch rate info objects for each case, seeds queue counts, calls `estimateRemainingGrvQueueDelay`, and verifies expected normal and optional batch delay. The disabled-rate test checks that disabled normal rate info returns zero delay. The rejection table varies `maxGrvQueueDelayMS`, request time offsets, remaining delay, and lease state.

## State and Persistence Behavior
Tests are in-memory only and rely on Flow unit-test assertions. Request timestamps are set relative to `now()`.

## Dependencies and Integration Points
It depends on `GrvQueueDelay.h`, server knobs, and `flow/UnitTest.h`. The cases are targeted at the code path used by `GrvProxyServer.cpp` before enqueuing bounded-delay GRV requests.

## Risks and Edge Cases
The tests explicitly encode that equal-to-threshold is not rejected, over-threshold is rejected, absent option is never rejected even with expired lease and infinite delay, expired lease rejects bounded requests, and future timestamps are clamped rather than producing negative elapsed delay.

## Test Signals
These are the primary regression tests for the queue-delay feature. Passing them signals that helper-level behavior remains stable, though they do not exercise full GRV proxy queue actor integration under concurrency.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/grvproxy/GrvQueueDelayTests.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/grvproxy/GrvTransactionRateInfo.cpp -->
# sources/storage-engines/foundationdb/fdbserver/grvproxy/GrvTransactionRateInfo.cpp

## Purpose
This file implements smoothed transaction-rate limiting for GRV proxy release windows. It tracks allowed rate, release history, available budget, and per-window limits used to decide whether queued transactions may start.

## Important APIs, Types, and Functions
- The constructor initializes `rateWindow`, `maxEmptyQueueBudget`, initial `rate`, and `Smoother` instances.
- `canStart(numAlreadyStarted, count)` checks whether starting additional transactions fits within `min(limit + budget, START_TRANSACTION_MAX_TRANSACTIONS_TO_START)`.
- `estimateDelay(numAlreadyStarted, count)` returns zero if start is allowed or the limiter is disabled, infinity if active rate is zero, otherwise deficit divided by rate.
- `endReleaseWindow(numStarted, queueEmpty, elapsed)` updates budget based on unused/excess limit over elapsed release-window time, caps budget when the queue is empty, and records released count in the smoother.
- `disable()` marks the limiter disabled and smoothly sets target rate to zero.
- `setRate(rate)` validates the new rate, updates current rate, resets smoothing when re-enabling, or smoothly changes target rate when already enabled.
- `startReleaseWindow()` computes current transaction limit from smoothed target rate minus smoothed release rate over the configured rate window.
- Unit-test helpers `mockClient` and `/GrvTransactionRateInfo/Simple` simulate an over-eager client and verify throttling.

## Control Flow
GRV proxy calls `startReleaseWindow()` before draining queues, then repeatedly calls `canStart()` to admit requests, then calls `endReleaseWindow()` with actual started counts and elapsed time. Ratekeeper updates arrive through `setRate()`. Lease expiry calls `disable()`, which avoids abrupt throttling by manipulating the smoother target while causing delay estimation to return zero while disabled.

## State and Persistence Behavior
All state is in memory: rate window, max empty-queue budget, current rate, computed limit, rolling budget, disabled flag, smoothed rate, and smoothed release counts. No persistence occurs.

## Dependencies and Integration Points
It depends on `fdbrpc/Smoother`, server knobs, Flow unit-test support, and GRV proxy code. `GrvProxyServer.cpp` holds one normal limiter and one batch limiter and updates them from ratekeeper replies.

## Risks and Edge Cases
- `budget` can compensate for bursts or prior overuse; incorrect elapsed/window values can over- or under-throttle.
- `limit` can be negative if prior releases exceeded allowed rate.
- `estimateDelay` reports infinity when active rate is zero, but zero when disabled; callers must distinguish disabled lease behavior separately when needed.
- `START_TRANSACTION_MAX_TRANSACTIONS_TO_START` caps release capacity independent of rate math.
- `setRate` asserts finite nonnegative input, so invalid ratekeeper data is fatal.

## Test Signals
The built-in unit test sets the rate to 10 while a mock client attempts 20 transactions per second and asserts roughly 600 starts over 60 seconds. It tests the limiter at a high level but not every budget or queue-empty branch.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/grvproxy/GrvTransactionRateInfo.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/grvproxy/GrvTransactionRateInfo.h -->
# sources/storage-engines/foundationdb/fdbserver/grvproxy/GrvTransactionRateInfo.h

## Purpose
This header declares the GRV proxy transaction-rate limiter class. It documents the release-window model used to enforce ratekeeper-provided transaction rates.

## Important APIs, Types, and Functions
- `GrvTransactionRateInfo(double rateWindow, double maxEmptyQueueBudget, double rate)` constructs limiter state.
- `startReleaseWindow()` computes how many transactions can be released in the current release window.
- `canStart(int64_t numAlreadyStarted, int64_t count) const` tests whether an additional batch can start.
- `estimateDelay(...) const` predicts when the same request would become startable.
- `endReleaseWindow(int64_t numStarted, bool queueEmpty, double elapsed)` adjusts budget and release smoothing after a drain pass.
- `setRate(double rate)` and `disable()` apply ratekeeper updates or lease expiry.
- `getRate()` and `getLimit()` expose current rate and computed limit for stats and admission logic.

## Control Flow
The intended lifecycle is rate updates via `setRate`, repeated release windows with `startReleaseWindow`/`canStart`/`endReleaseWindow`, and `disable` when rate updates stop for too long.

## State and Persistence Behavior
Private state is entirely in memory: rate window, empty-queue budget cap, rate, limit, budget, disabled flag, and two `Smoother` instances.

## Dependencies and Integration Points
The class depends on `fdbrpc/Smoother`. It is used by `GrvProxyServer.cpp` for normal and batch transaction queues, and by `GrvQueueDelay` for delay estimates.

## Risks and Edge Cases
The class exposes a small API but carries nuanced semantics: disabled means no estimated delay, active zero rate means infinite delay, and queue-empty capping prevents stale budget accumulation. Callers must call methods in the documented release-window order.

## Test Signals
The implementation file includes a Flow unit test for simple throttling. Queue-delay tests also indirectly validate `estimateDelay` interaction.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/grvproxy/GrvTransactionRateInfo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/grvproxy/HealthMetricsRequestServer.cpp -->
# sources/storage-engines/foundationdb/fdbserver/grvproxy/HealthMetricsRequestServer.cpp

## Purpose
This file implements a small request server that caches ratekeeper health metrics at the GRV proxy and answers `GetHealthMetricsRequest`s.

## Important APIs, Types, and Functions
- `HealthMetricsRequestServer::HealthMetricsRequestServer(GrvProxyInterface)` stores the GRV proxy interface.
- `update(HealthMetrics const&, bool detailed)` merges new metrics into the normal reply and, for detailed updates, into the detailed reply cache.
- `run()` waits forever on `grvProxy.getHealthMetrics`, then sends either the detailed or normal cached reply based on the request flag.

## Control Flow
`getRate` in `GrvProxyServer.cpp` calls `update` whenever a ratekeeper reply arrives. `grvProxyServerCore` runs `healthMetricsServer.run()` as an actor. Requests are served from the latest cached replies without contacting ratekeeper synchronously.

## State and Persistence Behavior
State is in-memory cached `GetHealthMetricsReply` objects. The normal reply is updated on every health metrics update; the detailed reply is updated only when the source update was detailed. Nothing is persisted.

## Dependencies and Integration Points
It depends on `GrvProxyInterface`, `GetHealthMetricsRequest`, `GetHealthMetricsReply`, and `HealthMetrics`. It is integrated into GRV proxy ratekeeper polling and request serving.

## Risks and Edge Cases
Before the first ratekeeper update, replies contain default-constructed metrics. Detailed requests can return the last detailed snapshot, which may lag normal metrics if detailed updates are less frequent. The loop assumes the GRV proxy stream remains valid for the actor lifetime.

## Test Signals
No dedicated test appears in this subset. Behavior is simple and is mainly exercised by GRV proxy integration tests or health-metric request paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/grvproxy/HealthMetricsRequestServer.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/grvproxy/HealthMetricsRequestServer.h -->
# sources/storage-engines/foundationdb/fdbserver/grvproxy/HealthMetricsRequestServer.h

## Purpose
This header declares the GRV proxy health metrics cache/server used to answer health metric requests from cached ratekeeper data.

## Important APIs, Types, and Functions
- `HealthMetricsRequestServer` owns a `GrvProxyInterface`, a normal `GetHealthMetricsReply`, and a detailed `GetHealthMetricsReply`.
- `update(HealthMetrics const& healthMetrics, bool detailed)` refreshes cached replies.
- `run()` serves the proxy request stream.

## Control Flow
The class is constructed by `grvProxyServerCore`, updated by ratekeeper polling, and run as a long-lived actor.

## State and Persistence Behavior
Only in-memory cached replies are stored. There is no disk or database persistence.

## Dependencies and Integration Points
The header includes `fdbclient/GrvProxyInterface.h` and Flow. It is private to the GRV proxy component and used by `GrvProxyServer.cpp`.

## Risks and Edge Cases
The split between normal and detailed cache means callers can observe different freshness depending on request type. The class has no explicit synchronization because it is used within Flow actor scheduling.

## Test Signals
No direct tests are present in this subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/grvproxy/HealthMetricsRequestServer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/grvproxy/include/fdbserver/grvproxy/GrvProxyServer.h -->
# sources/storage-engines/foundationdb/fdbserver/grvproxy/include/fdbserver/grvproxy/GrvProxyServer.h

## Purpose
This public header exposes the GRV proxy server actor entrypoint to the rest of fdbserver.

## Important APIs, Types, and Functions
- Forward declarations for `InitializeGrvProxyRequest` and `ServerDBInfo` avoid pulling heavier headers into consumers.
- `Future<Void> grvProxyServer(GrvProxyInterface proxy, InitializeGrvProxyRequest req, Reference<AsyncVar<ServerDBInfo> const> db)` starts and supervises a GRV proxy role for a worker.

## Control Flow
Consumers pass the proxy interface, initialization request containing master and lifetime data, and live server DB info. The implementation handles readiness, actor composition, and expected termination errors.

## State and Persistence Behavior
The header owns no state. Runtime state is allocated by the implementation in `GrvProxyData` and associated actors.

## Dependencies and Integration Points
It includes `fdbclient/GrvProxyInterface.h` and Flow. The public include directory makes this entrypoint available outside the `grvproxy` component, especially worker role startup code.

## Risks and Edge Cases
Because this is the public boundary, signature changes affect worker role integration. Forward declarations require implementation/consumer consistency for the request and DB-info types.

## Test Signals
Link tests in the GRV proxy CMake target validate that this public entrypoint links with core/logsystem dependencies.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/grvproxy/include/fdbserver/grvproxy/GrvProxyServer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/include/fdbserver/CoroFlow.h -->
# sources/storage-engines/foundationdb/fdbserver/include/fdbserver/CoroFlow.h

## Purpose
This header provides small interoperability helpers for using Flow futures from coroutine-style code and thread-pool-backed waiting.

## Important APIs, Types, and Functions
- `CoroThreadPool::init()` initializes coroutine/thread-pool support.
- `CoroThreadPool::waitFor(Future<Void>)` blocks or bridges until a Flow future completes.
- `CoroThreadPool::createThreadPool()` creates an `IThreadPool` reference.
- `waitForAndGet(Future<T>)` waits for a non-ready future via `success(f)` and returns the value.
- `waitFor(Future<Void>)` waits and throws the future error if completion is an error.

## Control Flow
Callers initialize the thread pool once, then use `waitFor` helpers to synchronously bridge Flow futures when needed. The templated helper only waits if the future is not already ready.

## State and Persistence Behavior
No persistent state. Any thread-pool state is hidden behind `CoroThreadPool` implementation elsewhere.

## Dependencies and Integration Points
It includes `fdbrpc/fdbrpc.h` for Flow future types and `flow/IThreadPool.h`. `fdbserver.cpp` calls `CoroThreadPool::init()` before network run-loop role dispatch.

## Risks and Edge Cases
Blocking on futures can deadlock if used on the wrong thread or before proper Flow/thread-pool initialization. `waitForAndGet` waits on `success(f)`, then calls `f.get()`, so errors propagate through `get()`.

## Test Signals
No direct tests in this subset; usage is exercised by server startup and any coroutine interop paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/include/fdbserver/CoroFlow.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/include/fdbserver/NetworkTest.h -->
# sources/storage-engines/foundationdb/fdbserver/include/fdbserver/NetworkTest.h

## Purpose
This header declares a small RPC interface and client/server entrypoints for FoundationDB network testing.

## Important APIs, Types, and Functions
- `NetworkTestInterface` contains request streams for unary `test` and streaming `testStream` requests, with constructors for remote address or local network endpoint registration.
- `NetworkTestRequest` carries a key, requested reply size, and reply promise.
- `NetworkTestReply` carries a `Value` payload.
- `NetworkTestStreamingRequest` carries a reply promise stream.
- `NetworkTestStreamingReply` carries stream sequence/ack fields plus an `index`; `expectedSize()` returns an expected large size.
- `networkTestServer()` and `networkTestClient(std::string const&)` are actor entrypoints.

## Control Flow
`fdbserver.cpp` dispatches the `networktestserver` role to `networkTestServer()` and `networktestclient` to `networkTestClient(testServersStr)`. The interface supports both single request/reply and streaming replies.

## State and Persistence Behavior
The declared messages are transient RPC payloads. There is no persistent state.

## Dependencies and Integration Points
It depends on FDB type aliases, fdbrpc request streams, Flow file identifiers, and `INetwork`. It integrates with the executable role system and network transport serialization.

## Risks and Edge Cases
Serialization file identifiers must remain stable for compatibility. `NetworkTestStreamingReply::expectedSize()` advertises a large size, so tests may stress transport buffering/memory. Constructors are declared but implemented elsewhere.

## Test Signals
The entire header exists for network test roles; runtime success/failure comes from those roles rather than unit tests in this subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/include/fdbserver/NetworkTest.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/include/fdbserver/fdbserver_stream_support.h -->
# sources/storage-engines/foundationdb/fdbserver/include/fdbserver/fdbserver_stream_support.h

## Purpose
This header defines Swift interop aliases for selected fdbserver Flow stream/request types, primarily around master/recovery RPC types.

## Important APIs, Types, and Functions
- `SWIFT_FUTURE_STREAM(TYPE)` creates `FutureStream_TYPE` and `FlowSingleCallbackForSwiftContinuation_TYPE` aliases.
- `SWIFT_REQUEST_STREAM(TYPE)` creates `RequestStream_TYPE` aliases.
- Aliases are generated for `UpdateRecoveryDataRequest`, `GetCommitVersionRequest`, `GetRawCommittedVersionRequest`, and `ReportRawCommittedVersionRequest`.

## Control Flow
There is no runtime control flow. Including the header makes C++ Flow stream/request types visible in a Swift-friendly alias form.

## State and Persistence Behavior
No state or persistence.

## Dependencies and Integration Points
It includes Flow Swift compatibility headers, pthread/stdint, `MasterInterface.h`, and generated `SwiftModules/FDBServer_CxxTypeConformances.h`. It supports Swift/C++ interop for server stream types used by master/recovery code.

## Risks and Edge Cases
Macro-generated names depend on `CONCAT3` and struct type names. Changes to the underlying request structs or generated Swift conformance headers can break interop compilation. The header is compile-time glue, so errors surface as build failures.

## Test Signals
No direct tests in this subset. Build success with Swift interop enabled is the primary signal.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/include/fdbserver/fdbserver_stream_support.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/kvstore/ArtMutationBuffer.h -->
# sources/storage-engines/foundationdb/fdbserver/kvstore/ArtMutationBuffer.h

## Purpose
This header defines `MutationBufferART`, an arena-backed adaptive radix tree wrapper for range mutation boundaries. It supports ordered lookup, iteration, erase, and boundary insertion while preserving mutation state across ranges.

## Important APIs, Types, and Functions
- Private members `Arena arena` and `art_tree* mutations` own all tree nodes and `RangeMutation` objects.
- `const_iterator` and `iterator` wrap `art_iterator` and expose `key()`, `mutation()`, comparison, increment/decrement, and mutable `value_ptr()` for insertion initialization.
- The constructor creates sentinel boundaries at `dbBegin.key` and `dbEnd.key`; the `dbEnd` mutation is marked as a clear boundary.
- `copyToArena<T>` deep-copies compatible objects into the mutation buffer arena.
- `upper_bound` and `lower_bound` return ART iterators for key search.
- `erase(begin, end)` removes a half-open iterator range from the underlying ART.
- `insert(KeyRef boundary)` finds or creates a boundary and initializes its `RangeMutation`, propagating clear state if the previous boundary clears after itself.

## Control Flow
Construction initializes the tree with full-keyspace sentinels, reducing edge cases for range mutation application. `insert` delegates to `insert_if_absent`; if a boundary exists it returns the existing iterator. Otherwise it allocates a new `RangeMutation`, finds the previous boundary, and if the previous boundary clears after itself, initializes the new boundary as cleared. `erase` walks from begin to end, erasing nodes one by one while saving the next iterator before deletion.

## State and Persistence Behavior
All state is in the arena and ART structure. Memory is released with the buffer arena lifetime; there is no persistence. Keys and mutations inserted into the tree must remain valid through arena ownership/deep copies where needed.

## Dependencies and Integration Points
It depends on `art.h`, `flow/Arena.h`, `KeyRef`, `dbBegin`, `dbEnd`, and `RangeMutation`. It is a lower-level KV storage mutation-buffer utility.

## Risks and Edge Cases
- Iterator erase assumes `next` remains valid enough after deleting the current ART node; correctness depends on `art_tree` iterator semantics.
- `RangeMutation` values are stored as `void*` in ART and cast back; type discipline is manual.
- Boundary insertion propagates `clearAfterBoundary`, so incorrect previous-boundary state changes all subsequent range semantics.
- Arena lifetime means individual mutations are not freed early.

## Test Signals
No direct tests in this subset. Expected coverage is through KV store mutation/range tests that exercise mutation buffering.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/kvstore/ArtMutationBuffer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/kvstore/CMakeLists.txt -->
# sources/storage-engines/foundationdb/fdbserver/kvstore/CMakeLists.txt

## Purpose
This CMake file defines the fdbserver KV-store static library, its tests, include paths, and optional RocksDB/liburing integration.

## Important APIs, Types, and Functions
- `fdb_find_sources(FDBSERVER_KVSTORE_SRCS)` discovers KV-store sources.
- `add_flow_target(STATIC_LIBRARY NAME fdbserver_kvstore ...)` builds the static library.
- `add_fdbserver_link_test(fdbserver_kvstorelinktest ...)` and `add_fdbserver_unit_test(fdbserver_kvstore_test kvstore ...)` register link and unit-test targets.
- `target_include_directories` exposes `include/` publicly and adds source, sqlite, fdbserver include, and generated include directories privately.
- `target_link_libraries(fdbserver_kvstore PUBLIC fdbserver_core sqlite)` links core and sqlite.
- `WITH_ROCKSDB` branch adds RocksDB dependency, include paths, compile definition, and optional liburing/LZ4 libraries.

## Control Flow
CMake discovers sources, builds `fdbserver_kvstore`, configures tests/includes, links required libraries, then conditionally extends the target when RocksDB support is enabled.

## State and Persistence Behavior
No runtime state. It controls build graph state and feature-dependent linkage.

## Dependencies and Integration Points
The KV-store component integrates with `fdbserver_core`, sqlite, generated fdbserver includes, RocksDB, liburing, and LZ4 depending on build options.

## Risks and Edge Cases
Automatic source discovery can accidentally include new files. RocksDB and liburing feature branches change public link libraries and compile definitions, so downstream storage engine behavior depends on build configuration.

## Test Signals
The file registers a `kvstore` unit-test target and a link test, which are the main build-level validation signals.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/kvstore/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/kvstore/DeltaTree.h -->
# sources/storage-engines/foundationdb/fdbserver/kvstore/DeltaTree.h

## Purpose
This header implements packed, memory-mappable binary search trees whose nodes store delta-compressed items. It provides two related templates, `DeltaTree` and `DeltaTree2`, for building balanced compressed trees, lazily decoding nodes, seeking/iterating, inserting within free space, and marking nodes deleted.

## Important APIs, Types, and Functions
- `lessOrEqualPowerOfTwo`, `perfectSubtreeSplitPoint`, and `perfectSubtreeSplitPointCached` compute balanced subtree root positions for compact tree construction.
- `DeltaTree<T, DeltaT>` is the older implementation. Its `Node` stores relative child offsets using either 16-bit or 32-bit offset fields, followed by variable-sized `DeltaT`. Header fields track `numItems`, `nodeBytesUsed`, `nodeBytesFree`, deleted bytes, initial/max height, and `largeNodes`.
- `DeltaTree::DecodedNode` lazily reconstructs `T` from delta and ancestor bounds, caching decoded children and ancestor links.
- `DeltaTree::Mirror` owns an arena-backed decoded mirror of a raw tree and supports `insert`, `erase`, and cursor creation.
- `DeltaTree::Cursor` supports seek, hinted seek, less/greater variants, first/last movement, next/previous movement, and deletion hiding.
- `DeltaTree::build` and `buildSubtree` serialize sorted input items into a near-perfect packed BST using prefix-source selection from previous/next ancestor.
- `DeltaTree2<T, DeltaT>` is a newer implementation with child offsets relative to the tree base, ref-counted `DecodeCache`, index-based decoded nodes, partial caches, cursor tree switching, better memory tracking, insertion, deletion, and build support.
- `DeltaTree2::DecodeCache` stores lower/upper bounds, an arena, decoded-node vector, optional memory tracker, and cache reset/update logic.
- `DeltaTree2::Cursor` resolves decoded items from partial caches, seeks, iterates, inserts, erases, and can switch to an updated tree while reusing cache.

## Control Flow
Build starts from sorted `[begin, end)` items and lower/upper bounds. It chooses a balanced root index for each subtree, selects the better prefix source between left/right ancestors, writes the item delta, recursively serializes left and right subtrees, stores child offsets, computes used/free bytes, and optionally zeroes unused space in `DeltaTree2`.

Read traversal creates decoded nodes on demand. A cursor starts at root, compares the search key to decoded `T` values, and follows child offsets. Move-next/move-prev find inorder successors/predecessors using child links and ancestor indices/pointers. Public seek variants call raw seek then hide deleted nodes by walking forward/backward.

Insertion finds the would-be parent, restores a deleted equal item if present, otherwise computes left/right base candidates, chooses the better prefix source, verifies delta plus node header fits in free bytes, writes the child node at the current tree end, links parent child offset and decoded-cache child index, updates byte counters and item count, and tracks max height. Erase marks the current or found node deleted and decrements `numItems`; `DeltaTree2` also increments `nodeBytesDeleted` by node space and decrements it when restoring.

## State and Persistence Behavior
The raw `DeltaTree`/`DeltaTree2` object is designed to live in a memory-mappable byte region. Its header and packed nodes are persistent within that region, including deleted flags stored inside deltas. Decode mirrors/caches are in-memory accelerators and can be rebuilt from raw bytes. Insertions append into `nodeBytesFree`; deletions mark nodes rather than compacting immediately. `DeltaTree2::build` zeroes unused space, which helps deterministic persistence and avoids stale bytes.

## Dependencies and Integration Points
The templates depend on `flow/flow.h`, `flow/Arena.h`, `fdbclient/FDBTypes.h`, and server knobs. The item type `T` and delta type `DeltaT` provide the important storage-engine-specific behavior: comparison, common-prefix calculation, delta sizing/writing, delta application, partial cache support in `DeltaTree2`, deleted flags, and debug strings.

## Risks and Edge Cases
- The packed layout uses `#pragma pack(push, 1)`, pointer arithmetic, variable-sized deltas, and 16-bit/32-bit child offsets. Alignment, overflow, and offset-origin mistakes are high-risk.
- `DeltaTree` child offsets are relative to the node, while `DeltaTree2` offsets are relative to the tree. Mixing assumptions would corrupt traversal.
- `numItems` is `uint16_t`; item counts and small offset limits constrain page capacity.
- `largeNodes` is chosen by `spaceAvailable > uint16_t::max`; the chosen header size must match all offset writes/reads.
- Deletion leaves bytes in place because descendants may borrow prefixes from deleted nodes. Compaction/rebuild must respect prefix dependencies.
- `DeltaTree2::DecodeCache` can reallocate its vector; code repeatedly reacquires references after `emplace_new` for this reason.
- Cursor methods assume valid cursor state for movement; calling `_moveNext`/`_movePrev` on invalid cursors is undefined.
- Hinted seek in the older cursor is explicitly commented as broken/slower, so callers should be cautious relying on it for performance.
- Insert can fail because the tree is empty, item exists, height limit is exceeded, or free space is insufficient.

## Test Signals
No direct tests are in this file, but the KV-store CMake target registers `fdbserver_kvstore_test`. Useful test coverage should include sorted build/seek iteration, prefix compression round trips, deletion and hidden iteration, insertion into free space, deleted-item restoration, small vs large node modes, cache reuse after tree switching, memory accounting, and persistence/reload from raw bytes.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/kvstore/DeltaTree.h -->
