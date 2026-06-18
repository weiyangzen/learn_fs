# subset-b-000504 Research

Grouped research report for the BeeGFS remote/sync job and worker-management files. Each section is source-path aligned for deterministic reconciliation into per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/rst/remote/internal/job/manager.go -->
# sources/distributed-fs/beegfs-go/rst/remote/internal/job/manager.go

## Purpose
This file implements the BeeRemote job manager. It accepts job requests from gRPC, filesystem-event channels, and worker callbacks; persists job state by path in a Badger-backed `kvstore.MapStore`; schedules generated work through `remote/internal/workermgr`; and reconciles worker results into final job states.

## Important APIs, Types, and Functions
`Config` defines the path DB location, async request queue depth, and per-RST historical job retention limits. `Manager` owns lifecycle context, readiness locks, request/update/result channels, the path store, the worker manager, and a lock-release callback. `NewManager` builds buffered channels and installs the default BeeGFS file-lock cleanup behavior. `Start` opens the Badger-backed path store, marks the manager ready, and starts a select loop over job requests, job updates, and work results. `GetJobs`, `SubmitJobRequest`, `UpdatePaths`, `UpdateJobs`, `UpdateWork`, `GetRSTConfig`, `GetStubContents`, and `Stop` are the primary external APIs.

## Control Flow
Startup opens the path database and starts a goroutine that serially drains async request channels, while direct RPC methods can call the same synchronous APIs. `SubmitJobRequest` constructs a `Job`, locks or creates the path entry, rejects conflicting active jobs for the same path/RST, prunes terminal history, resolves the target RST, generates a work submission, and calls `workerManager.SubmitJob`. `UpdateJobs` locks one path entry, selects jobs by path, job ID, and optional RST filters, applies cancellation/deletion through `updateJobState`, and deletes path entries only when all jobs are removed. `UpdateWork` locks the path entry, updates one work result, and when every work result is terminal or failed it completes, aborts, fails, or marks the job unknown.

## State and Persistence Behavior
The path store maps a BeeGFS path to `map[jobID]*Job`; this keeps active and historical jobs for all RSTs associated with that path. The manager uses Badger transactions through `CreateAndLockEntry`/`GetAndLockEntry` so job creation, update, and deletion are committed atomically with lock release. Active jobs block duplicate submissions for the same path/RST; terminal jobs can be retained and garbage-collected by `MinJobEntriesPerRST`/`MaxJobEntriesPerRST`. Work results are stored inside the persisted `Job`, including assigned node and pool information. The default lock cleanup clears BeeGFS access flags only after no active jobs remain and the file is not offloaded.

## Dependencies and Integration Points
The manager depends on `common/kvstore` and Badger for durable state, `common/rst` for job generation/completion and sentinel errors, `ctl/pkg/ctl/entry` for BeeGFS file data state and access-flag cleanup, `workermgr.Manager` for worker scheduling and cancellation, protobuf packages for all public wire messages, and gRPC `status` codes for worker-result errors. It is called by `remote/internal/server` and receives work results from BeeSync workers through `UpdateWork`.

## Risks and Edge Cases
The code intentionally notes a crash window after worker scheduling but before the updated path entry is committed; scheduled work could exist without durable assignment records. `Start` returns without unlocking `readyMu` if called while already ready, which is a deadlock risk for future callers. Async channel receives do not check `ok`, so closed channels would feed nil requests. Force cancellation/deletion can leave orphaned remote artifacts by design. The status message concatenation in missing-RST/abort-error branches duplicates existing messages due to `status.GetMessage() + (status.GetMessage() + ...)`. `UpdateWork` assumes the manager is ready indirectly through a valid store but does not take `readyMu`.

## Test Signals
`manager_test.go` exercises scheduling, duplicate conflict handling, multi-RST same-path submissions, async update channels, cancellation, deletion, completed-job protection, forced deletion, scheduling-error recovery, unknown-state handling, worker-result completion/cancellation transitions, mixed terminal-state unknown handling, and sentinel generation-status mapping. The tests use mock workers and mock filesystems; they do not cover real Badger crash recovery, real BeeGFS access-flag clearing, or the startup double-call lock bug.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/rst/remote/internal/job/manager.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/rst/remote/internal/job/manager_test.go -->
# sources/distributed-fs/beegfs-go/rst/remote/internal/job/manager_test.go

## Purpose
This file provides integration-style tests for the BeeRemote job manager using temporary Badger databases, mock BeeGFS filesystems, mock RSTs, and mock worker nodes. It validates that job state, persisted path entries, work results, and update semantics remain coherent across normal and failure paths.

## Important APIs, Types, and Functions
`tempPathForTesting` creates disposable DB directories under `/tmp`. `TestManage` covers startup, basic submission, duplicate handling, multi-RST scheduling, and async cancellation. `TestUpdateJobRequestDelete` focuses on cancellation/deletion by path and job ID, including terminal-state rules and force update. `TestManageErrorHandling` drives scheduling and cancellation failures. `TestUpdateJobResults` simulates worker result callbacks. `TestSubmitJobRequestSentinelErrorHandling` covers generation-status sentinel errors and database update behavior.

## Control Flow
Each test constructs a `workermgr.Manager` with mock worker expectations, starts it, creates a job manager using `withIgnoreReleaseUnusedFileLockFunc`, and submits protobuf job/update requests. Tests query jobs through `GetJobs` with exact path, path prefix, or job ID/path selectors, then inspect job and work-result states. Several tests send requests through the manager's channels and sleep briefly to let the async loop process updates.

## State and Persistence Behavior
Temporary path-store directories are removed at test cleanup. Tests assert that deleting the last job removes the path entry, that completed jobs remain persisted unless forced, that unknown jobs block new submissions until cancelled, and that result updates mutate stored work states. Mock worker responses populate the manager's persistent work-result map.

## Dependencies and Integration Points
The tests integrate `remote/internal/job`, `remote/internal/workermgr`, `remote/internal/worker`, `common/filesystem`, `common/kvstore`, `common/rst`, Testify assertions/mocks, and protobuf builders. They indirectly cover work manager scheduling contracts because the job manager uses `workerManager.SubmitJob` and `UpdateJob`.

## Risks and Edge Cases
The tests use `time.Sleep(2 * time.Second)` for async channel processing, which can make them slower and potentially timing-sensitive. They bypass real file-lock cleanup with `withIgnoreReleaseUnusedFileLockFunc`, so production lock-release errors are not covered. Mock workers return deterministic statuses but do not simulate network reconnects, real worker heartbeats, or Badger failures during commit.

## Test Signals
The file is itself the strongest test signal for job manager behavior. It confirms duplicate active jobs return the existing job, failed scheduling can produce cancelled or unknown jobs depending on cancellation confirmation, mixed terminal work results make the job unknown, and generation statuses like already-complete/offloaded are persisted as recreated final job records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/rst/remote/internal/job/manager_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/rst/remote/internal/job/utils.go -->
# sources/distributed-fs/beegfs-go/rst/remote/internal/job/utils.go

