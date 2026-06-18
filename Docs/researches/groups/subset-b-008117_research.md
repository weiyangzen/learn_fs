# subset-b-008117 Research

Grouped research for Apache Ozone security ACL tests and ozonefs common filesystem/client adapter files.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/security/TestOzoneTokenIdentifier.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/security/TestOzoneTokenIdentifier.java

Purpose: JUnit 5 coverage for `OzoneTokenIdentifier` signing, serialization, URL token encoding, and persisted codec compatibility. It verifies that token identity fields survive Hadoop `Writable` and `Token` round trips and that `TokenIdentifierCodec` can read current persisted bytes with and without an OM service id.

Important APIs and functions: `testSignToken`, `signTokenAsymmetric`, `verifyTokenAsymmetric`, `signTokenSymmetric`, `generateTestToken`, `testAsymmetricTokenPerf`, `testSymmetricTokenPerf`, `testReadWriteInProtobuf`, `testTokenSerialization`, and parameterized `testTokenPersistence`. The helper `getIdentifierInst` builds a representative identifier with owner, renewer, issue/max dates, sequence number, and OM cert serial id.

Control flow: asymmetric tests create a temporary keystore/truststore, generate an RSA key pair and certificate, sign `tokenId.getBytes()`, and verify the signature with the certificate. Serialization tests write the identifier through `DataOutputStream`, read via `readFields`, encode a Hadoop `Token` to URL form, decode it, then deserialize the embedded identifier.

State and persistence behavior: test state is local to temp directories and byte arrays. Persistence risk is centered on `OzoneTokenIdentifier.getBytes()`, protobuf/writable wire format, optional `omServiceId`, and `TokenIdentifierCodec.fromPersistedFormat`.

Dependencies and integration: Java crypto (`Signature`, `Mac`, `KeyGenerator`), Hadoop `Text` and `Token`, `KeyStoreTestUtil`, Ozone `TokenIdentifierCodec`, and JUnit temp dirs/parameterized tests. Risk areas include cryptographic algorithm availability, token equality including time fields, and backward compatibility of persisted token bytes. Test signals are positive round-trip equality checks; performance tests only log timings and do not assert thresholds.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/security/TestOzoneTokenIdentifier.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/security/acl/OzoneNativeAclTestUtil.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/security/acl/OzoneNativeAclTestUtil.java

Purpose: package-private helper for native ACL tests that mutates OM metadata tables directly. It exists because several older ACL APIs update persistent DB state without the in-memory cache path used by authorizer tests.

Important APIs and functions: `addVolumeAcl`, `addBucketAcl`, `addKeyAcl`, `setVolumeAcl`, `setBucketAcl`, `setKeyAcl`, `getVolumeAcls`, `getBucketAcls`, and `getKeyAcls`. Each setter reads the relevant `OmVolumeArgs`, `OmBucketInfo`, or `OmKeyInfo`, rebuilds it through a builder, and writes a `CacheValue` into the metadata table under a `CacheKey`.

Control flow: callers compute volume/bucket/key identifiers, retrieve table entries from `OMMetadataManager`, mutate ACL lists through builder methods, then add a cache entry at transaction index `1L`. Getter methods read directly from the relevant table and return the stored ACL list.

State and persistence behavior: this utility deliberately bypasses request handling and writes OM metadata table caches, not external filesystem state. It depends on existing rows being present; missing rows would cause null dereferences before assertions. It also assumes `BucketLayout` is passed correctly for key table selection.

Dependencies and integration: `OMMetadataManager`, HDDS table/cache APIs, `OzoneAcl`, bucket layouts, and OM helper types. Risks include stale cache/DB divergence, fixed transaction index reuse, and tests masking production paths by direct cache mutation. Test signal is indirect: native authorizer tests use these methods to set precise ACL preconditions.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/security/acl/OzoneNativeAclTestUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/security/acl/TestOzoneAdministrators.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/security/acl/TestOzoneAdministrators.java

