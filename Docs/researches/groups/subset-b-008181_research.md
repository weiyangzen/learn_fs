# subset-b-008181 research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/admin-handlers.go -->
# sources/object-store/minio/cmd/admin-handlers.go

## Purpose
`admin-handlers.go` implements a broad set of MinIO admin API HTTP handlers behind the routes registered in `admin-router.go`. It covers server update and service control, storage and realtime metrics, lock inspection and force unlock, profiling, explicit heal orchestration, performance tests, trace and console-log streams, KMS admin checks, server/cluster information, health diagnostics, raw data inspection, and host anonymization helpers. The file is the main integration point between authenticated admin REST calls and cluster-wide subsystems.

## Important APIs, Types, And Functions
- `ServerUpdateV2Handler` and deprecated `ServerUpdateHandler` validate `policy.ServerUpdateAdminAction`, fetch release metadata and binaries, verify checksums, call peer update RPCs through `globalNotificationSys`, commit binaries, return per-peer status, and signal restart on success.
- `ServiceHandler` and `ServiceV2Handler` translate `madmin.ServiceAction` values into internal `serviceSignal`s, enforce action-specific policy, notify peers, and locally freeze, unfreeze, restart, or stop. V2 adds dry-run, scheduled restart timing, local and peer waiting-drive status, and structured per-host results.
- `StorageInfoHandler`, `DataUsageInfoHandler`, `MetricsHandler`, `ServerInfoHandler`, and `HealthInfoHandler` expose storage, usage, realtime metrics, server summary, and streaming diagnostics.
- `HealHandler` is the HTTP facade for `globalAllHealState`: it parses `healInitParams`, handles token-proxied status requests, returns existing sequence tokens, force-starts or stops sequences, and keeps long-running start requests alive by periodically writing whitespace.
- `ForceUnlockHandler`, `TopLocksHandler`, `lriToLockEntry`, and `topLockEntries` expose distributed lock state and emergency unlock behavior for erasure pools.
- Profiling helpers include `StartProfilingHandler`, `ProfileHandler`, `DownloadProfilingHandler`, `dummyFileInfo`, and `embedFileInZip`.
- Performance endpoints include `SitePerfHandler`, `ClientDevNull`, `NetperfHandler`, `ObjectSpeedTestHandler`, `DriveSpeedtestHandler`, `makeObjectPerfBucket`, `deleteObjectPerfBucket`, `validateObjPerfOptions`, and `isAllowedRWAccess`.
- Diagnostics and security-related helpers include `TraceHandler`, `ConsoleLogHandler`, `KMSCreateKeyHandler`, `KMSStatusHandler`, `KMSKeyStatusHandler`, `getTLSInfo`, `fetchHealthInfo`, `InspectDataHandler`, `bytesToPublicKey`, `getSubnetAdminPublicKey`, `createHostAnonymizer`, and `anonymizeHost`.

## Control Flow
Most handlers follow a consistent pattern: derive `ctx` from the request, authenticate and authorize with `validateAdminReq` or `checkAdminRequestAuth`, parse route/query/body parameters, call object-layer or global subsystem operations, marshal JSON or stream event data, and return through MinIO response helpers. Cluster-aware handlers first perform local work or gather local data, then fan out through `globalNotificationSys` or peer REST clients and merge results.

Update flow downloads release metadata, parses the target release, skips when already current, downloads the binary once, verifies it locally and remotely, commits remotely and locally when not a dry-run, reports `WaitingDrives`, signals peers, writes JSON status, and finally sends `serviceRestart` to `globalServiceSignalCh`. Service-control flow validates requested action, optionally computes an execution time for restart, sends signals to remote peers in distributed erasure mode, writes the response before local stop/restart, then sends or performs the local signal.

