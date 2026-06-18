# subset-b-007991 Research

Grouped research report for subset-b-007991. Each section preserves the source path and is delimited for reconciliation into per-file reports.


<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/ratis/TestContainerCommandRequestMessage.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/ratis/TestContainerCommandRequestMessage.java

## Purpose
Tests `ContainerCommandRequestMessage` serialization behavior for container write requests that carry block, chunk, checksum, and small-file payload data through the Ratis request-message layer.

## Important APIs, types, and functions
- Uses `ContainerCommandRequestProto`, `PutSmallFileRequestProto`, `WriteChunkRequestProto`, `PutBlockRequestProto`, `BlockData`, `ChunkInfo`, `KeyValue`, and `BlockID` from the HDDS container protocol.
- Exercises `ContainerCommandRequestMessage.toMessage(...)` and message reconstruction paths around protobuf payloads and `ByteString` data.
- Builds checksum metadata through `Checksum` and `ChecksumData` using `ChecksumType`, with `ClientVersion` included in request construction.
- Test cases are `testPutSmallFile` and `testWriteChunk`.

## Control flow
The tests build randomized byte payloads, compute or attach checksum data, wrap the payload in the relevant container command request, convert it to a Ratis message, then deserialize and compare command fields and embedded data. The small-file path nests chunk and block metadata inside the `PutSmallFile` request, while the write-chunk path focuses on a separate chunk write request.

## State and persistence behavior
The file does not persist data to disk. State is local to generated protobuf builders, random payload arrays, checksum objects, and reconstructed message instances.

## Dependencies and integration points
This test bridges HDDS container protobufs, Ozone checksum code, and Apache Ratis message transport. It is a regression signal for datanode container command replication over Ratis.

## Risks and test signals
The main risk is losing payload bytes or checksum/block metadata during request wrapping. The tests signal that small-file and write-chunk commands preserve command type, block identifiers, chunk metadata, key-values, and data bytes after Ratis message conversion.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/ratis/TestContainerCommandRequestMessage.java -->


<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/ratis/TestRatisHelper.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/ratis/TestRatisHelper.java

## Purpose
Validates `RatisHelper` translation from Ozone configuration into Ratis `RaftProperties` for client, server, and gRPC transport settings.

## Important APIs, types, and functions
- Uses `OzoneConfiguration` as the source configuration object and `RaftProperties` as the generated Ratis property bag.
- Exercises `RatisHelper.createRaftClientProperties`, `createRaftGrpcPropertiesForClient`, `createRaftGrpcPropertiesForServer`, and `createRaftServerProperties`.
- Checks property lookup through Ratis config keys and Ozone HDDS Ratis config keys.

## Control flow
Each test creates an `OzoneConfiguration`, optionally sets Ozone-side keys, calls the relevant helper, and asserts the resulting Ratis properties contain expected timeout, retry, gRPC, or server values.

## State and persistence behavior
Configuration exists only in memory. No file or service state is mutated.

## Dependencies and integration points
The test covers the boundary between HDDS configuration classes and Apache Ratis runtime configuration, which is used by datanode and SCM Ratis clients and servers.

## Risks and test signals
Mis-mapped configuration keys can cause production clusters to run with unexpected Ratis defaults. These tests detect key translation regressions and separate client/server gRPC property behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/ratis/TestRatisHelper.java -->


<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/ratis/TestServerNotLeaderExceptionMessageParsing.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/ratis/TestServerNotLeaderExceptionMessageParsing.java

## Purpose
Tests parsing of Ratis `ServerNotLeaderException` messages so HDDS can extract leader information from known Ratis error text.

## Important APIs, types, and functions
- Exercises `RatisHelper` leader parsing logic for server-not-leader messages.
- Uses JUnit assertions to verify parsed host and port results for sample exception strings.

## Control flow
The test feeds representative exception messages into the parser and asserts the expected leader address is returned. It also covers message variants where leader information may be absent or formatted differently.

## State and persistence behavior
No persistent state is used. The test is pure string parsing.

## Dependencies and integration points
This is an integration guard for HDDS retry/failover behavior that depends on Ratis exception text when a client talks to a non-leader server.

## Risks and test signals
The brittle dependency is Ratis message format. A format change can break leader discovery and client rerouting; this test signals whether known message shapes still parse correctly.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/ratis/TestServerNotLeaderExceptionMessageParsing.java -->


<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/ratis/conf/TestRaftClientConfig.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/ratis/conf/TestRaftClientConfig.java

## Purpose
Covers defaults and setters for `RaftClientConfig`, the HDDS configuration object for Ratis client timeouts and request behavior.

## Important APIs, types, and functions
- Uses `OzoneConfiguration.getObject(RaftClientConfig.class)` to bind config keys to a typed object.
- Tests `defaults` and `setAndGet` for `Duration`-backed fields and client numeric settings.

## Control flow
The default test reads a fresh typed config and compares defaults. The setter test mutates fields on the object and checks getters return the updated values.

## State and persistence behavior
All state is in-memory configuration data. No persisted configuration files are read or written.

## Dependencies and integration points
This file verifies the annotation/config binding path used by HDDS Ratis client creation code.

## Risks and test signals
Default drift or broken setter/getter wiring can alter retry and timeout behavior cluster-wide. The test gives a focused signal for typed config regressions.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/ratis/conf/TestRaftClientConfig.java -->


<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/ratis/conf/TestRatisClientConfig.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/ratis/conf/TestRatisClientConfig.java

## Purpose
Validates defaults and mutability for `RatisClientConfig`, another typed HDDS Ratis client configuration bean.

## Important APIs, types, and functions
- Uses `OzoneConfiguration` typed object binding.
- Tests default values and setter/getter round trips for durations and retry-related client settings.

## Control flow
The tests instantiate the config object from a clean Ozone configuration, assert expected defaults, then set representative custom values and assert those values are returned.

## State and persistence behavior
State is local to the configuration object. There is no external persistence.

## Dependencies and integration points
The typed config is consumed by Ratis helper/client setup paths. The test protects the Ozone configuration framework to Java bean mapping.

## Risks and test signals
Incorrect defaults or property annotations can silently change client retry timing. The tests provide early detection of such mapping changes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/ratis/conf/TestRatisClientConfig.java -->


<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/resource/TestLeakDetector.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/resource/TestLeakDetector.java

## Purpose
Tests the generic `LeakDetector` utility behavior for resources that implement `UncheckedAutoCloseable`.

## Important APIs, types, and functions
- Defines a small `MyResource` wrapper whose `close` method increments an `AtomicInteger`.
- Uses `LeakDetector.track` and close semantics to detect whether tracked resources are closed.
- Test cases are `testNoLeaks` and `testLeaks`.

## Control flow
`testNoLeaks` creates and closes a tracked resource, expecting no leak callback. `testLeaks` creates a tracked resource without closing it and relies on detector cleanup/check behavior to report the leak path.

## State and persistence behavior
State is limited to an `AtomicInteger` and detector-held resource references. There is no disk persistence.

## Dependencies and integration points
The utility sits beneath HDDS resource management paths and integrates with Ratis `UncheckedAutoCloseable` conventions.

## Risks and test signals
Leak detectors can be noisy if close tracking is wrong or silent if references are lost too early. The tests signal expected closed and leaked-resource accounting.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/resource/TestLeakDetector.java -->


<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/scm/container/TestContainerChecksums.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/scm/container/TestContainerChecksums.java

## Purpose
Tests the value-object behavior of `ContainerChecksums`.

## Important APIs, types, and functions
- Exercises equality, hash code, and string rendering.
- Uses AssertJ/JUnit assertions against checksum fields stored by the value object.

## Control flow
The tests create equivalent and differing checksum objects, compare equality/hash behavior, and verify `toString` contains useful field content.

## State and persistence behavior
The class under test is immutable/value-like in these scenarios. There is no persistence.

## Dependencies and integration points
`ContainerChecksums` is used by SCM/container reporting logic where stable equality and readable diagnostics matter.

