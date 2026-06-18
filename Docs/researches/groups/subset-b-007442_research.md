# subset-b-007442 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/test/java/org/apache/hadoop/hdfs/nfs/nfs3/TestRpcProgramNfs3.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/test/java/org/apache/hadoop/hdfs/nfs/nfs3/TestRpcProgramNfs3.java

## Purpose
JUnit 5 integration coverage for `RpcProgramNfs3`, exercising the Hadoop NFSv3 server implementation against a live `MiniDFSCluster`. It validates the basic NFS procedure surface, host/export authorization through mocked `SecurityHandler` identities, encrypted-zone read/write behavior, idempotency metadata, and deprecated configuration-key compatibility.

## Important APIs, Types, and Functions
The fixture owns static cluster state: `MiniDFSCluster`, `DistributedFileSystem`, `NameNode`, `Nfs3`, `RpcProgramNfs3`, `HdfsAdmin`, and privileged/unprivileged `SecurityHandler` mocks. `setup()` configures proxy-user impersonation, a Java key provider, ephemeral NFS ports, and `dfs.nfs.exports.allowed.hosts=* rw`; `createFiles()` resets `/tmp`, `/tmp/foo`, and `/tmp/bar` before each test. Each test serializes NFS request objects through `XDR` and calls the corresponding `nfsd` method directly: `getattr`, `setattr`, `lookup`, `access`, `readlink`, `read`, `write`, `create`, `mkdir`, `symlink`, `remove`, `rmdir`, `rename`, `readdir`, `readdirplus`, `fsstat`, `fsinfo`, `pathconf`, and `commit`.

## Control Flow
Most tests follow the same path: resolve a DFS file ID via `NameNode.getRpcServer().getFileInfo`, build a `FileHandle(fileId, namenodeId)`, serialize the request, call the NFS procedure once as user `harry` and once as the current system user, then assert `NFS3ERR_ACCES` for the first path and success or async-null for the second. `testEncryptedReadWrite()` creates an HDFS encryption zone, writes bytes through NFS using `WRITE3Request`, commits through `COMMIT3Request`, then compares NFS and DFS reads; it also verifies that a DFS-created encrypted file can be read through NFS. Helper methods `createFileUsingNfs`, `getFileContentsUsingNfs`, `getFileContentsUsingDfs`, and `commit` encapsulate that flow.

## State and Persistence Behavior
The tests mutate an in-process HDFS namespace, create a temporary Java keystore under the test root, and start NFS services on ephemeral ports. NFS write and commit paths may return `null` because the write manager replies asynchronously through Netty `Channel` callbacks. File handles encode HDFS inode/file IDs and namenode IDs, so the test explicitly couples NFS object identity to NameNode metadata.

## Dependencies and Integration Points
The class integrates HDFS mini-cluster services, key-provider/encryption-zone support, NFS request/response model classes, ONC RPC XDR serialization, Hadoop proxy-user authorization, and Mockito security identities. It also checks `NfsConfiguration` deprecation mappings from legacy keys such as `nfs3.server.port`, `dfs.nfs3.dump.dir`, and `hadoop.nfs.userupdate.milly` to the current constants.

## Risks and Edge Cases
The fixture is broad and comparatively expensive because it starts a cluster and NFS service. It depends on local user identity, proxy-user refresh, and ephemeral port availability. Several assertions use `assertEquals(null, response)` for async success, so regressions in synchronous response behavior could break tests without necessarily indicating data failure. The encrypted-write helper pre-creates a zero-length file before writing through NFS, so it does not cover NFS-only file creation inside an encryption zone.

## Test Signals
Strong signals include positive/negative authorization checks across nearly every NFSv3 procedure, encrypted data integrity across DFS and NFS, read EOF validation, idempotency expectations for `NFSPROC3`, and deprecated-key compatibility. The class does not explicitly test network transport framing; it calls `RpcProgramNfs3` methods directly with serialized request buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/test/java/org/apache/hadoop/hdfs/nfs/nfs3/TestRpcProgramNfs3.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/test/java/org/apache/hadoop/hdfs/nfs/nfs3/TestViewfsWithNfs3.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/test/java/org/apache/hadoop/hdfs/nfs/nfs3/TestViewfsWithNfs3.java

