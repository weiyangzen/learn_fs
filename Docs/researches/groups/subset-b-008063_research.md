# Research group subset-b-008063

Grouped research for Apache Ozone common OM utility, helper, protocol, security, and snapshot test sources. Each section is bounded for reconciliation into the source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/web/utils/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/web/utils/package-info.java

Purpose: declares and documents the `org.apache.hadoop.ozone.web.utils` package as "Web utils." It has no executable code, exported classes, control flow, mutable state, or persistence behavior.

Important APIs/types/functions: the only Java element is the package declaration. Its effect is package-level Javadoc for any generated API docs and static analysis.

Dependencies and integration points: depends only on standard Java package-info semantics. It anchors documentation for web utility classes that may live in the same package elsewhere in the module.

Risks and test signals: risk is documentation drift rather than runtime behavior. No direct tests are present or needed for this file; build and Javadoc/package compilation are the relevant signals.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/web/utils/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/TestOmUtils.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/TestOmUtils.java

Purpose: unit tests for `OmUtils`, covering OM directory creation, HA service discovery, OM address parsing, listener-node filtering, transaction/object ID epoch encoding, and follower-read request classification.

Important APIs/types/functions: exercises `createOMDir`, `getOmHAAddressesById`, `getOzoneManagerServiceId`, `getOmHostsFromConfig`, `getOmAddress`, `getListenerOMNodeIds`, `getActiveNonListenerOMNodeIds`, `getOMEpoch`, `addEpochToTxId`, `getObjectIdFromTxId`, `shouldSendToFollower`, and `isReadOnly`. It also asserts `MAX_TRXN_ID` equals `2^54 - 2`.

Control flow and state: tests build temporary directories and in-memory `OzoneConfiguration` instances. HA service ID selection prefers `ozone.om.internal.service.id`, rejects mismatches and ambiguous multi-service config, and returns null for non-HA. Object IDs encode epoch in the top two bits and transaction ID shifted by eight bits.

Dependencies and integration points: integrates with `OMConfigKeys`, `ConfUtils`, `OzoneManagerProtocolProtos.OMRequest`, `GenericTestUtils.LogCapturer`, and JUnit temp directories. Follower-read tests iterate every protobuf command enum to ensure new commands are categorized.

Risks and test signals: catches filesystem permission regressions, HA config ambiguity, listener OM inclusion bugs, transaction ID overflow, and unsafe follower routing. The enum coverage test is a strong signal for future protobuf additions because uncategorized command types log an error and fail the test.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/TestOmUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/TestOzoneAcls.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/TestOzoneAcls.java

Purpose: validates parsing and representation of `OzoneAcl` strings for user, group, world, and anonymous identities, including rights bitsets and ACL scope suffixes.

Important APIs/types/functions: covers `OzoneAcl.parseAcl`, `OzoneAcl.parseAcls`, `isSet`, `getAclList`, `getName`, `getType`, and `getAclScope`. It checks rights `READ`, `WRITE`, `DELETE`, `LIST`, `NONE`, `CREATE`, `READ_ACL`, `WRITE_ACL`, and `ALL`.

Control flow and state: `testAclParse` drives a validity matrix of accepted and rejected strings. Later tests inspect parsed ACL objects and comma-separated ACL lists. World and anonymous identities normalize names such as `WORLD` and `ANONYMOUS`; scope strings like `[DEFAULT]` and `[ACCESS]` are decoded into enum values.

Dependencies and integration points: depends on `IAccessAuthorizer` identity and ACL enums and AssertJ/JUnit assertions. These parsing contracts feed OM ACL persistence, authorization checks, and CLI/API ACL input handling.

Risks and test signals: protects against accepting malformed identity prefixes, empty names where not allowed, invalid right characters, and losing scope metadata. Notably some strings containing extra valid rights plus unknown-looking characters are expected to parse only when all characters map to known ACL rights, so rights alphabet changes must be deliberate.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/TestOzoneAcls.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/client/checksum/TestCrcComposer.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/client/checksum/TestCrcComposer.java

Purpose: tests `CrcComposer` composition of per-chunk CRCs into either a single unstriped CRC or striped cell CRCs.

Important APIs/types/functions: uses `CrcComposer.newCrcComposer`, `newStripedCrcComposer`, `update(byte[], ...)`, `update(DataInputStream, ...)`, `update(int, ...)`, `digest`, and `CrcUtil.readInt/writeInt`. It uses Hadoop `DataChecksum.Type.CRC32C`.

Control flow and state: setup creates deterministic random data, full-data CRC, eight chunk CRCs of size 10 with a partial final chunk, and four cell CRCs of size 20 with a partial final cell. Tests feed CRCs through byte arrays, streams, and single-int updates. Striped tests verify chunk CRCs aggregate to expected cell CRC byte arrays.

Dependencies and integration points: integrates with Hadoop checksum math and Ozone client checksum storage formats. Multi-stage tests compose chunk CRCs into cells, then compose cells into the full object CRC.

Risks and test signals: detects incorrect final-part length handling, stripe boundary crossings, and byte-array CRC-length misalignment. The incorrect-chunk-size test proves callers must pass the real covered data length for the final CRC.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/client/checksum/TestCrcComposer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/client/checksum/TestCrcUtil.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/client/checksum/TestCrcUtil.java

Purpose: validates low-level CRC utility serialization, formatting, and Galois-field multiplication used by Ozone checksum composition.

Important APIs/types/functions: covers `CrcUtil.intToBytes`, `writeInt`, `readInt`, `toSingleCrcString`, `toMultiCrcString`, and `multiplyMod`. It also exposes shared helper `assertContains` for checksum tests and contains a nested benchmark driver.

Control flow and state: tests assert big-endian integer serialization and string formatting for zero, one, and multiple CRC values. `testMultiplyMod` generates 10 million random pairs for CRC32 and CRC32C, computes expected values via a reference `galoisFieldMultiply`, and compares optimized table multiplication.

Dependencies and integration points: uses Hadoop `DataChecksum.Type` and Hadoop `org.apache.hadoop.util.CrcUtil` polynomials/constants. The multiplication routine underpins `CrcComposer` and therefore checksum verification across chunk and stripe boundaries.

