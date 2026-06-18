# Research Report: subset-b-008090

Grouped research for the Ozone interface-client, interface-storage, mini-cluster, and integration-test resource files listed in work item `subset-b-008090`. Each section is delimited for reconciliation into the source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/resources/yarn-site.xml -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/resources/yarn-site.xml

Purpose: This is an integration-test `yarn-site.xml` placeholder. It declares an empty Hadoop `configuration` element with the standard configuration stylesheet PI, letting tests include a YARN site resource without overriding any properties.

Important APIs/types/functions: No code APIs are defined. The effective contract is the Hadoop XML configuration schema: a root `<configuration>` element with zero `<property>` children.

Control flow, state, and persistence: The file contributes no runtime state by itself. Hadoop configuration loading can merge it into an `OzoneConfiguration`/Hadoop `Configuration`; because it is empty, it preserves defaults and only satisfies classpath/resource expectations.

Dependencies and integration points: Integrated through Hadoop's configuration resource loader in integration tests. It depends on the standard `configuration.xsl` reference only for display tooling.

Risks: Adding properties here would globally affect integration tests that load YARN resources, possibly changing scheduler, resource-manager, or mini-cluster behavior. The current empty file has low behavioral risk but can mask missing test-specific configuration if a test assumes YARN is configured.

Test signals: Presence of the file is itself a test fixture signal. No direct unit tests are defined in this file.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/resources/yarn-site.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/interface-client/dev-support/findbugsExcludeFile.xml -->
# sources/object-store/apache-ozone/hadoop-ozone/interface-client/dev-support/findbugsExcludeFile.xml

Purpose: SpotBugs/FindBugs exclusion filter for `ozone-interface-client`. It suppresses findings for generated protobuf packages rather than hand-authored code.

Important APIs/types/functions: Defines two `<Match>` rules for packages `org.apache.hadoop.ozone.protocol.proto` and `org.apache.hadoop.ozone.security.proto`.

Control flow, state, and persistence: Build-time only. It changes static-analysis reporting, not compiled artifacts or runtime state.

Dependencies and integration points: Referenced by the module's build tooling conceptually, though the client POM also sets `spotbugs.skip=true` because this module is generated-code-only. It aligns with `OMAdminProtocol.proto`, `OmClientProtocol.proto`, `OmInterServiceProtocol.proto`, and `Security.proto`.

Risks: Broad package-level exclusions can hide defects if hand-written code is later added under the generated proto packages. If package names change, generated sources may start producing SpotBugs noise.

Test signals: No runtime tests. Build signal is that generated protobuf packages are intentionally excluded from static-analysis enforcement.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/interface-client/dev-support/findbugsExcludeFile.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/interface-client/pom.xml -->
# sources/object-store/apache-ozone/hadoop-ozone/interface-client/pom.xml

Purpose: Maven module descriptor for `ozone-interface-client`, the jar that publishes Ozone Manager client/admin/inter-service protobuf and gRPC generated Java APIs.

Important APIs/types/functions: The POM is not code, but it defines generation of Java protobuf and gRPC stubs from `src/main/proto`. It runs `protobuf-maven-plugin` goals `compile`, `test-compile`, `compile-custom`, and `test-compile-custom`, with output under `target/generated-sources/proto-java-protobuf-${protobuf.version}` and `grpc-java` as the custom plugin.

Control flow, state, and persistence: Build control is mostly generated-source oriented. It skips tests (`maven.test.skip=true`) and SpotBugs (`spotbugs.skip=true`), disables annotation processing with `maven-compiler-plugin proc=none`, and enables the Salesforce proto backward-compatibility plugin.

Dependencies and integration points: Depends on protobuf Java, gRPC API/protobuf/stub, Guava, HDDS interface-client, Javax annotation API for generated Java 11+ sources, and Netty HTTP/2/proxy runtime jars. Generated artifacts are consumed by Ozone client, OM server, admin CLI, S3, and HA code.

Risks: Proto field-number and enum-value compatibility is the primary risk; the POM includes compatibility tooling, but tests are skipped in this module. gRPC/protobuf plugin version drift can change generated API shape. Excluding `jsr305` from gRPC dependencies avoids dependency conflicts but can surface annotation compatibility issues.

Test signals: Explicitly states there are no tests in the module. Compatibility is expected to be enforced by proto-backwards-compatibility and downstream modules.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/interface-client/pom.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/interface-client/src/main/proto/OMAdminProtocol.proto -->
# sources/object-store/apache-ozone/hadoop-ozone/interface-client/src/main/proto/OMAdminProtocol.proto

Purpose: Private unstable protobuf/gRPC admin protocol for Ozone Manager administrative operations.

Important APIs/types/functions: Generates `org.apache.hadoop.ozone.protocol.proto.OzoneManagerAdminProtocolProtos`. Defines `OMConfigurationRequest/Response`, `OMNodeInfo`, `NodeState`, `DecommissionOMRequest/Response`, `CompactRequest/Response`, `TriggerSnapshotDefragRequest/Response`, and service `OzoneManagerAdminService`.

Control flow, state, and persistence: RPC methods are request/response envelopes. `getOMConfiguration` returns in-memory OM nodes and nodes from reloaded configuration. `decommission` removes an OM by node id/address. `compactDB` requests compaction of a named OM DB column family. `triggerSnapshotDefrag` can run synchronously or no-wait based on `noWait`.

Dependencies and integration points: Integrated with generated gRPC stubs from the interface-client module, admin CLI, OM HA administration, RocksDB column family management, and snapshot-defrag code. Uses proto2 required/optional semantics.

Risks: The interface is private and unstable but still a wire contract for admin clients. Field-number reuse or required-field changes can break rolling upgrades or mixed client/server versions. `CompactRequest.columnFamily` is stringly typed, so callers must align with OM DB table names. Snapshot defrag is operationally sensitive and may be long-running.

Test signals: No direct proto tests in this module. Downstream admin and OM integration tests should cover service implementations and compatibility plugin should catch incompatible schema edits.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/interface-client/src/main/proto/OMAdminProtocol.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/interface-client/src/main/proto/OmClientProtocol.proto -->
# sources/object-store/apache-ozone/hadoop-ozone/interface-client/src/main/proto/OmClientProtocol.proto

Purpose: Central private unstable protobuf protocol for client-to-OM namespace, object, security, tenant, snapshot, upgrade, quota-repair, tagging, and maintenance RPCs.

Important APIs/types/functions: Generates `OzoneManagerProtocolProtos` in `org.apache.hadoop.ozone.protocol.proto`. The `Type` enum maps command ids to all OM operations, including volume/bucket/key lifecycle, file-system optimized operations, ACLs, multipart upload, DB updates, upgrade prepare/finalize, delegation tokens, S3 secrets, tenants, snapshots, lease recovery, safe mode, quota repair, object and bucket tagging, and snapshot diff submission. `OMRequest` carries `cmdType`, `traceID`, `clientId`, optional user/version/layout/read-consistency metadata, and one optional typed request per command. `OMResponse` mirrors command status and typed response payloads. `Status` enumerates detailed success/failure codes. `OzoneManagerService.submitRequest` is the single RPC entry point.