Purpose: verifies `OzoneNativeAuthorizer` administrator and read-only administrator shortcuts for volume, bucket, and root volume listing operations.

Important APIs and functions: `testCreateVolume`, `testBucketOperation`, `testListAllVolume`, helper predicate factories backed by `OzoneAdmins`, `testAdminOperations`, `testGroupAdminOperations`, `getUserRequestContext`, `getTestVolumeobj`, and `getTestBucketobj`.

Control flow: tests create UGI test users/groups, build `OzoneObjInfo` instances, install admin/read-only-admin predicates on a shared `OzoneNativeAuthorizer`, then call `checkAccess` with `CREATE`, `LIST`, `READ`, `READ_ACL`, or `WRITE`. Positive cases cover wildcard admins, matching users, matching groups, and read-only admin read operations. Negative cases cover empty/mismatched admin lists and read-only admins attempting create.

State and persistence behavior: no OM metadata managers are configured, so some non-shortcut write paths intentionally fall through to null manager access and assert `NullPointerException`. The important state is the mutable authorizer admin predicate fields and global UGI test registry, reset in `finally`.

Dependencies and integration: `OzoneAdmins`, `UserGroupInformation`, `OzoneObjInfo`, `RequestContext`, and `OMException`. Risks include shared static `nativeAuthorizer` retaining predicates between tests and assertions depending on null managers. Test signals explicitly document precedence: full admins bypass ACL checks, read-only admins only bypass read-like operations.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/security/acl/TestOzoneAdministrators.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/security/acl/TestOzoneAuthorizerFactory.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/security/acl/TestOzoneAuthorizerFactory.java

Purpose: validates `OzoneAuthorizerFactory` class selection for OM and snapshot authorizers under ACL-disabled, native, third-party, and shared tmp-dir configurations.

Important APIs and functions: `aclsDisabled`, parameterized `nativeAuthorizer`, `thirdPartyAuthorizer`, parameterized `sharedTmpDirAuthorizer`, `assertSameInstanceForSnapshot`, `assertNewInstanceForSnapshot`, `configureOM`, `omMock`, and nested `MockNativeAuthorizer`/`MockThirdPartyAuthorizer`.

Control flow: tests build an `OzoneConfiguration`, mock an `OzoneManager`, set `OZONE_ACL_ENABLED`, `OZONE_ACL_AUTHORIZER_CLASS`, and optionally `OZONE_OM_ENABLE_OFS_SHARED_TMP_DIR`, then call `OzoneAuthorizerFactory.forOM`. Snapshot behavior is tested by stubbing `om.getAccessAuthorizer()` and calling `forSnapshot`.

State and persistence behavior: no persistence; all state is in mocked configuration and mocked OM getters. Snapshot behavior is the notable state rule: native authorizers get a new instance for snapshot access, while disabled and third-party authorizers reuse the OM instance.

Dependencies and integration: Ozone config keys, Mockito, JUnit parameter sources, `SharedTmpDirAuthorizer`, and factory code. Risks include factory behavior being sensitive to class inheritance from `OzoneNativeAuthorizer` and shared tmp-dir wrapping replacing a third-party authorizer when enabled. Test signal is type identity and instance identity assertions.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/security/acl/TestOzoneAuthorizerFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/security/acl/TestOzoneBlacklist.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/security/acl/TestOzoneBlacklist.java

Purpose: tests blacklist and read-blacklist precedence in `OzoneNativeAuthorizer`, including interaction with admin shortcuts.

Important APIs and functions: `testCreateVolume`, `testBucketOperation`, `testListAllVolume`, `testBlacklistedUserOperations`, `testBlacklistedGroupOperations`, `getUserRequestContext`, `getTestVolumeobj`, and `getTestBucketobj`.

Control flow: each test creates UGI test users/groups, sets admin or blacklist structures on a fresh authorizer, and calls `checkAccess`. Full blacklist entries deny matching users/groups even after admin access was granted. Read blacklist denies `LIST`, `READ`, and `READ_ACL` but leaves non-read operations to normal authorizer behavior. The bucket `WRITE` case asserts fall-through to null manager as a deliberate signal.