## Purpose
Integration tests for running Hadoop NFSv3 over `ViewFileSystem` with a federated `MiniDFSCluster`. The class validates that NFS exports, file handles, getattr/write routing, and rename semantics work when the visible namespace is composed from two underlying HDFS nameservices.

## Important APIs, Types, and Functions
`setup()` creates a two-nameservice `MiniDFSCluster` with `MiniDFSNNTopology.simpleFederatedTopology(2)`, obtains `hdfs1`, `hdfs2`, `nn1`, and `nn2`, configures `fs.defaultFS` to `viewfs:///`, and uses `ConfigUtil.addLink` to map `/hdfs1` to `/user1` and `/hdfs2` to `/user2`. It exports both viewfs paths via `NfsConfigKeys.DFS_NFS_EXPORT_POINT_KEY`, starts `Nfs3`, and captures `RpcProgramNfs3` plus `RpcProgramMountd`.

## Control Flow
The basic tests compare mountd export count with `viewFs.getChildFileSystems()`, verify viewfs path resolution against the backing HDFS paths, and compare `FileStatus` directory bits against each NameNode's `HdfsFileStatus`. The NFS access helpers build file handles using `Nfs3Utils.getNamenodeId(config, hdfsX.getUri())` and call `nfsd.getattr` or `nfsd.write`. Rename tests build source/destination directory handles for one or two namespaces and assert that cross-NameNode rename fails with `NFS3ERR_INVAL`, while same-NameNode rename succeeds and updates only the expected namespace.

## State and Persistence Behavior
The fixture persists temporary HDFS namespace entries in both federated namespaces for the duration of the class: base directories, files for access/write tests, and rename candidates. `viewFs` presents a synthetic namespace but the durable objects reside in `hdfs1` and `hdfs2`; NFS file handles carry the backing NameNode ID so routing depends on the handle, not just the path text.

## Dependencies and Integration Points
This class links HDFS federation, viewfs mount-table configuration, NFS export-point configuration, mountd export enumeration, XDR-serialized NFS requests, and router-like multi-NameNode file-handle lookup. It uses a mocked `SecurityHandler` for the current user and Hadoop proxy-user config to make direct NFS calls pass authorization.

## Risks and Edge Cases
The main risk covered is accidental cross-namespace mutation through NFS rename; the expected behavior is explicit invalidation rather than cross-NameNode move. The tests depend on stable namenode-ID generation from configured URIs; mismatched URI normalization can cause `NFS3ERR_IO` as demonstrated by `testWrongNfsAccess()`. The class does not test mountd network clients or dynamic viewfs link changes after service start.

## Test Signals
Signals include export count parity, viewfs-to-HDFS path resolution, metadata parity between viewfs and NameNode RPC, successful NFS getattr/write to both nameservices, rejected wrong-namenode handles, rejected cross-NN rename, and successful single-NN rename with before/after NameNode metadata checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/test/java/org/apache/hadoop/hdfs/nfs/nfs3/TestViewfsWithNfs3.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/test/java/org/apache/hadoop/hdfs/nfs/nfs3/TestWrites.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/test/java/org/apache/hadoop/hdfs/nfs/nfs3/TestWrites.java

## Purpose
Focused tests for the NFS write path, especially `OpenFileCtx`, `WriteCtx`, `WriteManager`, commit state transitions, stable-write semantics, and out-of-order/overlapping write assembly. Unlike `TestRpcProgramNfs3`, much of this class tests the write state machine directly with mocks.

## Important APIs, Types, and Functions
Key production types under test are `OpenFileCtx`, `WriteCtx`, `OffsetRange`, `OpenFileCtx.CommitCtx`, `OpenFileCtx.COMMIT_STATUS`, and `WriteManager`. `testAlterWriteRequest()` validates `OpenFileCtx.alterWriteRequest()` by checking `ByteBuffer` position/limit after trimming already-flushed bytes. `testCheckCommit*` methods exercise `checkCommit`, `checkCommitInternal`, and `commitBeforeRead` under normal, large-file-upload, AIX compatibility, and read-before-commit modes. `waitWrite()` polls the NFS write manager cache until pending writes drain.