Control flow, state, and persistence: This file does not implement behavior, but it defines the command-dispatch envelope OM uses to route requests through validation, Ratis submission, state-machine application, and response marshalling. Persisted or consensus-sensitive payloads include key info, bucket/volume info, snapshot info, deleted key/purge structures, multipart state, S3 secrets, tenant state, transaction updates, and lock timing details. Read consistency hints support default leader reads, linearizable leader/follower reads, and local-lease bounded-staleness reads.

Dependencies and integration points: Imports `hdds.proto` for shared HDDS messages and `Security.proto` for delegation token messages. It is consumed by Ozone clients, OM RPC server/client translators, OM Ratis state machine, S3 gateway paths, snapshot diff services, tenant/security code, and downstream generated-code users.

Risks: This is a large wire contract with many historical/deprecated fields. Proto2 field numbers are compatibility-critical; adding a command requires matching `Type`, `OMRequest`, `OMResponse`, server dispatch, ACL/security checks, audit, and tests. Several field names use mixed capitalization for historical reasons, so generated Java accessors can be surprising. The comments on `ReadConsistencyProto.DEFAULT` explicitly allow rare stale reads during leadership transitions. Some TODO bucket-tagging messages indicate incomplete implementation coupling.

Test signals: The interface-client module itself skips tests, so coverage is downstream. Strong test signals should come from OM request handler tests, client translator tests, Ratis replay/upgrade tests, snapshot/tenant/S3 integration tests, and proto backward-compatibility checks.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/interface-client/src/main/proto/OmClientProtocol.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/interface-client/src/main/proto/OmInterServiceProtocol.proto -->
# sources/object-store/apache-ozone/hadoop-ozone/interface-client/src/main/proto/OmInterServiceProtocol.proto

Purpose: Private unstable protobuf/gRPC protocol for OM-to-OM communication in HA setups, focused on bootstrapping a new OM into an existing OM ring.

Important APIs/types/functions: Generates `OzoneManagerInterServiceProtocolProtos`. Defines `BootstrapOMRequest` with node id, host address, Ratis port, and listener flag; `BootstrapOMResponse` with success, optional `ErrorCode`, and error message; `ErrorCode` values for Ratis disabled, leader undetermined/not ready, bootstrap error, and undefined error; service `OzoneManagerInterService.bootstrap`.

Control flow, state, and persistence: The protocol describes a coordination step where a joining OM contacts an existing OM service to bootstrap HA metadata/Ratis membership. It does not persist state itself, but request handling updates OM HA membership and depends on Ratis state.

Dependencies and integration points: Generated stubs are used by OM HA bootstrap/admin workflows. It integrates with OM Ratis membership, leader readiness checks, and listener/non-voting OM mode.

Risks: Bootstrap is cluster-membership sensitive. Misinterpreting `isListener` or leader readiness can create invalid HA topology or failed joins. Required fields mean old/new clients must supply node identity and Ratis address.

Test signals: Expected downstream coverage is OM HA bootstrap integration tests. The proto compatibility plugin should guard field-number changes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/interface-client/src/main/proto/OmInterServiceProtocol.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/interface-client/src/main/proto/Security.proto -->
# sources/object-store/apache-ozone/hadoop-ozone/interface-client/src/main/proto/Security.proto

Purpose: Stable protobuf interface for Hadoop/Ozone security tokens and credential transport.

Important APIs/types/functions: Generates `SecurityProtos` under `org.apache.hadoop.ozone.security.proto`. Defines `TokenProto`, `CredentialsKVProto`, `CredentialsProto`, and delegation-token request/response messages for get, renew, and cancel.

Control flow, state, and persistence: The file serializes security material: token identifiers, passwords, kind, service, credential aliases, and optional secrets. Delegation-token messages flow through OM client protocol and security services. It does not store data directly, but persisted or transmitted credentials must remain compatible.

Dependencies and integration points: Used by `OmClientProtocol.proto` token operations and by Hadoop security/token machinery. Proto package is `hadoop.common`, indicating common security reuse.

Risks: Marked stable, so compatibility requirements are stricter than the OM private protocols. Token bytes and secrets are sensitive; logs and debugging must avoid exposing serialized content. Required token fields make partial token objects invalid.

Test signals: No module-local tests. Downstream security and delegation-token integration tests are the meaningful coverage, along with proto compatibility checks.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/interface-client/src/main/proto/Security.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/interface-storage/dev-support/findbugsExcludeFile.xml -->
# sources/object-store/apache-ozone/hadoop-ozone/interface-storage/dev-support/findbugsExcludeFile.xml

Purpose: SpotBugs filter for `ozone-interface-storage` generated storage protobuf classes.

Important APIs/types/functions: Single package-level `<Match>` excludes `org.apache.hadoop.ozone.storage.proto`.

Control flow, state, and persistence: Build-time analysis filter only. It has no runtime effect on OM metadata or generated protobuf code.

Dependencies and integration points: Referenced by `interface-storage/pom.xml` as the SpotBugs exclude filter. It corresponds to generated classes from `OmStorageProtocol.proto`.

Risks: A package-level exclusion can hide findings if non-generated code is later placed in the proto package. If generated package names change, SpotBugs findings may reappear.

Test signals: Static-analysis configuration only; no runtime test signal.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/interface-storage/dev-support/findbugsExcludeFile.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/interface-storage/pom.xml -->
# sources/object-store/apache-ozone/hadoop-ozone/interface-storage/pom.xml

Purpose: Maven descriptor for `ozone-interface-storage`, the module holding OM storage interfaces, helper codecs, lock interfaces/metrics, and generated storage protobuf classes.

Important APIs/types/functions: Configures protobuf compilation for storage protos and SpotBugs exclusion for generated storage proto package. Disables annotation processing via compiler `proc=none`.

Control flow, state, and persistence: Build dependencies expose this module to core OM storage code. It compiles generated proto messages used by persisted metadata and Java interfaces/classes that define OM metadata table access and lock behavior.

Dependencies and integration points: Depends on JCIP annotations, Guava, protobuf Java, Hadoop common, HDDS common/interface/server framework, ozone-common, ozone-interface-client, RocksDB checkpoint differ, and Ratis common. Test dependencies include HDDS common test jar, SCM test jar, and HDDS test utils.

Risks: Since this module defines persistence-facing codecs and protocols, dependency or protobuf changes can affect on-disk compatibility. It also depends on interface-client, so client proto evolution can affect lock metrics proto conversion and tests.

Test signals: Includes focused unit tests for codecs, prefix info immutability/serialization, and DAG lock ordering. Protobuf compilation is part of the module build.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/interface-storage/pom.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/interface-storage/src/main/java/org/apache/hadoop/ozone/om/ExpiredOpenKeys.java -->
# sources/object-store/apache-ozone/hadoop-ozone/interface-storage/src/main/java/org/apache/hadoop/ozone/om/ExpiredOpenKeys.java

Purpose: Small aggregation container for expired open keys discovered by OM cleanup logic.

Important APIs/types/functions: Exposes `getOpenKeyBuckets()` for non-hsync open keys and `getHsyncKeys()` for hsync-ed keys. Package-private `addOpenKey(OmKeyInfo, String)` groups open key DB names by volume/bucket into `OpenKeyBucket.Builder`. Package-private `addHsyncKey(KeyArgs.Builder, long)` creates `CommitKeyRequest.Builder` entries for hsync cleanup.