## Purpose
This small utility file converts internal worker-result state into the protobuf shape returned by BeeRemote job APIs.

## Important APIs, Types, and Functions
`getProtoWorkResults(workResults map[string]worker.WorkResult) []*beeremote.JobResult_WorkResult` iterates over stored `worker.WorkResult` values and builds `beeremote.JobResult_WorkResult` messages. It carries through the latest `flex.Work`, assigned worker node ID, and assigned pool as a string.

## Control Flow
The function allocates an empty result slice, iterates over the map, builds one protobuf result for each entry, appends it, and returns the slice. Map iteration order is deliberately unspecified.

## State and Persistence Behavior
The function is read-only and performs no persistence. It copies pointers from persisted `WorkResult` structures into response messages, so callers receive the stored work object without re-synthesizing request details.

## Dependencies and Integration Points
It depends on `remote/internal/worker` for the internal result type and on `beeremote` protobufs for response construction. `manager.go` uses this helper in submission, update, duplicate-conflict, and sentinel-error responses.

## Risks and Edge Cases
Because Go map iteration is nondeterministic, response order is not stable. Callers and tests must match by request ID rather than slice index unless they control the map shape. The helper does not filter nil work results, so corrupted internal state could propagate nil protobuf fields into responses.

## Test Signals
`utils_test.go` validates status, message, assigned node, and assigned pool conversion while accounting for nondeterministic map order via request IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/rst/remote/internal/job/utils.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/rst/remote/internal/job/utils_test.go -->
# sources/distributed-fs/beegfs-go/rst/remote/internal/job/utils_test.go

## Purpose
This file tests conversion of internal `worker.WorkResult` records to BeeRemote protobuf job-result work-result records.

## Important APIs, Types, and Functions
`TestGetWorkResultsForResponse` builds two internal work results with distinct request IDs, nodes, pools, statuses, and messages, calls `getProtoWorkResults`, and verifies the response fields.

## Control Flow
The test uses the returned work result's request ID to reconstruct expected status/message/node values. This avoids assuming any ordering from Go map iteration.

## State and Persistence Behavior
The test is in-memory only and does not touch Badger or manager state. It verifies response construction over already materialized internal records.

## Dependencies and Integration Points
The test uses Testify, `worker.WorkResult`, `worker.BeeSync`, and `flex.Work` builders. It provides coverage for job-manager response helpers used by gRPC-facing APIs.

## Risks and Edge Cases
The test covers normal populated results but not nil `WorkResult`, empty maps, unknown pools, or duplicate/malformed request IDs. It also assumes request IDs are numeric for its expected-status calculation.

## Test Signals
Passing tests indicate that assigned node, assigned pool, status, and message survive conversion from internal state to protobuf response state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/rst/remote/internal/job/utils_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/rst/remote/internal/server/server.go -->
# sources/distributed-fs/beegfs-go/rst/remote/internal/server/server.go

## Purpose
This file implements the BeeRemote gRPC server. It exposes job submission/query/update, worker-result ingestion, RST configuration discovery, stub content lookup, and capability reporting by adapting protobuf RPCs to the `job.Manager`.

## Important APIs, Types, and Functions
`Config` holds listen address and TLS files. `BeeRemoteServer` embeds the unimplemented protobuf server and stores logger, wait group, gRPC server, job manager, component registry, and start time. `New` configures optional TLS and registers the service. `ListenAndServe` starts serving in a goroutine. RPC methods include `SubmitJob`, `GetJobs`, `UpdatePaths`, `UpdateJobs`, `GetRSTConfig`, `UpdateWork`, `GetStubContents`, and `GetCapabilities`.

## Control Flow
The server creates a `grpc.Server`, binds a TCP listener, and forwards RPCs to job-manager methods. Streaming RPCs (`GetJobs`, `UpdatePaths`) create buffered response channels and a sender goroutine, then wait until the manager closes the channel. `SubmitJob` maps sentinel job-manager errors into response status enums instead of returning gRPC errors for expected job states. `UpdateJobs` maps missing DB entries to gRPC `NotFound`.

## State and Persistence Behavior
The server itself persists nothing. It tracks outstanding RPCs with a wait group so `Stop` can stop the gRPC server and wait for handlers. All durable job and work state is delegated to `job.Manager`. Capabilities include process start time from `startTime`.

## Dependencies and Integration Points
This is the public BeeRemote RPC boundary. It integrates `job.Manager`, `registry.ComponentRegistry`, `common/rst` sentinel errors, `common/kvstore` errors, gRPC TLS credentials, protobuf `beeremote` and `flex`, and timestamp conversion.

## Risks and Edge Cases
Streaming send errors are ignored intentionally so the sender drains the response channel and avoids blocking the producer; this means client disconnect details are not surfaced. `ListenAndServe` treats any `Serve` return as an error, so a normal stop may report through `errChan` depending on gRPC behavior. TLS is disabled when cert/key are absent or `TlsDisable` is true, with only a warning.

## Test Signals
No direct server tests are in this subset. Behavior is indirectly exercised by job-manager tests and by BeeSync worker/client integration expectations, but RPC-level streaming, TLS, listener failure, and capability responses need dedicated coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/rst/remote/internal/server/server.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/rst/remote/internal/worker/beesync.go -->
# sources/distributed-fs/beegfs-go/rst/remote/internal/worker/beesync.go

## Purpose
This file implements the concrete BeeSync worker-node client used by BeeRemote to configure sync nodes, submit work requests, update work state, and monitor readiness.

## Important APIs, Types, and Functions
`BeeSyncNode` embeds `baseNode` and stores a gRPC connection and `flex.WorkerNodeClient`. `newBeeSyncNode` wires the node as its own `grpcClientHandler`. `connect` creates the gRPC connection, resolves unspecified BeeRemote bind addresses for callback reachability, checks worker capabilities, sends `UpdateConfig`, and sends `BulkUpdateWork`. `heartbeat`, `disconnect`, `SubmitWork`, `UpdateWork`, and `reportError` implement the rest of the worker interface.

## Control Flow
`connect` optionally reads a TLS CA file, opens a client connection via `beegrpc`, discovers a concrete Remote address if the configured host is unspecified, verifies required features via `registry.GetComponentRegistry`, applies node config, and replays bulk work updates. `SubmitWork` and `UpdateWork` require the node to be `ONLINE`, retry `FailedPrecondition` responses for configured attempts, notify the base handler once via `rpcErr`, and return protobuf work results. `SubmitWork` panics on `AlreadyExists` because duplicate work on a node is considered an invariant violation.

## State and Persistence Behavior
The BeeSync node itself does not persist data; it manages connection/client state and reports transitions to `baseNode`. Configuration and outstanding work are replayed to the sync node on reconnect. RPC wait-group accounting lets the base node drain or cancel in-flight unary calls during disconnect.

## Dependencies and Integration Points
The code depends on `common/beegfs/beegrpc` for TLS/proxy-aware client connections, `common/registry` for capability checks, gRPC status codes, protobuf `flex.WorkerNode`, and `baseNode` lifecycle management. It is instantiated by `worker.NewWorkerNodesFromConfig` and used by `workermgr.Pool`.