Risks and test signals: protects against endian changes, malformed CRC byte-array length acceptance, and arithmetic regressions in CRC polynomial multiplication. The random large-loop test is strong but can be expensive and timing-sensitive; timeout is set to 10 seconds for the test class.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/client/checksum/TestCrcUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/client/io/TestSelectorOutputStream.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/client/io/TestSelectorOutputStream.java

Purpose: tests `SelectorOutputStream`, which delays selecting one of two output streams until write volume crosses a threshold.

Important APIs/types/functions: exercises `write`, `flush`, `close`, `hflush`, and `hsync` on `SelectorOutputStream`. The test defines an `Op` enum to dispatch operations and a `SyncableOutputStreamForTesting` implementing Hadoop `Syncable`.

Control flow and state: `runTestSelector` uses memoized suppliers for below-threshold and above-threshold streams. Writes select the above-threshold stream immediately only when bytes written exceed the threshold; below-threshold selection is delayed until a terminal or flush operation needs it.

Dependencies and integration points: depends on Ratis `MemoizedSupplier` and checked functional interfaces, Hadoop `Syncable`, and Java `ByteArrayOutputStream`. It represents client write-path selection between small-object and large-object stream implementations.

Risks and test signals: catches premature stream creation, off-by-one threshold mistakes, and illegal hflush/hsync on non-`Syncable` delegates. Threshold cases at 2, 10, and 20 bytes for threshold 10 check below, exact, and above behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/client/io/TestSelectorOutputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/TestOmConfig.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/TestOmConfig.java

Purpose: validates `OmConfig` binding from `OzoneConfiguration`, invalid value handling, copying, and field-wise updates.

Important APIs/types/functions: exercises `conf.getObject(OmConfig.class)`, `OmConfig.Keys.SERVER_LIST_MAX_SIZE`, `OmConfig.Keys.USER_MAX_VOLUME`, `copy`, `setFrom`, and getters/setters for filesystem-path, key-name check, max list size, and max user volume count.

Control flow and state: tests create mutable in-memory configurations, set valid and invalid scalar values, and compare resulting objects. Invalid list sizes `-1` and `0` are overridden with defaults, while invalid user max volume throws `IllegalArgumentException`.

Dependencies and integration points: integrates with HDDS typed configuration binding through `MutableConfigurationSource` and `OzoneConfiguration`. These settings affect OM server list response limits and namespace/user behavior.

Risks and test signals: protects against invalid configuration reaching runtime and against shallow/incomplete copying when OM config is propagated or refreshed. Any new mutable `OmConfig` field should be added to `assertConfigEquals`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/TestOmConfig.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/exceptions/TestResultCodes.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/exceptions/TestResultCodes.java

Purpose: verifies ordinal and name alignment between `OMException.ResultCodes` and protobuf `OzoneManagerProtocolProtos.Status`.

Important APIs/types/functions: iterates `ResultCodes.values()` and `Status.values()`, checks equal enum counts, matching names by ordinal, and round-trip conversion through protobuf ordinal.

Control flow and state: no mutable state. The test loops all enum entries and fails on length mismatch, name mismatch, or conversion mismatch.

Dependencies and integration points: ties Java exception result codes to wire-level OM response statuses. Many protocol paths rely on ordinal compatibility when converting status values.

Risks and test signals: catches dangerous enum insertion/reordering in either Java or protobuf definitions. This is a persistence and compatibility risk because status ordinals may be serialized or mapped across client/server boundaries.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/exceptions/TestResultCodes.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/ha/TestHadoopRpcOMFollowerReadFailoverProxyProvider.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/ha/TestHadoopRpcOMFollowerReadFailoverProxyProvider.java

Purpose: tests follower-read behavior layered on top of `HadoopRpcOMFailoverProxyProvider` and Hadoop retry proxy mechanics.

Important APIs/types/functions: exercises `HadoopRpcOMFollowerReadFailoverProxyProvider`, `RetryProxy.create`, `getRetryPolicy`, `getProxy`, `getCurrentProxy`, `getLastProxy`, and `isUseFollowerRead`. It builds real `OMRequest` messages for `CreateKey` writes and `GetKeyInfo` reads.

Control flow and state: `setupProxyProvider` creates sorted mock OM proxies whose behavior is controlled by volatile flags in `OMAnswer`. Writes must route to the leader and leave the follower-read current proxy unchanged. Reads can use followers or leaders, fall back around unreachable followers, disable follower reads when followers report unsupported, and retry on `ReadIndexException` or `ReadException`.

Dependencies and integration points: uses Mockito, Hadoop `RetryInvocationHandler`, protobuf OM request/response types, Ratis read exceptions, and `RemoteException` wrapping for OM leader/follower errors. It also customizes proxy initialization to keep OM order deterministic.

Risks and test signals: protects against write requests accidentally sent to followers, follower-read mode sticking when unsupported, null/short invocation argument crashes, object methods selecting network proxies, and retry exhaustion when all OMs are unreachable. Threaded leader-ready tests verify retries wait until a leader becomes ready.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/ha/TestHadoopRpcOMFollowerReadFailoverProxyProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/ha/TestOMFailoverProxyProvider.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/ha/TestOMFailoverProxyProvider.java

Purpose: verifies core Hadoop RPC OM failover provider behavior for retry wait timing, proxy ordering, listener-node exclusion, and delegation-token service names.

Important APIs/types/functions: covers `HadoopRpcOMFailoverProxyProvider`, `selectNextOmProxy`, `performFailover`, `setNextOmProxy`, `getWaitTime`, `getOMProxyMap`, `OMProxyInfo.OrderedMap`, and `getCurrentProxyDelegationToken`.

Control flow and state: setup creates a three-node OM HA config. Tests alternate between failover to next nodes and same-node failover, verifying wait time resets or increases by `ozone.client.wait.between.retries.millis`. Listener nodes configured through `OZONE_OM_LISTENER_NODES_KEY` are omitted from the active proxy map.

Dependencies and integration points: uses `OzoneConfiguration`, `ConfUtils`, OM config keys, `UserGroupInformation`, and Hadoop `Text` token service names. The ordered map test shuffles input lists to prove iteration order follows constructor list order.