Control flow, state, and persistence: Maintains in-memory `Map<String, OpenKeyBucket.Builder>` keyed by `volume/bucket` and a list of `CommitKeyRequest.Builder`. It does not persist itself; callers convert builders into protobuf requests such as `DeleteOpenKeysRequest` or commit-related cleanup flows.

Dependencies and integration points: Uses `OmKeyInfo` for volume/bucket lookup, `OM_KEY_PREFIX` for grouping key construction, and generated `OpenKeyBucket`, `OpenKey`, `KeyArgs`, and `CommitKeyRequest` messages from `OmClientProtocol.proto`.

Risks: The map key is string-concatenated with `OM_KEY_PREFIX`; any inconsistency with OM DB key conventions can group keys incorrectly. The class is mutable and not synchronized, so it should remain request/local-thread scoped. Builders expose mutable protobuf state to callers.

Test signals: No direct test in this subset. Indirect signals should come from OM open-key expiration and hsync cleanup tests.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/interface-storage/src/main/java/org/apache/hadoop/ozone/om/ExpiredOpenKeys.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/interface-storage/src/main/java/org/apache/hadoop/ozone/om/OMMetadataManager.java -->
# sources/object-store/apache-ozone/hadoop-ozone/interface-storage/src/main/java/org/apache/hadoop/ozone/om/OMMetadataManager.java

Purpose: Core interface for Ozone Manager metadata access. It defines lifecycle, RocksDB/DBStore access, OM table accessors, namespace key construction, listing helpers, snapshot lookup, multipart and deleted-key helpers, and FSO/object-id path-key utilities.

Important APIs/types/functions: Key methods include `start`, `stop`, `getStore`, `getOmEpoch`, key builders such as `getVolumeKey`, `getBucketKey`, `getOzoneKey`, `getOzoneKeyFSO`, `getOzoneDirKey`, `getOpenKey`, `getMultipartKey`, FSO variants, and rename/delete path key helpers. It exposes tables for users, volumes, buckets, keys, files, deleted keys, open keys, delegation tokens, prefixes, multipart info/parts, transactions, tenants, snapshots, snapshot rename, compaction log, metadata, directories, and deleted directories. Helper methods cover bucket/volume emptiness, bucket/volume listing, snapshot lookup, expired multipart uploads, incomplete MPU checks, bucket prefix calculation, IDs, and block groups for deleted keys. Nested `VolumeBucketId` is a value object for volume/bucket ids.

Control flow, state, and persistence: Implementations are responsible for the OM metadata DB and cache-backed table semantics. The interface standardizes DB key encoding for legacy object-store layout and file-system-optimized layout, including open file keys and delete-table keys. Persistence flows through HDDS `Table` abstractions, `BatchOperation`, snapshots, transaction info, and RocksDB-backed stores.

Dependencies and integration points: Extends `DBStoreHAManager` and `AutoCloseable`. It integrates with OM request handlers, key/bucket/volume managers, snapshot subsystem, tenant and S3 secret metadata, deleted block service, compaction log, and lock/transaction code. It depends on many helper types such as `OmBucketInfo`, `OmKeyInfo`, `RepeatedOmKeyInfo`, `OmMultipartKeyInfo`, `OmDirectoryInfo`, `SnapshotInfo`, `CompactionLogEntry`, and HDDS DB abstractions.

Risks: This is a high-blast-radius contract. Key-format changes can break on-disk compatibility, snapshots, or FSO path resolution. Table accessors expose low-level mutable persistence surfaces, so callers must coordinate locks and batch writes correctly. Legacy and FSO layouts coexist, increasing risk of using the wrong table/key function. Snapshot and deleted-directory helpers are sensitive to object-id parsing and purge logic.

Test signals: This subset contains codec tests for persisted helper values, but not direct tests for all `OMMetadataManager` methods. Strong downstream coverage should include OM metadata manager implementation tests, upgrade/replay tests, FSO path tests, snapshot table tests, and key-format compatibility tests.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/interface-storage/src/main/java/org/apache/hadoop/ozone/om/OMMetadataManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/interface-storage/src/main/java/org/apache/hadoop/ozone/om/helpers/OmPrefixInfo.java -->
# sources/object-store/apache-ozone/hadoop-ozone/interface-storage/src/main/java/org/apache/hadoop/ozone/om/helpers/OmPrefixInfo.java

Purpose: Immutable persisted model for OM prefix path metadata, currently centered on prefix ACLs and metadata.

Important APIs/types/functions: `OmPrefixInfo` extends `WithObjectID` and implements `CopyObject<OmPrefixInfo>`. It exposes `getCodec()`, `getAcls()`, `getName()`, `newBuilder()`, `getProtobuf()`, `builderFromProtobuf()`, `getFromProtobuf()`, `copyObject()`, and `toBuilder()`. The nested `Builder` supports ACL set/add/remove operations, metadata addition, object/update id setters, validation, and `isAclsChanged()`.

Control flow, state, and persistence: The static codec is a `DelegatedCodec` over `Proto2Codec<PersistedPrefixInfo>`, so persisted bytes are `OmStorageProtocol.proto` `PersistedPrefixInfo`. `getProtobuf()` serializes name, ACLs, metadata, object ID, and update ID. Deserialization rebuilds metadata, ACL list, and optional object/update IDs. Internal ACL state is stored as a Guava `ImmutableList`.

Dependencies and integration points: Used by `OMMetadataManager.getPrefixTable()` for prefix ACL storage. Depends on `OzoneAcl`, `OzoneAclStorageUtil`, `KeyValueUtil`, HDDS DB codec interfaces, JCIP `@Immutable`, and `PersistedPrefixInfo`.

Risks: Builder validation requires a non-null name but does not validate path shape. ACL conversion depends on enum-name compatibility between `OzoneAcl` and storage proto. The object/update IDs are optional on read but always set on `getProtobuf()`, which can matter for compatibility with older records.

Test signals: `TestOmPrefixInfo` covers copy behavior, immutability, protobuf parsing, and protobuf generation. `TestOmPrefixInfoCodec` covers round-trip persisted-format codec behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/interface-storage/src/main/java/org/apache/hadoop/ozone/om/helpers/OmPrefixInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/interface-storage/src/main/java/org/apache/hadoop/ozone/om/helpers/OzoneAclStorage.java -->
# sources/object-store/apache-ozone/hadoop-ozone/interface-storage/src/main/java/org/apache/hadoop/ozone/om/helpers/OzoneAclStorage.java

Purpose: Package-private converter between runtime `OzoneAcl` objects and storage-layer protobuf `OzoneAclInfo`.

Important APIs/types/functions: Static `toProtobuf(OzoneAcl)` writes name, identity type, scope, and rights bytes. Static `fromProtobuf(OzoneAclInfo)` reconstructs a BitSet of ACL rights, maps bit indices to `IAccessAuthorizer.ACLType`, builds an `EnumSet`, and creates an `OzoneAcl`.

Control flow, state, and persistence: Stateless conversion helper. It defines the byte-level ACL rights persistence bridge for prefix metadata and other storage proto users.

Dependencies and integration points: Used by `OzoneAclStorageUtil` and `OmPrefixInfo`. Depends on `OzoneAcl`, `AclScope`, `IAccessAuthorizer`, and `OzoneManagerStorageProtos.OzoneAclInfo`.