## Risks and Edge Cases
The `alreadyNotified` flag is never set after sending `rpcErr`, so repeated retry iterations may attempt duplicate nonblocking notifications. `SubmitWork` panic on `AlreadyExists` can crash BeeRemote instead of isolating a bad node. `connect` treats feature incompatibility as retryable, which may cause repeated reconnect attempts for static version mismatches. Address autodetection mutates a cloned config only after a heartbeat succeeds; failures here can prevent node startup when Remote listens on an unspecified address.

## Test Signals
`beesync_connect_test.go` verifies feature negotiation failures and unimplemented capability handling. There is no direct test for successful config replay, TLS hints, SubmitWork retry behavior, panic-on-duplicate behavior, or address autodetection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/rst/remote/internal/worker/beesync.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/rst/remote/internal/worker/beesync_connect_test.go -->
# sources/distributed-fs/beegfs-go/rst/remote/internal/worker/beesync_connect_test.go

## Purpose
This file tests BeeSync worker-node connection capability negotiation against lightweight in-process gRPC worker servers.

## Important APIs, Types, and Functions
`testWorkerNodeServer` implements `GetCapabilities` with a configurable feature map. `unimplementedCapabilitiesServer` leaves capabilities unimplemented. `startWorkerNodeServer` creates a local gRPC server on `127.0.0.1:0`. `newTestBeeSyncNode` builds a TLS-disabled BeeSync node for the test address. `connectInputs` creates minimal config and bulk-update inputs. The two tests assert required-feature and unimplemented-capability failures.

## Control Flow
Each test starts a temporary gRPC server, constructs a BeeSync node, calls `node.connect`, and inspects the retry flag and error chain. The required-feature test provides one supported feature but asks for an extra feature. The unimplemented test checks behavior when the server does not support the capability RPC.

## State and Persistence Behavior
The tests use no persisted state. They allocate a gRPC listener and close it in cleanup; the BeeSync node closes its client connection with `disconnect`.

## Dependencies and Integration Points
The tests integrate the worker client with actual gRPC server plumbing and `common/registry` capability helpers. They validate the connection-time contract consumed by `baseNode.connectLoop`.

## Risks and Edge Cases
The tests focus on negative capability cases. They do not test successful `UpdateConfig`/`BulkUpdateWork`, heartbeat address discovery, TLS configuration, retry backoff, or runtime SubmitWork/UpdateWork behavior.

## Test Signals
Passing tests confirm that incompatible or capability-less sync nodes surface registry errors and are treated as retryable connection failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/rst/remote/internal/worker/beesync_connect_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/rst/remote/internal/worker/config.go -->
# sources/distributed-fs/beegfs-go/rst/remote/internal/worker/config.go

## Purpose
This file defines worker-node configuration and factory logic for BeeRemote worker clients.

## Important APIs, Types, and Functions
`Type` enumerates supported worker pools: `Unknown`, `BeeSync`, and `Mock`. `Config` includes identity, address, TLS/proxy settings, reconnect/disconnect/retry/heartbeat timing, and embedded type-specific config. `BeeSyncConfig` is currently empty. `MockConfig` and `MockExpectation` define Testify expectations for mock worker nodes. `NewWorkerNodesFromConfig` builds all valid workers while accumulating errors. `newWorkerNodeFromConfig` applies timing defaults, builds base contexts/wait groups, and dispatches to BeeSync or mock constructors.

## Control Flow
The public factory loops over configs, attempts to create each node, appends valid workers, and returns a `types.MultiError` if any config failed. The single-node factory fills zero timing values with defaults, initializes `baseNode` as `OFFLINE`, and switches on worker type.

## State and Persistence Behavior
No persistent state is written. The function initializes in-memory lifecycle state: node context, RPC context, wait group, state mutexes, and RPC error channel. Created nodes must later be driven by `Handle`.

## Dependencies and Integration Points
The file depends on `common/types.MultiError`, zap logging, and worker implementations in `beesync.go`/`mock.go`. `workermgr.NewManager` uses it to populate node pools.

## Risks and Edge Cases
Unknown worker types are rejected but do not prevent other valid nodes from being returned. Defaults are hard-coded here pending centralized config defaults, so CLI/config docs must remain aligned manually. The unbuffered `rpcErr` channel relies on nonblocking sends in worker implementations to avoid RPC deadlocks.

## Test Signals
This subset has indirect coverage through job-manager and work-manager tests that create mock nodes. There is no direct table test for defaults, multi-error behavior, or unknown type rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/rst/remote/internal/worker/config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/rst/remote/internal/worker/error.go -->
# sources/distributed-fs/beegfs-go/rst/remote/internal/worker/error.go

## Purpose
This file defines worker-package sentinel errors.

## Important APIs, Types, and Functions
`ErrWorkRequestNotFound` indicates that a requested work item does not exist on the worker node. It is used to distinguish a successful cleanup-equivalent condition from transport or state errors.

## Control Flow
There is no executable control flow beyond variable initialization.

## State and Persistence Behavior
No state is persisted. The sentinel supports `errors.Is` checks across worker and worker-manager layers.

## Dependencies and Integration Points
`BeeSyncNode.UpdateWork` returns `ErrWorkRequestNotFound` for gRPC `NotFound`. `workermgr.Manager.UpdateJob` treats this as a cancellation-equivalent outcome and marks the work request cancelled rather than unknown.

## Risks and Edge Cases
The sentinel conflates "not found because already gone" and "not found because the wrong node was contacted"; the caller currently treats it as safe cancellation. Correctness depends on worker assignment metadata being accurate.

## Test Signals
No direct tests target this file. Its behavior is indirectly covered by cancellation paths where worker update results are interpreted by `workermgr.UpdateJob`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/rst/remote/internal/worker/error.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/rst/remote/internal/worker/mock.go -->
# sources/distributed-fs/beegfs-go/rst/remote/internal/worker/mock.go

## Purpose
This file implements a Testify-backed worker node used by tests in other packages to simulate BeeSync worker behavior without running gRPC services.

## Important APIs, Types, and Functions
`MockNode` embeds `baseNode` and `mock.Mock`, satisfying both `Worker` and `grpcClientHandler`. `newMockNode` installs configured expectations. `connect`, `disconnect`, `SubmitWork`, and `UpdateWork` delegate to Testify calls. `heartbeat` returns a ready response without requiring expectations.

## Control Flow
Factory setup loops through `MockExpectation` entries and registers `On(...).Return(...)` calls. `SubmitWork` and `UpdateWork` reject offline nodes, call the configured mock method, report errors through `rpcErr`, and otherwise echo back work metadata with a fresh copy of the configured status.

## State and Persistence Behavior
No persistent state is used. The mock relies on `baseNode` state transitions and RPC wait-group tracking like real workers. It intentionally copies returned status objects to prevent tests from sharing mutable status pointers across requests.

