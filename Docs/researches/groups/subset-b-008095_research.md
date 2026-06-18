# subset-b-008095 research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/OzoneManager.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/OzoneManager.java

## Purpose
`OzoneManager` is the central server implementation for Apache Ozone Manager. It owns OM startup, storage validation, RPC/gRPC/HTTP endpoints, HA Ratis integration, metadata manager lifecycle, security token services, ACL and admin authorization helpers, S3 multi-tenancy routing, snapshot reads and diffs, prepare-state recovery, metrics, and many read-side methods from `OzoneManagerProtocol`, `OMInterServiceProtocol`, admin, auditor, and runtime-info interfaces.

## Important APIs, types, and functions
- `createOm`, `omInit`, `initializeSecurity`, and `StartupOption` construct, initialize, bootstrap, or securely enroll an OM.
- The constructor loads HA node details, validates `OMStorage`, checks SCM cluster identity, configures default bucket layout and replication, creates SCM clients, security clients, metrics, managers, Ratis directories, Ratis server, RPC translators, optional S3G gRPC server, and the request execution flow.
- `instantiateServices(boolean)` rebuilds all DB-dependent services: `OmMetadataManagerImpl`, volume/bucket/key/prefix managers, multi-tenancy manager, S3 secret manager, authorizer, active metadata reader, snapshot manager, snapshot metrics, and prepare state.
- `start`, `restart`, `stop`, `close`, `join`, `terminateOM`, and `shutDown` control runtime lifecycle.
- RPC setup is split across `getRpcServer`, `startRpcServer`, and `startGrpcServer`, registering client, inter-OM, admin, and reconfiguration protobuf services.
- Protocol methods include volume/bucket/key listing and lookup, file status/listing, ACL reads, delegation token operations, service discovery, open-file listing, leadership transfer, Ranger sync trigger, snapshot defrag trigger, tenant listing/user lookup, S3 volume resolution, multipart listing, DB update streaming, safe-mode proxying to SCM, quota repair, object tagging, snapshot diff APIs, and OM DB compaction.
- HA and Ratis helpers include `initializeRatisDirs`, `initializeRatisServer`, `bootstrap`, `updatePeerList`, `addOMNodeToPeers`, `removeOMNodeFromPeers`, `isLeaderReady`, `checkLeaderStatus`, `installSnapshotFromLeader`, `installCheckpoint`, and checkpoint replacement helpers.
- Authorization helpers include `checkAcls`, `getAclsEnabled`, `isAdminAuthorizationEnabled`, `checkAdminUserPrivilege`, owner lookup helpers, admin/blacklist accessors, and `resolveBucketLink` variants.

## Control flow
Construction first freezes configuration-derived identity and storage state, then validates OM initialization and SCM cluster matching before creating network endpoints. Security setup happens before service discovery and token managers; DB-dependent managers are created by `instantiateServices(false)` before the S3 gateway volume is ensured in the DB. Ratis directories and server are prepared before RPC translators are built, because the translators submit write requests through Ratis.

`start()` initializes metrics, starts metadata storage, conditionally starts secret managers, starts Ratis, seeds metrics from DB and the saved metrics file, starts topology, key manager, HTTP server, RPC server, trash emptier, optional gRPC server, and JMX, then bootstraps if requested and moves `omState` to `RUNNING`. `restart()` repeats most initialization after reloading selected config and services. `stop()` reverses the order: mark stopped, close reconfiguration and timers, stop RPC/gRPC/Ratis/key/security/topology/HTTP/multi-tenant/trash/metadata/snapshot/metrics/service resources, close SCM and certificates, unregister metrics, and shut down the EDEK cache loader.

Read operations generally wrap manager calls with ACL checks, metrics increments, and audit success/failure logging. Key and filesystem reads call `getReader(...)`, which may return the active metadata reader or a snapshot metadata reader from `OmSnapshotManager`. Bucket-link resolution recursively follows link buckets with loop detection and optional ACL checks before dispatching to the real bucket.

Snapshot installation is a coordinated state transition: download a DB checkpoint from the leader, stop background services, invalidate snapshot cache, pause the Ratis state machine, compare checkpoint transaction info to the local last-applied index, stop RPC and metadata if the checkpoint is newer, selectively back up and replace DB directory entries using a transient marker, instantiate services against the new DB, unpause the state machine at the checkpoint term/index, restart RPC, audit the install, and delete the backup.