Risks: Enum name and ordinal stability are critical. Rights bytes are decoded by ACLType ordinal via `BitSet.stream()`, so reordering ACLType values or adding incompatible positions can corrupt interpretation. `EnumSet.copyOf` on an empty list can throw, so empty rights may need upstream handling.

Test signals: Covered indirectly by `TestOmPrefixInfo` and `TestOmPrefixInfoCodec`, which serialize and deserialize ACL-bearing prefix info.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/interface-storage/src/main/java/org/apache/hadoop/ozone/om/helpers/OzoneAclStorage.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/interface-storage/src/main/java/org/apache/hadoop/ozone/om/helpers/OzoneAclStorageUtil.java -->
# sources/object-store/apache-ozone/hadoop-ozone/interface-storage/src/main/java/org/apache/hadoop/ozone/om/helpers/OzoneAclStorageUtil.java

Purpose: Package-private list conversion utility for ACL storage protobufs.

Important APIs/types/functions: `toProtobuf(List<OzoneAcl>)` maps each runtime ACL through `OzoneAclStorage.toProtobuf`. `fromProtobuf(List<OzoneAclInfo>)` maps each proto ACL through `OzoneAclStorage.fromProtobuf`.

Control flow, state, and persistence: Stateless helper. It preserves list order while converting between Java and persisted proto ACL representations.

Dependencies and integration points: Used by `OmPrefixInfo` serialization/deserialization. Depends on `OzoneAcl`, `OzoneAclInfo`, and `OzoneAclStorage`.

Risks: No null checks are present for the list or elements, so callers must provide valid lists. It allocates mutable `ArrayList`s, but callers such as `OmPrefixInfo` later wrap state immutably.

Test signals: Indirectly covered by prefix info tests and prefix codec round trips.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/interface-storage/src/main/java/org/apache/hadoop/ozone/om/helpers/OzoneAclStorageUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/interface-storage/src/main/java/org/apache/hadoop/ozone/om/helpers/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/interface-storage/src/main/java/org/apache/hadoop/ozone/om/helpers/package-info.java

Purpose: Package documentation for `org.apache.hadoop.ozone.om.helpers`.

Important APIs/types/functions: No executable API. The package-level Javadoc states that the package contains helpers for the OM storage proto layer.

Control flow, state, and persistence: No runtime behavior or state. It affects generated documentation and package intent.

Dependencies and integration points: Applies to helper classes such as `OmPrefixInfo`, `OzoneAclStorage`, codecs, and persisted metadata value helpers in the same package.

Risks: Low. Inaccurate package documentation can mislead maintainers but cannot change behavior.

Test signals: No direct tests.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/interface-storage/src/main/java/org/apache/hadoop/ozone/om/helpers/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/interface-storage/src/main/java/org/apache/hadoop/ozone/om/lock/DAGLeveledResource.java -->
# sources/object-store/apache-ozone/hadoop-ozone/interface-storage/src/main/java/org/apache/hadoop/ozone/om/lock/DAGLeveledResource.java

Purpose: Enum of hierarchical lock resources that define DAG-based lock ordering for OM snapshot/bootstrap-related resources.

Important APIs/types/functions: Values are `SNAPSHOT_GC_LOCK`, `SNAPSHOT_DB_LOCK`, `SNAPSHOT_LOCAL_DATA_LOCK`, `SNAPSHOT_DB_CONTENT_LOCK`, and `BOOTSTRAP_LOCK`. Each implements `IOzoneManagerLock.Resource` via `getName()` and `getResourceManager()`, and exposes `getChildren()` for lock ordering.

Control flow, state, and persistence: Each enum constant owns a `ResourceManager` holding thread-local lock timing. Child sets represent allowed downstream lock acquisition order: `SNAPSHOT_DB_CONTENT_LOCK` precedes DB/local-data locks, and `BOOTSTRAP_LOCK` precedes all snapshot locks. This is runtime concurrency state only, not persisted metadata.

Dependencies and integration points: Used by hierarchical lock manager implementations and snapshot/bootstrap code to avoid deadlocks. Integrates with `IOzoneManagerLock.ResourceManager`.

Risks: Introducing a cycle or incorrect parent/child edge can create deadlocks or block valid lock sequences. The constructor filters self-dependencies but does not detect larger cycles at runtime.

Test signals: `TestDAGLeveledResource.ensureNoCycleInDAGLevelResource` builds a Guava directed graph from enum values/children and asserts it has no cycle.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/interface-storage/src/main/java/org/apache/hadoop/ozone/om/lock/DAGLeveledResource.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/interface-storage/src/main/java/org/apache/hadoop/ozone/om/lock/HierarchicalResourceLockManager.java -->
# sources/object-store/apache-ozone/hadoop-ozone/interface-storage/src/main/java/org/apache/hadoop/ozone/om/lock/HierarchicalResourceLockManager.java

Purpose: Interface for deterministic, deadlock-resistant locking over DAG-structured OM resources.

Important APIs/types/functions: Defines `acquireReadLock(DAGLeveledResource, String)`, `acquireWriteLock(DAGLeveledResource, String)`, `acquireResourceWriteLock(DAGLeveledResource)`, `getCurrentLockedResources()`, and nested `HierarchicalResourceLock extends Closeable` with `isLockAcquired()`.

Control flow, state, and persistence: Implementations acquire resource/key locks and return a closeable handle for lifecycle management. `getCurrentLockedResources()` exposes the resources locked by the current thread. No persistence is implied.

Dependencies and integration points: Intended for resources such as FSO trees and snapshot chains, with `DAGLeveledResource` providing ordering. Implementations likely bridge to `IOzoneManagerLock`.

Risks: Correctness depends on implementations enforcing DAG order and reliable close/release semantics. Callers must close returned handles, preferably with try-with-resources, or leak locks.

Test signals: No direct implementation tests in this subset; `DAGLeveledResource` cycle test supports the ordering substrate.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/interface-storage/src/main/java/org/apache/hadoop/ozone/om/lock/HierarchicalResourceLockManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/interface-storage/src/main/java/org/apache/hadoop/ozone/om/lock/IOzoneManagerLock.java -->
# sources/object-store/apache-ozone/hadoop-ozone/interface-storage/src/main/java/org/apache/hadoop/ozone/om/lock/IOzoneManagerLock.java

Purpose: Primary interface for Ozone Manager metadata locks, including read/write keyed locks, resource locks, multi-user locks, metrics, and testing hooks.

Important APIs/types/functions: Methods acquire/release read and write locks for single or multiple resource key arrays, acquire/release resource write locks, acquire/release multi-user locks, inspect hold counts and current-thread ownership for tests, `cleanup()`, and `getOMLockMetrics()`. Default helpers `acquireResourceLock` and `acquireLock` return `UncheckedAutoCloseableSupplier<OMLockDetails>` wrappers that release once on close. Nested `Resource` provides name and `ResourceManager`; nested `ResourceManager` tracks per-thread read/write held-time start nanos via `ThreadLocal<LockUsageInfo>`.

Control flow, state, and persistence: Implementations perform actual locking. Default helper methods acquire, validate success, and protect release with `AtomicBoolean` to make close idempotent. Resource timing state is thread-local and removed when retrieved, supporting metrics for lock wait/hold durations. No persistence occurs.