## Dependencies and Integration Points
The mock depends on Testify mock and protobuf `flex`. It is used by job-manager tests and workermgr tests through `worker.Config{Type: worker.Mock}`.

## Risks and Edge Cases
`UpdateWork` cannot set `Path` in its returned `flex.Work` because the update request lacks a path; comments flag this as a possible source of future test issues. Expectations must include every method invoked by the test except heartbeat. Mock behavior may hide real gRPC status-code handling and reconnect behavior.

## Test Signals
The file is indirectly exercised by many tests in `remote/internal/job`. There are no direct tests of expectation setup, offline rejection, or error notification behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/rst/remote/internal/worker/mock.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/rst/remote/internal/worker/requests.go -->
# sources/distributed-fs/beegfs-go/rst/remote/internal/worker/requests.go

## Purpose
This file defines internal work-result metadata stored by BeeRemote for every work request assigned to a worker node.

## Important APIs, Types, and Functions
`WorkResult` stores `AssignedNode`, `AssignedPool`, and the latest protobuf `*flex.Work`. `Status` returns the mutable embedded status pointer. `InTerminalState` recognizes completed and cancelled work. `RequiresUserIntervention` recognizes failed work.

## Control Flow
The helper methods are simple status predicates used by job and worker managers. `Status` centralizes access to the protobuf status so callers can update state/message in place.

## State and Persistence Behavior
`WorkResult` is designed to be copied and Gob-encoded in job records. The comments note that `flex.Work` currently has no protobuf oneof fields, so custom Gob methods are not required for this wrapper. The latest worker result is persisted as part of `job.Job`.

## Dependencies and Integration Points
The type is used by `job.Manager`, `workermgr.Manager`, response utilities, and tests. It depends on worker `Type` and protobuf `flex.Work`.

## Risks and Edge Cases
Only `COMPLETED` and `CANCELLED` are considered terminal; `FAILED` requires user intervention and blocks automatic cleanup. If protobuf `flex.Work` changes shape, Gob compatibility may break. The mutable status pointer is convenient but allows callers to modify persisted state in place, so lock discipline must be maintained by owners.

## Test Signals
`requests_test.go` validates Gob round-tripping and checks expected protobuf field descriptors to catch shape changes that could break serialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/rst/remote/internal/worker/requests.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/rst/remote/internal/worker/requests_test.go -->
# sources/distributed-fs/beegfs-go/rst/remote/internal/worker/requests_test.go

## Purpose
This file guards the serialization contract for `worker.WorkResult`, which is stored in BeeRemote's Badger-backed job database.

## Important APIs, Types, and Functions
`TestEncodeDecodeWorkResults` constructs a populated `WorkResult`, Gob-encodes and decodes it, asserts equality, and validates protobuf descriptors for `flex.Work`, `flex.Work_Status`, and `flex.Work_Part`.

## Control Flow
After round-trip serialization, the helper `checkMessageFields` compares field counts, names, and protobuf kinds against expected maps. Descriptor assertions deliberately fail when the protobuf schema changes.

## State and Persistence Behavior
The test is in-memory only, but it models the persistence path used by the job path store. It confirms the current wrapper can be encoded without custom Gob methods despite embedding a protobuf message.

## Dependencies and Integration Points
It depends on Gob, protobuf reflection, Testify, `worker.WorkResult`, and `flex` message builders. The test protects `job.Manager` persistence indirectly because jobs contain maps of these records.

## Risks and Edge Cases
The test is intentionally schema-sensitive, so legitimate protobuf additions require test updates and a serialization review. It covers one representative populated object but not nil status, nil work, or unknown enum values.

## Test Signals
Passing tests indicate current work-result persistence can survive encode/decode and that protobuf field definitions have not silently changed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/rst/remote/internal/worker/requests_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/rst/remote/internal/worker/worker.go -->
# sources/distributed-fs/beegfs-go/rst/remote/internal/worker/worker.go

## Purpose
This file defines the common worker-node interface and the shared base lifecycle used by all BeeRemote worker clients.

## Important APIs, Types, and Functions
`Worker` is the external interface for node identity, state, lifecycle, work submission, and work updates. `grpcClientHandler` is the internal connection/heartbeat/disconnect interface implemented by concrete node types. `baseNode` stores logger, state, config, node/RPC contexts, RPC wait group, node mutex, and error channel. `State` enumerates `UNKNOWN`, `OFFLINE`, and `ONLINE`. `Handle`, `connectLoop`, `Stop`, `GetID`, `GetState`, and `GetNodeType` provide shared behavior.

## Control Flow
`Handle` serializes lifecycle handling with `nodeMu`, repeatedly connects offline nodes, marks them online, monitors shutdown, unary RPC errors, and heartbeat readiness, then transitions offline, drains in-flight RPCs up to `DisconnectTimeout`, cancels the RPC context, and disconnects. `connectLoop` retries `connect` with exponential backoff and jitter until success, fatal error, or node shutdown.

## State and Persistence Behavior
No durable state is written. Runtime state is protected by mutexes and contexts. `nodeCtx` controls the overall node lifetime; `rpcCtx` is recreated on every connection so RPCs can resume after disconnect; `rpcWG` tracks in-flight unary calls so disconnect can be graceful.

## Dependencies and Integration Points
Concrete implementations in `beesync.go` and `mock.go` embed `baseNode`. `workermgr.Pool` reads `GetState`, calls `SubmitWork` and `UpdateWork`, and starts `Handle` through `Pool.HandleAll`.

## Risks and Edge Cases
Heartbeat and reconnect are central to avoiding stale stateless sync nodes, but prolonged RPCs can be forcibly cancelled after timeout. The unbuffered `rpcErr` channel requires nonblocking send discipline. `connectLoop` jitter can set the delay to slightly below `MaxReconnectBackOff`, but if max is configured too low behavior may be noisy. There is no persistence of online/offline state, so all recovery depends on config replay.

## Test Signals
This file has no direct tests in the subset. It is indirectly exercised whenever mock workers are started in manager tests, but heartbeat failure, reconnect backoff, RPC drain timeout, and shutdown races are not directly covered.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/rst/remote/internal/worker/worker.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/rst/remote/internal/workermgr/errors.go -->
# sources/distributed-fs/beegfs-go/rst/remote/internal/workermgr/errors.go

## Purpose
This file defines sentinel errors used by the BeeRemote worker manager and worker pools.

## Important APIs, Types, and Functions
The exported errors are `ErrNoWorkersConnected`, `ErrFromAllWorkers`, `ErrNoWorkersInPool`, `ErrNoPoolsForNodeType`, and `ErrWorkerNotInPool`.

## Control Flow
There is no executable control flow beyond variable initialization. Callers wrap these sentinels with context and can inspect them with `errors.Is`.

## State and Persistence Behavior
No state is persisted. The errors annotate scheduling and cancellation failures that are stored later in work-result status messages by the manager.

## Dependencies and Integration Points
`pool.go` uses these errors when no workers can accept work or a target worker is missing. `manager.go` stores them in generated `flex.Work` statuses and uses them to decide whether all work requests were scheduled or updated.