## Risks and test signals
Incorrect equality or hash code would break map/set usage and test diagnostics. The file gives a low-level value semantics signal.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/scm/container/TestContainerChecksums.java -->


<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/scm/container/TestContainerHealthState.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/scm/container/TestContainerHealthState.java

## Purpose
Validates the `ContainerHealthState` enum contract, including individual and combined health states, numeric values, descriptions, and metric names.

## Important APIs, types, and functions
- Exercises enum constants such as under-replicated, over-replicated, mis-replicated, missing, unhealthy, empty, open-unhealthy, quasi-closed-stuck, and open-without-pipeline states.
- Tests `getValue`, `getDescription`, `getMetricName`, and `fromValue` style lookup behavior.
- Includes uniqueness, count, and gap checks for individual and combination value ranges.

## Control flow
The suite asserts explicit values and strings for each enum constant, verifies lookup from numeric values, and scans all enum values for uniqueness and contiguous ranges.

## State and persistence behavior
The file is pure enum contract testing. No persistence or mutable shared state is involved.

## Dependencies and integration points
Container health states feed replication manager reports, SCM metrics, JSON/protobuf serialization, and operational dashboards.

## Risks and test signals
Changing enum numeric values or names can break persisted reports, metrics, and compatibility. These tests are strong compatibility signals for state encoding and observability labels.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/scm/container/TestContainerHealthState.java -->


<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/scm/container/TestContainerInfo.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/scm/container/TestContainerInfo.java

## Purpose
Tests `ContainerInfo` identity, protobuf conversion, replication config handling, timestamps, pipeline IDs, and state restoration behavior.

## Important APIs, types, and functions
- Uses `ContainerInfo`, `ContainerID`, `PipelineID`, `RatisReplicationConfig`, `ECReplicationConfig`, and `HddsProtos` protobufs.
- Test cases cover hash behavior by container ID, Ratis and EC protobuf round trips, and restoration of lifecycle state.
- Uses `TestClock` and `ThreadLocalRandom` for deterministic time advancement and random IDs.

## Control flow
Builders create container metadata with owner, state, replication config, pipeline, and timestamps. Tests serialize to protobuf and reconstruct, then compare field preservation. Restore-state tests move container lifecycle data through persisted values.

## State and persistence behavior
No actual database is used, but protobuf round trips model persisted SCM container metadata. The tests pay attention to creation/modification timestamps and lifecycle state fields.

## Dependencies and integration points
`ContainerInfo` is central SCM metadata consumed by replication, placement, and pipeline code. The protobuf contract integrates with persisted SCM state and wire messages.

## Risks and test signals
Losing replication type/factor, EC config, pipeline ID, or timestamps during serialization can corrupt SCM metadata. The tests signal compatibility for both Ratis and EC containers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/scm/container/TestContainerInfo.java -->


<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/scm/container/TestContainerReplicaInfo.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/scm/container/TestContainerReplicaInfo.java

## Purpose
Tests construction of `ContainerReplicaInfo` from protobuf replica metadata.

## Important APIs, types, and functions
- Uses `DatanodeDetails`, `MockDatanodeDetails`, `HddsProtos.ContainerReplicaProto`, and replica state fields.
- Covers object creation with and without an explicit EC replica index.

## Control flow
The tests build protobuf representations of container replicas, convert them to Java objects, and assert datanode UUID, container ID, state, sequence ID, bytes used, key count, and optional replica index.

## State and persistence behavior
The protobuf is treated as serialized replica state, but no external store is used.

## Dependencies and integration points
Replica info is consumed by SCM container reports, replication manager decisions, and EC placement logic.

## Risks and test signals
Incorrect protobuf mapping can hide replica index or datanode identity, especially for EC containers. These tests signal accurate conversion from report wire format.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/scm/container/TestContainerReplicaInfo.java -->


<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/scm/container/TestReplicationManagerReport.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/scm/container/TestReplicationManagerReport.java

## Purpose
Tests `ReplicationManagerReport` metric counting, sample collection, JSON rendering, protobuf serialization, duplicate protection, and tolerance of unknown metrics.

## Important APIs, types, and functions
- Uses `ReplicationManagerReport`, `ContainerHealthState`, `ContainerInfo`, `ContainerID`, and `HddsProtos.LifeCycleState`.
- Exercises `increment`, `incrementAndSample`, `setComplete`, `setTimestamp`, `setStat`, `setSample`, `toProtobuf`, and `fromProtobuf`.
- Uses Jackson `ObjectMapper` through `JsonUtils` for JSON validation.

## Control flow
Tests increment lifecycle and health counters, attach mocked container IDs as samples, render JSON, validate sample-limit configuration, serialize random stats and samples to protobuf, deserialize back, and assert duplicate stat/sample setters throw.

## State and persistence behavior
Report fields model persisted or transmitted SCM health report state. Timestamp, sample limit, stats map, and sample lists are mutated in memory and round-tripped through protobuf.

## Dependencies and integration points
The report integrates SCM replication manager metrics with JSON APIs and HDDS protobufs used for persistence or transmission.

## Risks and test signals
Risks include duplicate metric writes, unknown metric incompatibility, sample over-collection, and JSON/protobuf drift. The suite signals report stability for operational metrics and upgrade tolerance.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/scm/container/TestReplicationManagerReport.java -->


<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/scm/container/common/helpers/TestExcludeList.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/scm/container/common/helpers/TestExcludeList.java

## Purpose
Tests time-based cleanup semantics for `ExcludeList`, which tracks datanodes excluded from placement or replication decisions.

## Important APIs, types, and functions
- Uses `ExcludeList`, `DatanodeDetails`, `TestClock`, `Instant`, and `ZoneOffset`.
- Test cases are `excludeNodesShouldBeCleanedBasedOnGivenTime` and `excludeNodeShouldNotBeCleanedIfExpiryTimeIsZero`.

## Control flow
Tests add generated datanodes to the exclude list, advance a test clock, call cleanup, and assert membership changes according to expiry duration. A zero-expiry scenario verifies entries are retained.

## State and persistence behavior
The exclude list is in-memory operational state keyed by datanode identity. No persistence is involved.

## Dependencies and integration points
Placement, replication, and pipeline selection logic can consult `ExcludeList` to avoid failed or unsuitable datanodes.

## Risks and test signals
Over-aggressive cleanup can reintroduce bad nodes too soon; missing cleanup can starve placement. These tests signal expiry behavior around time boundaries.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/scm/container/common/helpers/TestExcludeList.java -->


<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/scm/container/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/scm/container/package-info.java

## Purpose
Declares package-level documentation for `org.apache.hadoop.hdds.scm.container` tests.

## Important APIs, types, and functions
- Contains only package documentation and the package declaration.
- No classes, methods, or runtime APIs are defined.

## Control flow
There is no executable control flow.

## State and persistence behavior
No state or persistence behavior exists in this file.

## Dependencies and integration points
The file contributes JavaDoc/package metadata for SCM container test sources.

## Risks and test signals
Risk is limited to package documentation drift or missing package declaration. There are no runtime test signals.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/scm/container/package-info.java -->


<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/scm/ha/TestSCMNodeInfo.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/scm/ha/TestSCMNodeInfo.java

## Purpose
Tests SCM high-availability node information extraction from `OzoneConfiguration`, including explicit HA service IDs, node IDs, addresses, and default ports.

## Important APIs, types, and functions
- Uses `SCMNodeInfo`, `OzoneConfiguration`, `ConfigurationException`, and `ScmConfigKeys`.
- Covers HA node info, default ports, missing SCM address validation, and non-HA REST/default behavior.
- Setup populates service and node configuration keys before each test.

## Control flow
The tests configure one or more SCM service/node entries, call SCM node-info builders, and assert the returned list contains expected host/port combinations or throws when required addresses are missing.

## State and persistence behavior
Configuration state is in-memory. It models persisted `ozone-site.xml` values without reading files.