Long-running streaming handlers use keepalive loops. `MetricsHandler` encodes repeated `madmin.RealtimeMetrics` snapshots until count, context cancellation, or write failure. `TraceHandler` subscribes to `globalTrace`, asks peers to stream trace entries, writes buffered JSON entries, and periodically emits whitespace when idle. `ConsoleLogHandler` subscribes local console logs, starts peer log streaming, encodes entries through buffered channels, and also emits whitespace keepalives. `HealthInfoHandler` locks the cluster health check, starts `fetchHealthInfo`, event-streams incremental `madmin.HealthInfo` objects, and stops on deadline or client cancellation.

`InspectDataHandler` validates signed access, requires an object layer implementing `getRawDataer`, rejects bad volume/file paths, optionally switches to public-key encrypted `estream`, otherwise uses a generated one-time SIO key, embeds cluster metadata and command input, walks raw matching data into a zip, includes `format.json`, and appends a helper `start-minio.sh` script.

## State And Persistence Behavior
The file mostly orchestrates volatile runtime state rather than directly persisting application data. It mutates update binaries via `commitBinary`, writes service signals to `globalServiceSignalCh`, starts/stops in-memory profilers under `globalProfilerMu`, and interacts with `globalAllHealState` for in-memory heal sequence state. Performance tests may create, update metadata for, delete, or prefix-delete objects in `globalObjectPerfBucket`; `makeObjectPerfBucket` enables versioning metadata when site replication is on. `InspectDataHandler` streams raw disk content but does not store output server-side.

Several handlers acquire namespace locks via the object layer to serialize disruptive diagnostics: site perf, client dev-null, netperf, and health checks use locks under `minioMetaBucket`. Freeze/unfreeze operations call `globalNotificationSys.ServiceFreeze` to temporarily block S3 API traffic during speed tests. Health and server info read persisted configuration, data usage caches, bucket metadata, KMS status, logger targets, and environment variables, with sensitive values redacted.

## Dependencies And Integration Points
The file integrates with `madmin-go/v3` response contracts, MinIO IAM policy actions, the object-layer interface, erasure server pools, namespace locking, background healing, peer notification RPCs, KMS, event notifier, logger/audit targets, global trace/bootstrap tracers, console subsystem, data usage cache, Kubernetes/Docker detection, endpoint topology, and SIO/estream encryption. It also relies on route variables from `github.com/minio/mux` and response helpers from other `cmd` files.

## Risks And Edge Cases
This file has a high blast radius because many handlers perform cluster-wide disruptive actions. Update and service-control correctness depends on peer fan-out, waiting-drive reporting, and ensuring local restart happens only after responses are sent. Several streams use large buffered channels (`TraceHandler` uses 100k entries), so slow clients can cause drops or memory pressure. Long-lived goroutines must respect request cancellation; trace, logs, profiling, heal, and health code all rely on context cancellation and channel closure discipline.

Diagnostics can expose sensitive operational data. The code redacts known environment secrets in server info, supports strict anonymization in health output, rejects path traversal for raw data inspection, and encrypts inspect data when a public key is supplied. The legacy inspect path without public key still sends a symmetric key at stream start, which is compatibility-oriented and weaker operationally. Performance tests intentionally freeze S3 traffic and create or delete test data; incorrect permissions or cleanup failures can affect user buckets, especially when a custom bucket or `noclear` is used.

`DataUsageInfoHandler` marshals usage before optionally populating capacity fields, so the JSON response may omit those later capacity updates. This looks like a potential bug or stale behavior worth verifying against callers. `getPoolsInfo` trusts disk pool/set indexes when indexing server pools. `topLockEntries` aggregates by resource and UID and filters quorum unless stale is requested; stale lock reporting depends on caller expectations.

## Test Signals
`admin-handlers_test.go` directly tests service restart handling, `/info`, admin error mapping, heal init parameter validation, and `topLockEntries`. The tests exercise a single-node erasure testbed and signed admin requests, but they do not cover update, trace/log streaming, KMS, inspect-data encryption, health anonymization, or speed-test cleanup. Existing tests give good signals for basic routing/auth/service behavior and lock aggregation, while most high-risk diagnostic flows remain integration-test-heavy or untested in this subset.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/admin-handlers.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/admin-handlers_test.go -->
# sources/object-store/minio/cmd/admin-handlers_test.go