## Risks and Edge Cases
The errors intentionally describe broad classes. Recovery behavior depends on higher layers preserving enough contextual message text, such as worker type and node ID, when wrapping them.

## Test Signals
No direct tests target the error declarations. They are indirectly exercised by scheduling and cancellation error paths in job-manager tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/rst/remote/internal/workermgr/errors.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/rst/remote/internal/workermgr/manager.go -->
# sources/distributed-fs/beegfs-go/rst/remote/internal/workermgr/manager.go

## Purpose
This file implements BeeRemote's worker manager: it configures remote storage targets, groups worker nodes into pools by type, submits generated work requests to the right pool, updates outstanding work during job cancellation, and exposes stub-content lookup.

## Important APIs, Types, and Functions
`Config` is currently empty. `Manager` stores node pools, a worker-node wait group, RST providers, the BeeGFS mount provider, and required feature set. `JobSubmission` groups all work requests for one job. `JobUpdate` describes a requested update over existing work results. `NewManager` initializes RST providers and worker pools. `Start`, `SubmitJob`, `UpdateJob`, `GetStubContents`, and `Stop` are the core methods.

## Control Flow
`NewManager` builds an RST map from config, rejects the reserved job-builder RST ID, adds a job-builder client, creates worker nodes, and organizes them into pools with shared `UpdateConfigRequest`. `Start` refuses to run with no valid pools and starts all pool handlers. `SubmitJob` maps each `flex.WorkRequest` type to a worker pool, assigns it, records assignment metadata, and if any request fails to schedule it immediately calls `UpdateJob` to cancel scheduled or created requests. `UpdateJob` iterates existing work results, handles unassigned created requests locally, contacts the assigned pool/node for cancellation, and updates statuses/messages.

## State and Persistence Behavior
The worker manager itself persists no database state, but it produces the `worker.WorkResult` map that the job manager persists. It owns long-lived RST clients and worker node clients. The job-builder RST provider is synthetic and added alongside configured RSTs.

## Dependencies and Integration Points
It depends on `common/rst` providers, `common/filesystem`, `remote/internal/worker`, protobuf `beeremote` and `flex`, and zap logging. It is called by `job.Manager` for job scheduling, cancellation, RST config listing, and stub-content parsing.

## Risks and Edge Cases
Partial scheduling failure triggers best-effort cancellation; if cancellation is not confirmed, the job becomes unknown and requires user action. Unsupported work request types map to `worker.Unknown` and become failed results. The manager logs but tolerates invalid worker configs if at least one valid pool remains. `Stop` starts `node.Stop` calls asynchronously through pools but does not wait on `nodeWG` itself in this method.

## Test Signals
There are no direct tests for this file in the subset, but job-manager tests exercise successful scheduling, scheduling failure, cancellation success/failure, and unknown-state outcomes through mock workers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/rst/remote/internal/workermgr/manager.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/rst/remote/internal/workermgr/pool.go -->
# sources/distributed-fs/beegfs-go/rst/remote/internal/workermgr/pool.go

## Purpose
This file implements worker pools for BeeRemote. A pool contains workers of one type and provides round-robin assignment plus targeted update of existing work on the node that owns it.

## Important APIs, Types, and Functions
`Pool` stores node type, ordered workers, worker lookup map, next round-robin index, mutex, and shared worker config. `HandleAll` starts each node handler with config and an initial bulk work update. `StopAll` requests every node to stop. `assignToLeastBusyWorker` assigns a work request to an online node. `updateWorkRequestOnNode` sends an update to the originally assigned worker node.

## Control Flow
`HandleAll` sends `UNCHANGED` bulk updates on startup because offline work mutation is not yet supported. `assignToLeastBusyWorker` locks the pool, loops up to four passes, skips offline nodes, calls `SubmitWork` on online nodes, advances the round-robin cursor, retries other workers on send errors, and returns aggregate errors when all online attempts fail. `updateWorkRequestOnNode` locks, looks up the assigned node by ID, builds a `flex.UpdateWorkRequest`, and calls `UpdateWork`.

## State and Persistence Behavior
No durable state is written. The pool maintains only in-memory assignment cursor state. Assignment decisions are captured by the caller in persisted `worker.WorkResult.AssignedNode` and `AssignedPool`.

## Dependencies and Integration Points
The pool depends on `worker.Worker`, worker states/types, `common/types.MultiError`, and protobuf `flex`. It is owned by `workermgr.Manager`.

## Risks and Edge Cases
Despite the comment naming "least busy", assignment is currently round-robin and does not account for work size or active load. The whole pool lock is held during `SubmitWork`/`UpdateWork`, so slow RPCs serialize assignment/update operations for that pool. If all nodes are offline, it sleeps three times before failing, adding latency to job submission. `StopAll` starts stop requests in goroutines and does not wait by itself.

## Test Signals
No direct pool tests appear in this subset. Behavior is indirectly validated through job-manager tests using mock nodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/rst/remote/internal/workermgr/pool.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/rst/sync/cmd/beegfs-sync/main.go -->
# sources/distributed-fs/beegfs-go/rst/sync/cmd/beegfs-sync/main.go

## Purpose
This file is the BeeSync daemon entrypoint. It parses configuration, initializes logging and BeeGFS client access, starts the BeeRemote client, starts the local work manager, exposes the worker-node gRPC server, and coordinates shutdown.

## Important APIs, Types, and Functions
Global build variables define version metadata. `capabilities` advertises `registry.FeatureFilterFiles`. `main` defines all CLI flags, config/env precedence help, version/dump-config/profiling options, mount-point checks, signal handling, client/server/manager construction, and shutdown ordering.

## Control Flow
The program parses flags, optionally prints version or config, initializes `configmgr`, logger, CTL logging, and the BeeGFS mount provider, then sets up signal cancellation. It checks the BeeGFS client `sysBypassFileAccessCheckOnMeta` setting when available. It creates a BeeRemote client, starts `workmgr.NewAndStart`, creates and serves the worker-node server, blocks on server error or OS signal, then stops server, work manager, and Remote client in order.

## State and Persistence Behavior
The entrypoint configures default persistent DB paths for the work journal and job store under `/var/lib/beegfs/sync`. It does not directly write job state, but it enables pprof, logging rotation, and runtime config initialization. It writes no commits or research state.

## Dependencies and Integration Points
It integrates pflag, `common/configmgr`, `common/logger`, registry capabilities, CTL/procfs BeeGFS access, `sync/internal/beeremote`, `sync/internal/config`, `sync/internal/server`, and `sync/internal/workmgr`.

## Risks and Edge Cases
Fatal startup errors terminate the process. Dynamic config updates are not handled here beyond initial config manager setup and BeeRemote-provided runtime config through the worker server. The procfs mount setting check is warning-only if the parameter is unavailable, preserving backward compatibility but reducing enforcement on older clients. pprof is exposed on localhost port when enabled.