## Control Flow
The direct commit tests construct mocked `DFSClient` and `HdfsDataOutputStream`, set `fos.getPos()` and `ctx.nextOffset`, seed `pendingWrites` and `pendingCommits`, then assert each expected `COMMIT_STATUS`: inactive, inactive-with-pending-write, do-sync, finished, wait, special-wait, and special-success. The integration tests start a mini cluster and NFS service, create files via NFS `CREATE3Request`, issue `WRITE3Request`s with `DATA_SYNC`, `FILE_SYNC`, `UNSTABLE`, out-of-order offsets, or overlapping byte ranges, wait for pending writes to drain, then read back through NFS.

## State and Persistence Behavior
`OpenFileCtx` state includes active/inactive flags, pending write ranges, pending commit offsets, stream position, next expected write offset, large-file-upload mode, and AIX compatibility behavior. In the integration tests, the state persists through the write manager's open-file cache keyed by `FileHandle`, while HDFS persists completed byte content and file length.

## Dependencies and Integration Points
The tests integrate HDFS `DFSClient`, `HdfsDataOutputStream`, mini clusters, the Hadoop NFS RPC program, ONC RPC XDR request serialization, Netty `Channel` mocks for deferred commit replies, shell-based ID mapping, proxy-user authorization, and NFS status codes. Mockito is used heavily to force stream positions that would be hard to stage through real I/O.

## Risks and Edge Cases
Important edge cases include trimming a write request at offset 1, 12, and 19; commit offsets beyond flushed position; zero-offset commit behavior with pending ranges; inactive contexts with and without queued writes; large-file upload behavior where `nextOffset` and flushed position diverge; read-triggered commits that must not enqueue asynchronous waits; and overlapping writes that need deterministic final bytes. The tests use sleeps in `waitWrite()`, so slow systems can expose timing sensitivity.

## Test Signals
Strong signals include exhaustive commit-status assertions, explicit pending-commit map size/key checks, status-code assertions from `WriteManager.commitBeforeRead`, readback equality after stable writes, file-length sync after `FILE_SYNC`, out-of-order middle-block verification, complete overlapping-range reconstruction, and `checkSequential()` boundary checks across adjacent/non-adjacent pending ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/test/java/org/apache/hadoop/hdfs/nfs/nfs3/TestWrites.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/test/resources/core-site.xml -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/test/resources/core-site.xml

## Purpose
Test-resource `core-site.xml` that overrides Hadoop NFS test ports so the Hadoop NFS server and mount daemon do not collide with common system NFS services.

## Important Properties
`nfs.server.port` is set to `2079`, intentionally different from the default NFS port `2049`. `nfs.mountd.port` is set to `4272`, different from the default Hadoop mountd port `4242`. The file contains only these two properties under a Hadoop `<configuration>` root.

## Control Flow and Integration
The file is loaded as a standard Hadoop test resource by configurations used in the hadoop-hdfs-nfs test module. Runtime tests may still override ports to `0` for ephemeral allocation, but this file provides safe defaults when a test or local run relies on classpath configuration.

## State and Persistence Behavior
There is no application state or persistence beyond configuration values. The effect is process-local service binding behavior for NFS and mountd in tests.

## Dependencies and Risks
The file depends on Hadoop configuration's deprecated/current key resolution; these property names match legacy keys also covered by `TestRpcProgramNfs3.testDeprecatedKeys()`. A risk is that fixed ports can still conflict if multiple test JVMs use this resource without overriding to ephemeral ports.

## Test Signals
The signal is indirect: NFS test startup succeeds on non-privileged, non-default ports. Direct compatibility for these legacy keys is asserted in Java tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/test/resources/core-site.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/dev-support/findbugsExcludeFile.xml -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/dev-support/findbugsExcludeFile.xml