Prepare-state recovery occurs after metadata manager creation. On normal startup, OM compares a Ratis-replicated DB prepare marker with the local marker file, preferring the DB marker if both exist but differ, removing the DB marker when the local upgrade/downgrade startup flow removed the file, and failing startup if the file exists without a DB marker. After snapshot install, it restores or cancels prepare state from the snapshot DB marker.

## State and persistence behavior
Persistent state spans the OM VERSION file (`OMStorage`), RocksDB metadata tables, Ratis log/snapshot directories, prepare marker file under the OM current metadata directory, saved metrics JSON in the OM DB metadata directory, certificate serial IDs in storage, and transient DB backup/marker directories during checkpoint replacement. `addS3GVolumeToDB()` writes the default S3 volume and user entry directly to the DB and cache using a reserved transaction/object ID. `updateLayoutVersionInDB()` persists finalized metadata layout version in the meta table. `saveNewCertId()` persists certificate ID back to the VERSION file and shuts down on persistence failure.

In-memory state includes managers, authorizer, service provider, token managers, Ratis server, peer map, current transaction info, metrics, thread-local S3 authentication, booleans for RPC/gRPC running, feature flags, bucket layout and replication defaults, and `omState`. Several test flags alter reload, security, UGI, and snapshot-install behavior.

## Dependencies and integration points
This class is a hub for HDDS/Ozone subsystems: SCM clients and topology, Ratis, protobuf RPC translators, gRPC S3 gateway server, HTTP servlets, RocksDB metadata manager, KMS and EDEK warmup, delegation/block token security, certificate enrollment, S3 secret storage, Ozone native or Ranger authorizer, snapshot manager and defrag services, directory/key deleting services, multi-tenancy/Ranger sync, upgrade finalizer, reconfiguration, metrics/JMX, Hadoop `Trash`, and audit logging. External clients reach it through protobuf RPC, gRPC for S3 gateway OM requests, HTTP endpoints, and admin/reconfigure protocols.

## Risks and edge cases
- The class has a very large responsibility surface; changes to lifecycle order can break Ratis, metadata, security, or RPC availability.
- `StartupOption.REGUALR` is misspelled but part of the local API.
- Checkpoint installation is high risk: failed DB movement can force process exit if rollback cannot restore the previous state, and it intentionally stops RPC/metadata while moving files.
- Prepare-state divergence is guarded by DB/file marker reconciliation, but marker-file-only state is treated as corruption.
- `isLeaderReady()` returns true only when `omRatisServer` is non-null and ready, despite the comment saying non-Ratis always returns true.
- Some protocol methods are placeholders (`echoRPCReq`, `recoverLease`, `setTimes`) and return null or no-op.
- Bucket-link resolution must avoid loops and must use source-bucket ACL semantics before snapshot/key operations.
- S3 multi-tenancy routing depends on thread-local `S3_AUTH`; old gateways without S3 auth fall back to the default S3 volume.
- HTTP server startup failure is logged but non-fatal, so monitoring must detect missing web endpoints separately.
- Several operations rely on `getRemoteUser()` and `Server.getRemoteIp()` context; gRPC bridges must synthesize enough Hadoop RPC call context.

## Test signals
Useful tests include OM init with initialized/uninitialized storage, SCM cluster ID mismatch, secure startup without cert serial, default bucket layout validation before/after layout finalization, start/stop/restart resource ordering, RPC/gRPC endpoint enablement, HTTP failure tolerance, S3 volume auto-creation and cache updates, delegation token auth-method checks, admin authorization on leadership/repair/compaction APIs, bucket-link loop/dangling/ACL cases, prepare DB/file marker reconciliation across restart and snapshot install, checkpoint install success/rollback/failure paths, service list role/port construction, snapshot-reader routing for key/status/list/ACL/diff operations, and gRPC bridge behavior that depends on Hadoop `Server.Call` context.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/OzoneManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/OzoneManagerHttpServer.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/OzoneManagerHttpServer.java