## Test Signals
No direct tests cover `main.go`. Its dependencies are tested at lower layers, but CLI flag wiring, config precedence, shutdown ordering, procfs validation, and pprof setup are not directly covered in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/rst/sync/cmd/beegfs-sync/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/rst/sync/internal/beeremote/client.go -->
# sources/distributed-fs/beegfs-go/rst/sync/internal/beeremote/client.go

## Purpose
This file implements BeeSync's client wrapper for communicating back to BeeRemote. It supports dynamic provider replacement when BeeRemote sends updated callback configuration.

## Important APIs, Types, and Functions
`Config` stores static TLS/proxy settings plus dynamic `*flex.BeeRemoteNode`. `Client` embeds a `Provider`, stores config, and guards it with `readyMu`. `Provider` abstracts init/disconnect/update-work/submit-job operations. `New`, `CompareConfig`, `UpdateConfig`, `UpdateWorkRequest`, `SubmitJobRequest`, and `Disconnect` form the public API.

## Control Flow
`New` creates an empty client and applies initial dynamic config if present, tolerating nil config as an unready but valid client. `UpdateConfig` takes a write lock, disconnects the old provider, chooses a mock provider for `mock:0`, creates a gRPC provider for non-empty addresses, and rejects invalid addresses. Request methods take read locks, reject unready clients, call the provider, and classify gRPC status errors.

## State and Persistence Behavior
The client persists no job state. It owns connection/provider state and dynamic BeeRemote config. Updates are serialized against in-flight requests by the RW mutex, so provider replacement waits for active calls to finish.

## Dependencies and Integration Points
It is used by `sync/internal/workmgr` workers to send final work results and by the work manager during runtime config updates. It depends on protobuf `beeremote`/`flex`, gRPC status codes, protobuf equality, and concrete providers in `grpc.go`/`mock.go`.

## Risks and Edge Cases
There is no cancellation mechanism for in-flight `UpdateWorkRequest` calls during config updates; comments rely on worker retry behavior. Non-gRPC errors are treated as likely bugs but retryable for work updates. `NotFound` is non-retryable, matching force-deletion scenarios on BeeRemote. `UpdateConfig` disconnects the old provider before validating/creating the new one, so failed updates can leave the client without a provider.

## Test Signals
Work-manager tests use the mock provider path and exercise update-result retry behavior. There are no direct client tests for lock behavior, provider replacement failure, error classification, or `SubmitJobRequest`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/rst/sync/internal/beeremote/client.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/rst/sync/internal/beeremote/errors.go -->
# sources/distributed-fs/beegfs-go/rst/sync/internal/beeremote/errors.go

## Purpose
This file defines sentinel errors for BeeSync's BeeRemote client.

## Important APIs, Types, and Functions
`ErrNilConfiguration` identifies missing dynamic BeeRemote config. `ErrInvalidAddress` identifies an empty/invalid Remote address. `ErrUnableToConnect` wraps connection setup failures.

## Control Flow
There is no executable control flow beyond error initialization.

## State and Persistence Behavior
No state is persisted. The errors define stable conditions for client initialization/update logic.

## Dependencies and Integration Points
`client.go` returns `ErrNilConfiguration` for deferred setup and `ErrInvalidAddress` for unusable config. `grpc.go` wraps transport setup failures with `ErrUnableToConnect`.

## Risks and Edge Cases
The errors are broad and rely on wrapping messages for operational detail. Callers should use `errors.Is` when they need to distinguish deferred configuration from fatal setup.

## Test Signals
No direct tests target these sentinels. They are indirectly used by work-manager startup and BeeRemote client initialization paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/rst/sync/internal/beeremote/errors.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/rst/sync/internal/beeremote/grpc.go -->
# sources/distributed-fs/beegfs-go/rst/sync/internal/beeremote/grpc.go

## Purpose
This file implements the real gRPC provider used by BeeSync to communicate with BeeRemote and to initialize local BeeGFS network/auth configuration supplied by Remote.

## Important APIs, Types, and Functions
`grpcProvider` stores the gRPC connection and `beeremote.BeeRemoteClient`. Constants define local files for management TLS cert and auth secret. `init` opens the BeeRemote connection, writes dynamic management/auth materials, and initializes CTL global config. `disconnect`, `updateWork`, and `submitJob` perform provider operations.

## Control Flow
`init` optionally reads a TLS CA file, builds a proxy/TLS-aware client connection, creates the protobuf client, writes management TLS certificate and auth secret when enabled and provided, and calls `config.InitViperFromExternal` with management, auth, remote, worker, and timeout settings. `updateWork` and `submitJob` call the corresponding BeeRemote RPCs and add a TLS-misconfiguration hint for the common server-preface EOF message.

## State and Persistence Behavior
The provider writes BeeGFS management TLS and auth secret files under `/etc/beegfs` with mode `0600`. It initializes global CTL configuration, which cannot currently be changed after first initialization. It owns a gRPC connection that must be closed.

## Dependencies and Integration Points
It depends on `common/beegfs/beegrpc`, `ctl/pkg/config`, protobuf BeeRemote and Flex APIs, gRPC, and runtime CPU count. `beeremote.Client` creates this provider for real Remote addresses.

## Risks and Edge Cases
Updating BeeGFS network config after global Viper initialization is explicitly unsupported and returns an error requiring node restart. Secrets/certs are written to fixed paths, so permissions and filesystem availability matter. `disconnect` assumes `conn` is non-nil. TLS preface EOF hinting is message-string based and advisory only.

## Test Signals
No direct tests cover this file in the subset. Mock-provider tests cover higher-level client behavior, but real TLS/proxy connection setup, file writes, CTL config initialization, and RPC status mapping need integration tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/rst/sync/internal/beeremote/grpc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/rst/sync/internal/beeremote/mock.go -->
# sources/distributed-fs/beegfs-go/rst/sync/internal/beeremote/mock.go

## Purpose
This file provides a Testify-backed BeeRemote provider for BeeSync tests.

## Important APIs, Types, and Functions
`MockProvider` embeds `mock.Mock` and satisfies `Provider`. `init` and `disconnect` are no-ops. `updateWork` and `submitJob` call Testify expectations and return a configured error.

## Control Flow
Tests configure expectations on the mock provider after `beeremote.Client` selects it for address `mock:0`. Each provider method retrieves the first return argument and validates that non-nil values are errors.

## State and Persistence Behavior
No state is persisted. Test expectation state lives in the embedded Testify mock.

## Dependencies and Integration Points
The mock provider is selected by `Client.UpdateConfig` and is heavily used by `sync/internal/workmgr/manager_test.go` to assert final work results sent to BeeRemote.

## Risks and Edge Cases
The mock panics if a non-error return value is configured, which is useful for tests but not production behavior. It does not model gRPC status codes unless tests explicitly return status errors.

## Test Signals
The work-manager tests exercise `updateWork` expectations for completed, failed, and retrying work results. `submitJob` is not exercised in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/rst/sync/internal/beeremote/mock.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/rst/sync/internal/config/config.go -->
# sources/distributed-fs/beegfs-go/rst/sync/internal/config/config.go