## Purpose
FindBugs/SpotBugs exclusion filter for the HDFS Router-Based Federation module. It suppresses generated federation protocol classes and two intentional representation-exposure findings used by router-admin bulk add support.

## Important Rules
The first `<Match>` excludes the generated package `org.apache.hadoop.hdfs.federation.protocol.proto`, where static analysis findings are expected to be noisy and not hand-maintained. Two additional matches target `org.apache.hadoop.hdfs.tools.federation.AddMountAttributes`: method `getNss` suppresses `EI_EXPOSE_REP`, and method `setNss` suppresses `EI_EXPOSE_REP2`.

## Control Flow and Integration
This XML is consumed by the module's static-analysis build configuration. It does not execute code; it filters analyzer output so generated protobuf artifacts and intentional mutable-list accessors do not fail checks.

## State and Persistence Behavior
No runtime state. The persistent behavior is build policy: future FindBugs/SpotBugs scans will ignore these classes/methods until the file changes.

## Dependencies and Risks
The suppressions depend on fully qualified class/package names and bug-pattern identifiers. The main risk is over-broad package suppression hiding real issues if hand-written code is added under the generated proto package. The `AddMountAttributes` exclusions deliberately accept mutable representation exposure, so callers must treat that object as a controlled bulk-request builder.

## Test Signals
The relevant signal is build/static-analysis cleanliness rather than unit behavior. RAT excludes this file in the RBF POM, which confirms it is treated as dev-support metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/dev-support/findbugsExcludeFile.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/pom.xml -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/pom.xml

## Purpose
Maven module descriptor for `hadoop-hdfs-rbf`, the HDFS Router-Based Federation jar. It declares module dependencies, test dependencies, protobuf generation, webapp/resource preparation, static-source replacement, RAT exclusions, cleanup behavior, and a parallel-test profile.

## Important Build APIs and Configuration
The module inherits from `hadoop-project-dist`, sets `hadoop.component=hdfs`, and increases `surefire.fork.timeout` to 3600. Production/provided dependencies include `hadoop-common`, `hadoop-hdfs`, `hadoop-hdfs-client`, `hadoop-federation-balance`, `slf4j-reload4j`, Jetty AJAX utilities, Jettison, Jackson, and HikariCP. Test dependencies include mini-KDC, HDFS/common/federation-balance test jars, DistCp, ZooKeeper test jar, MapReduce components, Curator test, Derby, Mockito inline, AssertJ, and JUnit Jupiter.

## Control Flow
During `compile`, an antrun execution copies `proto-web.xml` to the generated router webapp `WEB-INF/web.xml`, copies other webapp files, and replaces `{release-year-token}` in HTML. During `process-test-resources`, another antrun execution copies generated webapps into test classes. During `pre-site`, it copies `hdfs-rbf-default.xml` and `configuration.xsl` into site resources. The protobuf plugin compiles module protos with additional proto paths to Hadoop common and HDFS client protos. The replacer plugin is enabled for generated, main, and test sources.

## State and Persistence Behavior
The POM drives generated artifacts under `target`, temporary site resources under `src/site/resources`, and test-specific directories. The clean plugin removes the copied `src/site/resources/hdfs-rbf-default.xml` without following symlinks. The parallel-tests profile isolates forked test directories through `${surefire.forkNumber}` and preserves a shared-data directory for rare cross-fork coordination.

## Dependencies and Integration Points
This file ties RBF to core HDFS, client protocol protobufs, federation balancing, router web UI assets, protobuf code generation, Hadoop's test infrastructure, and Maven quality plugins. Javadoc excludes generated federation and HDFS proto packages. RAT excludes dev-support and generated/static web artifacts.

## Risks and Edge Cases
Build changes here have broad blast radius because generated protobuf sources, router web UI packaging, and test classpath are all controlled here. Provided-scope Hadoop dependencies assume distribution packaging supplies them at runtime. The parallel-tests profile deliberately disables fork reuse and rewrites temp dirs; tests with hidden global state can still need `test.build.shared.data`.