Risks and test signals: catches retry backoff regressions, inclusion of listener OMs in write/read proxy sets, unstable token service strings, and unordered proxy maps that could destabilize failover behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/ha/TestOMFailoverProxyProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/helpers/OldSnapshotDiffJobCodecForTesting.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/helpers/OldSnapshotDiffJobCodecForTesting.java

Purpose: provides a test-only implementation of the old JSON `Codec<SnapshotDiffJob>` for compatibility testing.

Important APIs/types/functions: implements `getTypeClass`, `toPersistedFormatImpl`, `fromPersistedFormatImpl`, and `copyObject`. Serialization uses Jackson `ObjectMapper` configured to omit nulls and ignore unknown properties.

Control flow and state: stateless aside from a static mapper. Encoding writes `SnapshotDiffJob` as JSON bytes; decoding reads JSON bytes back. `copyObject` returns the same object and explicitly is not a deep copy.

Dependencies and integration points: used by `TestOmSnapshotDiffJobCodec` to generate legacy persisted data so the current `SnapshotDiffJob.codec()` can prove backward compatibility.

Risks and test signals: the main risk is divergence from the historical codec shape. Since this is a compatibility fixture, changes should be avoided unless the legacy format definition itself was wrong.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/helpers/OldSnapshotDiffJobCodecForTesting.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/helpers/TestAclListBuilder.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/helpers/TestAclListBuilder.java

Purpose: tests `AclListBuilder`, a mutation-tracking helper for ACL lists that preserves immutable inputs when no effective change occurs.

Important APIs/types/functions: exercises `AclListBuilder.of`, `copyOf`, `add`, `addAll`, `set`, `remove`, `build`, and `isChanged`.

Control flow and state: test data includes `alice` read/write ACLs that merge into one read-write entry and a separate `bob` read ACL. Reapplying the same operation returns false while preserving an already-true changed flag. `set` with same or equal list leaves the builder unchanged and returns the original list instance.

Dependencies and integration points: depends on `OzoneAcl.of` and ACL identity/type/scope enums. Builder behavior is important for OM metadata update paths that should avoid writing unchanged ACL lists.

Risks and test signals: catches duplicate ACL entries, lost merged rights, false positive dirty state, and no-op operations resetting dirty state. The instance identity assertions protect memory and persistence churn optimizations.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/helpers/TestAclListBuilder.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/helpers/TestMapBuilder.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/helpers/TestMapBuilder.java

Purpose: validates `MapBuilder`, a generic mutation-tracking map builder used to preserve unchanged metadata/tag maps.

Important APIs/types/functions: covers `MapBuilder.of`, `copyOf`, `put`, `putAll`, `remove`, `set`, `build`, `initialValue`, and `isChanged`.

Control flow and state: parameterized tests run over empty, one-entry, and two-entry immutable maps. Re-putting existing key/value pairs and removing missing keys are no-ops that return the initial map instance. Updating existing values, adding new keys, removing existing keys, or setting a different map marks changed.

Dependencies and integration points: uses Guava `ImmutableMap`, Java `HashMap` and `LinkedHashMap`. This behavior supports OM helper builders that want to avoid copying or persisting unchanged metadata.

Risks and test signals: catches incorrect dirty tracking, accidental loss of iteration order during removals, and returning mutable/new maps on no-op paths. `setImmutable` asserts immutable replacement can be preserved by identity.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/helpers/TestMapBuilder.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/helpers/TestOMNodeDetails.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/helpers/TestOMNodeDetails.java

Purpose: tests `OMNodeDetails`, the metadata holder for OM node identity, addresses, ports, listener/decommission state, protobuf conversion, and checkpoint endpoint URL generation.

Important APIs/types/functions: exercises builder setters for service ID, node ID, host/RPC/Ratis/HTTP/HTTPS addresses, `setIsListener`, `setRatisAddress`, getters, `setRatisListener`, `setDecommissioningState`, `getProtobuf`, `getFromProtobuf`, `getOMPrintInfo`, `getOMDBCheckpointEndpointUrl`, `getOMNodeAddressFromConf`, and `getOMNodeDetailsFromConf`.

Control flow and state: tests construct nodes from `InetSocketAddress` and host strings, mutate listener/decommission flags, round-trip active/decommissioned/listener nodes through `OMNodeInfo`, and read node address fields from `OzoneConfiguration`.

Dependencies and integration points: integrates with OM config keys, `ConfUtils`, admin protobuf `OMNodeInfo` and `NodeState`, and checkpoint HTTP/HTTPS endpoint construction.

Risks and test signals: catches wrong host/port derivation, missing listener state in protobuf, decommission state loss, malformed checkpoint URLs, and null handling for incomplete config. Checkpoint URL tests verify protocol, authority, path version, and query flags like `flushBeforeCheckpoint` and `includeSnapshotData`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/helpers/TestOMNodeDetails.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/helpers/TestOmBucketArgs.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/helpers/TestOmBucketArgs.java

Purpose: tests `OmBucketArgs` protobuf conversion for quota-presence flags and default replication configuration.

Important APIs/types/functions: covers `OmBucketArgs.newBuilder`, `setQuotaInNamespace`, `setQuotaInBytes`, `hasQuotaInBytes`, `hasQuotaInNamespace`, `setDefaultReplicationConfig`, `getProtobuf`, and `getFromProtobuf`.

Control flow and state: one path builds args without quota and confirms both presence flags stay false before and after protobuf conversion. Another path sets namespace and byte quota and verifies both flags survive. Replication tests confirm absent default replication remains null and EC default replication round-trips as type `EC`.

Dependencies and integration points: uses HDDS `DefaultReplicationConfig` and `ECReplicationConfig`. These args are used by OM bucket create/update request handling.

Risks and test signals: protects distinction between unset quota and quota value defaults, and catches loss of bucket default replication policy across the protobuf boundary.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/helpers/TestOmBucketArgs.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/helpers/TestOmBucketInfo.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/helpers/TestOmBucketInfo.java

Purpose: validates `OmBucketInfo` equality, protobuf conversion, bucket-link metadata, cloning, ACL copying, and EC default replication serialization.

Important APIs/types/functions: exercises `OmBucketInfo.newBuilder`, `getProtobuf`, `getFromProtobuf`, `copyObject`, `setSourceVolume`, `setSourceBucket`, `setDefaultReplicationConfig`, `getDefaultReplicationConfig`, and ACL getters.