## Dependencies and integration points
This is a guard for SCM HA bootstrap, node discovery, and address binding defaults.

## Risks and test signals
Bad config parsing can prevent SCM HA clusters from starting or bind them to wrong addresses. The tests signal defaults, required key validation, and non-HA compatibility.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/scm/ha/TestSCMNodeInfo.java -->


<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/scm/ha/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/scm/ha/package-info.java

## Purpose
Provides package-level JavaDoc for `org.apache.hadoop.hdds.scm.ha` tests.

## Important APIs, types, and functions
- Contains only package documentation and the package declaration.

## Control flow
No executable behavior is present.

## State and persistence behavior
No state or persistence behavior exists.

## Dependencies and integration points
The file integrates with generated JavaDoc and package metadata for SCM HA tests.

## Risks and test signals
Runtime risk is negligible; there are no direct tests in this file.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/scm/ha/package-info.java -->


<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/scm/net/TestNetUtils.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/scm/net/TestNetUtils.java

## Purpose
Tests normalization behavior in SCM network utility code.

## Important APIs, types, and functions
- Exercises `NetUtils.normalize` style behavior for network paths or node names.
- Uses JUnit assertions for normalized output variants.

## Control flow
The test feeds representative strings into the normalize function and asserts canonical output, including handling of separators or empty/default path shapes.

## State and persistence behavior
Pure string transformation; no state persists.

## Dependencies and integration points
SCM topology and placement code depend on stable network-location normalization.

## Risks and test signals
Incorrect normalization can misplace nodes in topology trees. This file signals canonical path formatting behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/scm/net/TestNetUtils.java -->


<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/scm/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/scm/package-info.java

## Purpose
Declares package-level documentation for SCM test sources.

## Important APIs, types, and functions
- Contains package JavaDoc and `org.apache.hadoop.hdds.scm` package declaration only.

## Control flow
No executable control flow.

## State and persistence behavior
No state or persistence behavior.

## Dependencies and integration points
Used by JavaDoc/package metadata tooling for SCM tests.

## Risks and test signals
No runtime risks or direct test signals.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/scm/package-info.java -->


<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/scm/pipeline/MockPipeline.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/scm/pipeline/MockPipeline.java

## Purpose
Provides factory helpers for constructing test `Pipeline` instances with standalone, Ratis, and EC replication configurations.

## Important APIs, types, and functions
- Public helpers include `createSingleNodePipeline`, overloaded `createPipeline`, `createRatisPipeline`, and overloaded `createEcPipeline`.
- Uses `Pipeline.Builder`, `PipelineID`, `DatanodeDetails`, `MockDatanodeDetails`, `DatanodeID`, `StandaloneReplicationConfig`, `RatisReplicationConfig`, and `ECReplicationConfig`.
- Builds replica-index maps for EC pipelines and node lists for replicated pipelines.

## Control flow
Factory methods allocate or accept datanodes, choose replication config, build the datanode list and optional replica-index map, assign a random pipeline ID, set pipeline state, and return a fully constructed `Pipeline`.

## State and persistence behavior
The helper creates in-memory test objects only. No real SCM pipeline state is persisted.

## Dependencies and integration points
Many tests use these helpers to create valid pipeline objects without standing up SCM or datanodes.

## Risks and test signals
Because it is test infrastructure, stale defaults can hide production contract changes. EC replica-index generation and node-count assumptions are the main maintenance risks.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/scm/pipeline/MockPipeline.java -->


<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestPipeline.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestPipeline.java

## Purpose
Tests `Pipeline` protobuf conversion, EC replica indexes, health semantics, builder copy behavior, replacement identity, and read-node targeting.

## Important APIs, types, and functions
- Uses `Pipeline`, `MockPipeline`, `PipelineID`, `DatanodeDetails`, `HddsProtos`, and replication config classes.
- Test cases include `protoIncludesNewPortsOnlyForV1`, `getProtobufMessageEC`, `testReplicaIndexesSerialisedCorrectly`, `testECPipelineIsAlwaysHealthy`, `testBuilderCopiesAllFieldsFromOtherPipeline`, `idChangedIfNodesReplaced`, `testCopyForReadFromNode`, and rejection of unknown read nodes.

## Control flow
The tests create pipelines, serialize to protobuf with specific client versions, inspect node/port and EC fields, copy builders, replace nodes, and build read-specific pipeline variants.

## State and persistence behavior
Pipelines are in-memory metadata objects. Protobuf conversion models wire/persisted state, especially client-version-sensitive datanode ports and EC replica indexes.

## Dependencies and integration points
Pipeline metadata is used by clients, SCM, and datanodes. Compatibility with protobuf client versions and EC topology is central.

## Risks and test signals
Risks include losing replica indexes, exposing incompatible ports to older clients, reusing IDs after node replacement, or accepting invalid read targets. The tests provide contract signals across these behaviors.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestPipeline.java -->


<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/security/TestSecurityConfigTlsSettings.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/security/TestSecurityConfigTlsSettings.java

## Purpose
Tests TLS protocol and cipher-suite parsing in `SecurityConfig`.

## Important APIs, types, and functions
- Uses `OzoneConfiguration` and `SecurityConfig`.
- Covers default protocols, single/multiple protocol values, whitespace trimming, empty protocol values, default ciphers, and multiple ciphers.

## Control flow
Each test sets relevant security configuration keys, constructs `SecurityConfig`, and asserts the returned protocol or cipher arrays/lists match expected values.

## State and persistence behavior
Configuration is in-memory. No keystores or certificates are persisted.

## Dependencies and integration points
`SecurityConfig` feeds TLS setup for Ozone/HDDS services and clients.

## Risks and test signals
Parsing errors can disable protocols unexpectedly or include malformed cipher names. These tests signal safe defaults and correct comma-separated value handling.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/security/TestSecurityConfigTlsSettings.java -->


<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/security/x509/CertificateTestUtils.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/security/x509/CertificateTestUtils.java

## Purpose
Provides reusable helpers for tests that need RSA key pairs and self-signed X.509 certificates.

## Important APIs, types, and functions
- Public helpers include `aKeyPair`, overloaded `createSelfSignedCert`, `subjectKeyIdOf`, `authorityKeyIdOf`, `pubKeyInfo`, and `extensionUtil`.
- Uses `SecurityConfig`, `HDDSKeyGenerator`, Bouncy Castle `X500Name`, `X509v3CertificateBuilder`, `JcaX509CertificateConverter`, key identifier utilities, and SHA/RSA algorithm identifiers.

## Control flow
Helpers generate a key pair from security configuration, build subject/issuer names and validity windows, attach basic constraints and key identifier extensions, sign the certificate, and convert it to a Java `X509Certificate`.

## State and persistence behavior
All certificate and key material is generated in memory. No files are written by this utility.

## Dependencies and integration points
This file is shared test infrastructure for HDDS certificate-authority, key, and TLS tests. It integrates Ozone security config with Bouncy Castle certificate generation.

## Risks and test signals
The helper can mask production certificate requirements if extensions or algorithms drift. Tests using it depend on sane validity periods, key IDs, and provider setup.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/security/x509/CertificateTestUtils.java -->


<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/security/x509/keys/TestHDDSKeyGenerator.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/security/x509/keys/TestHDDSKeyGenerator.java

## Purpose
Tests RSA key generation through `HDDSKeyGenerator` and `SecurityConfig`.

## Important APIs, types, and functions
- Uses `OzoneConfiguration`, `SecurityConfig`, `HDDSKeyGenerator`, `KeyPair`, `PublicKey`, `RSAPublicKey`, and `PKCS8EncodedKeySpec`.
- Test cases are `testGenerateKey` and `testGenerateKeyWithSize`.
- Initializes temporary security paths with `@TempDir`.

## Control flow
Setup configures security-related base directories, then tests generate key pairs with default and configured sizes and assert algorithm/type/bit-length properties.

## State and persistence behavior
Key pairs are generated in memory. Temporary directory configuration is present but this generator test does not validate persistent key storage.

