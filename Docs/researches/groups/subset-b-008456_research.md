# Research: subset-b-008456

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/clustercontroller/ClusterController.h -->
# sources/storage-engines/foundationdb/fdbserver/clustercontroller/ClusterController.h

## Purpose

`ClusterController.h` is the central in-memory control surface for FoundationDB cluster-controller behavior. It defines worker registration state, database metadata publication state, recruitment helpers for transaction-system roles, worker health aggregation, remote-DC failover decisions, and the hook points for the cluster-health metric monitor. Although this is a header, it contains substantial inline actor/control logic used by the cluster controller implementation.

## Important APIs, Types, and Functions

- `WorkerInfo` owns a registered process's watcher, registration reply promise, generation, reboot count, initial/current process classes, priority information, `WorkerDetails`, role halt futures, and reported issues. Its move operations preserve long-lived futures and role state.
- `WorkerFitnessInfo` and `RoleFitness` encode recruitment quality: process-class fitness, process reuse count, selected worker count, and TLog-specific degraded-process penalties.
- `hasWorkerIssue()` and `excludesFromTLogRecruitmentDueToLowDisk()` inspect worker issue strings, including the low-disk TLog recruitment exclusion signal.
- `RecruitWorkersInfo` and `RecruitRemoteWorkersInfo` wrap recruitment requests, replies, optional debug IDs, and completion triggers.
- `ClusterControllerData::DBInfo` tracks the published `ClientDBInfo`/`ServerDBInfo`, incompatible connections, master registration counts, recovery flags, database configuration, client status, recovery data, and client-count pruning actor.
- `UpdateWorkerList` asynchronously batches worker-list KV updates into `workerListKeys`, clearing the range on startup and applying process deltas transactionally.
- Recruitment helpers include `getStorageWorker()`, `getWorkersForSeedServers()`, `getWorkersForTlogsComplex()`, `getWorkersForTlogsSimple()`, `getWorkersForTlogsBackup()`, `getWorkersForTlogs()`, `getWorkersForSatelliteLogs()`, `getWorkerForRoleInDatacenter()`, and `getWorkersForRoleInDatacenter()`.
- Configuration-level orchestration lives in `findRemoteWorkersForConfiguration()`, `findWorkersForConfigurationFromDC()`, `findWorkersForConfigurationDispatch()`, and `findWorkersForConfiguration()`.
- Health/failover routines include `updateWorkerHealth()`, `updateRecoveredWorkers()`, `getDegradationInfo()`, `remoteDCIsHealthy()`, `canSafelyTriggerFailoverToRemoteDc()`, `triggerFailoverToRemoteDc()`, `shouldTriggerRecoveryDueToDegradedServers()`, `shouldTriggerFailoverDueToDegradedServers()`, and `recentRecoveryCountDueToHealth()`.
- `updateClusterHealthMonitorInputs()` is declared here and bridges controller state into `cluster_health::WorkerEventProvider`.

## Control Flow

Workers register into `id_worker`, and availability is checked through `workerAvailable()`, which combines startup grace time, failure-monitor availability, and optional reboot-stability filtering. Recruitment proceeds by filtering workers for locality, role fitness, exclusions, degraded status, issue flags, and current process reuse. TLog recruitment has specialized fast paths for common policies: complex `Across(Across(zoneid, One))`, simple `Across(zoneid, One)` or `One`, and a backup policy-engine path for custom policies. Multi-region recruitment prefers the cluster-controller DC when safe, can swap primary/remote region ordering based on priority and version lag, and updates `desiredDcIds` to drive failover or future controller placement decisions.

Health-control flow starts with `UpdateWorkerHealthRequest` messages updating `workerHealth`. Expired reports are pruned by `updateRecoveredWorkers()`. `getDegradationInfo()` folds peer complaints into deterministic degraded and disconnected server sets, avoids blaming both sides of the same degraded link, optionally detects whole-satellite degradation, and respects knobs for intra-DC-only latency and complaint thresholds. Recovery/failover decisions then check cluster topology, recovery state, CC exclusion, remote health, version lag, and bounded exclusion counts.