Control flow and state: tests construct normal and linked buckets, round-trip through protobuf, copy objects and compare equality/not-same identity, then verify ACL entries are retained. EC tests assert protobuf has no default replication when unset and has EC data/parity when set.

Dependencies and integration points: uses `StorageType`, `OzoneAcl`, `IAccessAuthorizer`, HDDS replication config classes, and OM protobuf `BucketInfo`.

Risks and test signals: catches shallow clone problems, lost bucket-link fields, lost ACLs, and mismatch between legacy replication fields and modern default replication config. Important for OM metadata persistence and bucket update semantics.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/helpers/TestOmBucketInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/helpers/TestOmKeyArgs.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/helpers/TestOmKeyArgs.java

Purpose: focused regression test for `OmKeyArgs.toBuilder()` preserving the `headOp` flag.

Important APIs/types/functions: uses `OmKeyArgs.Builder.setHeadOp`, `build`, `isHeadOp`, and `toBuilder`.

Control flow and state: a parameterized boolean test builds `OmKeyArgs` with both true and false `headOp` states, then rebuilds via `toBuilder` and asserts the flag is unchanged.

Dependencies and integration points: `headOp` affects key metadata/read request behavior, especially HEAD-like operations that should not be treated as normal reads in higher layers.

Risks and test signals: protects against builder copy omissions when adding or refactoring fields in `OmKeyArgs`. Any new boolean flags with request semantics should get similar toBuilder coverage.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/helpers/TestOmKeyArgs.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/helpers/TestOmKeyInfo.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/helpers/TestOmKeyInfo.java

Purpose: tests `OmKeyInfo` protobuf conversion, replication config encoding, hsync metadata detection, expected data generation, copy semantics, ACL/tag mutation effects, and location-list copying.

Important APIs/types/functions: exercises `OmKeyInfo.Builder`, `getProtobuf(ClientVersion)`, `getFromProtobuf`, `withMetadataMutations`, `isHsync`, `copyObject`, `toBuilder`, `setAcls`, `setTags`, and key-location helper classes.

Control flow and state: tests create key info with RATIS and EC replication. RATIS uses factor/type fields, while EC uses `EcReplicationConfig` and omits factor. Copy tests include multipart and non-multipart location groups, compare nested `OmKeyLocationInfoGroup` and `OmKeyLocationInfo`, then mutate ACLs and tags to verify equality changes.

Dependencies and integration points: uses HDDS replication configs, `BlockID`, SCM `Pipeline`, protobuf `KeyInfo`, Ozone ACLs, `ClientVersion`, `OzoneConsts.HSYNC_CLIENT_ID`, and `Time`.

Risks and test signals: protects metadata persistence, replication compatibility, hsync state detection, expected generation tracking, and deep copy of nested block locations. A minor test weakness is that it assigns `clone = key.getKeyLocationVersions().get(i)` instead of the clone list inside the loop, but overall equality checks still cover copy behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/helpers/TestOmKeyInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/helpers/TestOmKeyLocationInfoGroup.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/helpers/TestOmKeyLocationInfoGroup.java

Purpose: validates versioned block-location grouping in `OmKeyLocationInfoGroup`.

Important APIs/types/functions: exercises constructor, `getBlocksLatestVersionOnly`, `getLocationList(version)`, `generateNextVersion`, `getLocationList`, and `getVersion`.

Control flow and state: helper creates a group at version 2 containing two locations with create version 1 and one location with create version 2. Tests ensure latest-only returns the version 2 location, previous version lookup returns two locations, and generating the next version with a new list yields version 3.

Dependencies and integration points: depends on `OmKeyLocationInfo.Builder`. This data structure is used by `OmKeyInfo` to track block locations across key versions and multipart updates.

Risks and test signals: catches off-by-one version progression and incorrect filtering by create version. Persistence risk is moderate because location group ordering and versioning affect key reads and recovery.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/helpers/TestOmKeyLocationInfoGroup.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/helpers/TestOmMultipartKeyInfo.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/helpers/TestOmMultipartKeyInfo.java

Purpose: tests `OmMultipartKeyInfo` copy, protobuf conversion, replication config preservation, owner/ACL preservation, part-list isolation, and schema-version constraints.

Important APIs/types/functions: exercises builder setters for upload ID, owner, ACLs, creation time, replication config, schema version, and part key info list; `copyObject`, `getProto`, `getFromProto`, `addPartKeyInfo`, and `getPartKeyInfoMap`.

Control flow and state: loops over standalone, RATIS, and EC replication configs for copy and proto tests. It verifies copied part maps are distinct by mutating the original after copying. Schema version 1 rejects adding part info and rejects serializing a legacy part list.

Dependencies and integration points: uses OM protobuf `MultipartKeyInfo`, `PartKeyInfo`, and `KeyInfo`, HDDS replication configs, `OzoneAcl`, and `Time`. This maps directly to multipart upload metadata persisted by OM.

Risks and test signals: catches loss of replication metadata, shallow part-map copies, owner/ACL loss, and invalid mixing of schema-version 1 with legacy part lists.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/helpers/TestOmMultipartKeyInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/helpers/TestOmMultipartPartInfo.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/helpers/TestOmMultipartPartInfo.java

Purpose: tests `OmMultipartPartInfo` conversion to/from protobuf and creation from `OmKeyInfo`.

Important APIs/types/functions: exercises `OmMultipartPartInfo.from`, `getProto`, `getFromProto`, getters for part name/number/ETag/data size/modification/object/update IDs/key locations, and validation of required protobuf fields.

Control flow and state: a valid part info is built from key metadata containing `OzoneConsts.ETAG`, converted to protobuf, decoded, and field-compared. Separate tests clear required fields one by one and expect `IllegalArgumentException`. Object ID and update ID are optional and default to 0 when missing.

Dependencies and integration points: uses OM protobuf `MultipartPartInfo` and `KeyLocationList`, `OmKeyInfo`, `OmKeyLocationInfoGroup`, HDDS `BlockID`, RATIS replication config, and SCM `Pipeline`.

Risks and test signals: protects multipart list-parts responses and persisted part metadata from missing required data. The missing-ETag test is important because S3 multipart semantics require stable part ETags.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/helpers/TestOmMultipartPartInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/helpers/TestOmMultipartPartKey.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/helpers/TestOmMultipartPartKey.java