## Dependencies and integration points
The generator feeds HDDS certificate/key storage and CA initialization flows.

## Risks and test signals
Wrong algorithms or key sizes weaken TLS and certificate behavior. The test signals that configured RSA key size is honored.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/security/x509/keys/TestHDDSKeyGenerator.java -->


<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/security/x509/keys/TestKeyCodec.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/security/x509/keys/TestKeyCodec.java

## Purpose
Tests PEM/DER-style key encoding and decoding behavior in `KeyCodec`.

## Important APIs, types, and functions
- Uses `KeyCodec`, `SecurityConstants`, `KeyPairGenerator`, and Java `KeyPair` APIs.
- Covers unknown encoding failure and parameterized public/private key encode-decode round trips for configured encodings.

## Control flow
The tests generate RSA keys, encode public or private keys through the codec, decode the bytes back, and assert equality with the original key. An invalid encoding path asserts exception behavior.

## State and persistence behavior
All key material is in memory. Encoded byte arrays represent persisted key-file payloads but are not necessarily written to disk here.

## Dependencies and integration points
`KeyCodec` is used by `KeyStorage` and security bootstrap code to read/write key files.

## Risks and test signals
Encoding drift can make existing key files unreadable. These tests signal compatibility for supported encodings and fail-fast behavior for invalid encodings.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/security/x509/keys/TestKeyCodec.java -->


<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/security/x509/keys/TestKeyStorage.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/security/x509/keys/TestKeyStorage.java

## Purpose
Tests `KeyStorage` behavior for internal and external CA key storage, including read/write round trips, permissions, overwrite protection, and failure paths.

## Important APIs, types, and functions
- Uses `KeyStorage`, `KeyCodec`, `SecurityConfig`, RSA `KeyPair`, `PrivateKey`, `PublicKey`, and POSIX permission constants `DIR_PERMISSIONS` and `FILE_PERMISSIONS`.
- Internal-CA nested tests cover `storeKeyPair`, `storePrivateKey`, `storePublicKey`, `readPrivateKey`, `readPublicKey`, `readKeyPair`, suffixed storage paths, codec failures, IO failures, overwrite rejection, and initialization failures.
- External-CA nested tests cover reading configured external key paths and rejecting writes.
- Uses Mockito to simulate `FileSystemProvider`, `FileSystem`, `Path`, and codec exceptions.

## Control flow
A static RSA key pair is generated once. Each test configures mocked `SecurityConfig` paths and codec behavior. Internal storage tests write keys to a temp directory, assert files and permissions, decode file contents, and read through `KeyStorage`. Failure tests replace codec or filesystem behavior to force exceptions. External storage tests pre-create key files and verify read-only access.

## State and persistence behavior
This file actively writes temporary key files and validates filesystem permissions. It models production key persistence under component-specific security directories and external CA key paths.

## Dependencies and integration points
`KeyStorage` is part of HDDS security bootstrap and CA/key management. It integrates `SecurityConfig`, filesystem permissions, key encoding, and external CA configuration.

## Risks and test signals
Risks include overwriting private keys, writing with weak permissions, failing to read external CA keys, and obscuring IO/codec errors. The suite gives strong signals for key-file durability, read-only external CA semantics, and permission enforcement.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/security/x509/keys/TestKeyStorage.java -->


<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/security/x509/keys/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/security/x509/keys/package-info.java

## Purpose
Declares package documentation for X.509 key-related tests.

## Important APIs, types, and functions
- Contains package JavaDoc and `org.apache.hadoop.hdds.security.x509.keys` declaration only.

## Control flow
No executable control flow.

## State and persistence behavior
No runtime state or persistence.

## Dependencies and integration points
Supports package metadata for HDDS security key tests.

## Risks and test signals
No direct runtime risk or test signal.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/security/x509/keys/package-info.java -->


<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/security/x509/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/security/x509/package-info.java

## Purpose
Provides package-level documentation for X.509 certificate-related test utilities and tests.

## Important APIs, types, and functions
- Contains JavaDoc and the `org.apache.hadoop.hdds.security.x509` package declaration.
- No executable classes or methods are defined.

## Control flow
No executable control flow.

## State and persistence behavior
No state or persistence behavior.

## Dependencies and integration points
Documents the package containing certificate test helpers and X.509 security tests.

## Risks and test signals
No direct runtime test signal; risk is limited to stale package documentation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/security/x509/package-info.java -->


<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/tracing/TestLoopSampler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/tracing/TestLoopSampler.java

## Purpose
Tests `LoopSampler`, a deterministic ratio-based sampling helper used by tracing samplers.

## Important APIs, types, and functions
- Exercises constructor validation and `shouldSample` behavior for negative, zero, one, above-one, and half sampling ratios.
- Test cases include `negativeRatioThrows`, `zeroNeverSamples`, `oneAlwaysSamples`, `aboveOneIsCappedToAlwaysSample`, and `halfSamplesStatistically`.

## Control flow
The tests instantiate samplers with representative ratios and call the sampling decision repeatedly, asserting deterministic always/never behavior or approximate statistical behavior for 0.5.

## State and persistence behavior
Sampler state is in-memory counters/randomness used to decide sampling. No persistence.

## Dependencies and integration points
`LoopSampler` underlies trace and span sampling configuration in HDDS tracing.

## Risks and test signals
Bad ratio handling can produce too many or too few spans. Tests signal bounds handling and practical midpoint sampling behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/tracing/TestLoopSampler.java -->


<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/tracing/TestSpanSampling.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/tracing/TestSpanSampling.java

## Purpose
Tests span-specific OpenTelemetry sampling configuration and behavior.

## Important APIs, types, and functions
- Uses OpenTelemetry `Sampler`, `SamplingResult`, `SamplingDecision`, `SpanContext`, `TraceFlags`, `TraceState`, `SpanKind`, `Attributes`, and `Context`.
- Exercises parsing of span sampling config maps, invalid/malformed entries, rate clamping, child-span sampling decisions, and sampler descriptions.
- Uses configured span names and parent contexts to distinguish root trace decisions from child span decisions.

## Control flow
Parsing tests convert configuration strings to name-to-rate maps. Sampling tests create sampled and unsampled parent contexts, invoke the sampler with span names, and assert record/drop decisions according to trace-level and span-level sampling rules.

## State and persistence behavior
State consists of in-memory maps of span names to sampler ratios and OpenTelemetry context objects. No persistence.

## Dependencies and integration points
This file covers HDDS tracing integration with OpenTelemetry SDK sampling APIs.

## Risks and test signals
Incorrect parsing or parent handling can flood tracing backends or lose important child spans. The suite signals malformed-config tolerance, rate caps, parent unsampled behavior, and configured span overrides.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/tracing/TestSpanSampling.java -->


<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/tracing/TestTraceAllMethod.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/tracing/TestTraceAllMethod.java

## Purpose
Tests tracing proxy behavior for interfaces annotated to trace all methods, including default methods and unknown methods.

## Important APIs, types, and functions
- Defines a `Service` interface and `ServiceImpl` test implementation with normal, skipped, throwing, and default methods.
- Uses OpenTelemetry `Span.current()` to detect active span state.
- Tests `testUnknownMethod` and `testDefaultMethod` through `TracingUtil.createProxy` behavior.

## Control flow
Proxy instances invoke service methods through tracing utilities. The implementation records whether a span is active, while tests assert default method dispatch and behavior when a method is not matched to a concrete implementation path.

## State and persistence behavior
State is limited to the implementation's boolean span-active observation. No persistence.

## Dependencies and integration points
The file provides fixtures reused by `TestTracingUtil` and guards dynamic proxy tracing around Java interface/default method semantics.

## Risks and test signals
Dynamic proxy tracing can mishandle default methods or exception unwrapping. This test signals proxy dispatch correctness and span activation boundaries.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/tracing/TestTraceAllMethod.java -->