## Purpose
`OzoneManagerHttpServer` is a thin `BaseHttpServer` specialization for Ozone Manager. It wires OM-specific HTTP/HTTPS configuration keys, security settings, and servlet endpoints into the shared HDDS HTTP server infrastructure.

## Important APIs, types, and functions
- The constructor calls `super(conf, "ozoneManager")`, registers `ServiceListJSONServlet`, `SnapshotListJSONServlet`, `OMDBCheckpointServlet`, and `OMDBCheckpointServletInodeBasedXfer`, then stores the live `OzoneManager` in the web app context under `OzoneConsts.OM_CONTEXT_ATTRIBUTE`.
- Overrides map base-server hooks to `OMConfigKeys`: HTTP/HTTPS address keys, bind host keys, default ports, Kerberos keytab and SPNEGO principal keys, enabled key, auth type, and auth config prefix.

## Control flow
Construction is the full setup path. Consumers, mainly `OzoneManager.start()` and `restart()`, instantiate it and call `start()` from `BaseHttpServer`. Servlet code later retrieves the OM object from web context attributes to serve service discovery, snapshot lists, and DB checkpoint download endpoints.

## State and persistence behavior
The class itself persists no data. Its endpoints can expose live service state and DB checkpoint data through servlets. Configuration controls whether HTTP is enabled, addresses, bind hosts, HTTPS, SPNEGO/Kerberos, and HTTP auth behavior.

## Dependencies and integration points
It depends on HDDS `BaseHttpServer`, mutable configuration, OM servlet classes, `OzoneConsts` endpoint constants, and `OMConfigKeys`. It is integrated into OM lifecycle as a non-fatal service: OM logs HTTP startup failure and continues.

## Risks and edge cases
Incorrect servlet-to-context wiring would break checkpoint download or service-list APIs. Auth key mismatches could expose endpoints or block administrators unexpectedly. Because HTTP startup failure is non-fatal, callers should not infer OM unavailability from missing web UI alone.

## Test signals
Tests should verify servlet registration paths, context contains the exact OM instance, address/default/auth config keys match OM config constants, HTTPS/SPNEGO settings are honored through `BaseHttpServer`, and OM startup proceeds if this server fails to start.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/OzoneManagerHttpServer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/OzoneManagerPrepareState.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/OzoneManagerPrepareState.java

## Purpose
`OzoneManagerPrepareState` owns the in-memory and marker-file portion of OM prepare mode. Prepare mode blocks ordinary write requests while allowing only `Prepare` and `CancelPrepare`, and records a marker file so an OM remains prepared after restart.

## Important APIs, types, and functions
- `NO_PREPARE_INDEX` is the sentinel for no prepared index.
- Constructors either initialize `NOT_PREPARED` state or restore from an existing marker file against the current transaction index.
- `enablePrepareGate()` moves to `PREPARE_GATE_ENABLED` and clears the index.
- `cancelPrepare()` clears the gate/index/status and deletes the marker file.
- `finishPrepare(long)` enables the gate, writes the marker file, and marks `PREPARE_COMPLETED`.
- `restorePrepareFromIndex(...)` and `restorePrepareFromFile(...)` validate restored prepare index against current index and rebuild prepared state.
- `requestAllowed(Type)` enforces the write gate.
- `getState()` returns a snapshot object containing index and protobuf `PrepareStatus`.
- `getPrepareMarkerFile()` maps configuration to `<ozone metadata dir>/current/<PREPARE_MARKER>`.

## Control flow
The normal prepare flow first calls `enablePrepareGate()` to reject future writes, then `finishPrepare(index)` to write the marker and set completed status once the prepare point is known. Startup/snapshot recovery flows read either a DB marker from `OzoneManager` or the local marker file, then call `restorePrepareFromIndex` or `restorePrepareFromFile`. All public mutating/read methods are synchronized to keep gate, index, and status consistent.

## State and persistence behavior
State is three synchronized fields: `prepareGateEnabled`, `prepareIndex`, and `status`. Persistence is a UTF-8 marker file containing the prepare log index. Marker file read, parse, write, and delete errors become `OMException` with `PREPARE_FAILED`. The class does not write the DB prepare marker; `OzoneManager` reconciles that Ratis-replicated state with this local file.