Dependencies and integration points: Used across OM request handlers and metadata managers to protect namespace tables. Integrates with `OMLockDetails`, `OMLockMetrics`, `LockUsageInfo`, Ratis unchecked closeable supplier, and resource enums such as `DAGLeveledResource`.

Risks: Lock ordering and release symmetry are critical. Default helpers throw `RuntimeException` if acquisition fails, so callers must be prepared for unchecked failure. ThreadLocal timestamp removal on getter means metrics code must call it exactly when releasing; missed or repeated calls can lose timing data.

Test signals: Interface-specific implementation tests are elsewhere. This subset has lock DAG tests and `OMLockDetails` proto fields in `OmClientProtocol.proto` for response/debug integration.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/interface-storage/src/main/java/org/apache/hadoop/ozone/om/lock/IOzoneManagerLock.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/interface-storage/src/main/java/org/apache/hadoop/ozone/om/lock/LockUsageInfo.java -->
# sources/object-store/apache-ozone/hadoop-ozone/interface-storage/src/main/java/org/apache/hadoop/ozone/om/lock/LockUsageInfo.java

Purpose: Simple mutable holder for per-thread lock-held start timestamps used by lock metrics.

Important APIs/types/functions: Stores `startReadHeldTimeNanos` and `startWriteHeldTimeNanos`, both initialized to `-1`, with setters and getters.

Control flow, state, and persistence: Runtime-only state. Instances are held in `ThreadLocal`s by `IOzoneManagerLock.ResourceManager`.

Dependencies and integration points: Used by `ResourceManager` to isolate read/write lock timing per thread.

Risks: Sentinel `-1` requires consumers to handle uninitialized values correctly. The class itself is not synchronized; thread safety comes from ThreadLocal usage.

Test signals: No direct tests in this subset. Indirectly exercised by lock metric implementations.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/interface-storage/src/main/java/org/apache/hadoop/ozone/om/lock/LockUsageInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/interface-storage/src/main/java/org/apache/hadoop/ozone/om/lock/OMLockDetails.java -->
# sources/object-store/apache-ozone/hadoop-ozone/interface-storage/src/main/java/org/apache/hadoop/ozone/om/lock/OMLockDetails.java

Purpose: Mutable timing/result object describing an OM lock operation.

Important APIs/types/functions: Static empty acquired/not-acquired instances, fields for `lockAcquired`, wait/read/write nanos, `add(long, LockOpType)`, `merge(OMLockDetails)`, getters/setters, `toProtobufBuilder()`, `toString()`, and `clear()`. Internal enum `LockOpType` classifies wait/read/write timing.

Control flow, state, and persistence: Accumulates timing across lock operations and can serialize to `OMLockDetailsProto` from `OmClientProtocol.proto`. It is runtime state carried in responses/logging/metrics rather than DB-persisted state.

Dependencies and integration points: Returned by `IOzoneManagerLock` operations, used by request code to capture lock timing, and converted to client protocol protobuf for observability.

Risks: Static `EMPTY_DETAILS_*` instances are mutable because `clear`, setters, and `merge` are public; callers must avoid mutating shared constants. `merge` overwrites `lockAcquired` with the merged object while adding timings, which is meaningful but can surprise callers aggregating mixed results.

Test signals: No direct unit test in this subset. Proto field definition exists in `OmClientProtocol.proto`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/interface-storage/src/main/java/org/apache/hadoop/ozone/om/lock/OMLockDetails.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/interface-storage/src/main/java/org/apache/hadoop/ozone/om/lock/OMLockMetrics.java -->
# sources/object-store/apache-ozone/hadoop-ozone/interface-storage/src/main/java/org/apache/hadoop/ozone/om/lock/OMLockMetrics.java

Purpose: Hadoop Metrics2 source for OM lock wait and hold time statistics.

Important APIs/types/functions: Static `create()` registers the source in `DefaultMetricsSystem`; `unRegister()` removes it. Setter methods add samples for read wait, read held, write wait, and write held times in milliseconds. Getter methods expose stat strings and latest max values. `getMetrics` snapshots all four `MutableStat`s into a metrics record.

Control flow, state, and persistence: Runtime metrics only. The object owns a `MetricsRegistry` and four `MutableStat`s. Samples are accumulated and exposed through Hadoop Metrics2; no DB persistence occurs.

Dependencies and integration points: Used by OM lock implementations via `IOzoneManagerLock.getOMLockMetrics()`. Depends on Hadoop metrics2, `DefaultMetricsSystem`, and Ozone metrics context.

Risks: Registration uses a fixed source name, so multiple registrations without unregistering can conflict. `lastStat().max()` depends on metrics snapshot state; callers should interpret longest values in relation to metrics intervals.

Test signals: No direct unit test in this subset. Metrics behavior is typically verified in lock implementation or metrics integration tests.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/interface-storage/src/main/java/org/apache/hadoop/ozone/om/lock/OMLockMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/interface-storage/src/main/java/org/apache/hadoop/ozone/om/lock/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/interface-storage/src/main/java/org/apache/hadoop/ozone/om/lock/package-info.java

Purpose: Package documentation for OM lock classes.

Important APIs/types/functions: No executable API. Javadoc states the package contains classes related to Ozone Manager lock.

Control flow, state, and persistence: Documentation only.

Dependencies and integration points: Applies to `IOzoneManagerLock`, `DAGLeveledResource`, lock metrics/details, and hierarchical lock manager interfaces.

Risks: Low documentation-only risk.

Test signals: No direct tests.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/interface-storage/src/main/java/org/apache/hadoop/ozone/om/lock/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/interface-storage/src/main/java/org/apache/hadoop/ozone/om/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/interface-storage/src/main/java/org/apache/hadoop/ozone/om/package-info.java

Purpose: Package documentation for the storage-interface OM package.

Important APIs/types/functions: No executable API. Javadoc names `OMMetadataManager` as the package role.

Control flow, state, and persistence: Documentation only.

Dependencies and integration points: Applies to `OMMetadataManager` and small OM storage support classes in the package.

Risks: Low. The terse package description gives little guidance for future maintainers but has no behavioral effect.

Test signals: No direct tests.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/interface-storage/src/main/java/org/apache/hadoop/ozone/om/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/interface-storage/src/main/proto/OmStorageProtocol.proto -->
# sources/object-store/apache-ozone/hadoop-ozone/interface-storage/src/main/proto/OmStorageProtocol.proto

Purpose: Private unstable protobuf schema for selected OM storage-layer persisted values.

Important APIs/types/functions: Generates `OzoneManagerStorageProtos` under `org.apache.hadoop.ozone.storage.proto`. Defines `OzoneAclInfo` with identity type, name, rights bytes, and ACL scope; `PersistedPrefixInfo` for prefix name, ACLs, metadata, object ID, and update ID; `PersistedUserVolumeInfo` for user-to-volume mappings and IDs; `GlobalStatsValueProto`; `FileSizeCountKeyProto`; and `SnapDiffObjectInfo`.

Control flow, state, and persistence: These messages are persisted in OM metadata tables and consumed by codecs such as `OmPrefixInfo.getCodec()`. Proto2 required/optional/repeated fields define on-disk compatibility. Metadata uses shared `hadoop.hdds.KeyValue` from `hdds.proto`.