## State and Persistence Behavior

Most state is controller-local and volatile: worker maps, outstanding recruitment requests, health maps, degraded-server exclusions, failover priority `AsyncVar`s, and metric monitor inputs. Persistent effects are narrow: `UpdateWorkerList` writes worker process data under `workerListKeys`, and `DBInfo` publishes changing database interfaces through `AsyncVar<ClientDBInfo>` and `AsyncVar<ServerDBInfo>` consumed by clients and servers. `DBInfo::countClients()` periodically prunes stale client status using coordinator register intervals. No durable schema is defined here, but recruitment choices and failover priorities affect recovery state through surrounding actors.

## Dependencies and Integration Points

This file integrates with `DatabaseContext`, `StorageServerInterface`, `WorkerInterface`, replication policies, process classes, locality data, the failure monitor, server knobs, `RatekeeperMonitor`, and `ClusterHealthMonitor`. It depends heavily on Flow futures, actors, `AsyncVar`, `AsyncTrigger`, `PromiseStream`, `TraceEvent`, deterministic random selection, and FDB replication-policy primitives. It exposes `clusterRegisterMaster()` for master registration and stores `cluster_health::WorkerEventProvider` plus `cluster_health::Monitor` so the cluster controller can emit aggregate health metrics.

## Risks

Recruitment quality depends on subtle ordering of fitness, process reuse, degraded status, locality, and controller-DC preference. Changes can create nondeterministic recruitment, worse role placement, or unnecessary recovery. Health-triggered recovery/failover is knob-sensitive; overly aggressive thresholds can churn recoveries, while conservative thresholds can leave degraded transaction-system roles in place. Worker issue strings are untyped, so misspellings or changes to producer semantics can silently alter TLog recruitment. The header's large inline implementation raises coupling risk and makes isolated testing harder.

## Test Signals

The code contains simulation-only assertions comparing optimized recruitment with backup policy-engine recruitment and detecting nondeterministic role fitness. Trace events such as `RecruitStorageTry`, `GetTLogTeamWorkerUnavailable`, `BetterMasterExists`, `NewRecruitmentIsWorse`, `ClusterControllerUpdateWorkerHealth`, and `ClusterControllerTriggerFailover` are key operational signals. Direct unit tests for this header are not in this subset; adjacent test coverage primarily exercises the cluster-health factor layer.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/clustercontroller/ClusterController.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/clustercontroller/ClusterHealthIFactor.cpp -->
# sources/storage-engines/foundationdb/fdbserver/clustercontroller/ClusterHealthIFactor.cpp

## Purpose

`ClusterHealthIFactor.cpp` implements the concrete cluster-health factors declared in `ClusterHealthIFactor.h`. Each factor reads a focused set of latest worker trace events through `IWorkerEventProvider` and returns a `cluster_health::Level` describing the severity of that signal.

## Important APIs, Types, and Functions

- `filterEmptyEvents()` removes worker results whose `TraceEventFields` are empty, allowing role-filtered providers to ignore stale or non-role workers.
- `fetchSpaceLevel()` is shared by storage and TLog disk-space checks. It returns `METRICS_MISSING` when provider results are absent or empty, computes minimum available/total ratio, and maps it to `HEALTHY`, `INTERVENTION_REQUIRED`, or `CRITICAL_INTERVENTION_REQUIRED`.
- `StorageSpaceFactor::fetchLevel()` reads `StorageMetrics` fields `KvstoreBytesAvailable` and `KvstoreBytesTotal`.
- `TLogSpaceFactor::fetchLevel()` reads `TLogMetrics` fields `QueueDiskBytesAvailable` and `QueueDiskBytesTotal`.
- `StorageReplicationFactor::fetchLevel()` reads data-distributor `MovingData` counters and maps zero-replica teams to `OUTAGE`, one-replica teams to critical if the provider says to treat them as critical, queued/in-flight repairs to `SELF_HEALING`, and clean metrics to `HEALTHY`.
- `RecoveryStateFactor::fetchLevel()` maps controller recovery state before `ACCEPTING_COMMITS` to `OUTAGE`, before `FULLY_RECOVERED` to `SELF_HEALING`, and fully recovered to `HEALTHY`.
- `ProcessErrorsFactor::fetchLevel()` treats non-empty latest process-error events as `CRITICAL_INTERVENTION_REQUIRED`, all-empty successful responses as `HEALTHY`, and all-missing/all-failed data as `METRICS_MISSING`.
- `RkThrottlingFactor::fetchLevel()` reads `RkUpdate`, returning `OUTAGE` when `TPSLimit` is zero, critical when `TPSLimit / ReleasedTPS` is below the configured threshold, and healthy otherwise.