Purpose: validates byte-level codec behavior for `OmMultipartPartKey`, including prefix keys, full keys, upload IDs with slashes, sort order, and malformed input rejection.

Important APIs/types/functions: uses `OmMultipartPartKey.getCodec`, `of`, `prefix`, `hasPartNumber`, `getPartNumber`, `getUploadId`, `toString`, `Codec.toPersistedFormat`, `fromPersistedFormat`, `supportCodecBuffer`, `toHeapCodecBuffer`, and `fromCodecBuffer`.

Control flow and state: full keys encode upload ID plus a separator and big-endian int part number; prefix keys encode upload ID only. Parameterized tests cover all valid part numbers in `[1,10000]` whose low byte equals separator byte `0x2f`, ensuring the decoder finds the real separator. Byte comparison proves numerical part order sorts correctly.

Dependencies and integration points: integrates with HDDS `Codec`, `CodecBuffer`, and `CodecException`. The codec defines RocksDB key layout for multipart part entries.

Risks and test signals: catches naive slash splitting, malformed UTF-8 acceptance, empty/invalid key acceptance, null factory inputs, lexicographic part ordering bugs, and malformed surrogate encoding. This is high-risk persistence code because byte order controls DB scans.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/helpers/TestOmMultipartPartKey.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/helpers/TestOmMultipartUpload.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/helpers/TestOmMultipartUpload.java

Purpose: tests parsing of multipart upload database keys into `OmMultipartUpload` fields.

Important APIs/types/functions: covers `OmMultipartUpload.getDbKey`, `OmMultipartUpload.from`, and getters for volume, bucket, key, and upload ID.

Control flow and state: builds a DB key for `vol1/bucket1/dir1/key1/uploadId`, parses it, and asserts all components including a nested key path are preserved.

Dependencies and integration points: this helper underpins OM multipart upload table key parsing and S3 MPU request handling.

Risks and test signals: catches delimiter parsing errors where object keys contain slashes. Coverage is narrow and does not test malformed keys or upload IDs containing delimiter-like content.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/helpers/TestOmMultipartUpload.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/helpers/TestOmSnapshotDiffJobCodec.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/helpers/TestOmSnapshotDiffJobCodec.java

Purpose: verifies the current `SnapshotDiffJob` codec can read JSON data persisted by the old Jackson-based codec.

Important APIs/types/functions: uses `OldSnapshotDiffJobCodecForTesting.toPersistedFormatImpl`, `SnapshotDiffJob.codec()`, and `fromPersistedFormatImpl`. It inspects job ID, status, volume, bucket, snapshots, full-diff flags, native-diff flag, sub-status, total entries, largest entry key, and progress percent.

Control flow and state: constructs a `SnapshotDiffJob`, serializes it using the old codec, decodes it with the new codec, and compares critical fields. The test expects `keysProcessedPct` to be `0.0` after fallback decoding.

Dependencies and integration points: integrates with snapshot diff response `JobStatus` and `SubStatus`, HDDS DB codec APIs, and legacy RocksDB persisted JSON format.

Risks and test signals: protects rolling upgrade/backward compatibility for existing snapshot diff jobs. Any change to new codec fallback logic should preserve this test or include migration handling.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/helpers/TestOmSnapshotDiffJobCodec.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/helpers/TestOmSnapshotInfo.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/helpers/TestOmSnapshotInfo.java

Purpose: tests `SnapshotInfo` metadata conversion to/from protobuf, snapshot status mapping, size accounting fields, cleaning flags, and generated snapshot names.

Important APIs/types/functions: exercises `SnapshotInfo.Builder`, `getProtobuf`, `getFromProtobuf`, `SnapshotStatus.valueOf`, getters for IDs/names/status/sizes/flags, and `SnapshotInfo.generateName`.

Control flow and state: helper methods build equivalent object and protobuf records containing snapshot UUIDs, volume/bucket/name, previous snapshot IDs, path, deep-clean flags, referenced/exclusive sizes, replicated sizes, and deltas from directory deep cleaning. Tests compare individual fields and full object equality.

Dependencies and integration points: uses OM protobuf `SnapshotInfo`, `SnapshotStatusProto`, HDDS UUID protobuf conversion, and `Time`. The object is persisted by OM snapshot tables and used by snapshot diff/cleanup paths.

Risks and test signals: catches lost accounting fields, status mapping regressions, and protobuf/object equality drift. `generateName` asserts stable UTC-like timestamp formatting with millisecond precision for snapshot names.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/helpers/TestOmSnapshotInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/helpers/TestOmVolumeArgs.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/helpers/TestOmVolumeArgs.java

Purpose: tests `OmVolumeArgs` builder ACL mutation behavior and copy semantics.

Important APIs/types/functions: exercises `OmVolumeArgs.Builder`, `copyObject`, `toBuilder`, `addAcl`, `setAcls`, `removeAcl`, metadata addition, quota/object/update IDs, and ACL getters.

Control flow and state: setup obtains the current user. `createSubject` builds a volume with owner, admin, metadata, quota, object/update IDs, and a read ACL. Tests assert `copyObject` returns the same instance, adding write rights changes the ACL entry, setting ACLs replaces the list, and removing the read ACL yields an empty list.

Dependencies and integration points: uses `UserGroupInformation`, `OzoneAcl`, Guava `ImmutableMap`, and `Time`. These args back OM volume table records and ACL updates.

Risks and test signals: highlights that `copyObject` is identity-returning, so callers must not assume deep copy. ACL builder operations are the main regression surface covered here.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/helpers/TestOmVolumeArgs.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/helpers/TestOzoneAclUtil.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/helpers/TestOzoneAclUtil.java

Purpose: tests ACL list mutation helpers in `OzoneAclUtil`, including add/remove semantics, null handling, merging permissions, and scope separation.

Important APIs/types/functions: exercises `OzoneAclUtil.addAcl`, `removeAcl`, `OzoneAcl.of`, `OzoneAcl.parseAcl`, `getAclList`, `isSet`, `getAclScope`, `getAclByteString`, and default rights from `OmConfig`.