State and persistence behavior: no metadata persistence; mutable state lives in `OzoneNativeAuthorizer` admin, full blacklist, and read blacklist fields. UGI test state is reset after each test.

Dependencies and integration: `OzoneBlacklist`, `OzoneAdmins`, `UserGroupInformation`, `RequestContext`, and Ozone object builders. Risks include ordering bugs where admin checks might wrongly bypass blacklist checks or read blacklist might block writes. Test signals assert blacklist denial has higher precedence than admin allow for matching users/groups.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/security/acl/TestOzoneBlacklist.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/security/acl/TestOzoneNativeAuthorizer.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/security/acl/TestOzoneNativeAuthorizer.java

Purpose: broad parameterized coverage for native ACL evaluation across volume, bucket, key, and prefix resources.

Important APIs and functions: `data`, `createAll`, static `setup`, `createVolume`, `createBucket`, `createKey`, four parameterized `testCheckAccessFor*` methods, ACL mutation helpers, `resetAclsAndValidateAccess`, `getAclName`, `validateAll`, and `validateNone`.

Control flow: setup creates `OmTestManagers`, managers, write client, metadata manager, native authorizer, admin/test UGIs, and configures native authorizer class. Each parameter row creates a volume, bucket, and key or directory using randomized names, sets parent volume/bucket ACLs for child objects, then repeatedly resets object ACLs to each `ACLType`, checks authorizer decisions, adds additional ACLs, and verifies unavailable rights remain denied.

State and persistence behavior: test objects are persisted in OM test metadata; volume/bucket cache entries are mutated through `OzoneNativeAclTestUtil` while key/prefix ACLs go through `OzoneManagerProtocol`. Random names avoid collisions. Special cases skip `WRITE` and sometimes `CREATE` because those require open-key or non-existing-object semantics.

Dependencies and integration: `OmTestManagers`, OM managers, `OzoneManagerProtocol`, `OzoneAclUtil`, `OzoneObjInfo`, `RequestContext`, UGI, and AssertJ/JUnit parameterization. Risks include cache-vs-DB inconsistency, randomized identity type additions, and the `validateAll` loop building one context before changing rights. Test signals emphasize `ALL`, `NONE`, user/group/world/anonymous identities, parent ACL requirements, and admin allowance for volume create.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/security/acl/TestOzoneNativeAuthorizer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/security/acl/TestOzoneObj.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/security/acl/TestOzoneObj.java

Purpose: focused unit test for `OzoneObjInfo` builder path-viewer behavior when volume, bucket, and key fields are present or null.

Important APIs and functions: `testGetPathViewer` and helper `getBuilder`. The helper creates a mocked `KeyManager`, an `OzonePrefixPathImpl`, and returns a builder with resource type `VOLUME`, store type `OZONE`, optional volume/bucket/key names, and the prefix path viewer.

Control flow: builds object info for complete, all-null, and volume-only path inputs, asserting expected volume name and non-null prefix path viewer each time.

State and persistence behavior: no persistence; all state is in-memory builder fields and a Mockito mock. The test guards builder behavior around nullable path components.

Dependencies and integration: `OzoneObjInfo`, `OzonePrefixPathImpl`, `KeyManager`, Mockito, and JUnit assertions. Risks are modest: this only checks non-null viewer plumbing and does not verify path traversal behavior. Test signal is that `OzoneObjInfo` should retain the provided viewer even for partially specified objects.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/security/acl/TestOzoneObj.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/security/acl/TestParentAcl.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/security/acl/TestParentAcl.java

Purpose: verifies native authorizer parent ACL requirements when accessing buckets and keys. It confirms child ACL alone is insufficient and access requires suitable parent or grandparent rights.

Important APIs and functions: static `setup`, `testKeyAcl`, `testBucketAcl`, `testParentChild`, `resetAcl`, ACL mutation helpers backed by `OzoneNativeAclTestUtil`, and object creation helpers. `testKeyAcl` is marked `@Unhealthy("HDDS-6335")`, a significant signal that key-path parent ACL behavior is known problematic.