## Dependencies and integration points
It integrates with `OzoneManagerStateMachine.preAppendTransaction` and `OzoneManagerRatisServer.submitRequest`, which use `requestAllowed` to block writes. `OzoneManager.instantiatePrepareStateOnStartup()` and `instantiatePrepareStateAfterSnapshot()` coordinate this class with transaction info and DB markers. It uses `ServerUtils.getOzoneMetaDirPath`, `OMStorage.STORAGE_DIR_CURRENT`, and `OzoneConsts.PREPARE_MARKER` for file location.

## Risks and edge cases
The class reads the marker file with one `stream.read(data)` call, which assumes the requested byte count is returned. A malformed marker, unreadable marker, missing marker during explicit restore, or marker index greater than current index all fail prepare recovery. `restorePrepareFromIndex` writes the restored index to disk but stores `currentIndex` in memory, so callers must understand the difference between requested prepare point and current applied index.

## Test signals
Tests should cover fresh state, gate request filtering, prepare/cancel idempotence, marker file creation/deletion path, malformed marker content, missing marker restore, marker index greater than current index, restoration with and without writing the marker, and concurrent reads of `getState()` while state transitions occur.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/OzoneManagerPrepareState.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/OzoneManagerServiceGrpc.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/OzoneManagerServiceGrpc.java

## Purpose
`OzoneManagerServiceGrpc` exposes Ozone Manager protobuf requests over gRPC for S3 gateway clients. It adapts gRPC calls into the existing OM protobuf translator path that normally expects Hadoop IPC context.

## Important APIs, types, and functions
- Extends generated `OzoneManagerServiceGrpc.OzoneManagerServiceImplBase`.
- Stores an `OzoneManagerProtocolServerSideTranslatorPB`.
- `submitRequest(OMRequest, StreamObserver<OMResponse>)` logs the command type, creates a synthetic Hadoop `Server.Call`, delegates to `omTranslator.submitRequest(NULL_RPC_CONTROLLER, request)`, writes the response, and completes the observer.
- `getClientId()` returns random UUID bytes for the synthetic call context.

## Control flow
Every gRPC request installs a new `Server.Call` in `Server.getCurCall()` before delegation. This supplies retry/client-id metadata needed by OM Ratis request creation. On successful translator return, it calls `onNext` then `onCompleted`. On any thrown `Throwable`, it logs, wraps the cause in `IOException`, and sends `Status.INTERNAL` through `onError`.

## State and persistence behavior
The service has no persisted state. Per-call state is the temporary Hadoop IPC thread-local call and a local `AtomicInteger` used to assign the synthetic call id. Mutations and persistence occur downstream through the translator and OM/Ratis path.

## Dependencies and integration points
It bridges gRPC, generated OM protobuf types, Hadoop IPC classes under `org.apache.hadoop.ipc_`, the server-side translator, and Ratis request construction. `OzoneManager.startGrpcServer()` creates this service inside `GrpcOzoneManagerServer` when the S3G gRPC server is enabled.

## Risks and edge cases
Catching `Throwable` is broad and may hide serious errors. `new IOException(e.getCause())` can lose the top-level exception message and may produce a weak error description when the cause is null. The synthetic `Server.Call` dependency is explicitly marked TODO; changes in Hadoop IPC or Ratis request code can break gRPC handling if the context shape changes. The call count is local to a single request, so every request starts at call id 1.

## Test signals
Tests should verify successful delegation calls `onNext` and `onCompleted`, translator exceptions become gRPC INTERNAL errors, a Hadoop `Server.Call` with non-empty client id is present during translator execution, command type logging does not mutate requests, and Ratis-enabled OM writes succeed through the gRPC path.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/OzoneManagerServiceGrpc.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/OzoneManagerStarter.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/OzoneManagerStarter.java

## Purpose
`OzoneManagerStarter` is the Picocli/GenericCli entry point for starting, initializing, upgrade/downgrade prepare cancellation, and bootstrapping an Ozone Manager process.