Control flow and state: default ACLs are built from current user and groups with configured user/group default rights. Add tests merge new permissions into existing ACL entries and avoid duplicate entries. Remove tests handle null lists, missing entries, missing permissions, removal of newly added permissions, and full entry removal.

Dependencies and integration points: depends on `UserGroupInformation`, `OzoneConfiguration.newInstanceOf(OmConfig.class)`, ACL identity/scope/type enums, and Java list mutation. It is central to OM authorization metadata updates.

Risks and test signals: catches duplicate ACL entries, permission-bit removal errors, null list behavior, and accidental merging between `ACCESS` and `DEFAULT` scope ACLs. Scope test confirms same identity and rights can coexist separately by scope.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/helpers/TestOzoneAclUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/helpers/TestOzoneFsUtils.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/helpers/TestOzoneFsUtils.java

Purpose: tests filesystem-style path validation and hsync feature gating in `OzoneFSUtils`.

Important APIs/types/functions: exercises `OzoneFSUtils.isValidName`, `canEnableHsync`, and `isValidKeyPath`.

Control flow and state: name tests accept absolute `/a/b` style names and reject relative paths, dot components, colon components, and double slashes. `canEnableHsync` is parameterized across server/client hbase enhancement config and `ozone.fs.hsync.enabled`; hsync is allowed only when both relevant enhancement and fs hsync flags are true. Key path validation returns valid relative paths, handles empty path based on `throwOnEmpty`, and throws `OMException` for invalid patterns.

Dependencies and integration points: uses `OzoneConfiguration`, `OzoneConfigKeys`, and `OMException`. These utilities guard OM key namespace operations and HBase-oriented hsync features.

Risks and test signals: catches path traversal and malformed key names, client/server config key confusion, and accidental hsync enablement when prerequisites are disabled. Coverage includes trailing slash as a valid key path.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/helpers/TestOzoneFsUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/helpers/TestOzoneIdentityProvider.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/helpers/TestOzoneIdentityProvider.java

Purpose: tests `OzoneIdentityProvider` identity extraction from IPC `Schedulable` requests, preferring trusted S3 caller context when present.

Important APIs/types/functions: exercises `OzoneIdentityProvider.makeIdentity`, `Schedulable.getUserGroupInformation`, optional `getCallerContext`, and `OM_S3_CALLER_CONTEXT_PREFIX`.

Control flow and state: three schedulables model default UGI-only requests, S3 gateway requests with a prefixed caller context, and requests with an untrusted/non-prefixed caller context. The provider returns the access ID from prefixed context, otherwise falls back to UGI short username.

Dependencies and integration points: uses Hadoop IPC `CallerContext`, `Schedulable`, and `UserGroupInformation`. It integrates with OM scheduling/identity attribution and S3 gateway caller propagation.

Risks and test signals: protects against trusting arbitrary caller context, failing when default schedulable throws `UnsupportedOperationException` for caller context, and losing S3 end-user identity behind the gateway principal.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/helpers/TestOzoneIdentityProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/helpers/TestQuotaUtil.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/helpers/TestQuotaUtil.java

Purpose: tests quota size calculations for replicated and erasure-coded keys.

Important APIs/types/functions: exercises `QuotaUtil.getReplicatedSize` and `getSizePerReplica` with `RatisReplicationConfig` and `ECReplicationConfig`.

Control flow and state: RATIS factor THREE multiplies logical size by three, while factor ONE leaves it unchanged. EC(3,2) tests cover full stripes, partial stripes within the first data chunk, partial stripes beyond the first chunk, and single-stripe partial data. Per-replica EC size is expected to be replicated size divided by required nodes.

Dependencies and integration points: uses HDDS replication config APIs and one-megabyte EC cell size. These calculations feed bucket/volume quota accounting and snapshot size estimates.

Risks and test signals: catches EC parity overhead miscalculation, especially partial stripe rounding. Incorrect results would affect quota enforcement and storage usage reporting.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/helpers/TestQuotaUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/helpers/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/helpers/package-info.java

Purpose: package-level documentation for `org.apache.hadoop.ozone.om.helpers` tests, stating that the package contains unit tests of helpers.

Important APIs/types/functions: contains only the package declaration and Javadoc. It has no runtime behavior, mutable state, control flow, or persistence.

Dependencies and integration points: uses Java package-info conventions. It helps Javadoc and tooling group helper tests.

Risks and test signals: no direct runtime risk. The main maintenance risk is stale package description if the package contents change significantly.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/helpers/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/protocolPB/TestGrpcOmTransportConcurrentFailover.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/protocolPB/TestGrpcOmTransportConcurrentFailover.java

Purpose: stress-tests `GrpcOmTransport` failover under high concurrency against three in-process mock OM gRPC servers.

Important APIs/types/functions: exercises `GrpcOmTransport.submitRequest`, HA config keys for OM RPC/gRPC addresses, `OzoneManagerServiceGrpc`, `ServerBuilder`, and failover response handling for `OMNotLeaderException` descriptions.

Control flow and state: setup starts three servers on fixed ports, configures OM service ID and nodes, marks `om0` leader, sends warm-up requests, then changes leadership to `om2`. The main test launches 500 threads, each sending 10 `ListVolume` requests through one transport. Mock servers count requests, failures, and successes with atomic counters.

Dependencies and integration points: uses real gRPC servers, Mockito delegation, `UserGroupInformation`, `OzoneConfiguration`, and Java concurrency primitives. It models concurrent clients sharing failover state during OM leadership changes.

Risks and test signals: catches failover synchronization bugs where not all requests eventually reach the new leader. The test expects all concurrent requests to succeed on `om2` and at least one failed request on `om0`; fixed ports and high thread count may be environment-sensitive.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/protocolPB/TestGrpcOmTransportConcurrentFailover.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/protocolPB/TestOmTransportFactory.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/protocolPB/TestOmTransportFactory.java

Purpose: tests discovery and configuration selection for `OmTransportFactory`.

Important APIs/types/functions: exercises `OmTransportFactory.createFactory`, Java `ServiceLoader.load`, `OZONE_OM_TRANSPORT_CLASS`, `OZONE_OM_TRANSPORT_CLASS_DEFAULT`, and factory method `createOmTransport`.