## Purpose
This file defines the top-level BeeSync application configuration consumed by `configmgr`.

## Important APIs, Types, and Functions
`AppConfig` combines mount point, work-manager config, BeeRemote client config, worker server config, logging config, and developer options. It implements `configmgr.Configurable` through `NewEmptyInstance`, `UpdateAllowed`, and `ValidateConfig`.

## Control Flow
`NewEmptyInstance` returns a fresh config object for unmarshalling. `UpdateAllowed` currently permits all config updates because dynamic BeeRemote-provided settings are handled outside `configmgr`. `ValidateConfig` rejects nonpositive worker counts and nonpositive active work queue sizes.

## State and Persistence Behavior
The file defines configuration shape only. Persistence paths are contained inside nested work-manager config and are validated by the components that open them.

## Dependencies and Integration Points
It integrates `common/configmgr`, `common/logger`, `sync/internal/beeremote`, `sync/internal/server`, and `sync/internal/workmgr`. `cmd/beegfs-sync/main.go` uses it as the config manager schema.

## Risks and Edge Cases
Validation is intentionally minimal and does not check mount point, TLS file existence, DB path validity, or server address syntax. Because `UpdateAllowed` returns nil, future config-manager dynamic updates could be accepted even if components cannot apply them unless additional validation is added.

## Test Signals
No direct tests cover this config type. Startup paths indirectly rely on `ValidateConfig`, but invalid config combinations beyond worker counts and queue size are not tested here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/rst/sync/internal/config/config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/rst/sync/internal/server/server.go -->
# sources/distributed-fs/beegfs-go/rst/sync/internal/server/server.go

## Purpose
This file implements BeeSync's worker-node gRPC server, which BeeRemote calls to configure the node, submit work, cancel/update work, check heartbeat readiness, and inspect capabilities.

## Important APIs, Types, and Functions
`Config` defines address and TLS settings. `WorkerNodeServer` embeds the unimplemented Flex worker server and stores logger, wait group, gRPC server, work manager, capability registry, and start time. `New`, `ListenAndServe`, `Stop`, `UpdateConfig`, `BulkUpdateWork`, `SubmitWork`, `UpdateWork`, `Heartbeat`, and `GetCapabilities` implement lifecycle and RPC behavior.

## Control Flow
`New` creates a TLS-enabled or plaintext gRPC server and registers the Flex worker service. `ListenAndServe` starts a TCP listener and serves in a goroutine. `UpdateConfig` forwards RST and BeeRemote config to the work manager and returns success/failure in-band. `BulkUpdateWork` currently accepts only `UNCHANGED`. `SubmitWork` and `UpdateWork` call work-manager methods. `Heartbeat` reports manager readiness.

## State and Persistence Behavior
The server persists no state directly. It tracks active RPC handlers with a wait group. Durable work state lives in `workmgr.Manager`. Capabilities include start timestamp and build info from the registry.

## Dependencies and Integration Points
It integrates `sync/internal/workmgr`, `common/registry`, gRPC/TLS, protobuf `flex`, and zap logging. BeeRemote's `BeeSyncNode.connect`, `SubmitWork`, `UpdateWork`, and heartbeat calls target this server.

## Risks and Edge Cases
`BulkUpdateWork` does not yet support cancellation or replay updates for outstanding work, limiting offline recovery behavior. TLS is disabled if cert/key are missing or explicitly disabled, with only a warning. Some RPC methods do not increment/decrement the server wait group, unlike the remote server, so `Stop` may not fully wait for every handler path.

## Test Signals
No direct tests cover this server. BeeSync connection tests use minimal worker servers instead of this implementation, and work-manager tests call the manager directly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/rst/sync/internal/server/server.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/rst/sync/internal/workmgr/errors.go -->
# sources/distributed-fs/beegfs-go/rst/sync/internal/workmgr/errors.go

## Purpose
This file defines BeeSync work-manager sentinel errors.

## Important APIs, Types, and Functions
`ErrNotReady` indicates work operations were requested before BeeRemote-provided runtime config was applied. `ErrConfigUpdateNotAllowed` describes unsupported post-initial configuration changes, although this particular sentinel is not used in the selected manager code.

## Control Flow
There is no executable control flow beyond variable initialization.

## State and Persistence Behavior
No state is persisted. The errors give stable markers for readiness and config-update failures.

## Dependencies and Integration Points
`manager.go` wraps `ErrNotReady` in gRPC `FailedPrecondition` responses from `SubmitWorkRequest` and `UpdateWork`. Config update restrictions are mostly enforced by RST client-store and BeeRemote client behavior.

## Risks and Edge Cases
Unused sentinels can drift from actual enforcement. Callers receiving `ErrNotReady` should retry after BeeRemote sends configuration.

## Test Signals
No direct tests target this file. Readiness failures are not a major focus in the included manager tests, which call `UpdateConfig` during setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/rst/sync/internal/workmgr/errors.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/rst/sync/internal/workmgr/manager.go -->
# sources/distributed-fs/beegfs-go/rst/sync/internal/workmgr/manager.go

## Purpose
This file implements BeeSync's local work manager. It durably journals assigned work requests, indexes them by job/request ID, feeds workers through a priority scheduler, handles cancellation/update requests from BeeRemote, and coordinates shutdown.

## Important APIs, Types, and Functions
`Config` defines work journal path, job store path, active queue size, and worker count. `Manager` owns readiness, worker/manager contexts, Badger-backed `workJournal` and `jobStore`, active work map, active queue, scheduler, RST client store, and BeeRemote client. Key methods are `NewAndStart`, `IsReady`, `UpdateConfig`, `manage`, `pullInWork`, `pullInRescheduledWork`, `initScheduler`, `SubmitWorkRequest`, `UpdateWork`, and `Stop`.

## Control Flow
Startup creates Badger stores, initializes the scheduler, recovers existing journal entries by priority, starts manager and worker goroutines, and waits for dynamic config before pulling work. `manage` receives priority tokens, moves ready new and rescheduled journal entries into `activeWork` and `activeWorkQueue`, and removes active entries when workers report completion. `SubmitWorkRequest` requires readiness, creates/locks a job index entry, rejects duplicate job/request IDs, creates a prioritized journal entry, initializes a scheduled work result, stores the job-to-submission mapping, and adds a scheduler token. `UpdateWork` supports cancellation: it finds the job mapping, cancels active contexts if present, carefully locks journal entries with documented lock ordering, deletes journal/job entries, adjusts scheduler tokens, and returns the final cancellation response.

## State and Persistence Behavior
`workJournal` stores `workEntry` values keyed by fixed-width priority/submission IDs; each entry contains the request, latest result, and optional execute-after time. `jobStore` maps job IDs to request IDs and submission IDs. `activeWork` is in-memory only and maps a `workIdentifier` to a cancellable context. On restart, `initScheduler` repopulates scheduler tokens from the journal. Completed work is removed only after the worker successfully reports results to BeeRemote; failed reporting leaves entries for retry/recovery.