<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/tracing/TestTracingConfig.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/tracing/TestTracingConfig.java

## Purpose
Tests typed tracing configuration parsing for trace sampling ratio, tracing endpoint, and explicit span sampling rules.

## Important APIs, types, and functions
- Uses `InMemoryConfigurationForTesting`, `MutableConfigurationSource`, and `TracingConfig`.
- Covers clamping ratios above one, valid ratios, negative ratio handling, explicit endpoint, and span sampling config string parsing.

## Control flow
Tests set tracing configuration keys in memory, bind to `TracingConfig`, and assert normalized values returned by getters.

## State and persistence behavior
Configuration is in-memory only. It models persisted Ozone config keys without disk IO.

## Dependencies and integration points
`TracingConfig` feeds `TracingUtil.initTracing` and OpenTelemetry exporter/sampler setup.

## Risks and test signals
Bad config normalization can over-sample, under-sample, or target the wrong collector endpoint. The tests signal bounds and explicit override behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/tracing/TestTracingConfig.java -->


<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/tracing/TestTracingUtil.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/tracing/TestTracingUtil.java

## Purpose
Tests `TracingUtil` initialization, proxy creation, span creation/export/import, child span execution, exception propagation, and text-map extraction.

## Important APIs, types, and functions
- Uses `TracingUtil.createProxy`, `initTracing`, `createActivatedSpan`, `exportCurrentSpan`, `importAndCreateSpan`, `executeInNewSpan`, `executeAsChildSpan`, and `TextExtractor`.
- Uses OpenTelemetry `Span`, `SpanContext`, and `Scope`.
- Reuses `TestTraceAllMethod.Service` and `ServiceImpl` fixtures.

## Control flow
The tests enable tracing in memory, initialize tracing services, create proxies, invoke normal and `@SkipTracing` methods, export W3C `traceparent` carriers, import parent contexts into child spans, run callbacks under new spans, and inspect text extractor behavior for empty or malformed carriers.

## State and persistence behavior
Tracing provider/context state is process-local. Span carriers are strings representing propagated trace context. No external collector or persistent trace store is required.

## Dependencies and integration points
The file covers HDDS tracing integration with OpenTelemetry context propagation and Java dynamic proxies.

## Risks and test signals
Risks include leaking spans into skipped methods, wrapping exceptions incorrectly, losing parent trace IDs, and accepting malformed carrier strings incorrectly. The suite signals core tracing correctness without depending on a live tracing backend.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/tracing/TestTracingUtil.java -->


<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/tracing/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/tracing/package-info.java

## Purpose
Declares package-level documentation for tracing tests.

## Important APIs, types, and functions
- Contains package JavaDoc and `org.apache.hadoop.hdds.tracing` declaration only.

## Control flow
No executable behavior.

## State and persistence behavior
No state or persistence behavior.

## Dependencies and integration points
Provides package metadata for tracing test sources.

## Risks and test signals
No direct runtime test signal.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/tracing/package-info.java -->


<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/utils/MockGatheringChannel.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/utils/MockGatheringChannel.java

## Purpose
Implements a test `GatheringByteChannel`/`WritableByteChannel` that captures writes and can simulate partial write behavior.

## Important APIs, types, and functions
- Implements `write(ByteBuffer)`, `write(ByteBuffer[])`, `write(ByteBuffer[], int, int)`, `isOpen`, and `close`.
- Uses `adjustedWrite` to limit or randomize the number of bytes accepted.
- Exposes behavior for tests that need gathering-channel semantics without real IO.

## Control flow
Write methods iterate through buffers, compute allowed write size, copy bytes from source buffers into an internal sink or counters, and return the number of bytes written. `close` flips channel state; `isOpen` reports it.

## State and persistence behavior
State is in-memory channel-open status and captured/counted bytes. No disk or socket IO occurs.

## Dependencies and integration points
Used by chunk buffer and codec tests to verify write-to-channel behavior and partial-write handling.

## Risks and test signals
If the mock diverges from `GatheringByteChannel` semantics, tests may pass unrealistic write loops. Partial-write simulation is the key integration signal.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/utils/MockGatheringChannel.java -->


<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/utils/TestHddsIdFactory.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/utils/TestHddsIdFactory.java

## Purpose
Tests concurrent uniqueness of IDs produced by `HddsIdFactory`.

## Important APIs, types, and functions
- Uses `HddsIdFactory.getLongId`, `ExecutorService`, `Callable`, `Future`, and a concurrent set.
- Defines cleanup for executor shutdown and helper `addTasks` to submit work.

## Control flow
The test starts multiple tasks that request IDs concurrently, collects them into a concurrent set, waits for all tasks, and asserts no duplicate IDs are produced.

## State and persistence behavior
State is in-memory ID generator state and concurrent collections. No persistence.

## Dependencies and integration points
`HddsIdFactory` supplies unique IDs across HDDS components; concurrency safety is critical for metadata identifiers.

## Risks and test signals
Race conditions in ID generation could cause duplicate metadata IDs. This test signals thread-safety under parallel access.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/utils/TestHddsIdFactory.java -->


<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/utils/TestIOUtils.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/utils/TestIOUtils.java

## Purpose
Tests null-safe close behavior in HDDS `IOUtils`.

## Important APIs, types, and functions
- Uses `IOUtils.closeQuietly` with a null closeable and a `ByteArrayOutputStream` import context.
- Test case is `closeQuietlyNull`.

## Control flow
The test calls the close helper with null and expects no exception.

## State and persistence behavior
No meaningful state or persistence; the focus is defensive close behavior.

## Dependencies and integration points
Close helpers are used broadly in IO cleanup paths where nulls may occur after failed initialization.

## Risks and test signals
A null-unsafe close helper can turn cleanup paths into secondary failures. This test signals null tolerance.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/utils/TestIOUtils.java -->


<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/utils/TestProtobufUtils.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/utils/TestProtobufUtils.java

## Purpose
Tests UUID conversion between Java `UUID` and HDDS protobuf UUID representation.

## Important APIs, types, and functions
- Uses `ProtobufUtils`, `HddsProtos.UUID`, and Java `UUID`.
- Test cases are `testUuidToProtobuf` and `testUuidConversion`.

## Control flow
The tests create UUID values, convert to protobuf, inspect most/least-significant bit fields, convert back, and assert equality.

## State and persistence behavior
The protobuf representation models persisted or wire-format UUID state. No actual store is used.

## Dependencies and integration points
UUID conversion is used across HDDS protobuf APIs for datanodes, pipelines, and other identifiers.

## Risks and test signals
Swapping UUID bit order would corrupt identity matching. These tests signal exact bit-preserving conversion.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/utils/TestProtobufUtils.java -->


<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/utils/TestResourceCache.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/utils/TestResourceCache.java

## Purpose
Tests `ResourceCache` lifecycle behavior: caching, removal, conditional removal, and clearing with cleanup callbacks.

## Important APIs, types, and functions
- Uses `ResourceCache`, `AtomicLong`, and `Consumer` cleanup callbacks.
- Test cases include `testResourceCache`, `testRemove`, `testRemoveIf`, and `testClear`.

## Control flow
Tests request resources by key, verify cache hits reuse existing resources, remove specific entries or entries matching predicates, and assert cleanup counters/callbacks run for evicted resources.

## State and persistence behavior
The cache is an in-memory map of keys to resources plus cleanup side effects. No persistence.

## Dependencies and integration points
Resource caching supports shared expensive objects in HDDS utilities while ensuring deterministic cleanup.

## Risks and test signals
Bugs can leak resources or prematurely close shared ones. Tests signal reuse and cleanup behavior for each eviction path.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/utils/TestResourceCache.java -->


<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/utils/TestRetriableTask.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/utils/TestRetriableTask.java

## Purpose
Tests `RetriableTask` execution behavior under success, transient failures, and retry-policy termination.