## Important APIs, types, and functions
- `main` disables JVM network address caching if configured, then runs the command with `OMStarterHelper`.
- `call()` handles plain `ozone om` by running common initialization and starting OM.
- `--init` calls `receiver.init(conf)` and fails if OM init returns false.
- `--upgrade`/`--downgrade` calls `receiver.startAndCancelPrepare(conf)` to remove local prepare state before starting.
- `--bootstrap [--force]` initializes storage, chooses `BOOTSTRAP` or `FORCE_BOOTSTRAP`, and starts OM in bootstrap mode.
- `commonInit()` loads `OzoneConfiguration` and prints the startup/shutdown banner.
- `OMStarterHelper` creates real `OzoneManager` instances and delegates lifecycle operations; it also registers a shutdown hook for normal start.

## Control flow
The CLI path always calls `commonInit()` before invoking a receiver operation. Normal start creates OM, calls `start()`, and leaves it running with a shutdown hook that stops and joins it. Bootstrap initializes storage first, then creates an OM with the selected startup option in try-with-resources, starts it, and joins. Upgrade/downgrade creates OM, cancels prepare state before serving, starts, and joins.

## State and persistence behavior
The starter itself only stores `conf` and an injected receiver. It triggers persistent effects through `OzoneManager.omInit`, security initialization, prepare marker deletion via `cancelPrepare`, bootstrap Ratis configuration changes, and normal OM lifecycle. The shutdown hook stops runtime services but does not create commits or external state beyond normal OM persistence.

## Dependencies and integration points
It integrates Picocli, `GenericCli`, HDDS version provider, `HddsServerUtil.startupShutdownMessage`, `OzoneNetUtils`, `ShutdownHookManager`, and `OzoneManager`. The `OMStarterInterface` injection boundary is the primary test seam.

## Risks and edge cases
Bootstrap force mode intentionally skips remote config validation and can crash existing OMs if configs are stale. `startAndCancelPrepare` cancels local marker state before start; operators must use it consistently across OMs during upgrade/downgrade to avoid divergence as described in `OzoneManager`. Normal `start` does not call `join()` directly and relies on non-daemon server threads plus shutdown hook behavior.

## Test signals
Tests should verify subcommand dispatch, receiver injection, startup banner arguments, init failure handling, force/non-force bootstrap option selection, shutdown hook stop/join behavior, and upgrade/downgrade cancellation ordering before OM start.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/OzoneManagerStarter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/OzoneManagerUtils.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/OzoneManagerUtils.java

## Purpose
`OzoneManagerUtils` provides small static helpers for OM request handling, especially bucket lookup/layout resolution through bucket links and delegation-token audit map construction.

## Important APIs, types, and functions
- `getBucketInfo(OMMetadataManager, volName, buckName)` reads the bucket table and reports precise volume-not-found or bucket-not-found exceptions.
- `getBucketLayout(...)` returns the resolved bucket layout after following link buckets.
- `getResolvedBucketInfo(...)` follows bucket links and returns the final source bucket information.
- `resolveBucketInfoLink(...)` is the recursive implementation with visited-set loop detection.
- `buildTokenAuditMap(Token<OzoneTokenIdentifier>)` extracts token kind and service into a linked audit map.

## Control flow
Bucket resolution reads the requested bucket. If it is not a link, it returns immediately. If it is a link, it adds the current volume/bucket pair to a visited set, fails on repeats, and recurses to the source volume/bucket until a non-link bucket is found. Missing bucket resolution first checks whether the volume exists so the caller receives a more specific result code.

## State and persistence behavior
The utility is stateless and performs no writes. It reads OM metadata tables through `OMMetadataManager`; audit-map construction reads token metadata only.

## Dependencies and integration points
The class is used in the OM write request path, as noted by the in-file call trace from `OzoneManagerStateMachine#applyTransaction` through request factories to bucket layout resolution. It depends on `OMMetadataManager`, `OmBucketInfo`, `BucketLayout`, Apache Commons `Pair`, `OMException`, and token/audit constants.

## Risks and edge cases
Deep link chains recurse and could be expensive or stack-heavy if misconfigured. Link cycles are detected only by exact volume/bucket pairs. Dangling links surface as bucket or volume not found. The utility does not perform ACL checks; callers that expose client-visible operations must enforce authorization separately.

## Test signals
Tests should cover direct bucket layout, chained links, link loop detection, dangling source bucket, missing source volume, missing requested bucket with existing volume, missing volume, and null token kind/service values in audit-map construction.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/OzoneManagerUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/OzonePrefixPathImpl.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/OzonePrefixPathImpl.java