Dependencies and integration points: Used by storage helper classes, OM metadata tables, prefix ACL handling, namespace summary/global stats, file-size count keys, and snapshot diff logic.

Risks: Storage proto changes are on-disk compatibility risks. Required fields cannot be omitted in new records. ACL rights bytes and enum mappings must remain compatible with runtime `OzoneAcl`/`IAccessAuthorizer` semantics. The interface is marked private unstable but still affects persisted OM DB content.

Test signals: `TestOmPrefixInfo`, `TestOmPrefixInfoCodec`, and related codec tests validate a subset of storage proto round trips. Broader compatibility should be covered by upgrade and metadata DB tests.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/interface-storage/src/main/proto/OmStorageProtocol.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/interface-storage/src/test/java/org/apache/hadoop/ozone/om/helpers/TestOmKeyInfoCodec.java -->
# sources/object-store/apache-ozone/hadoop-ozone/interface-storage/src/test/java/org/apache/hadoop/ozone/om/helpers/TestOmKeyInfoCodec.java

Purpose: Unit test for `OmKeyInfo.getCodec()` persisted-format behavior, especially pipeline elision and file checksum preservation.

Important APIs/types/functions: Extends `Proto2CodecTestBase<OmKeyInfo>`, returns `OmKeyInfo.getCodec()`, constructs `OmKeyInfo` with random HDDS pipeline/block locations, Ratis replication config, metadata, and an empty `MD5MD5CRC32GzipFileChecksum`. `test()` runs round trips with one and two chunks.

Control flow, state, and persistence: The test serializes an `OmKeyInfo` to persisted bytes and deserializes it. It asserts that persisted key locations do not retain pipeline objects and that file checksum survives the codec round trip.

Dependencies and integration points: Uses HDDS test pipeline utilities, `BlockID`, `OmKeyLocationInfo`, `OmKeyLocationInfoGroup`, Hadoop `FileChecksum`, and JUnit. It validates DB-storage behavior for key metadata.

Risks: Test prints serialized size to stdout, which is noisy but useful for manual observation. It focuses on latest version first location and may not cover multi-version edge cases.

Test signals: Direct positive signal for key codec pipeline stripping and checksum persistence. Inherits invalid-protobuf behavior checks from `Proto2CodecTestBase` unless overridden upstream.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/interface-storage/src/test/java/org/apache/hadoop/ozone/om/helpers/TestOmKeyInfoCodec.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/interface-storage/src/test/java/org/apache/hadoop/ozone/om/helpers/TestOmMultipartKeyInfoCodec.java -->
# sources/object-store/apache-ozone/hadoop-ozone/interface-storage/src/test/java/org/apache/hadoop/ozone/om/helpers/TestOmMultipartKeyInfoCodec.java

Purpose: Unit test for `OmMultipartKeyInfo.getCodec()` serialization and invalid-data handling.

Important APIs/types/functions: Extends `Proto2CodecTestBase<OmMultipartKeyInfo>`, returns `OmMultipartKeyInfo.getCodec()`, creates an object with random upload ID, creation time, and Ratis THREE replication config.

Control flow, state, and persistence: The test serializes a multipart key info object, deserializes it, and asserts equality. It then attempts to parse random UTF-8 bytes and expects an `IllegalArgumentException` with a specific message.

Dependencies and integration points: Uses HDDS replication proto, Ozone multipart helper, AssertJ/JUnit, and codec base tests. It validates OM multipart upload table value persistence.

Risks: Catches and prints unexpected `IOException`s instead of failing immediately in some branches, which can weaken failure clarity if an exception leaves data null in unexpected ways. The exact invalid-data message is brittle.

Test signals: Positive round-trip signal and negative malformed-input signal for multipart key codec.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/interface-storage/src/test/java/org/apache/hadoop/ozone/om/helpers/TestOmMultipartKeyInfoCodec.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/interface-storage/src/test/java/org/apache/hadoop/ozone/om/helpers/TestOmPrefixInfo.java -->
# sources/object-store/apache-ozone/hadoop-ozone/interface-storage/src/test/java/org/apache/hadoop/ozone/om/helpers/TestOmPrefixInfo.java

Purpose: Unit tests for `OmPrefixInfo` object semantics and protobuf conversion.

Important APIs/types/functions: Helpers build test `OzoneAclInfo`, metadata `KeyValue`, persisted prefix info, and runtime `OmPrefixInfo`. Tests cover `copyObject`, ACL immutability, `getFromProtobuf` with metadata/ACL, and `getProtobuf`.

Control flow, state, and persistence: The tests construct runtime and proto prefix representations, verify equality/copy isolation, assert that returned ACL list is immutable, and verify metadata/ACL counts and names across conversion.

Dependencies and integration points: Uses `OzoneAcl`, `IAccessAuthorizer`, `OzoneManagerStorageProtos.PersistedPrefixInfo`, HDDS `KeyValue`, and JUnit. It validates prefix table value conversion behavior.

Risks: Tests one ACL and one metadata entry; broader edge cases such as empty ACL rights, multiple ACL scopes, and object/update id compatibility are not fully covered.

Test signals: Strong focused signal for `OmPrefixInfo` immutability and proto conversion basics.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/interface-storage/src/test/java/org/apache/hadoop/ozone/om/helpers/TestOmPrefixInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/interface-storage/src/test/java/org/apache/hadoop/ozone/om/helpers/TestOmPrefixInfoCodec.java -->
# sources/object-store/apache-ozone/hadoop-ozone/interface-storage/src/test/java/org/apache/hadoop/ozone/om/helpers/TestOmPrefixInfoCodec.java

Purpose: Unit test for `OmPrefixInfo.getCodec()` persisted bytes round trip.

Important APIs/types/functions: Extends `Proto2CodecTestBase<OmPrefixInfo>`, returns `OmPrefixInfo.getCodec()`, creates a prefix `/user/hive/warehouse` with a user ACL and metadata `id=100`.

Control flow, state, and persistence: Serializes the `OmPrefixInfo` with the codec, deserializes it, and asserts exact object equality.

Dependencies and integration points: Uses `OzoneAcl`, ACL identity/type enums, metadata builder methods, and HDDS codec base. It validates persisted prefix table values.

Risks: Covers a single happy-path ACL and metadata record. Does not explicitly test malformed bytes beyond inherited base tests.

Test signals: Direct codec round-trip coverage for prefix metadata persistence.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/interface-storage/src/test/java/org/apache/hadoop/ozone/om/helpers/TestOmPrefixInfoCodec.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/interface-storage/src/test/java/org/apache/hadoop/ozone/om/helpers/TestRepeatedOmKeyInfoCodec.java -->
# sources/object-store/apache-ozone/hadoop-ozone/interface-storage/src/test/java/org/apache/hadoop/ozone/om/helpers/TestRepeatedOmKeyInfoCodec.java

Purpose: Unit test for `RepeatedOmKeyInfo.getCodec(boolean)`, covering pipeline stripping, compatibility with pipeline-bearing encodings, bucket ID persistence, and basic thread-safety.