## Purpose
`admin-handlers_test.go` provides unit and lightweight integration coverage for selected admin handler paths. It builds an in-process single-node erasure backend, registers the admin router, signs admin requests, and verifies service control, server info, admin error mapping, heal parameter parsing, and distributed-lock aggregation.

## Important APIs, Types, And Functions
- `adminErasureTestBed` captures temporary erasure disk paths, the initialized `ObjectLayer`, admin router, and a cancellation function.
- `prepareAdminErasureTestBed` resets globals, enables erasure mode, initializes an erasure object layer and test config, sets boot time/endpoints, initializes subsystems, starts IAM, and registers admin routes with config operations enabled.
- `TearDown` cancels the context, removes temporary disks, and resets globals.
- `initTestErasureObjLayer` creates sixteen random disks, builds erasure server pools, and publishes `globalObjectAPI`.
- `cmdType`, `restartCmd`, `stopCmd`, `toServiceSignal`, and `toServiceAction` map test commands to internal service signals and `madmin.ServiceAction`s.
- `getServiceCmdRequest` and `buildAdminRequest` construct signed V4 admin requests.
- Tests include `TestServiceRestartHandler`, `TestAdminServerInfo`, `TestToAdminAPIErrCode`, `TestExtractHealInitParams`, and `TestTopLockEntries`.

## Control Flow
The shared test setup is explicit and global-state-heavy. Each integration-style test creates a context, calls `prepareAdminErasureTestBed`, sets `globalMinioAddr` for admin peer behavior, builds a signed request against `adminPathPrefix + adminAPIVersionPrefix`, runs it through the registered mux router, checks HTTP status, and decodes JSON where needed. Service restart starts a goroutine that reads from `globalServiceSignalCh` and compares the internal signal with the expected value.

`TestExtractHealInitParams` does combinatorial validation over query parameter combinations and route-variable combinations. It expects invalid cases when both force flags are present, when a client token is mixed with force flags, or when a prefix is given without a bucket. The body is fixed valid JSON, so JSON parser failures are intentionally not tested.

`TestTopLockEntries` constructs synthetic lock requester info for grouped delete-object locks and concurrent read locks across four owners. It creates identical `PeerLocks` maps per owner, builds expected `madmin.LockEntry` values, calls `topLockEntries`, sorts expected and actual by resource/UID, and compares fields except elapsed time.

## State And Persistence Behavior
Tests create and delete temporary erasure disk directories and mutate numerous MinIO globals (`globalIsErasure`, `globalObjectAPI`, `globalEndpoints`, `globalBootTime`, IAM/config subsystems, `globalMinioAddr`). `TearDown` is required to clean disks and restore globals. The service restart test reads from the global service signal channel but only starts a receiver for restart; stop command helpers exist but are not currently exercised.

## Dependencies And Integration Points
The file relies on test helpers from the broader MinIO `cmd` package: `resetTestGlobals`, `getRandomDisks`, `mustGetPoolEndpoints`, `newErasureServerPools`, `newTestConfig`, subsystem initialization functions, `newTestRequest`, and `signRequestV4`. It integrates with `madmin-go/v3`, `internal/auth`, `mux`, the admin router, IAM policy setup, and erasure object-layer internals.

## Risks And Edge Cases
Because tests mutate package globals, ordering and cleanup discipline matter. Missing `TearDown` or early failures before defers could leak temporary state into later tests. The service restart test can block if the handler does not send the expected signal; it uses a `WaitGroup` without timeout. The lock aggregation test constructs each peer with the full lock map, which verifies aggregation/quorum behavior under a synthetic model but may not reflect divergent peer lock views.

Coverage is selective. It does not test dry-run service behavior, stop handling, update handling, freeze/unfreeze, streaming handlers, KMS, inspect data, health anonymization, metrics, or most peer-failure paths. `TestExtractHealInitParams` assumes the body is valid and therefore does not cover `ErrRequestBodyParse`.