Control flow and state: one test mocks `ServiceLoader` to return a dummy implementation and verifies it is selected. Another mocks an empty loader, verifies the configured default class is used, verifies a configured concrete class name instantiates, and verifies a nonexistent class name throws `IOException`.

Dependencies and integration points: uses Mockito static mocking, `OzoneConfiguration`, `ConfigurationSource`, and `UserGroupInformation`. This factory determines whether OM clients use Hadoop RPC, gRPC, or plugin transports.

Risks and test signals: protects extension discovery, default transport fallback, and config error reporting. A regression here can prevent clients from constructing any OM transport.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/protocolPB/TestOmTransportFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/protocolPB/TestOzoneManagerProtocolClientSideTranslatorPB.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/protocolPB/TestOzoneManagerProtocolClientSideTranslatorPB.java

Purpose: tests client-side protobuf translator request construction for `startQuotaRepair`.

Important APIs/types/functions: exercises `OzoneManagerProtocolClientSideTranslatorPB.startQuotaRepair`, `OmTransport.submitRequest`, and protobuf `StartQuotaRepairRequest/Response`, `OMRequest`, `OMResponse`, command type `StartQuotaRepair`, and status `OK`.

Control flow and state: mocked transport returns a successful response. Argument captors inspect outgoing `OMRequest` and verify empty and specified bucket lists are encoded correctly. Null bucket lists throw `NullPointerException` with message containing `buckets == null` and do not call transport.

Dependencies and integration points: uses Mockito and AssertJ. Translator correctness is required for OM admin/repair client APIs.

Risks and test signals: catches wrong command type, bucket list loss, and unintended RPC calls on invalid input. Coverage is narrow but precise for quota repair API contract.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/protocolPB/TestOzoneManagerProtocolClientSideTranslatorPB.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/protocolPB/TestS3GrpcOmTransport.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/protocolPB/TestS3GrpcOmTransport.java

Purpose: tests `GrpcOmTransport` request submission, failover retry behavior, per-request failover counts, and non-retry behavior for oversized gRPC metadata/response errors.

Important APIs/types/functions: exercises `GrpcOmTransport.startClient`, `submitRequest`, failover config keys, gRPC in-process server/channel builders, protobuf `ServiceList` requests, and `OMNotLeaderException` error wrapping.

Control flow and state: an in-process gRPC service either returns a fixed successful `OMResponse` or throws a not-leader error depending on `doFailover` and `completeFailover` flags. Tests verify normal submission, one failover followed by success, retry exhaustion with max attempts 0, failover counters reset per request, and `RESOURCE_EXHAUSTED` style max message length failures do not retry.

Dependencies and integration points: uses `GrpcCleanupRule`, `ManagedChannel`, `UserGroupInformation`, `OzoneConfiguration`, and Ratis `RaftPeerId`. This is the direct client transport for gRPC OM calls.

Risks and test signals: catches retry policy regressions, failover counter leakage across requests, and inappropriate retry on response-size/resource errors. The test notes suggested leader ID is not currently used by the client.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/protocolPB/TestS3GrpcOmTransport.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/protocolPB/grpc/TestClientAddressClientInterceptor.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/protocolPB/grpc/TestClientAddressClientInterceptor.java

Purpose: tests the gRPC client interceptor that adds client IP address and hostname metadata to outgoing requests.

Important APIs/types/functions: exercises `ClientAddressClientInterceptor.interceptCall`, `ClientCall.start`, `GrpcClientConstants.CLIENT_HOSTNAME_METADATA_KEY`, and `CLIENT_IP_ADDRESS_METADATA_KEY`.

Control flow and state: the test statically mocks `Context.key("CLIENT_IP_ADDRESS")` and `Context.key("CLIENT_HOSTNAME")` to return context keys with known values. It intercepts a mocked channel call, starts the returned call with mocked metadata, and verifies both metadata entries are written.

Dependencies and integration points: uses gRPC `ClientInterceptor`, `Context`, `Metadata`, `Channel`, `CallOptions`, `MethodDescriptor`, and Mockito static mocking. It feeds server-side identity/audit paths.

Risks and test signals: catches missing or swapped metadata propagation from client context. It does not cover null context values or downstream server behavior, which is covered by the server interceptor test.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/protocolPB/grpc/TestClientAddressClientInterceptor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/protocolPB/grpc/TestClientAddressServerInterceptor.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/protocolPB/grpc/TestClientAddressServerInterceptor.java

Purpose: tests the gRPC server interceptor that reads client address metadata and installs it into gRPC context keys.

Important APIs/types/functions: exercises `ClientAddressServerInterceptor.interceptCall`, `Contexts.interceptCall`, `GrpcClientConstants.CLIENT_HOSTNAME_CTX_KEY`, `CLIENT_IP_ADDRESS_CTX_KEY`, and corresponding metadata keys.

Control flow and state: mocked headers return host and IP values. Static mocking captures the `Context` passed to `Contexts.interceptCall`; after attaching that context, the test asserts the context keys expose the captured host and IP values.

Dependencies and integration points: uses gRPC `ServerInterceptor`, `ServerCall`, `ServerCallHandler`, `Metadata`, `Context`, and Mockito. It completes the client-to-server propagation chain for audit/logging identity details.

Risks and test signals: catches missing context propagation and mismatched metadata/context keys. The test relies on `context.attach()` without detach because it is a short isolated unit test.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/protocolPB/grpc/TestClientAddressServerInterceptor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/protocolPB/TestOMPBHelper.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/protocolPB/TestOMPBHelper.java

Purpose: regression test for `OMPBHelper.convertMD5MD5FileChecksum`, ensuring backward compatibility with a prior 20-byte MD5 protobuf bug.

Important APIs/types/functions: exercises `OMPBHelper.convertMD5MD5FileChecksum`, protobuf `MD5MD5Crc32FileChecksumProto`, `ChecksumTypeProto`, Hadoop `MD5MD5CRC32FileChecksum`, and `MD5Hash.MD5_LEN`.

Control flow and state: runs the same conversion with a normal 16-byte MD5 and a buggy 20-byte buffer whose final four bytes are zero. It writes the resulting checksum to a byte stream, reads bytes-per-CRC, CRC-per-block, and MD5 bytes back from a `ByteBuffer`, and asserts only the first 16 bytes are retained.