## Purpose
`OzonePrefixPathImpl` implements the ACL-facing `OzonePrefixPath` abstraction for a volume/bucket/key prefix. It resolves the prefix status and can lazily iterate child paths in batches through `KeyManager`.

## Important APIs, types, and functions
- The constructor builds a head `OmKeyArgs`, retrieves the file status, translates `FILE_NOT_FOUND` to `KEY_NOT_FOUND` for legacy caller compatibility, and sets `checkRecursiveAccess` when a directory has children.
- `getOzoneFileStatus()` returns the resolved prefix status.
- `getChildren(String)` returns a `PathIterator`.
- `PathIterator` batches `keyManager.listStatus(...)`, rejects a file prefix where a directory is expected, removes duplicate continuation entries, and advances using the previous returned trimmed name.
- `isCheckRecursiveAccess()` indicates whether recursive ACL checks are needed for non-empty directories.

## Control flow
Construction validates the prefix and determines whether recursive access checks are meaningful. Child iteration starts with `prevKey=""`, then `hasNext()` fetches the next batch only after the current iterator is exhausted and a current value exists. `next()` delegates to `hasNext()` and throws `NoSuchElementException` at end.

## State and persistence behavior
The object stores volume, bucket, `KeyManager`, batch size, initial path status, and recursive-check flag. It does not persist or mutate metadata; it reads file status, child status lists, and child-existence information from `KeyManager` and `OMFileRequest`.

## Dependencies and integration points
It integrates native ACL checks with OM key/file metadata by implementing `OzonePrefixPath`. It depends on `KeyManager`, `OmKeyArgs`, `OzoneFileStatus`, `OMFileRequest.hasChildren`, `OMException`, and Commons `StringUtils`.

## Risks and edge cases
`hasNext()` suppresses `IOException` by logging at debug and returning false, which can make permission or metadata errors look like end-of-iteration. The fixed batch size of 1000 is not configurable. Duplicate continuation removal mutates the returned list. File prefixes are rejected only when the first batch contains exactly the file status matching the requested prefix.

## Test signals
Tests should cover constructor translation from `FILE_NOT_FOUND` to `KEY_NOT_FOUND`, directory child detection, empty directory recursive flag, file prefix rejection in `PathIterator`, paginated listing with duplicate start-key removal, iteration across multiple batches, and iterator behavior when `listStatus` throws.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/OzonePrefixPathImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/OzoneTrash.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/OzoneTrash.java

## Purpose
`OzoneTrash` is an Ozone-specific wrapper around Hadoop `Trash` that installs `TrashPolicyOzone` so OM can run a trash emptier with Ozone-aware behavior.

## Important APIs, types, and functions
- The constructor calls the Hadoop `Trash` constructor and creates `new TrashPolicyOzone(fs, conf, om)`.
- `getEmptier()` delegates to the Ozone trash policy's emptier.

## Control flow
`OzoneManager.startTrashEmptier()` creates a `TrashOzoneFileSystem`, constructs `OzoneTrash`, obtains the emptier runnable, and runs it in a daemon thread. This class only chooses the policy and returns its runnable.

## State and persistence behavior
The only field is `trashPolicy`. Trash checkpointing and deletion state are handled by `TrashPolicyOzone` and the supplied `FileSystem`; this wrapper does not persist anything directly.

## Dependencies and integration points
It depends on Hadoop `Trash`, `TrashPolicy`, `FileSystem`, `Configuration`, and Ozone `TrashPolicyOzone`. It is integrated into OM lifecycle through `startTrashEmptier()` and `stopTrashEmptier()`.

## Risks and edge cases
If `TrashPolicyOzone` construction fails, OM trash emptier startup fails and can abort OM start for invalid trash interval or filesystem setup errors. Since `getEmptier()` bypasses the superclass policy, any Hadoop `Trash` behavior changes are only inherited for construction-level setup, not emptier selection.

## Test signals
Tests should verify the wrapper returns the `TrashPolicyOzone` emptier, propagates construction and `getEmptier()` IOExceptions, and integrates with OM trash interval handling for disabled, negative, and positive intervals.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/OzoneTrash.java -->