## Test Signals
The file itself is the test signal for `admin-handlers.go` and `admin-heal-ops.go`. It confirms that a registered admin route can authenticate and return server info in a single-node erasure setup, that restart command signaling reaches `globalServiceSignalCh`, that `toAdminAPIErrCode` maps quorum errors specially, that heal initialization rejects conflicting token/force combinations and invalid prefix-without-bucket paths, and that `topLockEntries` preserves key lock fields while aggregating server lists.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/admin-handlers_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/admin-heal-ops.go -->
# sources/object-store/minio/cmd/admin-heal-ops.go

## Purpose
`admin-heal-ops.go` implements the in-memory state machine and traversal logic behind MinIO admin heal operations. It tracks active heal sequences by path, exposes status/result consumption, prevents overlapping heals, supports stop and force-start, tracks local disk healing state, and queues bucket/object/meta heal tasks into the background heal routine.

## Important APIs, Types, And Functions
- `healStatusSummary` constants describe lifecycle states: not started, running, stopped, and finished.
- `allHealState` is the global coordinator with a mutex, `healSeqMap` indexed by heal path, `healLocalDisks` for local disk endpoints needing or undergoing healing, and `healStatus` keyed by disk ID.
- `newHealState`, `periodicHealSeqsClean`, `getHealSequence`, `getHealSequenceByToken`, `LaunchNewHealSequence`, `stopHealSequence`, and `PopHealStatusJSON` are the main sequence-management API used by admin handlers and background heal code.
- `healSequenceStatus` is the JSON status payload containing summary, failure detail, start time, settings, and result items.
- `healSource` describes a bucket/object/version heal task plus optional no-wait and options overrides.
- `healSequence` stores a single sequence's path, reporting settings, timings, token/client identity, cancel function, status, result indexes, scanned/healed/failed counters, activity timestamp, logger context, and mutex.
- `newHealSequence`, `healSequenceStart`, `traverseAndHeal`, `healItems`, `healDiskMeta`, `healMinioSysMeta`, `healBuckets`, `healBucket`, `healObject`, `queueHealTask`, and result/counter helpers implement the traversal and task queueing flow.

## Control Flow
A handler creates a `healSequence` with validated bucket/prefix/options and passes it to `LaunchNewHealSequence`. If the request is force-started, the existing sequence on the same path is stopped first. Otherwise, launch rejects an active sequence on the same path and then rejects any active sequence whose path overlaps the new path in either direction. Once accepted, the sequence is stored in `allHealState.healSeqMap`, a client token is returned, and a goroutine starts `healSequenceStart` unless the token is the special background-healing token.

`healSequenceStart` marks the sequence running, starts `traverseAndHeal`, then waits for either traversal completion or context cancellation. Completion sets `endTime` and marks finished on nil error or stopped with failure detail on error. Cancellation marks the sequence ended and drains the traversal channel asynchronously to avoid leaking the traversal goroutine.

Traversal heals MinIO system metadata for site-wide heals, then heals either the requested bucket or all buckets sorted newest first. Bucket healing first queues a bucket-level heal task, then calls `objAPI.HealObjects` to visit object versions and invoke `healObject`. `queueHealTask` increments scanned counters, sends work to `globalBackgroundHealRoutine.tasks`, optionally returns immediately for no-wait tasks, waits for a response when needed, updates healed/failed counters, annotates quorum-loss detail, and pushes a `madmin.HealResultItem` into the status buffer when progress reporting is enabled.

Status consumption is token-gated. `PopHealStatusJSON` finds the sequence by path, validates the client token, marshals the current status, remembers the last sent result index, and clears consumed `Items` from memory. If the sequence no longer exists, it returns a synthetic finished status.

## State And Persistence Behavior
All explicit heal sequence state in this file is in memory. Completed sequences remain in `healSeqMap` for `keepHealSeqStateDuration` and are removed by `periodicHealSeqsClean`. Forced stop removes the sequence immediately after it has ended. Heal result buffering is bounded by `maxUnconsumedHealResultItems`; if clients stop consuming results for `healUnconsumedTimeout`, push operations fail with `errHealIdleTimeout`, effectively stopping traversal.