## Important APIs, types, and functions
- Uses `RetriableTask`, Hadoop `RetryPolicy`, `RetryPolicies`, `TimeUnit`, `AtomicInteger`, `IOException`, and `ZipException`.
- Test cases are `returnsSuccessfulResult`, `returnsSuccessfulResultAfterFailures`, and `respectsRetryPolicy`.

## Control flow
The tests construct tasks that either return immediately, fail a fixed number of times before succeeding, or fail with a policy-controlled exception. They assert returned results and retry counts/policy outcomes.

## State and persistence behavior
State is limited to in-memory retry counters and exceptions. No persistence.

## Dependencies and integration points
`RetriableTask` wraps retry policy behavior used by HDDS operations that need transient failure tolerance.

## Risks and test signals
Incorrect retry-loop control can cause premature failure, infinite retries, or ignored exception classes. These tests signal basic policy adherence.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/utils/TestRetriableTask.java -->


<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/utils/TestSimpleStriped.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/utils/TestSimpleStriped.java

## Purpose
Tests `SimpleStriped` read/write lock behavior against Guava-style striped locks.

## Important APIs, types, and functions
- Uses `SimpleStriped`, Guava `Striped`, `ReadWriteLock`, and `ReentrantReadWriteLock`.
- Test case is `testReadWriteLocks`.

## Control flow
The test creates striped read/write locks, retrieves locks for keys, and asserts lock identity/behavior matches expected striping semantics.

## State and persistence behavior
State is in-memory lock arrays/stripes. No persistence.

## Dependencies and integration points
Striped locks are used to reduce lock cardinality while protecting keyed resources in HDDS.

## Risks and test signals
Incorrect striping can map keys inconsistently or allocate wrong lock types. This test signals basic lock factory behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/utils/TestSimpleStriped.java -->


<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/utils/TestSlidingWindow.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/utils/TestSlidingWindow.java

## Purpose
Tests `SlidingWindow` event counting/expiration behavior with a controllable clock.

## Important APIs, types, and functions
- Uses `SlidingWindow`, `Duration`, and `TestClock`.
- Covers constructor validation, adding events, full expiration, partial expiration, and zero window size.

## Control flow
Setup creates a test clock and sliding window. Tests add events, advance time, and assert window counts after no expiration, partial expiration, complete expiration, and zero-duration cases.

## State and persistence behavior
State is in-memory timestamped event buckets. No persistence.

## Dependencies and integration points
Sliding-window counters are useful for rate or recent-event tracking in HDDS utilities.

## Risks and test signals
Boundary mistakes can overcount or undercount recent activity. The tests signal time-window edge behavior using deterministic time.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/utils/TestSlidingWindow.java -->


<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/utils/db/CodecTestUtil.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/utils/db/CodecTestUtil.java

## Purpose
Provides reusable assertions for testing HDDS database `Codec` implementations, including codec-buffer and persisted-format behavior.

## Important APIs, types, and functions
- Public helpers include `runTest`, `newCodecWithoutCodecBuffer`, `toPersistedFormat`, `fromPersistedFormat`, `getTypeClass`, `copyObject`, and `gc`.
- Uses `Codec`, `CodecBuffer`, `ByteBuffer`, weak references, and logging.
- Checks object equality, serialized byte behavior, copied object behavior, and buffer cleanup expectations.

## Control flow
`runTest` executes a codec through persisted-format conversion, object restoration, optional object copy, type-class verification, and buffer lifecycle checks. Helper wrappers adapt codecs that do not support `CodecBuffer` directly.

## State and persistence behavior
The byte arrays and buffers represent persisted database values, but tests remain in memory. `gc` and weak references are used to probe object/buffer retention behavior.

## Dependencies and integration points
HDDS metadata stores rely on codecs for RocksDB/table serialization. This utility standardizes codec contract tests.

## Risks and test signals
Codec bugs can corrupt persisted metadata or leak buffers. This helper gives shared signals for serialization fidelity, copy semantics, and buffer cleanup.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/utils/db/CodecTestUtil.java -->


<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/utils/db/Proto2CodecTestBase.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/utils/db/Proto2CodecTestBase.java

## Purpose
Abstract base test for protobuf-v2-backed `Codec` implementations.

## Important APIs, types, and functions
- Requires subclasses to provide `getCodec`.
- Tests invalid protobuf bytes, `fromPersistedFormat`, and `toPersistedFormat`.
- Uses `InvalidProtocolBufferException` and JUnit assertions.

## Control flow
The base tests feed invalid bytes to the codec and expect parse failure, then exercise serialization and deserialization of valid subclass-provided values through the codec contract.

## State and persistence behavior
Serialized byte arrays model persisted database values. No external DB is used.

## Dependencies and integration points
Subclasses can inherit these tests to validate HDDS protobuf codecs used by metadata tables.

## Risks and test signals
A codec that accepts invalid bytes or emits non-round-trippable data can corrupt metadata reads. This base class signals core protobuf codec correctness.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/utils/db/Proto2CodecTestBase.java -->


<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/utils/db/TestLeakDetector.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/utils/db/TestLeakDetector.java

## Purpose
Tests the DB package `LeakDetector` utility.

## Important APIs, types, and functions
- Uses the `LeakDetector` class from `org.apache.hadoop.hdds.utils.db` and JUnit assertions.
- The single test named `test` validates expected leak detector behavior.

## Control flow
The test creates detector-managed resources or markers and verifies the detector reports expected non-leak/leak behavior according to its API.

## State and persistence behavior
State is in-memory detector tracking. No external persistence.

## Dependencies and integration points
The detector is related to DB codec/buffer lifecycle checks where unclosed buffers are a risk.

## Risks and test signals
If leak detection fails, DB buffer leaks may go unnoticed or tests may become flaky. This file provides a focused detector smoke test.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/utils/db/TestLeakDetector.java -->


<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/utils/io/TestRandomAccessFileChannel.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/utils/io/TestRandomAccessFileChannel.java

## Purpose
Tests safe lifecycle and read behavior of `RandomAccessFileChannel`.

## Important APIs, types, and functions
- Uses `RandomAccessFileChannel`, `RandomAccessFile`, `FileChannel`, reflection helpers, `ByteBuffer`, and temporary files.
- Covers open failure cleanup, idempotent close, closing both channel and RAF when one close fails, null close safety, zero-sized reads, and try-with-resources closing.
- Helper methods include `closeAndVerify` and `setField`.

## Control flow
Tests construct or partially mock channel internals, invoke close/read operations, inject failing close behavior where needed, and assert no leaks or expected return values/exceptions.

## State and persistence behavior
Uses temporary files and Java file channels. It validates OS resource cleanup but does not depend on durable data beyond temp-file lifecycle.

## Dependencies and integration points
The wrapper is used by HDDS/Ozone IO paths requiring random-access reads with robust close semantics.

## Risks and test signals
File descriptor leaks and close masking are the primary risks. The tests signal cleanup correctness across construction and close failure cases.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/utils/io/TestRandomAccessFileChannel.java -->


<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/utils/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/utils/package-info.java

## Purpose
Declares package documentation for HDDS utility tests.

## Important APIs, types, and functions
- Contains only package JavaDoc and the `org.apache.hadoop.hdds.utils` package declaration.

## Control flow
No executable control flow.

## State and persistence behavior
No state or persistence behavior.

## Dependencies and integration points
Supports package-level metadata for utility test sources.

## Risks and test signals
No runtime test signal.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/utils/package-info.java -->


<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/io_/retry/TestRetryProxy.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/io_/retry/TestRetryProxy.java

## Purpose
Tests Hadoop-compatible retry proxy behavior in the shaded `org.apache.hadoop.io_` retry package.

## Important APIs, types, and functions
- Uses `RetryProxy`, `RetryPolicies`, `RetryPolicy`, `RetryAction`, `RetryDecision`, `FailoverProxyProvider`, and the local `UnreliableInterface`/`UnreliableImplementation` fixtures.
- Covers try-once failure, RPC invocation metadata, retry forever, fixed sleep retry, maximum-count retry, exponential retry, interruptible retry, SASL no-retry, access-control no-retry, and wrapped access-control handling.
- Uses Mockito to delegate mocked policy decisions to real policies while capturing the final retry action.