## Control Flow

All factor methods are Flow coroutine futures. They fetch provider data, distinguish absent metrics from empty-role results, parse expected trace fields, and return a severity. Parse failures are caught as `Error`, logged with warning trace events, and converted to `METRICS_MISSING`. `CODE_PROBE` calls instrument expected branches for simulation coverage.

## State and Persistence Behavior

The factor implementations are stateless aside from constructor thresholds in the disk-space and ratekeeper-throttling factors. They do not persist data and do not cache metrics; each evaluation is a fresh provider read.

## Dependencies and Integration Points

The file depends on `RecoveryState`, `TraceEventFields`, Flow futures, `CODE_PROBE`, and the provider abstraction from `ClusterHealthMonitor.h`. It is invoked by `cluster_health::Monitor::run()`, which aggregates factor levels into the `ClusterHealthMetric` trace event.

## Risks

The factors depend on exact trace-event names and field names. Missing or renamed fields downgrade to `METRICS_MISSING`, which may hide a real outage behind telemetry failure. `RkThrottlingFactor` skips zero `ReleasedTPS` when `TPSLimit` is nonzero, so idle clusters are healthy, but a mix of idle and throttled workers must still be interpreted carefully. `StorageReplicationFactor` relies on data-distributor counters being current and role-filtered.

## Test Signals

`ClusterHealthMonitorTesting.cpp` exercises healthy, intervention, critical, outage, self-healing, stale-role, and missing-metric branches for all implemented factors. Runtime trace events include `StorageSpaceFactorFetchFailed`, `TLogSpaceFactorFetchFailed`, `StorageReplicationFactorFetchFailed`, and `RkThrottlingFactorFetchFailed`.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/clustercontroller/ClusterHealthIFactor.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/clustercontroller/ClusterHealthIFactor.h -->
# sources/storage-engines/foundationdb/fdbserver/clustercontroller/ClusterHealthIFactor.h

## Purpose

`ClusterHealthIFactor.h` defines the extension interface for cluster-health factors and declares the concrete factors used by the cluster-health monitor.

## Important APIs, Types, and Functions

- `IFactor` is the polymorphic interface. `getName()` supplies a stable factor name for trace fields, and `fetchLevel()` asynchronously evaluates the factor against an `IWorkerEventProvider`.
- `TrackCodeProbes` is a boolean parameter that lets tests or production monitor execution choose whether to fire branch coverage probes.
- `StorageSpaceFactor` and `TLogSpaceFactor` store intervention and critical disk-space thresholds.
- `StorageReplicationFactor`, `RecoveryStateFactor`, and `ProcessErrorsFactor` are threshold-free signal evaluators.
- `RkThrottlingFactor` stores the critical `TPSLimit / ReleasedTPS` threshold.

## Control Flow

The header establishes a simple pull model: `Monitor` owns factors, calls `fetchLevel()`, and receives one `Level` per factor. Implementations can choose any provider method but must return a single health level.

## State and Persistence Behavior

Only threshold constructor parameters are retained. No durable state is represented here.

## Dependencies and Integration Points

The declarations forward-reference `Level` and `IWorkerEventProvider` from the cluster-health monitor layer and use Flow's `Future`. This intentionally separates factor declarations from concrete worker/event-log collection.

## Risks