The actual healing side effects are delegated to the object layer and background heal routine. This file queues `healTask`s that can repair bucket metadata, object metadata/data, and MinIO system metadata. Local disk healing state is tracked in maps and can be updated from `healingTracker` snapshots; `getLocalHealingDisks` returns copied status suitable for background heal status responses.

## Dependencies And Integration Points
This file is tightly coupled to `admin-handlers.go` via `globalAllHealState`, `HealHandler`, and background status endpoints. It depends on `madmin-go/v3` heal types, MinIO object-layer methods (`ListBuckets`, `HealObjects`), `globalBackgroundHealRoutine.tasks`, `healingTracker`, endpoint topology, logging request info, API error conversion, `waitForLowHTTPReq`, and global distributed-mode token decoration helpers.

## Risks And Edge Cases
Concurrency is central. `allHealState` and each `healSequence` use locks, but operations such as stop wait loops and result pushing can block for long periods. `stopHealSequence` sleeps in one-second increments until `hasEnded`, so a traversal stuck inside a slow heal operation delays stop responses. `pushHealResultItem` uses a bounded buffer but waits up to 24 hours when clients do not consume results, which protects memory at the cost of pausing healing work for a very long time.

Path overlap checks use prefix matching over joined paths. This prevents many conflicts but requires path normalization to be correct before sequence creation. Background healing is special-cased to never end and not spawn a redundant goroutine. `healSequenceStart` sets cancellation summary to finished rather than stopped, which may be intentional graceful-stop semantics but can be surprising to status consumers. `queueHealTask` may silently skip no-wait tasks when the background queue is full, relying on later background healing.

## Test Signals
`admin-handlers_test.go` covers `extractHealInitParams`, which validates inputs before this state machine is entered. It does not directly test `LaunchNewHealSequence`, overlap rejection, stop behavior, result consumption, timeout behavior, or traversal. The strongest test signal for this file in the subset is therefore parameter-level validation rather than state-machine coverage.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/admin-heal-ops.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/admin-router.go -->
# sources/object-store/minio/cmd/admin-router.go

## Purpose
`admin-router.go` defines the versioned MinIO admin HTTP route surface and common middleware for admin handlers. It wires `/minio/admin/<version>` paths to methods on `adminAPIHandlers`, applies gzip, tracing, audit logging, and object-layer readiness checks, and conditionally registers erasure-only or config-enabled APIs.

## Important APIs, Types, And Functions
- Constants define `adminPathPrefix`, `adminAPIVersion`, `adminAPIVersionPrefix`, and special site-replication/client speedtest route suffixes.
- `gzipHandler` is a package-level gzhttp wrapper configured with minimum response size and best-speed gzip compression.
- `hFlag` and flags `noGZFlag`, `traceAllFlag`, and `noObjLayerFlag` control middleware behavior.
- `hFlag.Has` checks flag inclusion.
- `adminMiddleware` wraps each handler with request context setup, audit logging, optional object-layer availability check, trace header/body instrumentation, and optional gzip compression.
- `adminAPIHandlers` is the receiver type for all admin handler methods.
- `registerAdminRouter` creates the admin subrouter and registers all admin API routes for the configured version.

## Control Flow
`registerAdminRouter` creates a subrouter under `adminPathPrefix`, iterates the supported admin API versions, and registers routes by HTTP method, path, handler method, middleware flags, and query constraints. The router registers V2 and deprecated forms for service and update APIs; info, inspect, storage, data usage, metrics; erasure-only heal, pools, rebalance; profiling; config operations when `enableConfigOps` is true; IAM and identity provider operations; bucket quota, replication, batch, metadata, tier, site-replication, lock, speedtest, trace, log, KMS, health, and token-revocation APIs.

`adminMiddleware` is applied at registration time. At request time it attaches a new MinIO request context with handler API name, defers audit logging, checks object-layer and notification subsystem readiness unless `noObjLayerFlag` is present, wraps the handler in header-only or full request tracing based on `traceAllFlag`, and gzip-wraps the resulting handler unless `noGZFlag` is present.