Important APIs/types/functions: Extends `Proto2CodecTestBase<RepeatedOmKeyInfo>`, default codec is `getCodec(true)`. Builds `OmKeyInfo` objects with random pipelines and block locations. Tests `threadSafety`, `testWithoutPipeline`, and `testCompatibility` for one and two chunks.

Control flow, state, and persistence: Serializes deleted/repeated key info with a bucket ID. The no-pipeline codec strips pipeline data on write. Compatibility test writes with pipeline-retaining codec and reads with no-pipeline codec, asserting pipeline is preserved when present in stored bytes. Thread-safety test concurrently serializes copied objects while mutating the original repeated key list.

Dependencies and integration points: Uses HDDS pipelines, Ratis replication config, `RepeatedOmKeyInfo`, deleted-key table semantics, Guava `ThreadFactoryBuilder`, and JUnit.

Risks: Thread-safety check is timing-based and daemon-thread based, so it can miss rare races. The serialization loop is high count and could be expensive in constrained environments.

Test signals: Good signal for deleted-key codec compatibility across old/new persisted formats and concurrent copy/serialization behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/interface-storage/src/test/java/org/apache/hadoop/ozone/om/helpers/TestRepeatedOmKeyInfoCodec.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/interface-storage/src/test/java/org/apache/hadoop/ozone/om/helpers/TestS3SecretValueCodec.java -->
# sources/object-store/apache-ozone/hadoop-ozone/interface-storage/src/test/java/org/apache/hadoop/ozone/om/helpers/TestS3SecretValueCodec.java

Purpose: Unit test for `S3SecretValue.getCodec()`.

Important APIs/types/functions: Extends `Proto2CodecTestBase<S3SecretValue>`, returns `S3SecretValue.getCodec()`, creates an S3 secret with random UUID access/secret values.

Control flow, state, and persistence: Serializes the secret value, asserts bytes are non-null, deserializes it, and asserts equality.

Dependencies and integration points: Uses OM S3 secret helper, HDDS codec base, UUIDs, and JUnit. It validates S3 secret table value persistence.

Risks: Test uses random values but only one happy path; it does not verify redaction/log safety or malformed data beyond inherited base behavior.

Test signals: Direct codec round-trip signal for S3 secret values.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/interface-storage/src/test/java/org/apache/hadoop/ozone/om/helpers/TestS3SecretValueCodec.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/interface-storage/src/test/java/org/apache/hadoop/ozone/om/helpers/TestTransactionInfoCodec.java -->
# sources/object-store/apache-ozone/hadoop-ozone/interface-storage/src/test/java/org/apache/hadoop/ozone/om/helpers/TestTransactionInfoCodec.java

Purpose: Unit test for `TransactionInfo.getCodec()` persisted-format behavior.

Important APIs/types/functions: Extends `Proto2CodecTestBase<TransactionInfo>`, returns `TransactionInfo.getCodec()`. Tests round trip for `TransactionInfo.valueOf(11, 100)` and overrides malformed-buffer test.

Control flow, state, and persistence: Serializes transaction term/index-like data, deserializes it, and checks equality. Invalid UTF-8 bytes are expected to throw `IllegalArgumentException` containing `Unexpected split length`.

Dependencies and integration points: Uses HDDS `TransactionInfo`, codec base, AssertJ, and JUnit. Transaction info is central for OM DB transaction tracking/checkpoint/replay state.

Risks: Invalid-data assertion is tied to a specific parsing message. Only one positive value pair is tested.

Test signals: Direct positive and negative codec coverage for persisted transaction info.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/interface-storage/src/test/java/org/apache/hadoop/ozone/om/helpers/TestTransactionInfoCodec.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/interface-storage/src/test/java/org/apache/hadoop/ozone/om/helpers/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/interface-storage/src/test/java/org/apache/hadoop/ozone/om/helpers/package-info.java

Purpose: Package documentation for OM helper unit tests.

Important APIs/types/functions: No executable API. Javadoc says the package contains unit tests for helpers in OM.

Control flow, state, and persistence: Documentation only.

Dependencies and integration points: Applies to codec and helper tests in `org.apache.hadoop.ozone.om.helpers`.

Risks: Low documentation-only risk.

Test signals: No test logic itself; it identifies the scope of adjacent tests.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/interface-storage/src/test/java/org/apache/hadoop/ozone/om/helpers/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/interface-storage/src/test/java/org/apache/hadoop/ozone/om/lock/TestDAGLeveledResource.java -->
# sources/object-store/apache-ozone/hadoop-ozone/interface-storage/src/test/java/org/apache/hadoop/ozone/om/lock/TestDAGLeveledResource.java

Purpose: Unit test ensuring `DAGLeveledResource` remains acyclic.

Important APIs/types/functions: `ensureNoCycleInDAGLevelResource()` constructs a Guava directed graph containing every enum value and edges from each resource to its children, then asserts `Graphs.hasCycle(graph)` is false.

Control flow, state, and persistence: Test-only control flow. It models lock-order dependencies and checks graph validity; no runtime state is persisted.

Dependencies and integration points: Uses Guava graph utilities and JUnit. It protects the lock-ordering contract used by hierarchical OM resource locks.

Risks: The test only checks cycles, not semantic correctness of the order. A wrong but acyclic edge set could still allow unsafe lock behavior.

Test signals: Direct regression signal for accidental cycles in resource ordering.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/interface-storage/src/test/java/org/apache/hadoop/ozone/om/lock/TestDAGLeveledResource.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/interface-storage/src/test/java/org/apache/hadoop/ozone/om/lock/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/interface-storage/src/test/java/org/apache/hadoop/ozone/om/lock/package-info.java

Purpose: Package documentation for OM lock unit tests.

Important APIs/types/functions: No executable API. Javadoc states this package contains unit tests of OzoneManager lock.

Control flow, state, and persistence: Documentation only.

Dependencies and integration points: Applies to lock tests in `org.apache.hadoop.ozone.om.lock`.

Risks: Low documentation-only risk.

Test signals: No test logic itself; scope marker for adjacent tests.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/interface-storage/src/test/java/org/apache/hadoop/ozone/om/lock/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/mini-cluster/dev-support/findbugsExcludeFile.xml -->
# sources/object-store/apache-ozone/hadoop-ozone/mini-cluster/dev-support/findbugsExcludeFile.xml

Purpose: SpotBugs filter for the `ozone-mini-cluster` module.

Important APIs/types/functions: Defines an empty `<FindBugsFilter>`, meaning no module-specific exclusions are currently active.

Control flow, state, and persistence: Build-time static-analysis configuration only.

Dependencies and integration points: Referenced by `mini-cluster/pom.xml` in the SpotBugs plugin configuration.

Risks: Low. The empty file is useful as a stable hook for future exclusions, but adding broad exclusions later could hide test-harness bugs.

Test signals: Static-analysis configuration only.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/mini-cluster/dev-support/findbugsExcludeFile.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/mini-cluster/pom.xml -->
# sources/object-store/apache-ozone/hadoop-ozone/mini-cluster/pom.xml

Purpose: Maven descriptor for `ozone-mini-cluster`, the integration-test harness jar for creating in-process Ozone clusters.

Important APIs/types/functions: Configures dependencies needed to instantiate SCM, OM, datanodes, clients, security, Ratis, and test utilities. Skips javadoc. Runs SpotBugs with the module exclude file and disables annotation processing.