Adding a factor requires updating both declaration and `Monitor::create()` wiring. Factor names become trace-detail suffixes, so renames can break dashboards or alert queries. Because `fetchLevel()` is asynchronous and virtual, implementations must avoid long blocking work and must handle missing telemetry explicitly.

## Test Signals

Every declared concrete factor has direct unit coverage in `ClusterHealthMonitorTesting.cpp`; the interface itself is exercised through fake providers and direct `fetchLevel()` calls.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/clustercontroller/ClusterHealthIFactor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/clustercontroller/ClusterHealthMonitor.cpp -->
# sources/storage-engines/foundationdb/fdbserver/clustercontroller/ClusterHealthMonitor.cpp

## Purpose

`ClusterHealthMonitor.cpp` implements production event collection and the periodic aggregate cluster-health metric loop.

## Important APIs, Types, and Functions

- `latestEventOnWorker()` requests the latest event by name from one `WorkerInterface`, applies a 2-second timeout, and records either trace fields or an empty result plus failed address.
- `latestEventOnInterfaces()` maps role interfaces such as storage servers or TLogs back to worker event-log endpoints, requests scoped event names of the form `<interface id>/<eventName>`, and returns per-address results and failures.
- `levelToInt()` maps levels to metric values: healthy 100, self-healing 80, intervention 60, critical 40, metrics missing 20, outage 0.
- `levelToStr()` maps levels to stable trace strings.
- `WorkerEventProvider` setters populate workers, recovery state, role interfaces, and policy flags from cluster-controller state.
- Provider methods fetch latest events for all workers, the current ratekeeper, current data distributor, storage servers, and TLogs.
- `Monitor::run()` periodically evaluates all factors and logs `ClusterHealthMetric` with per-factor levels, aggregate level/value, and limiting factor.
- `Monitor::create()` wires the default factor list from server knobs.

## Control Flow

The monitor exits immediately if `CLUSTER_HEALTH_METRIC_ENABLE` is false. Otherwise it loops forever, delaying by `CLUSTER_HEALTH_METRIC_POLL_INTERVAL`, launching all factor futures, waiting for all, and selecting the lowest-valued level as the aggregate. Provider collection uses timeout-wrapped RPCs and converts per-worker failures into empty metrics plus an error set rather than failing the whole factor.

## State and Persistence Behavior

The provider stores snapshots of controller input state in memory. The monitor stores its factor vector and provider reference. The only output is trace logging; there is no persistence or local cache.

## Dependencies and Integration Points

This file depends on `WorkerEvents`, `EventLogRequest`, Flow generic actors, `TraceEvent`, `fmt::format`, server knobs, worker interfaces, storage server interfaces, TLog interfaces, and factor implementations. `ClusterControllerData` owns the provider and monitor and is responsible for refreshing provider inputs.

## Risks

The 2-second event-log timeout trades freshness for bounded polling cost; slow workers become failed/missing metrics. Interface-to-worker matching by network address can miss role metrics if address mappings are stale or incomplete. `levelToInt()` ordering defines aggregate severity; any new level must be added consistently to both mappings and factor interpretation. The monitor emits one trace per poll, so knob settings control operational overhead.

## Test Signals

The aggregate loop is indirectly validated by factor tests and provider fakes, but this file has limited direct tests in the subset. Operational validation comes from `ClusterHealthMetric` trace details such as `FactorStorageSpace`, `FactorRkThrottling`, `Aggregate`, `AggregateValue`, and `LimitingFactor`.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/clustercontroller/ClusterHealthMonitor.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/clustercontroller/ClusterHealthMonitor.h -->
# sources/storage-engines/foundationdb/fdbserver/clustercontroller/ClusterHealthMonitor.h

## Purpose

`ClusterHealthMonitor.h` defines the health-level model, worker-event provider abstraction, production provider storage, and monitor public API.

## Important APIs, Types, and Functions