After all versioned routes are registered, `NotFoundHandler` and `MethodNotAllowedHandler` are set to traced error handlers for the admin subrouter.

## State And Persistence Behavior
The file does not persist state. It constructs router registrations and a gzip wrapper at package initialization. Middleware reads global object-layer and notification subsystem readiness and writes request-scoped logging/audit state. Route availability depends on globals such as `globalIsDistErasure`, `globalIsErasure`, and the `enableConfigOps` argument.

## Dependencies And Integration Points
The router integrates with `github.com/minio/mux`, `madmin.AdminAPIVersion`, `gzhttp`, MinIO logging/audit/tracing helpers, `newObjectLayerFn`, `globalNotificationSys`, and every handler method implemented across admin-related files. It is the primary boundary between MinIO's HTTP layer and admin subsystem methods.

## Risks And Edge Cases
Because route matching uses query constraints in several places, route ordering matters for overloaded paths such as `/service`, `/update`, `/list-canned-policies`, and heal paths. Misplaced or missing middleware flags can break streaming responses (`noGZFlag`), allow handlers to run before object-layer readiness, or omit full request tracing. `noObjLayerFlag` is necessary for initialization-time diagnostics like `/info` but expands handler responsibility for nil global checks.

The route file is very broad; adding new admin APIs risks accidental mismatch between method/path/query, policy enforcement in the target handler, and middleware flags. Conditional erasure-only registration means clients may see route-not-found rather than handler-level not-implemented errors depending on deployment mode.

## Test Signals
`admin-handlers_test.go` indirectly verifies router registration for `/service?type=2` and `/info` by constructing signed requests and serving them through the mux router returned by `registerAdminRouter`. There is no exhaustive route-table test in this subset, so most route registrations rely on broader integration coverage or client compatibility tests outside these files.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/admin-router.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/admin-server-info.go -->
# sources/object-store/minio/cmd/admin-server-info.go

## Purpose
`admin-server-info.go` builds the local node portion of MinIO admin server information. It collects endpoint identity, pool membership, peer reachability, process/runtime memory and GC stats, redacted MinIO environment variables, and local disk state for inclusion in `madmin.ServerProperties`.

## Important APIs, Types, And Functions
- `getLocalServerProperty(endpointServerPools EndpointServerPools, r *http.Request, metrics bool) madmin.ServerProperties` is the file's sole function.
- It uses endpoint pool topology to determine local pool numbers and network status.
- It reads Go runtime memory and GC stats, truncating GC pause slices to at most five entries.
- It redacts sensitive MinIO environment variables before adding them to the response.
- It obtains local storage info from the object layer when initialized, otherwise returns offline disk placeholders.

## Control Flow
The function selects an address from `globalLocalNodeName`, `r.Host`, or distributed-erasure global state. It walks all endpoints. Local endpoints add pool numbers and are marked online in the network map. Remote endpoints are checked once per host with `isServerResolvable` and classified online, offline, or timed out based on network error helpers.

After network collection, it reads `runtime.MemStats` and `debug.GCStats`, constructs `madmin.ServerProperties`, sorts pool numbers, and sets `PoolNumber` only when exactly one pool is local; otherwise it uses `math.MaxInt` to indicate unset/multiple. It scans `os.Environ`, keeps only `MINIO` and `_MINIO` variables, and redacts known credentials plus variables containing `password` or ending in `key`. Finally, it reads local object-layer storage info with the requested metrics flag or returns initializing/offline disk state if the object layer is unavailable.

## State And Persistence Behavior
The function is read-only. It observes globals, endpoint reachability, environment variables, runtime process stats, and object-layer storage state. It does not mutate persistent storage or global state.

## Dependencies And Integration Points
This function is called by `getServerInfo` in `admin-handlers.go`. It depends on endpoint types, `globalLocalNodeName`, `globalIsDistErasure`, `globalBootTime`, build metadata (`Version`, `CommitID`), `newObjectLayerFn`, `getOfflineDisks`, `globalEndpoints`, MinIO config/KMS environment variable names, and `madmin-go/v3` response types.