Control flow, state, and persistence: Build configuration only, but it assembles runtime dependencies for mini-cluster classes that create temporary metadata, Ratis, DB, HTTP, OM, SCM, and datanode directories during tests.

Dependencies and integration points: Depends on Guava, Commons IO/Lang, Hadoop auth/common, many HDDS modules, Ozone client/common/manager, Ratis common/server API, and SLF4J. The module is used by integration tests and HA mini-cluster variants.

Risks: This module pulls server and test utility dependencies into a test harness; version conflicts can surface as integration-test failures. Since it depends on live OM/SCM/datanode classes, configuration defaults and port allocation are sensitive.

Test signals: Mini-cluster behavior is validated by downstream integration tests that instantiate `MiniOzoneCluster`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/mini-cluster/pom.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/mini-cluster/src/main/java/org/apache/hadoop/ozone/MiniOzoneCluster.java -->
# sources/object-store/apache-ozone/hadoop-ozone/mini-cluster/src/main/java/org/apache/hadoop/ozone/MiniOzoneCluster.java

Purpose: Public test-harness interface and builder base for creating and controlling in-process Ozone clusters.

Important APIs/types/functions: Static factories `newBuilder` and `newHABuilder`; cluster accessors for config, SCM, OM, datanodes, client, SCM location client, cluster id/name/base dir; readiness waits; restart/shutdown operations for SCM, OM, and datanodes; start/stop lifecycle. Nested `Builder` configures cluster id/path, SCM configurator, datanode count/start flag, certificate/secret clients, datanode factory, and extra services. Nested `DatanodeFactory` and `Service` allow customization.

Control flow, state, and persistence: The builder creates unique cluster ids and temporary paths under `test.build.data` or `target/test/data`. `prepareForNextBuild()` clones configuration and unsets directories/HTTP base paths so the same builder can create multiple isolated clusters. Cluster lifecycle methods control in-process services and temp storage cleanup.

Dependencies and integration points: Integrates with `MiniOzoneClusterImpl`, `MiniOzoneHAClusterImpl`, OM, SCM, datanode service, Ozone client factory, Hadoop/Ozone configuration keys, certificate/secret clients, and Ratis `ExitUtils` to disable system exit in tests.

Risks: Builders are stateful and reused by provider code; missing cleanup of config keys can make clusters share directories. Datanode count zero disables SCM safemode, which is correct for fast tests but changes behavior. Callers own clients returned by `newClient()` and must close or rely on cluster shutdown.

Test signals: Downstream integration tests use this interface directly. No direct unit test in this subset.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/mini-cluster/src/main/java/org/apache/hadoop/ozone/MiniOzoneCluster.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/mini-cluster/src/main/java/org/apache/hadoop/ozone/MiniOzoneClusterImpl.java -->
# sources/object-store/apache-ozone/hadoop-ozone/mini-cluster/src/main/java/org/apache/hadoop/ozone/MiniOzoneClusterImpl.java

Purpose: Concrete implementation of `MiniOzoneCluster` that starts a single in-process SCM, OM, optional datanodes, and extra services for integration tests.

Important APIs/types/functions: Implements readiness waits, SCM/OM/datanode accessors, client creation, SCM location client creation, restart/shutdown/start operations, and service management. Static helpers stop OM/SCM/datanodes/services safely. Nested `Builder` initializes configuration, creates and starts SCM/OM, initializes SCM/OM storage, creates datanodes, configures ports/directories, and builds the cluster.

Control flow, state, and persistence: Build flow sets mini-cluster metrics/cache modes, initializes metadata directory, tunes OM Ratis timeout and SCM client retry, configures safemode minimum datanodes, starts SCM, starts OM, creates datanode services, starts extra services, injects certificate/secret clients, optionally starts datanodes, and prepares the builder for next use. Runtime readiness waits for SCM leadership, healthy datanode count, safemode exit, and open pipelines. Shutdown closes tracked clients, stops services, deletes base dir, shuts caches/metrics, and asserts RocksDB object metrics have no leaks. Persistence lives under per-cluster temp `scm` and `om` subdirectories for data, Ratis, snapshots, HTTP base, and snapshot diff DB.

Dependencies and integration points: Integrates with HDDS SCM, SCM HA utilities, Ratis server initialization, OM storage/security initialization, datanode services, Ozone client factory, metrics system, container/datanode store caches, RocksDB leak detection, GenericTestUtils port/wait utilities, and Ozone/SCM config keys.

Risks: Port allocation and localhost binding are critical; the code explicitly binds SCM servers to `127.0.0.1` to avoid `0.0.0.0` leaking into datanode connection config. Builder reuse depends on `prepareForNextBuild()` and `removeConfiguration()` correctness. Shutdown swallows exceptions after logging, so test failures can hide cleanup issues. There is duplicated `setSecretKeyClient(secretKeyClient)` in build flow, harmless but noisy. Timing-based readiness waits can be flaky under slow machines.

Test signals: This class is primarily tested by being used across integration tests. Internal leak detection (`ManagedRocksObjectMetrics.INSTANCE.assertNoLeaks`) and codec buffer leak detection provide cleanup signals during shutdown.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/mini-cluster/src/main/java/org/apache/hadoop/ozone/MiniOzoneClusterImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/mini-cluster/src/main/java/org/apache/hadoop/ozone/MiniOzoneClusterProvider.java -->
# sources/object-store/apache-ozone/hadoop-ozone/mini-cluster/src/main/java/org/apache/hadoop/ozone/MiniOzoneClusterProvider.java

Purpose: Background pre-creation and asynchronous cleanup provider for mini-clusters used by test suites that need one cluster per test.

Important APIs/types/functions: Constructor accepts a configured `MiniOzoneCluster.Builder` and a `clusterLimit`, then starts create and reap threads. `provide()` returns a pre-created ready cluster, enforcing the limit. `destroy(MiniOzoneCluster)` queues a used cluster for shutdown. `shutdown()` interrupts creation, destroys remaining clusters, marks shutdown, and joins the reaper.

Control flow, state, and persistence: The create thread builds clusters until interrupted or limit reached, waits for readiness, and puts them into a single-slot queue. The reaper polls an expired-cluster queue and calls `shutdown()` without relying on interrupts. The provider tracks created/leased clusters in a set to clean up leftovers. Persistence belongs to the clusters it creates and is deleted by their shutdown.

Dependencies and integration points: Wraps `MiniOzoneCluster.Builder` and is intended for JUnit `BeforeAll`/`BeforeEach`/`AfterEach`/`AfterAll` workflows. Uses blocking queues, background threads, and SLF4J logging.

Risks: Methods are synchronized while potentially blocking on queue operations, so misuse can serialize test setup/teardown. Creation failures in the background thread become `RuntimeException`s that may surface asynchronously. The provider always tries to keep one cluster in reserve until the limit, so clusterLimit must match expected usage. `shutdown` sets the flag after destroying remaining clusters to allow reaper drain, which depends on queue polling.

Test signals: No direct tests in this subset. Integration-test runtime behavior is the primary signal: faster per-test cluster acquisition and reliable cleanup at suite shutdown.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/mini-cluster/src/main/java/org/apache/hadoop/ozone/MiniOzoneClusterProvider.java -->