## Test Signals
Signals include Maven compile success with generated protos, surefire execution with Derby log isolation, webapp resources present for tests, RAT passing with explicit excludes, and parallel profile creating fork-scoped dirs. Dependency declarations indicate the module supports Kerberos, ZooKeeper, DB-backed state stores, MapReduce integration, and mocked/unit-level test paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/pom.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/conf/hdfs-rbf-site.xml -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/conf/hdfs-rbf-site.xml

## Purpose
Template site-override configuration for HDFS Router-Based Federation. It is intentionally empty and provides the standard place for deployments to add router-specific overrides.

## Important Structure
The file has the standard Hadoop XML prolog, stylesheet/license comments, and an empty `<configuration>` element. It does not declare any properties.

## Control Flow and Integration
Hadoop deployments and tests can place this file on the classpath so `Configuration` can merge site-specific RBF settings over defaults from `hdfs-rbf-default.xml` and other Hadoop defaults.

## State and Persistence Behavior
No runtime state is defined by this checked-in file. Persistence is operational: administrators can edit or replace this file in deployed configs to persist router settings.

## Dependencies and Risks
The file depends on Hadoop's conventional `*-site.xml` resource loading. Because it is empty, the risk is omission rather than wrong defaults: a deployment relying only on this file will use default RBF settings and may lack required router addresses, state-store settings, security principals, or mount-table behavior.

## Test Signals
There are no direct tests in this file. Its signal is structural: it should remain parseable as Hadoop configuration XML and serve as a documented override hook.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/conf/hdfs-rbf-site.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/protocolPB/AsyncRpcProtocolPBUtil.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/protocolPB/AsyncRpcProtocolPBUtil.java

## Purpose
Utility for bridging Hadoop protobuf RPC calls into the asynchronous router execution model. It centralizes client-side async IPC response handling and server-side deferred protobuf responses for RBF protocol translators.

## Important APIs, Types, and Functions
`asyncIpcClient` invokes a shaded protobuf IPC call via `ipc(call)`, retrieves `ProtobufRpcEngine2.getAsyncReturnMessage()` and `Client.getResponseFuture()`, then maps the eventual RPC result through an `ApplyFunction<T,R>` before returning `AsyncUtil.asyncReturn(clazz)`. `asyncRouterServer` registers a deferred server callback with `ProtobufRpcEngine2.Server.registerForDeferredResponse2()`, invokes a `ServerReq<T>`, obtains the current async `CompletableFuture`, and maps the result through `ServerRes<T>` into a protobuf `Message`. `setAsyncResponderExecutor` configures the executor used by client response handling.

## Control Flow
Client flow starts the IPC, captures thread-local router context, and attaches `handleAsync` to the response future. On success it reads the async return message, logs call context, applies the response converter, and completes Hadoop's async return channel. On failure it wraps exceptions through router async helpers. Server flow registers a deferred response immediately, chains request execution into the current async future, and either calls `callback.setResponse(value)` or `callback.error(...)`.

## State and Persistence Behavior
The only static mutable state is `asyncResponderExecutor`. Per-call state is held in `CompletableFuture`s, protobuf callbacks, and `ThreadLocalContext`. There is no persistent storage, but preserving caller/thread-local context is critical for correct logging, caller identity, and router behavior.

## Dependencies and Integration Points
The class depends on `ProtobufRpcEngine2`, Hadoop IPC `Client` and `Server`, `CallerContext`, shaded protobuf `Message`, router `AsyncUtil`, router `ThreadLocalContext`, and `ApplyFunction`. It is directly imported by `RouterClientNamenodeProtocolServerSideTranslatorPB` and similar async-aware translators.

## Risks and Edge Cases
If `asyncResponderExecutor` is unset, client-side `handleAsync` uses a null executor path that can fail depending on JDK overload behavior; initialization ordering matters. `asyncRouterServer` casts `AsyncUtil.getAsyncUtilCompletableFuture()` to `CompletableFuture<T>`, so request/result type mismatches surface at runtime. Error handling uses `e.getCause()` for callback errors, which can be null for unusual completion failures.