Control flow: setup creates an OM test environment and native authorizer. Tests create randomized volumes/buckets/keys, snapshot original ACLs, then run `testParentChild` with combinations like parent `READ` plus child `WRITE_ACL`, `DELETE`, `READ_ACL`, `LIST`, and parent `WRITE` plus child `CREATE`/`WRITE`. For buckets, bucket ACL alone denies until volume ACL is added. For keys, key ACL and bucket ACL deny until volume ACL is also added.

State and persistence behavior: OM metadata tables hold volume, bucket, and key ACL state. The test repeatedly resets ACLs to avoid cross-case leakage. There is an apparent risk in `testKeyAcl`: `originalKeyAcls` is loaded from bucket ACLs, not key ACLs, which may weaken reset fidelity.

Dependencies and integration: `OmTestManagers`, OM managers, write client, `OzoneAcl`, `BucketLayout.DEFAULT`, `OzoneManagerProtocol`, UGI, and `@Unhealthy`. Risks include known HDDS-6335 instability, direct cache mutation, and parent ACL semantics diverging between bucket and key code paths.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/security/acl/TestParentAcl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/security/acl/TestRequestContext.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/security/acl/TestRequestContext.java

Purpose: validates `RequestContext` builder defaults, optional policy/S3 fields, recursive access flag, and `toBuilder` copy/modify behavior.

Important APIs and functions: `testRecursiveAccessFlag`, `testSessionPolicy`, `testToBuilderWithNoModifications`, and `testToBuilderWithModifications`.

Control flow: tests build default contexts, toggle `setRecursiveAccessCheck`, set session policy JSON strings, build a fully populated context, call `toBuilder`, and compare every preserved field. Modification tests create a second context from `toBuilder` with changed host, UGI, ACL rights, owner, recursive flag, session policy, and S3 action while asserting the original remains unchanged.

State and persistence behavior: immutable built contexts are the central state. No external persistence occurs. The test verifies copied fields include host, IP default, client UGI, service id, ACL identity/type, owner, recursive flag, session policy, and S3 action.

Dependencies and integration: `UserGroupInformation`, `IAccessAuthorizer` enums, JUnit assertions. Risks include accidental shallow mutation in builder reuse or future fields omitted from `toBuilder`. Test signal is strong for builder immutability and field preservation but does not parse or validate policy JSON.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/security/acl/TestRequestContext.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/security/acl/TestSharedTmpDirAuthorizer.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/security/acl/TestSharedTmpDirAuthorizer.java

Purpose: verifies dispatch behavior of `SharedTmpDirAuthorizer`, ensuring shared tmp bucket paths use the native authorizer while other paths use the configured delegate authorizer.

Important APIs and functions: static `setUp`, `ozoneObjArgs`, and parameterized `testCheckAccess`.

Control flow: setup creates Mockito mocks for `OzoneNativeAuthorizer` and a mock third-party authorizer, then wraps them. The parameterized test builds a key `OzoneObjInfo` for four volume/bucket combinations and calls `checkAccess`. It verifies `nativeAuthorizer.checkAccess` only for `volume=tmp,bucket=tmp`; all other combinations verify delegate `authorizer.checkAccess`.

State and persistence behavior: no persisted state; only mock invocation history. The static shared authorizer is reused across parameter rows, so Mockito call accumulation is a minor maintenance risk if verification becomes stricter.

Dependencies and integration: `SharedTmpDirAuthorizer`, `OzoneObjInfo`, `RequestContext`, Mockito, JUnit parameterization. Risks include hard-coded tmp volume/bucket matching and lack of assertion on returned boolean. Test signal is routing, not authorization result semantics.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/security/acl/TestSharedTmpDirAuthorizer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/security/acl/TestVolumeOwner.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/security/acl/TestVolumeOwner.java