## Control flow
Setup creates an unreliable implementation. Tests wrap it in `RetryProxy` with different policies, invoke methods that succeed, fail once, fail many times, or throw fatal/security exceptions, and assert call counts, returned results, thrown exceptions, and policy decisions.

## State and persistence behavior
State is in-memory retry counters inside `UnreliableImplementation` and captured retry actions. No persistence.

## Dependencies and integration points
This package preserves Hadoop retry semantics for Ozone code paths that use retry proxies without depending directly on Hadoop package names.

## Risks and test signals
Incorrect proxy logic can retry non-retriable security failures, fail to retry transient failures, or lose invocation metadata. The suite gives broad behavior signals for retry policy integration.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/io_/retry/TestRetryProxy.java -->


<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/io_/retry/UnreliableImplementation.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/io_/retry/UnreliableImplementation.java

## Purpose
Provides a test implementation of `UnreliableInterface` with methods that succeed or fail in controlled ways for retry tests.

## Important APIs, types, and functions
- Implements `alwaysSucceeds`, `alwaysFailsWithFatalException`, `failsOnceThenSucceeds`, `failsTenTimesThenSucceeds`, `failsWithSASLExceptionTenTimes`, `failsWithAccessControlExceptionEightTimes`, and `failsWithWrappedAccessControlException`.
- Throws `IOException`, `SaslException`, `AccessControlException`, local `UnreliableException`, and `FatalException` depending on method.
- Maintains counters for controlled failure counts.

## Control flow
Each method increments internal counters and either throws until a threshold is reached or returns success immediately. Security-related methods throw exceptions that retry policies should not retry indefinitely.

## State and persistence behavior
State is in-memory call counters. No persistence.

## Dependencies and integration points
Used directly by `TestRetryProxy` as the target object behind retry proxies.

## Risks and test signals
If fixture behavior changes, retry tests may stop validating intended policy branches. Its value is deterministic failure sequencing.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/io_/retry/UnreliableImplementation.java -->


<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/io_/retry/UnreliableInterface.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/io_/retry/UnreliableInterface.java

## Purpose
Defines the retry-test contract implemented by `UnreliableImplementation`.

## Important APIs, types, and functions
- Declares methods that always succeed, always fail fatally, fail once, fail ten times, and fail with SASL or access-control exceptions.
- Defines nested exception types `UnreliableException` and `FatalException`.
- Uses Hadoop retry annotations such as `@Idempotent` where relevant and imports retry interfaces.

## Control flow
As an interface, it has no implementation control flow beyond method signatures and exception contracts.

## State and persistence behavior
No state or persistence in the interface.

## Dependencies and integration points
Used by `RetryProxy` tests to generate dynamic proxies with known method exception signatures and idempotency metadata.

## Risks and test signals
The interface is a fixture contract; changing signatures or annotations changes what retry proxy behavior is exercised.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/io_/retry/UnreliableInterface.java -->


<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/ozone/TestOzoneConsts.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/ozone/TestOzoneConsts.java

## Purpose
Tests compatibility of Ozone tenant policy label constants.

## Important APIs, types, and functions
- Uses `OzoneConsts` tenant-policy label constants.
- Test case is `testOzoneTenantPolicyLabelCompatibility`.

## Control flow
The test compares current constants to expected compatibility values.

## State and persistence behavior
No mutable state or persistence.

## Dependencies and integration points
Tenant policy labels may be consumed by external APIs, persisted metadata, or authorization policy integration.

## Risks and test signals
Renaming constants can break compatibility. This test is a direct constant-value guard.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/ozone/TestOzoneConsts.java -->


<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/ozone/common/NativeCheckSumCRC32.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/ozone/common/NativeCheckSumCRC32.java

## Purpose
Provides a test checksum adapter around Hadoop native CRC32 support for comparing checksum implementations.

## Important APIs, types, and functions
- Implements Java `Checksum`-style methods `update(int)`, `update(byte[], int, int)`, `getValue`, and `reset`.
- Uses `NativeCRC32Wrapper` for native CRC operations and throws `NotImplementedException` for unsupported update shapes where applicable.
- Supports `ByteBuffer`-oriented native checksum comparison in tests.

## Control flow
The adapter forwards supported update calls to the native wrapper, returns the native checksum value, and resets native state when requested.

## State and persistence behavior
State is native checksum accumulator state. No persistence.

## Dependencies and integration points
Used by checksum comparison tests to ensure Ozone checksum code matches native Hadoop implementations.

## Risks and test signals
Native checksum availability and API limitations can affect tests. The adapter isolates native behavior for cross-implementation validation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/ozone/common/NativeCheckSumCRC32.java -->


<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/ozone/common/TestChecksum.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/ozone/common/TestChecksum.java

## Purpose
Tests Ozone `Checksum` computation and verification for chunk data.

## Important APIs, types, and functions
- Uses `Checksum`, `ChecksumData`, `OzoneChecksumException`, `ContainerProtos.ChecksumType`, and `ByteBuffer`.
- Parameterized helpers cover different checksum types through `getChecksum`, `testVerifyChecksum`, `testIncorrectChecksum`, and `testChecksumMismatchForDifferentChecksumTypes`.

## Control flow
Tests generate random/string data, compute checksum data, verify correct buffers pass, mutate data or checksum type, and assert mismatch exceptions for invalid cases.

## State and persistence behavior
Checksum data represents metadata persisted with chunks, but test state is in memory.

## Dependencies and integration points
Checksum verification protects Ozone container chunk IO and small-file/write paths.

## Risks and test signals
Incorrect checksum verification can accept corrupted data or reject valid data. Tests signal positive verification and mismatch detection across algorithms.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/ozone/common/TestChecksum.java -->


<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/ozone/common/TestChecksumByteBuffer.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/ozone/common/TestChecksumByteBuffer.java

## Purpose
Tests checksum factories over heap and direct `ByteBuffer` inputs.

## Important APIs, types, and functions
- Uses Java `Checksum`, `ByteBuffer`, `PureJavaCrc32`, `PureJavaCrc32C`, and Ozone byte-buffer checksum factory helpers.
- Test cases are `testCrc32ByteBufferFactory`, `testCrc32CByteBufferFactory`, and `testWithDirectBuffer`.
- Inner `VerifyChecksumByteBuffer` compares implementations.

## Control flow
The tests feed equivalent data through checksum implementations using byte arrays, heap buffers, and direct buffers, then compare final checksum values.

## State and persistence behavior
State is checksum accumulator state and buffer positions. No persistence.

## Dependencies and integration points
Ozone checksum computation must work for direct buffers used in high-performance IO paths.

## Risks and test signals
A factory that mishandles direct buffers or buffer positions can corrupt checksum validation. These tests signal parity with known Java CRC implementations.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/ozone/common/TestChecksumByteBuffer.java -->


<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/ozone/common/TestChecksumCache.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/ozone/common/TestChecksumCache.java

## Purpose
Tests checksum caching/reuse behavior for Ozone checksum algorithms.

## Important APIs, types, and functions
- Uses `Checksum`, `Checksum.Algorithm`, `ContainerProtos.ChecksumType`, `ByteString`, and `ByteBuffer`.
- Parameterized tests iterate over checksum types/algorithms and functions that compute checksum bytes.

## Control flow
For each algorithm, tests compute checksum data for buffers and compare outputs across cached/reused checksum instances or computation paths.

## State and persistence behavior
State is in-memory checksum object cache and generated checksum bytes. No persistence.

## Dependencies and integration points
Checksum caching affects hot chunk IO paths by reducing object allocation while preserving correctness.

## Risks and test signals
Reusing checksum instances without reset can produce wrong values. Tests signal cache correctness across algorithms.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/ozone/common/TestChecksumCache.java -->