## Dependencies and Integration Points
The manager depends on Badger/`kvstore`, `common/scheduler`, `common/rst.ClientStore`, `sync/internal/beeremote.Client`, protobuf `flex`, gRPC status codes, and worker code in `work.go`. It is invoked by the worker-node gRPC server and by `cmd/beegfs-sync`.

## Risks and Edge Cases
The code has explicit deadlock-sensitive lock ordering between `activeWorkMu` and journal entries. Cancellation of inactive work may block the manager from pulling new work while waiting for a journal lock. Work-result delivery to BeeRemote is retried by worker logic and can keep DB entries active indefinitely if Remote is unreachable. Dynamic RST updates after initial setup are not supported by underlying clients. The constructor uses `m.scheduler.GetPriorityLevels()` before assigning `m.scheduler`, which appears risky unless the zero-value manager has been initialized elsewhere; this path deserves review.

## Test Signals
`manager_test.go` covers config updates, duplicate submission rejection, successful and failed work processing, BeeRemote response failure retention, cancellation of failed/active/inactive requests, refusal to cancel completed work, DB cleanup, and benchmarks for submission and Badger operations. Tests use mock RSTs and mock BeeRemote providers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/rst/sync/internal/workmgr/manager.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/rst/sync/internal/workmgr/manager_test.go -->
# sources/distributed-fs/beegfs-go/rst/sync/internal/workmgr/manager_test.go

## Purpose
This file tests BeeSync work-manager persistence, scheduling, cancellation, BeeRemote reporting, and performance characteristics using temporary Badger databases and mock providers.

## Important APIs, Types, and Functions
`baseTestRequest` defines a reusable upload work request. Helper matchers compare protobuf job/request IDs and statuses in Testify mocks. `getTestManager` creates temp DB paths, logger, mock BeeRemote client, mock filesystem, starts the manager, and applies runtime config. `TestUpdateConfig`, `TestSubmitWorkRequest`, and `TestUpdateRequests` are functional tests. Benchmark functions measure manager submission and raw Badger store overhead.

## Control Flow
Tests set expectations on a mock RST client and BeeRemote mock provider, submit work requests, sleep for worker processing, and assert DB entry counts and active-work sizes. Cancellation tests deliberately constrain queue size and worker count to create active and inactive scenarios, then call `UpdateWork` and inspect returned work states and remaining DB mappings.

## State and Persistence Behavior
Each test uses separate temporary work journal and job store directories. Tests verify successful BeeRemote reporting cleans both stores, failed BeeRemote reporting retains entries and active work for retry, cancelling failed work removes entries, completed work cannot be cancelled, and inactive queued work can be cancelled with scheduler token cleanup.

## Dependencies and Integration Points
The file integrates `workmgr.Manager`, `beeremote.MockProvider`, `rst.MockClient`, mock filesystem, Badger options, scheduler behavior indirectly, Testify, protobuf cloning, and zaptest logging.

## Risks and Edge Cases
Tests rely on fixed sleep intervals for asynchronous worker processing. They use mock RSTs and mock Remote, so they do not cover real network failures, gRPC status-code retry classification, real object storage behavior, or restart recovery from pre-existing journals except through initialization code paths. Benchmark code includes manual Badger tuning experiments and is not a correctness gate.

## Test Signals
The tests confirm the work manager's main invariants: duplicate work is rejected, final successful reports clean persistent state, failed reports preserve retryable state, cancellation takes ownership of responses, completed work is not downgraded to cancelled, and multiple work requests for the same job can be indexed and removed independently.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/rst/sync/internal/workmgr/manager_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/rst/sync/internal/workmgr/utils.go -->
# sources/distributed-fs/beegfs-go/rst/sync/internal/workmgr/utils.go

## Purpose
This file contains BeeSync work-manager test helpers plus production helpers for creating initial work results and splitting a work segment into upload parts.

## Important APIs, Types, and Functions
`tempPathForTesting` creates temporary Badger directories for tests. `assertDBEntriesLenForTesting` counts entries in the work journal and job store. `newWorkFromRequest` creates an initial scheduled `work` result from a `workRequest`. `generatePartsFromSegment` returns a closure that yields `(partNumber, offsetStart, offsetStop)` tuples until `-1, -1, -1`.

## Control Flow
`newWorkFromRequest` computes the number of parts, generates part descriptors from the request segment, and returns a `flex.Work` with scheduled status and initialized parts. `generatePartsFromSegment` special-cases empty files where `OffsetStop == -1`, otherwise divides the inclusive byte range across the requested part numbers and assigns any remainder to the final part.

## State and Persistence Behavior
The test helpers create and delete temporary directories and iterate persistent stores. The production helpers do not persist directly, but their generated `work` records are stored in the work journal and later updated by workers.

## Dependencies and Integration Points
The file depends on `kvstore` iteration through manager stores, `flex` protobuf builders, Testify `require` in test helpers, and the `work`/`workRequest` wrappers from `work.go`. `SubmitWorkRequest` calls `newWorkFromRequest` to initialize journal state.

## Risks and Edge Cases
`newWorkFromRequest` computes `numberOfParts` before checking whether `Segment` is nil, which could panic for nil segments despite the later nil check. Part splitting assumes valid part ranges and does not validate negative or reversed part numbers. Temporary cleanup sleeps one second to avoid DB shutdown races, slowing tests.

## Test Signals
`utils_test.go` covers initial work response generation, empty file part generation, evenly divided ranges, remainders assigned to the last part, and nonzero starting offsets/part numbers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/rst/sync/internal/workmgr/utils.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/rst/sync/internal/workmgr/utils_test.go -->
# sources/distributed-fs/beegfs-go/rst/sync/internal/workmgr/utils_test.go

## Purpose
This file tests BeeSync utility behavior for initial work-result creation and segment-to-part splitting.

## Important APIs, Types, and Functions
`TestNewWorkResponseFromRequest` verifies `newWorkFromRequest` copies job/request IDs, sets scheduled status, writes the expected message, and creates the expected number of parts. `TestGenerateParts` table-tests the part generator across empty files, even splits, uneven splits, and nonzero offsets/part numbers.

## Control Flow
The tests instantiate protobuf segments and repeatedly call the closure returned by `generatePartsFromSegment`, checking emitted tuples until the sentinel `-1, -1, -1` appears.

## State and Persistence Behavior
The tests are in-memory only. They validate data that will later be persisted into the BeeSync work journal.

## Dependencies and Integration Points
The tests depend on Testify assertions and protobuf `flex` builders. They provide coverage for the initialization path used by `Manager.SubmitWorkRequest`.

## Risks and Edge Cases
The tests do not cover nil segments, invalid part ranges, zero parts, or reversed offsets. They also do not verify checksum/entity-tag fields because those are populated later during work execution.

## Test Signals
Passing tests confirm current inclusive offset math and last-part remainder behavior, including the special empty-file marker.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/rst/sync/internal/workmgr/utils_test.go -->