Purpose: tests volume-owner authorization rules in `OzoneNativeAuthorizer` for volume, bucket, and key operations.

Important APIs and functions: static `setup`, `prepareTestVols`, `prepareTestBuckets`, `prepareTestKeys`, `testVolumeOps`, `testBucketOps`, `testKeyOps`, `getUserRequestContext`, object-name helpers, object builders, and `getAclsToTest`.

Control flow: setup creates two volumes with distinct owners, two buckets under each, and two keys under each bucket. One key gets `ALL` ACLs for `testUgi`; the other gets `NONE`, allowing owner behavior to be tested independent of direct key ACLs. Volume tests assert admins can create, non-admin non-owners cannot create, volume owners still cannot perform admin `CREATE`, and owners can perform all non-`CREATE`/non-`NONE` operations. Bucket/key tests assert matching volume owner is allowed without object ACLs while non-owner is denied.

State and persistence behavior: OM test metadata persists volumes, buckets, and committed keys. `RequestContext.ownerName` is the main owner signal; the local `isOwner` parameter is unused and only expresses intent in call sites.

Dependencies and integration: `OmTestManagers`, native authorizer managers, `OzoneAclUtil`, `StandaloneReplicationConfig`, `OzoneManagerProtocol`, UGI, and JUnit. Risks include conflating request-supplied ownerName with looked-up volume ownership, and the unused helper parameter hiding assertion intent. Test signals clarify that volume owners have broad non-admin access to child buckets/keys.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/security/acl/TestVolumeOwner.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/security/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/security/package-info.java

Purpose: package-level documentation marker for Ozone security tests.

Important APIs and functions: no executable APIs or functions; it only declares `package org.apache.hadoop.ozone.security` with a short Javadoc comment.

Control flow: none.

State and persistence behavior: none.

Dependencies and integration: participates in Java package documentation and source organization for test classes under `org.apache.hadoop.ozone.security`. Risk is minimal; test signal is only organizational.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/security/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/pom.xml -->
# sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/pom.xml

Purpose: Maven module descriptor for `ozone-filesystem-common`, a jar containing shared Ozone filesystem implementations and client adapters.

Important APIs and functions: Maven coordinates inherit from `hdds-hadoop-dependency-client` version `2.3.0-SNAPSHOT`, artifact id `ozone-filesystem-common`, packaging `jar`, UTF-8 source encoding, dependencies, and compiler plugin configuration.

Control flow: build-time only. Maven resolves dependency versions through the parent, compiles module sources, and disables annotation processing with `maven-compiler-plugin` `<proc>none</proc>`.

State and persistence behavior: no runtime persistence, but dependency selection controls the runtime ABI available to filesystem code. Dependencies include Guava, OpenTelemetry API, Jakarta annotations, Apache Commons, Hadoop common/HDFS client, HttpClient, Ozone client/common/HDDS modules, Ratis common, and SLF4J.

Dependencies and integration: integrates the filesystem common jar with Hadoop FS APIs and Ozone client/HDDS protocol layers. Risks include parent-managed dependency drift, Hadoop compatibility constraints, and annotation processing being disabled. Test/build signals are Maven compile and downstream module tests that depend on these classes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/pom.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/BasicKeyInfo.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/BasicKeyInfo.java

Purpose: minimal Ozone key metadata DTO used by filesystem adapter iterators without exposing broader Ozone client classes across classloader boundaries.

Important APIs and functions: constructor `BasicKeyInfo(String name, long modificationTime, long size)` and getters `getName`, `getModificationTime`, and `getDataSize`.

Control flow: construction assigns immutable-by-convention private fields; getters return stored values. There are no setters, validation, equality, or serialization methods.

State and persistence behavior: in-memory value object only. It carries key name, modification time, and data size from `OzoneKey` into listing/rename/delete logic.