Dependencies and integration points: uses `ByteString`, Hadoop checksum classes, random values, and `StringUtils.bytes2Hex` for diagnostic output. This helper affects protocol compatibility for file checksum responses.

Risks and test signals: catches checksum conversion failures for historical persisted/wire data. Randomized bytes-per-CRC and crc-per-block increase coverage, but the test uses random diagnostics and prints to stdout.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/protocolPB/TestOMPBHelper.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/security/TestGDPRSymmetricKey.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/security/TestGDPRSymmetricKey.java

Purpose: tests `GDPRSymmetricKey` creation with generated and supplied secrets.

Important APIs/types/functions: exercises constructors `GDPRSymmetricKey(SecureRandom)` and `GDPRSymmetricKey(String, String)`, `getCipher`, and `acceptKeyDetails`.

Control flow and state: default generation uses `SecureRandom` and must create a cipher whose algorithm equals `OzoneConsts.GDPR_ALGORITHM_NAME`. Valid 16-character input also creates the expected cipher and exposes non-empty key details. Invalid 5-character input throws `IllegalArgumentException` with an exact secret-length message.

Dependencies and integration points: uses Java crypto, Commons `RandomStringUtils.secure`, and Ozone GDPR constants. These keys support GDPR metadata encryption/decryption behavior.

Risks and test signals: catches wrong algorithm selection, empty persisted key detail fields, and weak/invalid secret length acceptance. It does not test actual encryption/decryption output.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/security/TestGDPRSymmetricKey.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/security/TestOzoneDelegationTokenSelector.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/security/TestOzoneDelegationTokenSelector.java

Purpose: tests `OzoneDelegationTokenSelector` matching of delegation tokens by requested OM service.

Important APIs/types/functions: exercises `selectToken`, Hadoop `Token<OzoneTokenIdentifier>`, `OzoneTokenIdentifier.KIND_NAME`, `Text` service strings, and token `setService`.

Control flow and state: creates a token with service string `om1:9862,om2:9862,om3:9862`. Selecting for `om1:9862` returns the token. After changing token service to `om1:9863`, selecting `om1:9862` returns null and selecting `om1:9863` returns the token.

Dependencies and integration points: uses Hadoop security token APIs and random identifier/password bytes. This selector is used by clients choosing OM delegation tokens from UGI credentials.

Risks and test signals: catches service matching regressions for HA comma-separated service names and single-node services. It does not cover wrong token kind or multiple candidate ordering.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/security/TestOzoneDelegationTokenSelector.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/security/acl/TestAssumeRoleRequest.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/security/acl/TestAssumeRoleRequest.java

Purpose: tests `AssumeRoleRequest` and nested `OzoneGrant` value semantics, getters, immutability of S3 actions, and equality/hash behavior.

Important APIs/types/functions: exercises `AssumeRoleRequest` constructor, getters for host/IP/client UGI/target role/grants, `OzoneGrant` getters for objects/permissions/S3 actions, and `equals/hashCode`.

Control flow and state: builds bucket `OzoneObjInfo` targets, ACL permission sets, and grants with empty or populated S3 action sets. Tests assert two equivalent requests compare equal, target role differences compare unequal, S3 action sets are unmodifiable, and grants/requests with S3 actions differ from those without.

Dependencies and integration points: uses `UserGroupInformation`, `OzoneObjInfo`, `IAccessAuthorizer.ACLType`, and Java set implementations. It represents IAM/S3 assume-role authorization input.

Risks and test signals: catches mutable grant action exposure and equality omissions for S3 actions. Correct value semantics are important for policy caching, deduplication, and audit comparisons.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/security/acl/TestAssumeRoleRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/security/acl/TestOzoneObjInfo.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/security/acl/TestOzoneObjInfo.java

Purpose: tests `OzoneObjInfo` builder accessors and protobuf path parsing for Ozone authorization objects.

Important APIs/types/functions: exercises `OzoneObjInfo.Builder`, `build`, getters for volume/bucket/key, and `OzoneObjInfo.fromProtobuf`.

Control flow and state: builder tests check null and populated volume, bucket, and key combinations. Protobuf tests create KEY objects with paths both with and without a leading delimiter and with long nested key paths, including a trailing slash. `fromProtobuf` must preserve the full key suffix after volume and bucket.

Dependencies and integration points: uses `OzoneManagerProtocolProtos.OzoneObj`, `OZONE_URI_DELIMITER`, `OzoneObj.ResourceType`, and `OzoneObj.StoreType`. These objects feed ACL authorization requests.

Risks and test signals: catches path splitting bugs where nested key slashes are truncated or leading delimiter variants are misread. The test also documents that key name may exist even if volume/bucket are null when built directly.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/security/acl/TestOzoneObjInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/security/acl/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/security/acl/package-info.java

Purpose: package-level documentation for ACL-related unit tests under `org.apache.hadoop.ozone.security.acl`.

Important APIs/types/functions: contains only Javadoc and the package declaration. It has no runtime control flow, state, persistence, or external API beyond package documentation.

Dependencies and integration points: uses Java package-info conventions for documentation/tooling grouping.

Risks and test signals: no direct behavior risk. Documentation can drift if the package broadens beyond ACL-related tests.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/security/acl/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/snapshot/TestSnapshotDiffResponse.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/snapshot/TestSnapshotDiffResponse.java

Purpose: tests user-facing `SnapshotDiffResponse.toString()` messages for report-only snapshot diff polling.

Important APIs/types/functions: exercises `SnapshotDiffResponse` constructors, `toString`, `setSubStatus`, `setProgressPercent`, `SnapshotDiffReportOzone`, `JobStatus`, and `SubStatus`.

Control flow and state: creates an empty snapshot diff report and wraps it in responses with `NOT_FOUND`, `REJECTED`, `FAILED`, and `IN_PROGRESS` statuses in report-only mode. Tests assert strings include guidance for `--get-report`, resubmission guidance, failure reason, sub-status, and progress percentage.

Dependencies and integration points: integrates with snapshot diff CLI/API presentation, `SnapshotDiffReportOzone`, and snapshot diff status enums.

Risks and test signals: catches regressions in operator guidance and status detail visibility. This is not persistence code, but message clarity is important for snapshot diff workflows and automation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/snapshot/TestSnapshotDiffResponse.java -->