## Risks And Edge Cases
Network status depends on a five-second resolvability check per remote host; large clusters or slow DNS/network conditions can make `/info` slower. Environment redaction is pattern-based and may miss secrets that do not match known names, contain `password`, or end in `key`, though it covers core MinIO/KMS variables. Conversely, benign variables ending in `key` are redacted. The function includes environment variable names even when values are redacted, which can still reveal configuration shape.

`PoolNumber` uses `math.MaxInt` for unset/multiple-pool cases, so callers must use `PoolNumbers` for accurate multi-pool reporting. The address choice differs between standalone and distributed erasure modes, and `r` can be nil for internal health generation.

## Test Signals
`TestAdminServerInfo` in `admin-handlers_test.go` indirectly covers this function by calling `/info` through the router and verifying the response region in a single-node erasure setup. The test does not assert redaction, runtime stats, network classification, pool-number behavior, or offline object-layer behavior.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/admin-server-info.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/api-datatypes.go -->
# sources/object-store/minio/cmd/api-datatypes.go

## Purpose
`api-datatypes.go` defines small XML-facing datatypes used by S3-compatible API request and response processing, especially multi-object delete and create-bucket location parsing. The types bridge MinIO internal replication/versioning metadata with AWS-compatible XML field names.

## Important APIs, Types, And Functions
- `DeletedObject` describes a deleted object in XML responses with optional delete-marker fields, object key, version ID, delete-marker modification time, replication state, and an internal `found` flag.
- `DeleteMarkerMTime` embeds `time.Time` and customizes XML marshaling.
- `DeleteMarkerMTime.MarshalXML` omits zero timestamps and emits RFC3339 timestamps otherwise.
- `ObjectV` carries an object key and version ID.
- `ObjectToDelete` embeds `ObjectV` and adds delete-marker replication status, version purge status, internal purge-status aggregation, and replication decision text.
- `createBucketLocationConfiguration` maps the `CreateBucketConfiguration` XML body and location constraint.
- `DeleteObjectsRequest` maps the multi-delete request body with quiet mode and a list of `ObjectToDelete` entries.

## Control Flow
There is no runtime control flow beyond XML marshaling. The Go `encoding/xml` package uses field tags during request decode and response encode. `DeleteMarkerMTime.MarshalXML` checks `IsZero`; when zero it returns nil without emitting an element, otherwise it encodes the embedded time formatted with `time.RFC3339`.

## State And Persistence Behavior
The file defines transient request/response structs only. It does not persist state. Internal fields such as `ReplicationState`, `ReplicateDecisionStr`, and `found` are used by other API logic to carry decisions alongside XML-facing data without exposing them directly.

## Dependencies And Integration Points
The file depends on `encoding/xml` and `time`, plus package-local types `ReplicationState` and `VersionPurgeStatusType`. It integrates with S3 API handlers that parse `CreateBucketConfiguration` and `DeleteObjectsRequest` XML bodies and produce `DeletedObject` response entries. Replication and versioning subsystems consume the hidden status fields.

## Risks And Edge Cases
XML tag compatibility is important because clients expect AWS S3 field names such as `DeleteMarkerVersionId`, `Key`, `VersionId`, `CreateBucketConfiguration`, and `LocationConstraint`. A zero `DeleteMarkerMTime` emits no XML, which is intentional but can surprise callers expecting an empty element. The unexported `found` flag is not serialized and must only be interpreted inside package logic. This file does not validate object names, versions, or replication status values; validation must happen in consuming handlers.

## Test Signals
No tests in this subset directly cover these datatypes. Coverage likely comes from broader S3 API delete/create-bucket tests outside the listed files. Relevant missing tests would include XML round trips for multi-delete quiet/object entries and `DeleteMarkerMTime` zero/non-zero marshal behavior.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/api-datatypes.go -->