Dependencies and integration: intentionally depends only on primitive Java types and `String`. Integrated by `BasicOzoneClientAdapterImpl.IteratorAdapter`, `BasicRootedOzoneClientAdapterImpl.IteratorAdapter`, and `BasicOzoneFileSystem.OzoneListingIterator`. Risks are low, but mutable non-final fields and lack of null/negative validation leave correctness to callers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/BasicKeyInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/BasicOzFs.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/BasicOzFs.java

Purpose: Hadoop `AbstractFileSystem` bridge for the `o3fs` scheme that delegates FileContext-style calls to `BasicOzoneFileSystem`.

Important APIs and functions: constructor `BasicOzFs(URI, Configuration)`, `getUriDefaultPort`, and overridden `finalize`.

Control flow: construction calls `DelegateToFileSystem` with the provided URI, a new `BasicOzoneFileSystem`, the Hadoop configuration, Ozone URI scheme, and authority handling flag `false`. Default port returns `-1` because Ozone FS URIs do not have a required default port. Finalization closes `fsImpl` then delegates to `super.finalize`.

State and persistence behavior: no persistence; state is held by `DelegateToFileSystem` and the wrapped filesystem. Resource cleanup is tied to finalization as a fallback.

Dependencies and integration: Hadoop `DelegateToFileSystem`, `Configuration`, Ozone constants, HDDS audience/stability annotations. Risks include reliance on deprecated/finalization cleanup and constructor-time creation of a concrete basic filesystem. Test signals would come from Hadoop FileContext integration rather than this class directly.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/BasicOzFs.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/BasicOzoneClientAdapterImpl.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/BasicOzoneClientAdapterImpl.java

Purpose: bucket-scoped `OzoneClientAdapter` implementation for `BasicOzoneFileSystem`. It binds one volume and bucket, exposes Hadoop filesystem operations over Ozone client APIs, and intentionally omits statistics support.

Important APIs and functions: constructors for default/configured/host-port clients, `readFile`, `createFile`, `createStreamFile`, `renameKey`, `createDirectory`, `deleteObject(s)`, `getFileStatus`, `listKeys`, `listStatus`, delegation token and key provider methods, file checksum, snapshot create/rename/delete/diff, lease recovery, `finalizeBlock`, `setTimes`, `isFileClosed`, and `setSafeMode`.

Control flow: construction validates HA service-id/port combinations, creates an RPC `OzoneClient`, resolves volume/bucket, refreshes bucket replication config on a timer, validates link bucket layout, and closes the client if initialization fails. File IO delegates to `OzoneBucket`, translating common `OMException` result codes to Hadoop exceptions. Listing converts full or light Ozone statuses to `FileStatusAdapter`. Snapshot diff creates temporary snapshots when either side is the active filesystem, polls until jobs are `DONE`, aggregates paged reports, then deletes temporary snapshots.

State and persistence behavior: persistent mutations happen through Ozone OM/object-store calls: file creation, directory creation, deletes, renames, snapshots, lease recovery, block finalization, times, and safe mode. Local state caches client, object store, volume, bucket, replication configs, security flag, configured datanode port, config, and clock.

Dependencies and integration: Ozone client, OM helpers, HDDS replication/pipeline/container calls, Hadoop `FileStatus`/checksum/token abstractions, `OzoneTokenIdentifier`, and SLF4J. Risks include stale bucket replication config, exception swallowing in delete returning false, unsupported EC/non-replicated finalize fallback, blocking snapshot diff polling, and no-op counters. Test signals should cover exception translation, replication refresh, snapshot temp cleanup, block location host/port mapping, and lease recovery errors.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/BasicOzoneClientAdapterImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/BasicOzoneFileSystem.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/BasicOzoneFileSystem.java

Purpose: minimal Hadoop `FileSystem` implementation for `o3fs`, built on `OzoneClientAdapter`. It translates Hadoop paths and operations into bucket-scoped Ozone key operations.

Important APIs and functions: `initialize`, `createAdapter`, `open`, `create`, `createNonRecursive`, output stream selection, `rename`, `renameFSO`, delete helpers and iterators, `listStatus`, working/home/trash methods, `mkdirs`, `getFileStatus`, block locations, delegation token/canonical service, checksums, snapshots, `setTimes`, `OzoneFileStatusIterator`, `listFileStatus`, `pathToKey`, `OzoneListingIterator`, and `setSafeModeUtil`.