- `Level` orders the health vocabulary from `OUTAGE` through `HEALTHY`.
- `LatestWorkerEvents` is an optional pair of `WorkerEvents` and a set of failed worker-address strings. Absence means no provider data for that role or signal.
- `IWorkerEventProvider` abstracts recovery-state reads, the one-replica-left policy flag, and latest event-log reads by scope.
- `WorkerEventProvider` is the production implementation. It stores worker details, recovery state, role interfaces, storage servers, TLogs, and the one-replica criticality flag.
- `Monitor` owns factor objects and a provider reference; `create()` constructs the standard factor set and `run()` emits the metric loop.

## Control Flow

The header separates health evaluation from event acquisition. Factors consume only the provider interface, which allows production code to use worker event-log RPCs while tests provide deterministic in-memory metrics.

## State and Persistence Behavior

All state is in-memory snapshots. The provider does not own role actors; it stores interfaces copied from the controller. No persistence is defined.

## Dependencies and Integration Points

The header imports `ClusterHealthIFactor.h`, storage server and TLog interfaces, `RecoveryState`, `WorkerEvents`, and Flow. It is included by both the cluster controller and factor implementation files, making it the central boundary between controller state and health factor evaluation.

## Risks

The provider contract must preserve the distinction between absent role data, empty successful responses, and failed event-log requests. Consumers use these differences to choose `HEALTHY` versus `METRICS_MISSING`. Any new provider scope should be reflected in tests to avoid mixing stale all-worker events with role-specific events.

## Test Signals

`ClusterHealthMonitorTesting.cpp` implements `FakeWorkerEventProvider` against this interface and verifies expected factor behavior for present, absent, empty, and partially failed event sets.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/clustercontroller/ClusterHealthMonitor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/clustercontroller/ClusterHealthMonitorTesting.cpp -->
# sources/storage-engines/foundationdb/fdbserver/clustercontroller/ClusterHealthMonitorTesting.cpp

## Purpose

`ClusterHealthMonitorTesting.cpp` provides Flow unit tests for every concrete cluster-health factor using a fake provider and synthetic trace fields.

## Important APIs, Types, and Functions

- `FakeWorkerEventProvider` implements `IWorkerEventProvider` with maps from event names to `LatestWorkerEvents` for all-worker, ratekeeper, data-distributor, storage-server, and TLog scopes.
- Helper builders create storage/TLog space metrics, process-error metrics, ratekeeper updates, and `MovingData` metrics with sensible defaults.
- `MovingDataMetricsBuilder` makes data-distributor replication counters readable and avoids boilerplate missing fields.
- Test cases cover `StorageSpaceFactor`, `TLogSpaceFactor`, `StorageReplicationFactor`, `RecoveryStateFactor`, `ProcessErrorsFactor`, and `RkThrottlingFactor`.
- `forceLinkClusterHealthMonitorTests()` ensures tests are linked where needed.

## Control Flow

Each test instantiates one factor and a fake provider, sets provider state, awaits `fetchLevel()`, and asserts the returned `Level`. Some tests intentionally set both all-worker and role-specific event maps to confirm that factors use the role-specific provider path and ignore stale broader events.

## State and Persistence Behavior

All test state is local and in-memory. There is no persistence; synthetic `NetworkAddress` values identify fake workers.

## Dependencies and Integration Points

The tests depend on Flow `UnitTest`, `RecoveryState`, the factor declarations, and the monitor/provider interface. They validate the contract between provider return shapes and factor severity decisions.

## Risks

The tests focus on factor mapping logic, not production RPC timeouts or monitor aggregation. They do not cover malformed trace fields exhaustively, multi-worker threshold edge ordering beyond representative cases, or knob-driven monitor creation.

## Test Signals

Coverage includes healthy/intervention/critical disk thresholds, missing metrics, stale-role filtering, zero-replica outage, one-replica critical policy, self-healing repair moves, recovery-state mapping, process-error healthy versus critical behavior, partial event-log failure behavior, ratekeeper outage on zero TPS limit, idle healthy behavior, and role-specific ratekeeper filtering.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbserver/clustercontroller/ClusterHealthMonitorTesting.cpp -->