## Test Signals
No direct tests are present in this item. Indirect signals come from async router RPC tests that expect translator methods to return `null` immediately while deferred protobuf responses are delivered through Hadoop RPC callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/protocolPB/AsyncRpcProtocolPBUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/protocolPB/RouterAdminProtocol.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/protocolPB/RouterAdminProtocol.java

## Purpose
Private stable Java protocol interface used by `routeradmin` clients to communicate with the Router admin/statestore surface.

## Important APIs and Types
The interface declares no methods itself; it composes five manager protocols: `MountTableManager`, `RouterStateManager`, `NameserviceManager`, `GenericRefreshProtocol`, and `RouterGenericManager`. These inherited contracts cover mount-table CRUD/bulk operations, router safe mode/state, nameservice enable/disable state, generic refresh operations, and generic router administration.

## Control Flow
There is no executable control flow. The interface is a type-level aggregation that lets translators and RPC clients expose one admin protocol rather than several unrelated manager references.

## State and Persistence Behavior
No state is held by the interface. Implementations such as `RouterAdminServer` may persist mount table and nameservice state through the federation state store.

## Dependencies and Integration Points
This interface is the native side paired with `RouterAdminProtocolPB` and the client/server protobuf translators. It integrates RBF resolver, router, nameservice, generic refresh, and generic admin APIs into Hadoop IPC.

## Risks and Edge Cases
Adding or changing inherited manager interfaces changes the router-admin RPC surface and requires matching protobuf service and translator updates. Because the interface is annotated `Private` and `Stable`, it is not a public end-user API but should remain internally compatible across module components.

## Test Signals
Testing is indirect through router-admin translator tests, admin CLI tests, and mount-table/state-store integration tests that call inherited methods through this aggregate type.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/protocolPB/RouterAdminProtocol.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/protocolPB/RouterAdminProtocolPB.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/protocolPB/RouterAdminProtocolPB.java

## Purpose
Protocol-buffer RPC interface for Router admin operations. It extends the generated `RouterAdminProtocolService.BlockingInterface` and adds Hadoop security and protocol metadata annotations.

## Important APIs and Types
Annotations bind the service to `HdfsConstants.ROUTER_ADMIN_PROTOCOL_NAME` with protocol version `1`, use `RBFConfigKeys.DFS_ROUTER_KERBEROS_PRINCIPAL_KEY` as the server principal, and select delegation tokens through `DelegationTokenSelector`. The inherited generated blocking interface defines the protobuf methods implemented by `RouterAdminProtocolServerSideTranslatorPB`.

## Control Flow
There is no method body. Hadoop RPC uses the annotations and generated service interface to create secure protobuf RPC proxies and dispatch server-side calls.

## State and Persistence Behavior
The interface stores no state. Runtime security state is external: Kerberos principals and delegation tokens are resolved through Hadoop security configuration and token selectors.

## Dependencies and Integration Points
This file links generated router protocol protobufs, Hadoop IPC `ProtocolInfo`, HDFS delegation-token selection, and RBF security configuration. It is the wire-level counterpart to the native `RouterAdminProtocol` aggregation.

## Risks and Edge Cases
Changing the protocol name, version, or security annotations can break compatibility with existing routeradmin clients. Token/kerberos annotations must match Router server configuration or secure clusters will fail authentication.

## Test Signals
Signals are indirect: secure router-admin integration tests should be able to create authenticated proxies, and method-support checks in `RouterAdminProtocolTranslatorPB` should query this PB protocol successfully.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/protocolPB/RouterAdminProtocolPB.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/protocolPB/RouterAdminProtocolServerSideTranslatorPB.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/protocolPB/RouterAdminProtocolServerSideTranslatorPB.java

## Purpose
Server-side protobuf translator for Router admin RPCs. It receives generated protobuf requests, converts them to native federation store protocol objects, calls `RouterAdminServer`, and converts native PBImpl responses back to protobuf messages.