Control flow: initialization parses authority as `bucket.volume[.om-host[:port]|.serviceId]`, configures listing page size, streaming threshold, hsync support, creates an adapter, and sets `/user/<user>` working dir. Reads/writes convert paths to keys. Writes may use `SelectorOutputStream` to choose normal or Ratis data stream output after a byte threshold. Non-FSO rename validates source/destination status and iterates/prefix-renames keys; FSO rename delegates one key rename. Deletes either delegate directly for FSO buckets or iterate key batches for legacy layouts. Listings page through adapter results and handle duplicate continuation entries.

State and persistence behavior: local state includes URI, username, working dir, adapter, listing page size, hsync and streaming settings. Persistent effects occur through adapter creates, deletes, renames, directory markers, snapshots, setTimes, and safe mode. Fake parent directories are recreated after successful legacy delete/rename when needed.

Dependencies and integration: Hadoop `FileSystem`, FSData streams, permissions, `OzoneFSUtils`, `OzoneClientUtils`, Ozone config keys, `FileStatusAdapter`, and Ozone adapter interface. Risks include URI parsing rigidity, non-atomic batch rename/delete for legacy keys, fake-directory marker races, duplicate handling in paged listings, append unsupported, and output stream selection changing based on written byte threshold. Test signals should stress path parsing, root operations, FSO vs legacy behavior, pagination, snapshot path construction, and trash roots.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/BasicOzoneFileSystem.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/BasicRootedOzoneClientAdapterImpl.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/BasicRootedOzoneClientAdapterImpl.java

Purpose: rooted/OFS `OzoneClientAdapter` implementation that interprets full OFS paths containing volume, bucket, key, and snapshot components. It supports root/volume/bucket listing and can create missing volumes/buckets for recursive writes.

Important APIs and functions: constructors, `initDefaultFsBucketLayout`, `getBucket`, file create/read/stream create, `rename`, `createDirectory`, `deleteObject(s)`, root/volume/bucket/snapshot `getFileStatus` and `listStatus`, trash-root discovery, delegation token/key provider/canonical service, status conversion helpers, checksum, snapshot create/rename/delete/diff, `isFileClosed`, lease recovery, `finalizeBlock`, `setTimes`, and `setSafeMode`.

Control flow: construction creates RPC client under a temporarily cleared context classloader, validates HA addressing, initializes security and client replication config, caches proxy/object store, and validates default OFS bucket layout as FSO or legacy only. `getBucket` can create missing volume/bucket for write paths and handles races with already-exists errors. Path operations use `OFSPath`; root and volume status/listing are synthetic, bucket/key operations delegate to `OzoneBucket`, and snapshot listings use `objectStore.listSnapshot`. Batch deletes require all paths in the same bucket.

State and persistence behavior: local state includes client, object store, proxy, replication config, security flag, configured DN port, default OFS bucket layout, config, and client config. Persistent mutations include volume/bucket creation, key creation/deletion/rename, snapshots, lease recovery, block finalization, setTimes, and safe mode. Root/volume/bucket `FileStatusAdapter`s are synthesized from Ozone metadata.

Dependencies and integration: `OFSPath`, Ozone object store/client/proxy APIs, Hadoop `FileStatus`, UGI, HDDS replication and container calls, snapshot classes, and Ozone config. Risks include cross-bucket rename/delete refusal, automatic volume/bucket creation under recursive writes, orphan link bucket empty-list behavior, root listing cost, snapshot temp cleanup, context-classloader manipulation, and finalize fallback only supporting replicated configs. Test signals should cover root/volume/bucket path classification, pagination start paths with/without authority, snapshot indicator handling, same-bucket guards, and ACL behavior for implicit creation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/BasicRootedOzoneClientAdapterImpl.java -->