<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/ozone/common/TestChecksumImplsComputeSameValues.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/ozone/common/TestChecksumImplsComputeSameValues.java

## Purpose
Compares multiple CRC32 and CRC32C implementations to ensure they compute identical values.

## Important APIs, types, and functions
- Uses Java `CRC32`, Hadoop `PureJavaCrc32`, `PureJavaCrc32C`, `NativeCRC32Wrapper`, and `NativeCheckSumCRC32`.
- Test cases are `testCRC32ImplsMatch`, `testCRC32CImplsMatch`, and helper `validateImpls`.

## Control flow
The tests generate random data, feed the same buffers through each implementation, and assert all reported checksum values match.

## State and persistence behavior
Only checksum accumulators and random test buffers are used. No persistence.

## Dependencies and integration points
Ozone may use native or pure-Java checksum implementations depending on platform/runtime. Parity is essential for data integrity.

## Risks and test signals
Platform-specific checksum drift would cause false corruption reports or missed corruption. These tests signal implementation equivalence.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/ozone/common/TestChecksumImplsComputeSameValues.java -->


<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/ozone/common/TestChunkBuffer.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/ozone/common/TestChunkBuffer.java

## Purpose
Tests common `ChunkBuffer` behavior across byte-buffer, incremental, and list-backed implementations.

## Important APIs, types, and functions
- Uses `ChunkBuffer`, `ByteBuffer`, `ByteString`, `MockGatheringChannel`, `CodecBuffer`, and `CodecTestUtil`.
- Test cases include `testImplWithByteBuffer`, `testIncrementalChunkBuffer`, and `testImplWithList`.
- Helper assertions cover duplication, iteration, conversion to `ByteString`, and writing to channels/output streams.

## Control flow
The tests build buffers with random data, run a shared test routine across implementations, duplicate buffers, iterate chunks, convert to protobuf `ByteString`, and write through gathering channels while validating positions and content.

## State and persistence behavior
State is in-memory byte buffer content, positions, and chunk-buffer lifecycle. `CodecBuffer` cleanup is checked to avoid buffer leaks. No durable persistence.

## Dependencies and integration points
`ChunkBuffer` is used throughout Ozone chunk IO, checksum calculation, and protobuf conversion.

## Risks and test signals
Risks include incorrect buffer position handling, content loss across duplicate/iterate/write, and memory leaks. The tests provide broad implementation-contract coverage.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/ozone/common/TestChunkBuffer.java -->


<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/ozone/common/TestChunkBufferImplWithByteBufferList.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/ozone/common/TestChunkBufferImplWithByteBufferList.java

## Purpose
Tests validation and iteration behavior for the list-backed `ChunkBuffer` implementation.

## Important APIs, types, and functions
- Uses list-backed chunk buffer creation, `ByteBuffer`, Guava `ImmutableList`, and `BufferOverflowException`.
- Covers null list rejection, empty list acceptance, multiple-current-buffer rejection, and iteration with chunk sizes smaller, equal to, or larger than component buffers.

## Control flow
Tests allocate buffers with controlled positions/limits, construct list-backed chunk buffers, then iterate with requested chunk sizes and assert produced chunks and empty behavior.

## State and persistence behavior
State is in-memory buffer list position/limit state. No persistence.

## Dependencies and integration points
List-backed buffers support chunk data assembled from multiple byte buffers, including incremental/chained IO paths.

## Risks and test signals
Incorrect iteration can merge/split data wrongly or overflow target chunks. Tests signal constructor validation and boundary behavior across buffer-list shapes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/ozone/common/TestChunkBufferImplWithByteBufferList.java -->


<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/ozone/common/TestStateMachine.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/ozone/common/TestStateMachine.java

## Purpose
Tests generic `StateMachine` transition behavior with local enum states and events.

## Important APIs, types, and functions
- Defines local `STATES` and `EVENTS` enums.
- Uses `StateMachine`, `InvalidStateTransitionException`, and set utilities.
- Test case is `testStateMachineStates`.

## Control flow
The test builds a state machine with allowed transitions, exercises valid transitions, checks final states, and asserts invalid transitions throw the expected exception.

## State and persistence behavior
State is in-memory current-state tracking inside the state machine. No persistence.

## Dependencies and integration points
The generic state-machine utility can be reused by Ozone lifecycle components.

## Risks and test signals
A broken transition table can allow invalid lifecycle transitions or reject valid ones. This test signals core transition enforcement.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/ozone/common/TestStateMachine.java -->


<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/ozone/container/ContainerTestHelper.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/ozone/container/ContainerTestHelper.java

## Purpose
Provides a large collection of static helpers for building container protocol requests, responses, block/chunk metadata, data buffers, checksums, pipelines, and temporary files for Ozone container tests.

## Important APIs, types, and functions
- Helpers include `getChunk`, `getData`, `setDataChecksum`, `getWriteChunkRequest`, `getListBlockRequest`, `getPutBlockRequest`, `newWriteChunkRequestBuilder`, `getWriteSmallFileRequest`, `getReadSmallFileRequest`, `getReadChunkRequest`, `newReadChunkRequestBuilder`, `getCreateContainerRequest`, `getCreateContainerSecureRequest`, `getUpdateContainerRequest`, `getCreateContainerResponse`, and further response/request builders.
- Uses container protobufs such as `ContainerCommandRequestProto`, `ContainerCommandResponseProto`, `DatanodeBlockID`, `KeyValue`, checksum fields, and command-specific request/response types.
- Uses `BlockID`, container `BlockData`, `ChunkInfo`, `Checksum`, `ChunkBuffer`, `ClientVersion`, `Token`, `UniqueId`, `Pipeline`, and `MockPipeline`.

## Control flow
Most helpers build valid protobuf request builders from IDs, pipeline metadata, datanode UUIDs, block IDs, chunk data, checksums, and optional tokens. Data helpers create random buffers and reset positions after checksum computation. File helpers write/read temporary data for tests that need on-disk chunk content.

## State and persistence behavior
The helper mostly creates in-memory protocol objects, but some methods write temporary files or read file contents. Static constants provide dummy container and datanode IDs for repeatable test construction.

## Dependencies and integration points
This is central shared test infrastructure for Ozone container, datanode, and client command tests. It integrates SCM pipeline helpers, container common helper classes, protobuf protocol definitions, checksum logic, and security tokens.

## Risks and test signals
Because many tests depend on these builders, incorrect defaults can create unrealistic requests or hide protocol changes. Key risks are stale client-version fields, missing checksum data, wrong block/chunk IDs, and helper-generated requests that diverge from production client behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/ozone/container/ContainerTestHelper.java -->


<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/ozone/ha/TestOzoneNetUtils.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/ozone/ha/TestOzoneNetUtils.java

## Purpose
Tests Ozone network utility behavior for preserving host names in socket addresses.

## Important APIs, types, and functions
- Uses `OzoneNetUtils.getAddressWithHostName`, Hadoop `NetUtils`, and `InetSocketAddress`.
- Test case is `testGetAddressWithHostName`.

## Control flow
The test creates or parses a socket address, passes it through Ozone net utility code, and asserts the resulting address retains the expected host name rather than only resolved address data.

## State and persistence behavior
No persistent state; only socket address objects are used.

## Dependencies and integration points
HA and service discovery code often needs configured hostnames preserved for certificates, RPC, or advertised addresses.

## Risks and test signals
Premature DNS resolution or lost hostnames can break HA routing and TLS hostname checks. This test signals hostname-preserving address handling.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/ozone/ha/TestOzoneNetUtils.java -->


<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/ozone/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/ozone/package-info.java

## Purpose
Declares package-level documentation for Ozone test sources.

## Important APIs, types, and functions
- Contains package JavaDoc and `org.apache.hadoop.ozone` package declaration only.

## Control flow
No executable control flow.

## State and persistence behavior
No state or persistence behavior.

## Dependencies and integration points
Supports package metadata for Ozone tests.

## Risks and test signals
No runtime test signal.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/ozone/package-info.java -->