## Important APIs, Types, and Functions
The class implements `RouterAdminProtocolPB` and holds a final `RouterAdminServer server`. It covers mount-table operations (`addMountTableEntry`, `addMountTableEntries`, `removeMountTableEntry`, `updateMountTableEntry`, `getMountTableEntries`, `refreshMountTableEntries`, `getDestination`), router state (`enterSafeMode`, `leaveSafeMode`, `getSafeMode`), nameservice state (`disableNameservice`, `enableNameservice`, `getDisabledNameservices`), and refresh (`refreshSuperUserGroupsConfiguration`).

## Control Flow
Each RPC method has a consistent synchronous adapter flow: construct the matching request PBImpl from the incoming proto, call the server method, cast the returned native response to the matching response PBImpl, and return `getProto()`. For empty request types, the server-side translator still wraps incoming request protos into request PBImpls where available. `IOException` is caught and rethrown as protobuf `ServiceException`.

## State and Persistence Behavior
The translator itself is stateless except for the server reference. Persistent effects are delegated to `RouterAdminServer`, which may mutate mount table entries, nameservice disabled state, router safe mode state, and refresh router/user-group configuration.

## Dependencies and Integration Points
It connects generated `HdfsServerFederationProtos` messages, native store protocol interfaces, PBImpl classes, and the router admin server. It must stay aligned with `RouterAdminProtocolTranslatorPB`, `RouterAdminProtocolPB`, and the generated protobuf service definitions.

## Risks and Edge Cases
The file relies on response implementations being PBImpl instances; a non-PB implementation returned by `RouterAdminServer` would cause a `ClassCastException`. Exception translation preserves the original exception as a `ServiceException`, unlike the client translator which currently wraps only the remote message. Adding a new admin RPC requires changes in generated protos, server implementation, and both translators.

## Test Signals
Expected tests should verify one-to-one request/response translation, `IOException` to `ServiceException` conversion, mount-table CRUD behavior through router-admin RPC, bulk add support, safe-mode transitions, nameservice enable/disable, and proxy-user refresh status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/protocolPB/RouterAdminProtocolServerSideTranslatorPB.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/protocolPB/RouterAdminProtocolTranslatorPB.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/protocolPB/RouterAdminProtocolTranslatorPB.java

## Purpose
Client-side translator for Router admin RPCs. It exposes native manager interfaces while forwarding calls through a `RouterAdminProtocolPB` protobuf proxy.

## Important APIs, Types, and Functions
The class implements `ProtocolMetaInterface`, `MountTableManager`, `RouterStateManager`, `NameserviceManager`, `RouterGenericManager`, `Closeable`, and `ProtocolTranslator`. `close()` stops the RPC proxy, `getUnderlyingProxyObject()` exposes it, and `isMethodSupported()` delegates to `RpcClientUtil`. Admin methods convert PBImpl request objects to protos, invoke the proxy, and wrap response protos in PBImpl response objects.

## Control Flow
Mount-table and nameservice methods expect incoming native requests to be PBImpls, cast them, extract `getProto()`, and call `rpcProxy`. Safe-mode and disabled-nameservice list calls build empty request protos directly. `refreshSuperUserGroupsConfiguration()` builds an empty proto, calls the proxy, then unwraps a boolean status from `RefreshSuperUserGroupsConfigurationResponsePBImpl`. `ServiceException` is converted to `IOException` using `getRemoteException(e).getMessage()`.

## State and Persistence Behavior
The translator holds only the `rpcProxy`; all durable state changes occur remotely in the Router admin server/state store. `close()` is important lifecycle behavior because it releases the Hadoop RPC proxy.

## Dependencies and Integration Points
The class depends on generated federation protobuf messages, PBImpl store protocol classes, Hadoop IPC `RPC`, `RpcClientUtil`, `ProtocolTranslator`, and `ShadedProtobufHelper.getRemoteException`. It is the client counterpart to `RouterAdminProtocolServerSideTranslatorPB`.

## Risks and Edge Cases
The implementation assumes callers pass PBImpl request objects; alternate implementations of native request interfaces will fail with `ClassCastException`. Exception translation currently constructs `IOException` from only the remote exception message, which may drop the remote exception class. Method-support checks must use the same protocol version and RPC kind as server registration.

## Test Signals
Tests should assert close/proxy behavior, method-support probing, correct proto forwarding for mount-table and nameservice operations, safe-mode empty-request behavior, refresh status unwrapping, and useful IOException conversion on remote service failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/protocolPB/RouterAdminProtocolTranslatorPB.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/protocolPB/RouterClientNamenodeProtocolServerSideTranslatorPB.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/protocolPB/RouterClientNamenodeProtocolServerSideTranslatorPB.java

## Purpose
Async server-side protobuf translator that exposes the HDFS `ClientNamenodeProtocol` over an RBF `RouterRpcServer`. It subclasses the standard NameNode server-side translator but overrides methods to call the router asynchronously through `AsyncRpcProtocolPBUtil.asyncRouterServer`.

## Important APIs, Types, and Functions
The constructor accepts a `ClientProtocol`, calls the superclass constructor, and casts it to `RouterRpcServer`. The class overrides most client-facing HDFS operations: block location/defaults, create/append/addBlock/complete, metadata changes, listing, leases, datanode and filesystem stats, safe mode, upgrades, snapshots, cache directives/pools, ACLs, encryption zones, xattrs, storage policies, edit-log queries, erasure coding, quota usage, open-file listing, msync, satisfy-storage-policy, HA state, slow datanode reports, and enclosing-root lookup. Conversion is delegated to `PBHelperClient` and many void methods return superclass-provided `VOID_*` response constants.

## Control Flow
Every overridden method starts `asyncRouterServer(requestLambda, responseLambda)` and returns `null`, relying on Hadoop protobuf RPC deferred response callbacks. Request lambdas read fields from the incoming proto, convert optional fields and repeated lists to native types, and call the corresponding `RouterRpcServer` method. Response lambdas build the expected response proto, handling nullable native results for file info, listings, snapshot listings, encryption zones, storage policies, delegation tokens, and similar optional values.

## State and Persistence Behavior
The translator stores only the router server reference. All filesystem state changes are delegated to `RouterRpcServer`, including namespace mutation, block allocation, leases, snapshots, cache metadata, ACL/xattr/storage-policy changes, encryption-zone operations, erasure-coding policy changes, quotas, and router-visible HA/safemode operations. Per-call async state lives in `CompletableFuture`s and deferred protobuf callbacks managed by `asyncRouterServer`.

## Dependencies and Integration Points
This class is a high-volume integration point among generated HDFS protobuf request/response types, `RouterRpcServer`, `ClientProtocol`, `PBHelperClient`, Hadoop security token protos, HA protos, erasure-coding/encryption/xattr/ACL protos, and async router utilities. It defines the wire behavior that HDFS clients observe when connected to a Router instead of a NameNode.

## Risks and Edge Cases
Because almost every method returns `null` immediately, correctness depends on deferred response registration and completion; any synchronous caller assumption would break. Optional proto fields require careful defaults, such as create permissions with masked/unmasked modes, append flags defaulting to `APPEND`, `complete` file IDs defaulting to `GRANDFATHER_INODE_ID`, optional snapshot names, optional storage types, and optional null responses. Large repeated-list conversions can allocate arrays. Methods without an `@Override` annotation, such as `listReencryptionStatus` and `getCurrentEditLogTxid`, should be watched for signature drift against the generated interface.

## Test Signals
Useful signals are router client integration tests that compare behavior against direct NameNode protocol behavior, async RPC tests that verify deferred responses and errors, and conversion-specific tests for optional fields, empty listings, batched listing exceptions, delegation tokens, HA state enum mapping, erasure-coding responses, and metadata mutations. High-risk methods include create/append/addBlock/complete, rename2 option mapping, batched listing partial exception encoding, and all nullable response builders.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/protocolPB/RouterClientNamenodeProtocolServerSideTranslatorPB.java -->
