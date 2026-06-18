# subset-b-008046 Research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/invoker/ScmInvokerCodeGenerator.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/invoker/ScmInvokerCodeGenerator.java

Purpose: test-side generator for the production `ScmInvoker` subclasses used by SCM HA Ratis replication. It reflects an SCM handler API, discovers methods annotated with `@Replicate`, and emits Java source for an invoker class with a replicate-method enum, proxy implementation, local dispatch switch, and response encoding.

Important APIs and types: `generate(Class<?>, boolean)` is the main entry point; `generateClass()` assembles class text; `updateFile()` preserves the existing generated file header/imports and replaces the class body; `DeclaredMethod` models generated signatures such as `invokeLocal(String,Object[])`; helper methods format class names, parameters, throws clauses, default primitive values, overload parameter arrays, and line wrapping. The generator depends on `Replicate`, `ScmInvoker`, `SCMRatisResponse`, Ratis `Message`, `NameAndParameterTypes`, and MD5 comparison utilities.

Control flow: methods are sorted by name, arity, and parameter types for deterministic output. `printEnum()` groups non-default `@Replicate` methods by name and records valid arities/types. `printProxyClassMethod()` routes annotated calls through `invokeReplicateDirect` or `invokeReplicateClient` based on annotation invocation type, while unannotated methods call the local implementation. `printInvokeMethod()` emits a switch over method name, handles overload disambiguation with runtime argument checks, supplies primitive defaults for missing non-overloaded arguments, and serializes non-void return values.

State and persistence: generator state is only in-memory string buffers plus indentation. Persistence is file-system based: it writes a temporary Java file, compares MD5 hashes with the current target, deletes unchanged temp files, and optionally replaces the target. Risks include reflection sensitivity to API shape, generic return parsing that assumes class-loadable type arguments, manual import preservation, and overload ambiguity if generated parameter metadata is incomplete. Test signals come from `TestScmInvokerCodeGenerator`, which fails whenever checked-in generated classes drift from this generator.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/invoker/ScmInvokerCodeGenerator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/invoker/ScmInvokerCodeGeneratorMains.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/invoker/ScmInvokerCodeGeneratorMains.java

Purpose: convenience launcher collection for regenerating production `ScmInvoker` implementations from known SCM replicated APIs. It is package-private test code and is intended for manual execution when an SCM HA handler interface changes.

Important APIs and types: nested classes expose `main(String...)` methods for `DeletedBlockLogStateManager`, `ContainerStateManager`, `PipelineStateManager`, `RootCARotationHandler`, `FinalizationStateManager`, `SecretKeyState`, `SequenceIdGenerator.StateManager`, `StatefulServiceStateManager`, and `CertificateStore`. The nested `All` class runs all generators in a fixed sequence.

Control flow: each nested main delegates directly to `ScmInvokerCodeGenerator.generate(type, true)`, which updates the generated class under the main SCM invoker source directory. `All.main()` chains those individual launchers without arguments.

State and persistence: this file owns no state, but every launcher can mutate checked-in production Java files through the generator. Integration is tightly coupled to the current list of replicated SCM services; adding a new `@Replicate` handler requires adding a corresponding launcher if maintainers want the `All` entry point to cover it. Risks are operational rather than algorithmic: accidentally running a single launcher can leave only part of the invoker set regenerated, and generator output still requires manual import review as documented in the generator.

Test signals: `TestScmInvokerCodeGenerator` covers drift for the same API set. This mains file itself has no assertions; its value is reproducible manual regeneration.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/invoker/ScmInvokerCodeGeneratorMains.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/invoker/TestScmInvokerCodeGenerator.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/invoker/TestScmInvokerCodeGenerator.java

Purpose: regression test ensuring generated SCM HA invoker source files are up to date with their handler interfaces and with `ScmInvokerCodeGenerator` behavior.

Important APIs and types: `runTest(Class<?>)` creates a generator, emits the class body, calls `updateFile(..., overwrite=false)` against `src/main/java/org/apache/hadoop/hdds/scm/ha/invoker/`, and asserts the returned file is null. Individual JUnit tests cover the known replicated handlers: deleted block log, container state, pipeline state, root CA rotation, finalization state, secret key state, sequence ID state manager, stateful service state manager, and certificate store.

Control flow: each test delegates to the shared helper. `updateFile` writes a temporary candidate and returns null only when the candidate MD5 matches the existing checked-in generated invoker. Any API drift, generator formatting change, or stale generated source produces a non-null temp file and fails with a message naming the affected invoker class.

State and persistence: the test may create temporary candidate files in the production invoker directory when output differs because it passes `overwrite=false`; unchanged outputs are deleted by the generator. The test relies on execution from the module working directory because `DIR` is relative. Risks include brittle failures after legitimate API changes until generated files are refreshed, and sensitivity to import/header preservation in the existing generated files.

Integration points: this is the CI signal protecting SCM HA Ratis dispatch code from silently diverging from handler interfaces.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/invoker/TestScmInvokerCodeGenerator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/io/TestScmBigIntegerCodec.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/io/TestScmBigIntegerCodec.java

Purpose: minimal serialization round-trip test for `ScmBigIntegerCodec`, which is part of SCM HA request/response argument encoding.

Important APIs and types: the test constructs `ScmBigIntegerCodec`, serializes `BigInteger.valueOf(100)` to protobuf `ByteString`, deserializes it, and asserts equality with JUnit `assertEquals`.

Control flow: there is one JUnit method, `testCodec()`, with a straight-line encode/decode/assert path. No fixtures are required.

State and persistence: no persistent state is touched. The only state is the codec instance and local serialized bytes. Dependencies are `java.math.BigInteger` and Ratis-shaded protobuf `ByteString`.

Integration points: this test guards the codec used by SCM Ratis payloads when replicated methods carry `BigInteger` values. The signal is intentionally narrow; it does not test negative values, zero, very large values, null handling, or malformed bytes. Main risk is that codec behavior for edge-case `BigInteger` representations could regress without this test catching it.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/io/TestScmBigIntegerCodec.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/io/TestScmCodecFactoryReplicateCoverage.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/io/TestScmCodecFactoryReplicateCoverage.java

Purpose: reflective coverage test that catches missing `ScmCodecFactory` registrations for parameters of `@Replicate` APIs, plus a focused encode/decode regression for a container-state transition method.

Important APIs and types: `replicateHandlerTypes()` enumerates replicated SCM handler interfaces. `replicateApisRegisterParameterCodecsInScmCodecFactory()` scans every public method with `@Replicate`, inspects each `Parameter.getParameterizedType()`, and calls `ScmCodecFactory.resolve()` plus `getCodec()` on concrete classes and collection type arguments. `assertTypeResolvable()` handles `Class`, `ParameterizedType`, and upper-bounded `WildcardType`. The second test builds an `SCMRatisRequest` for `RequestType.CONTAINER` and `transitionDeletingOrDeletedToTargetState`.

Control flow: codec failures are accumulated into a multi-line error list rather than failing on the first missing type, giving maintainers a complete registration gap list. Collection generics are recursively validated before the raw collection codec is checked.

State and persistence: no disk state. The test reflects live class metadata and exercises SCM Ratis request serialization into a Ratis `Message`.

Integration points and risks: it protects Ratis replication paths that ordinary mocked tests can miss because mocks often bypass `SCMRatisRequest.encode()`. The handler type list is manual, so new replicated interfaces must be added. Generic inspection is limited to collection-style parameters and resolvable class bounds, so complex nested generic shapes could need extension.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/io/TestScmCodecFactoryReplicateCoverage.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/io/TestScmListCodec.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/io/TestScmListCodec.java

Purpose: negative test for `ScmListCodec` deserialization, ensuring list payloads without an element type are rejected with a useful protocol error.

Important APIs and types: the test builds an `SCMRatisProtocol.ListArgument` with a value but intentionally omits `type`. It constructs `ScmListCodec` with an empty `ScmCodecFactory.ClassResolver`, deserializes the protobuf `ByteString`, and expects `InvalidProtocolBufferException`.

Control flow: the single JUnit method uses `assertThrows`, then asserts the exception message contains `Missing ListArgument.type`. This checks both failure mode and diagnostic content.

State and persistence: no persistence. Inputs are in-memory protobuf messages. Dependencies include Ratis-shaded protobuf, `Collections.emptyList()`, and JUnit assertions.

Integration points and risks: `ScmListCodec` is used for SCM HA Ratis list arguments, so missing type metadata could otherwise decode ambiguously or fail later. The test only covers missing type, not unknown type names, malformed element payloads, empty lists, nested lists, or resolver collisions.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/io/TestScmListCodec.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/io/TestScmX509CertificateCodec.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/io/TestScmX509CertificateCodec.java

Purpose: verifies SCM HA certificate argument encoding for valid X.509 certificates and malformed bytes.

Important APIs and types: `initSecurityProvider()` initializes Ozone security providers through `SecurityConfig.initSecurityProvider(new OzoneConfiguration())`. `codec()` uses `KeyStoreTestUtil.generateKeyPair("RSA")` and `generateCertificate(...)`, serializes with `ScmX509CertificateCodec`, deserializes, and asserts certificate equality. `testCodecError()` wraps the UTF-8 bytes of `dummy` with protobuf `UnsafeByteOperations` and expects `InvalidProtocolBufferException`.

Control flow: JUnit `@BeforeAll` sets security providers once. The valid path exercises a real generated RSA certificate; the invalid path exercises defensive decoding and exception translation.

State and persistence: no filesystem persistence, but it depends on JVM crypto/security provider setup. The codec stores certificate material in protobuf `ByteString` during the test.

Integration points and risks: this protects SCM HA Ratis payloads for certificate-bearing APIs such as CA/certificate store replication. Coverage is good for basic DER/PEM handling but does not test multiple algorithms, certificate chains, expired certs, or null values. Crypto provider initialization is a common environmental risk if test order or provider availability changes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/io/TestScmX509CertificateCodec.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/package-info.java

Purpose: package documentation marker for tests under `org.apache.hadoop.hdds.scm.ha`.

Important APIs and types: no classes, methods, or fields are declared beyond the package statement. The Javadoc says the package contains HA related tests.

Control flow, state, and persistence: none. The file has no executable logic and no dependencies other than the package namespace.

Integration points and risks: its only integration role is documentation and Java package metadata. It can help Javadocs or IDE package views, but it provides no test signal by itself. The primary risk is drift in package-level documentation if the test package scope changes substantially.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/metadata/OldPipelineIDCodecForTesting.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/metadata/OldPipelineIDCodecForTesting.java

Purpose: test-only implementation of the legacy `PipelineID` RocksDB codec, used as a compatibility oracle for current `PipelineID.getCodec()` behavior.

Important APIs and types: implements `Codec<PipelineID>`. `toPersistedFormat(PipelineID)` writes a 16-byte UUID representation: most significant bits first, then least significant bits, each big-endian via `ByteBuffer.putLong`. `fromPersistedFormatImpl(byte[])` reads the two longs with `toLong(...)`, creates a `UUID`, and returns `PipelineID.valueOf(id)`. `copyObject()` is unsupported.

Control flow: encoding allocates a 16-byte array and copies two 8-byte arrays into it. Decoding validates each 8-byte segment length in `toLong`; short arrays throw `ArrayIndexOutOfBoundsException` with a specific size message.

State and persistence: no internal state. Its output shape models persisted SCM metadata bytes in RocksDB. Dependencies are `PipelineID`, `UUID`, `ByteBuffer`, and the HDDS `Codec` contract.

Integration points and risks: paired with `TestPipelineIDCodec` to ensure upgrades and downgrades can read existing pipeline IDs. Because it intentionally preserves old behavior, spelling mistakes or exception types should not be cleaned up casually if tests depend on exact legacy semantics. It does not implement object copying, so it should remain limited to compatibility tests.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/metadata/OldPipelineIDCodecForTesting.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/metadata/OldX509CertificateCodecForTesting.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/metadata/OldX509CertificateCodecForTesting.java

Purpose: singleton test-only legacy codec for persisted X.509 certificates, used to verify current certificate codec compatibility with older SCM metadata format.

Important APIs and types: implements `Codec<X509Certificate>`. `get()` returns the singleton instance. `toPersistedFormatImpl()` converts a certificate to PEM text with `CertificateCodec.getPEMEncodedString(object)` and UTF-8 bytes. `fromPersistedFormatImpl()` reconstructs a certificate through `CertificateCodec.getX509Certificate(rawData)`. `copyObject()` returns the same immutable certificate reference.

Control flow: encoding and decoding are straight-line calls into the certificate utility layer, with checked exceptions propagated according to the codec contract.

State and persistence: the singleton is stateless; the persisted representation is PEM-encoded certificate bytes. Dependencies include `CertificateCodec`, `SCMSecurityException`, Java security certificate types, and HDDS `Codec`.

Integration points and risks: `TestX509CertificateCodec` compares the new RocksDB metadata codec against this old codec for generated RSA certificates. Risk centers on preserving legacy PEM byte compatibility; changing this class would change the compatibility oracle rather than production behavior. It does not test certificate chains or private keys.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/metadata/OldX509CertificateCodecForTesting.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/metadata/TestPipelineIDCodec.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/metadata/TestPipelineIDCodec.java

Purpose: validates `PipelineID` RocksDB serialization format and compatibility between legacy and current codecs.

Important APIs and types: the test owns `oldCodec = new OldPipelineIDCodecForTesting()` and `newCodec = PipelineID.getCodec()`. It checks all-zero UUID bytes, all-`0xFF` UUID bytes, 100 random UUIDs, and round-trip behavior through both codecs. `CodecTestUtil.runTest(newCodec, pid, 16, oldCodec)` verifies direct and buffer-oriented codec operations against the legacy implementation.

Control flow: `checkPersisting()` builds a `PipelineID`, encodes with old and new codecs, and compares against an expected 16-byte big-endian layout. `assertUuid()` verifies new bytes match old bytes and both codecs decode legacy bytes back to the same `PipelineID`.

State and persistence: no RocksDB instance is opened; persisted state is modeled as byte arrays. The expected format is exactly 16 bytes: UUID most significant long followed by least significant long, big-endian.

Integration points and risks: this is an upgrade/downgrade guard for SCM pipeline metadata. It catches endianness changes, length changes, and decode incompatibility. Random UUID coverage broadens byte-pattern signal, but malformed length/error behavior is only indirectly covered by the old codec.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/metadata/TestPipelineIDCodec.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/metadata/TestSequenceIdTypeCodec.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/metadata/TestSequenceIdTypeCodec.java

Purpose: verifies persisted `SequenceIdType` enum encoding remains byte-compatible with the previous string-based representation.

Important APIs and types: `enumCodec = SequenceIdType.getCodec()` and `stringCodec = StringCodec.get()`. Tests iterate over every `SequenceIdType` value and compare exact bytes, decode legacy string bytes with the enum codec, decode new enum bytes with `StringCodec`, and run `CodecTestUtil.runTest()` for heap/direct byte buffer compatibility.

Control flow: every JUnit method loops across all enum values, so adding a new enum constant automatically receives coverage. Assertions enforce exact equality with `type.name()` encoded by `StringCodec`.

State and persistence: no database state. The persisted form is a byte array representing the enum name string. This matters for cluster upgrade and downgrade paths because existing RocksDB keys/values may have been written as strings.

Integration points and risks: protects the SCM sequence ID metadata table and any code that expects stable enum names on disk. Renaming enum constants or changing `getByteArray()`/codec behavior would break compatibility. The tests do not cover invalid names, nulls, or case normalization, which remain separate error-handling concerns.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/metadata/TestSequenceIdTypeCodec.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/metadata/TestX509CertificateCodec.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/metadata/TestX509CertificateCodec.java

Purpose: compatibility test for persisted SCM metadata `X509CertificateCodec`, comparing the current codec with the legacy PEM codec across multiple RSA key sizes.

Important APIs and types: `oldCodec = OldX509CertificateCodecForTesting.get()` and `newCodec = X509CertificateCodec.get()`. `genKeyPair(String,int)` creates RSA key pairs with a specified size. `initSecurityConfig()` initializes Ozone security providers. `testRSA()` runs `runTestRSA()` for key sizes 512, 1024, 2048, and 4096. Each run generates a self-signed certificate with `KeyStoreTestUtil.generateCertificate(...)` and uses `CodecTestUtil.runTest(newCodec, x509, null, oldCodec)`.

Control flow: generated certificates vary in key size and random validity duration. The test prints the PEM string, then exercises new codec serialization, deserialization, copying/buffer paths, and old-codec compatibility through the utility.

State and persistence: no database is opened. Persisted state is represented as certificate bytes, with the old codec modeling PEM UTF-8. Dependencies include Java crypto, Ozone security provider setup, `CertificateCodec`, and HDDS codec testing utilities.

Integration points and risks: guards SCM certificate table upgrade compatibility. Environmental risks include crypto provider availability and slower large-key generation. It does not test non-RSA certificates, malformed bytes, certificate chains, or security policy around expired certificates.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/metadata/TestX509CertificateCodec.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/node/DatanodeAdminMonitorTestUtil.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/node/DatanodeAdminMonitorTestUtil.java

Purpose: shared utility class for tests around `DatanodeAdminMonitor` and `NodeDecommissionMetrics`, especially decommission and maintenance progress where replication state must be simulated.

Important APIs and types: `generateReplica()` creates `ContainerReplica` instances and mutates the supplied datanode persisted operational state. `generateReplicaCount()` builds `RatisContainerReplicaCount`; `generateECReplicaCount()` builds `ECContainerReplicaCount` from tuples of node state, datanode, and replica index. `mockGetContainerReplicaCount()` and `mockGetContainerReplicaCountForEC()` reset and configure a mocked `ReplicationManager` to return generated counts. `mockCheckContainerState()` controls whether `ReplicationManagerReport` is incremented as under-replicated. `DatanodeAdminHandler` counts event invocations.

Control flow: mock helpers reset the replication manager, install a default sample-limit config, answer `getContainerReplicaCount` based on the requested container ID, and stub `checkContainerStatus` to either mark under-replication and return true or return false.

State and persistence: no persistent storage. It mutates mock state and datanode operational state in-memory. Dependencies include Mockito, SCM container replication classes, EC/Ratis replication count types, event handling, and protobuf node states.

Integration points and risks: used by admin monitor and metrics tests to isolate workflow behavior from full replication manager complexity. Risks include mock reset erasing prior stubs, helper-generated replica indexes/default sequence IDs not matching every production case, and direct datanode state mutation influencing assertions.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/node/DatanodeAdminMonitorTestUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/node/ScmNodeTestUtil.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/node/ScmNodeTestUtil.java

Purpose: tiny package-level utility interface for node tests that need to inject a datanode-to-container mapping into an `SCMNodeManager`.

Important APIs and types: static method `setContainers(SCMNodeManager, DatanodeDetails, Set<ContainerID>)` calls `scm.getNodeStateManager().setContainersForTesting(datanode.getID(), containers)`. It can throw `NodeNotFoundException`.

Control flow: no branching; the method is a single delegation to the underlying `NodeStateManager` test hook.

State and persistence: mutates only in-memory node state held by the tested SCM node manager. It does not touch RocksDB or filesystem state.

Integration points and risks: used by tests such as decommission manager and dead-node handler to create known container placement state without going through heartbeats or container reports. The main risk is bypassing production update paths, so tests using it verify downstream behavior from an injected state rather than report ingestion itself.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/node/ScmNodeTestUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/node/TestCommandQueue.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/node/TestCommandQueue.java

Purpose: verifies `CommandQueue` maintains per-datanode command summary counts and clears them when commands are drained or the queue is cleared.

Important APIs and types: constructs `CommandQueue`, `CloseContainerCommand`, `CreatePipelineCommand`, and `ReplicateContainerCommand`. Uses `DatanodeID` keys and protobuf `SCMCommandProto.Type` values. A low-priority replication command is also enqueued to ensure summary counting is by command type, not priority.

Control flow: the test adds several commands to two datanodes, checks unknown datanode counts return zero, validates per-type counts and summary map for datanode one, then calls `getCommand(datanode1ID)` and verifies datanode one counts are reset while datanode two counts remain. Finally, `clear()` zeroes all remaining counts.

State and persistence: state is fully in-memory in the command queue. No external resources are used.

Integration points and risks: `CommandQueue` feeds commands returned on datanode heartbeats and exposes summary metrics/inspection. This test protects count bookkeeping when duplicate commands and multiple command types are queued. It does not cover concurrent access, command ordering details, or queue size limits.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/node/TestCommandQueue.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/node/TestContainerPlacement.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/node/TestContainerPlacement.java

Purpose: integration-style test for capacity-based container placement using real SCM node/container manager wiring and synthetic node reports.

Important APIs and types: setup creates a temp metadata directory, `DBStore`, `SCMHAManagerStub`, `SequenceIdGenerator`, `MockNodeManager`, and `MockPipelineManager`. `createNodeManager()` builds `SCMNodeManager` with event handlers, network topology schemas, storage config, layout version manager, and empty SCM context. `createContainerManager()` spies the pipeline manager and stubs `checkSpaceAndRecordAllocation` true before constructing `ContainerManagerImpl`.

Control flow: `testContainerPlacementCapacity()` configures `SCMContainerPlacementCapacity`, registers four datanodes, pushes storage reports with capacity/used/remaining values, processes heartbeats, sleeps for asynchronous processing, checks aggregated node stats, allocates a Ratis container, manually adds replicas to the first replication-factor datanodes, and asserts the container manager sees the expected replica count.

State and persistence: uses a real RocksDB-backed `DBStore` under `@TempDir` for SCM metadata tables. It mutates node reports, node stats, pipeline/container state, and container replicas. Cleanup closes the DB store and SCM node/client resources.

Integration points and risks: exercises placement policy, node stats aggregation, pipeline allocation checks, and container state manager replica tracking. The explicit sleep is a flakiness risk; manual replica insertion bypasses datanode report flow; xceiver client is constructed but not central to assertions.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/node/TestContainerPlacement.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/node/TestDatanodeAdminMonitor.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/node/TestDatanodeAdminMonitor.java

Purpose: isolated unit tests for `DatanodeAdminMonitorImpl`, covering decommission and maintenance workflow state transitions without requiring a full live SCM.

Important APIs and types: setup creates `SimpleMockNodeManager`, mocked `ReplicationManager`, `EventQueue`, a `START_ADMIN_ON_NODE` counting handler, and `NodeDecommissionMetrics`. Tests use `DatanodeAdminMonitorTestUtil` to mock Ratis/EC `ContainerReplicaCount` and replication health. Helper `generateContainers()` creates container ID sets; `getFirstTrackedNode()` inspects monitor tracking state.

Control flow: tests cover queue/cancel counters; decommission start event and pipeline closure gating; immediate decommission when no containers/pipelines exist; waiting for under-replicated containers; special handling of quasi-closed unhealthy replicas with unique origins; ignoring deleting containers; EC unrecoverable replica replacement; aborts when decommissioning nodes return to unexpected state or dead health; start-time tracking; maintenance transition to `IN_MAINTENANCE`, expiry back to `IN_SERVICE`, expiry while closing pipelines or replicating containers, dead maintenance nodes staying tracked, cancellation to `IN_SERVICE`, and pending replication API categories.

State and persistence: all state is in memory: mock node statuses, container sets, monitor queues/tracked nodes, metrics, and event queue. No database or filesystem is used.

Integration points and risks: verifies the monitor contract with `NodeManager`, `ReplicationManager`, metrics, and SCM events. It is broad but mock-heavy; correctness depends on `DatanodeAdminMonitorTestUtil` accurately modeling replication-manager responses. Timing-sensitive maintenance expiry is simulated by setting expiry in the past.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/node/TestDatanodeAdminMonitor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/node/TestDatanodeUsageInfo.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/node/TestDatanodeUsageInfo.java

Purpose: verifies `DatanodeUsageInfo.toProto()` includes optional filesystem-level capacity fields only when they have been explicitly set.

Important APIs and types: creates random `DatanodeDetails`, `SCMNodeStat`, `DatanodeUsageInfo`, and converts to `HddsProtos.DatanodeUsageInfoProto` with `ClientVersion.CURRENT_VERSION`.

Control flow: `testToProtoDoesNotIncludeFilesystemFieldsByDefault()` asserts `hasFsCapacity()` and `hasFsAvailable()` are false while standard capacity/used/remaining are populated. `testToProtoIncludesFilesystemFieldsWhenPresent()` calls `setFilesystemUsage(2000L, 1500L)` and asserts the optional proto fields are present and correct.

State and persistence: no persistence. State is local object fields and generated protobufs.

Integration points and risks: protects client-facing or admin-facing datanode usage serialization, especially backward-compatible optional fields. It does not test older client versions, reserved/committed fields, sorting, or null datanode behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/node/TestDatanodeUsageInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/node/TestDeadNodeHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/node/TestDeadNodeHandler.java

Purpose: integration and race-regression tests for `DeadNodeHandler` and related `HealthyReadOnlyNodeHandler` topology behavior.

Important APIs and types: setup builds a real test `StorageContainerManager`, obtains `SCMNodeManager`, `PipelineManagerImpl`, and `ContainerManager`, sets SCM context leader/safemode status, injects a mock Ratis pipeline provider, and creates a `DeadNodeHandler` with mocked `DeletedBlockLog`. Helpers set node health state, register container IDs on datanodes through `ScmNodeTestUtil`, and register container replicas.

Control flow: `testOnMessage()` registers datanodes with storage and metadata reports, exits safemode, waits for pipelines, allocates containers, assigns replicas, and then exercises dead handling first for an `IN_MAINTENANCE` node and then an `IN_SERVICE` node. It asserts topology removal, replication-manager notification suppression or firing, deleted-block callbacks, command queue cleanup, and replica removal behavior. Other tests cover skipping topology removal when the node has resurrected to `HEALTHY_READONLY`, unconditionally re-adding removed healthy-readonly nodes, and a controlled thread interleaving where `DeadNodeHandler` blocks before topology removal while the node resurrects.

State and persistence: uses temp SCM metadata, live in-memory topology, container state, pipeline state, command queues, and mocked deleted-block log. Threading tests use latches and a spawned thread.

Integration points and risks: protects dead-node cleanup, replication notification, topology consistency, and resurrection races. `testOnMessage` is marked flaky, indicating timing/environment sensitivity around pipeline creation and full SCM setup.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/node/TestDeadNodeHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/node/TestFetchMetrics.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/node/TestFetchMetrics.java

Purpose: smoke tests for `FetchMetrics`, verifying metrics JSON retrieval returns a payload containing a `beans` field for unfiltered and filtered JMX queries.

Important APIs and types: a static `FetchMetrics` instance calls `getMetrics(null)` and `getMetrics("Hadoop:service=StorageContainerManager,name=NodeDecommissionMetrics")`. Tests use regex `Pattern.compile("beans", Pattern.MULTILINE)` and assert a match.

Control flow: both tests are straight-line fetch/regex/assert paths. They do not parse JSON structurally.

State and persistence: no persistence. It depends on the JVM's metrics/JMX infrastructure available during tests.

Integration points and risks: provides a low-cost signal that metrics fetch plumbing returns JMX-like output. Because it only searches for the word `beans`, it does not validate the requested bean exists, specific metrics are present, or malformed filters fail correctly.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/node/TestFetchMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/node/TestNodeDecommissionManager.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/node/TestNodeDecommissionManager.java

Purpose: unit/integration tests for user-facing `NodeDecommissionManager` admin operations: host parsing, decommission, maintenance, recommission, leadership recovery, and safety checks for minimum available nodes.

Important APIs and types: setup creates a test SCM and real `SCMNodeManager`, mocked `ContainerManager`, `NodeDecommissionManager`, and allocation stubs producing mock `ContainerInfo` for Ratis or EC configs. Helpers create mock containers, inject container sets via `ScmNodeTestUtil`, simulate node-not-found behavior with a mocked node manager, and generate datanodes with unique, duplicate, and ambiguous host/port combinations.

Control flow: tests validate `HostDefinition` parsing and invalid ports; errors for missing hosts, wrong ports, and ambiguous host addresses; decommission/recommission by IP or `ip:port`; maintenance/recommission with expiry; rejection of transitions between decommission and maintenance workflows; `onBecomeLeader()` re-tracking nodes already in decommission/maintenance states; decommission safety failures for Ratis, EC, mixed Ratis+EC, not-in-service nodes, and node-not-found cases; maintenance safety failures and forced bypass for Ratis, EC, and mixed containers with configurable minimum replicas/redundancy.

State and persistence: uses temp SCM metadata through `HddsTestUtils.getScm`, real node manager state, mocked container metadata, datanode persisted operational state, and monitor tracked-node state. No commits or external services.

Integration points and risks: protects admin command semantics and cluster-safety validation before changing node op states. Risks include complex mock behavior that may not capture every real container-manager failure, static container ID counter shared across tests, and reliance on generated datanode addressing patterns.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/node/TestNodeDecommissionManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/node/TestNodeDecommissionMetrics.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/node/TestNodeDecommissionMetrics.java

Purpose: verifies `NodeDecommissionMetrics` reflects `DatanodeAdminMonitorImpl` workflow state for decommission, maintenance, recommission, pipelines, and container replication categories.

Important APIs and types: setup creates `SimpleMockNodeManager`, mocked `ReplicationManager`, monitor, event queue, `START_ADMIN_ON_NODE` handler, and metrics via `NodeDecommissionMetrics.create()`. Teardown unregisters metrics. Tests use `DatanodeAdminMonitorTestUtil.mockGetContainerReplicaCount()` to control container health classifications.

Control flow: tests start monitoring datanodes in entering maintenance or decommissioning states, call `monitor.run()`, and assert totals plus host-specific metric getters. Covered counters include tracked decommissioning/maintenance nodes, recommission nodes, pipelines waiting to close, under-replicated containers, sufficiently replicated containers, unclosed containers, aggregation across multiple datanodes, and workflow start time bounds.

State and persistence: all state is in-memory monitor/node-manager state and registered metrics. Metrics registration is process-global enough that `unRegister()` in teardown is important to prevent leakage between tests.

Integration points and risks: this is the observability companion to admin monitor tests, ensuring admin progress can be scraped and attributed by host. Mocked replication responses mean metric correctness is tested after classification inputs are supplied, not the full replication classification algorithm itself.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/node/TestNodeDecommissionMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/node/TestNodeReportHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/node/TestNodeReportHandler.java

Purpose: tests `NodeReportHandler` updates SCM node capacity metrics from datanode node reports.

Important APIs and types: setup creates `SCMNodeManager` with mocked `SCMStorageConfig`, `HDDSLayoutVersionManager`, `NetworkTopologyImpl`, event queue, and empty SCM context. The test class implements `EventPublisher`, logging published events. `getNodeReport()` wraps generated protobuf `NodeReportProto` in `NodeReportFromDatanode`.

Control flow: `testNodeReport()` creates storage and metadata reports for a random datanode, confirms no node metric exists before registration, registers the node with one storage report, checks capacity/remaining/scmUsed values, then invokes `nodeReportHandler.onMessage()` with two storage reports and verifies aggregated metrics double.

State and persistence: temp directories provide storage path strings, but no disk data is persisted. Node manager state holds reports and derived `SCMNodeMetric`.

Integration points and risks: protects heartbeat report ingestion and metric aggregation. It does not validate emitted events beyond logging, nor does it cover failed reports, missing metadata reports, filesystem fields, or multi-datanode aggregation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/node/TestNodeReportHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/node/TestNodeStateManager.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/node/TestNodeStateManager.java

Purpose: unit tests for `NodeStateManager`, the internal state store and health transition engine used by `SCMNodeManager`.

Important APIs and types: setup creates a minimal `ConfigurationSource`, `SCMContext` with finalization complete by default, mocked `HDDSLayoutVersionManager`, and `MockEventPublisher`. Tests use `DatanodeDetails`, `DatanodeInfo`, `NodeStatus`, `HddsProtos.NodeState`, `SCMEvents`, `FinalizationCheckpoint`, `LayoutVersionProto`, and container IDs.

Control flow: tests add/retrieve nodes, count all/filtered nodes, mark nodes stale and dead based on heartbeat age, verify allowed health transitions and fired events, test resurrection through `HEALTHY_READONLY` before returning to `HEALTHY`, and validate layout-version/finalization behavior where lower-MLV datanodes become healthy-readonly only after SCM crosses `MLV_EQUALS_SLV`. Additional tests set operational state, add/remove container mappings, ensure changing op state re-emits the appropriate current health event, and update a node by UUID with new address, host, op state, and layout version.

State and persistence: all state is in-memory inside `NodeStateManager`, including node maps, statuses, heartbeat timestamps, known layout versions, and container sets. The mock publisher records events and payloads for assertions.

Integration points and risks: this is core safety coverage for node lifecycle, event publication, and upgrade finalization gating. Risks include the anonymous configuration returning null for all keys, so defaults from utility methods shape timeouts, and tests focus on single-node paths rather than high-concurrency updates.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/node/TestNodeStateManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/node/TestPendingContainerTracker.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/node/TestPendingContainerTracker.java

Purpose: verifies `PendingContainerTracker` and per-datanode pending allocation buckets used to reserve space for containers that have been allocated but not yet confirmed by reports.

Important APIs and types: setup creates a tracker with 5 GiB max container size, 1000 `DatanodeInfo` instances with large default storage reports, and 10,000 `ContainerID`s. Tests call `checkSpaceAndRecordAllocation()`, `removePendingAllocation()`, and inspect `DatanodeInfo.getPendingContainerAllocations()` count/contains behavior. Storage reports are generated with `HddsTestUtils.createStorageReports()`.

Control flow: tests cover recording one allocation per datanode, removals, two-window rolling expiration after two intervals, removing nonexistent containers, unknown datanode zero count, multi-threaded add/remove operations, retaining empty buckets for reuse, removal from current/previous windows, many containers on one datanode, many datanodes with multiple containers, idempotent repeated recording, and multi-volume space checks where aggregate remaining is insufficient, pending slots consume per-volume capacity, and committed bytes reduce available slots.

State and persistence: all state is in-memory in datanode pending allocation windows and storage report snapshots. The rolling-window test uses real sleeps with a short interval; concurrency test uses Java threads.

Integration points and risks: protects placement/space accounting from over-allocating containers before reports catch up. Risks include timing sensitivity in roll-window tests, absence of explicit assertions after the concurrency test beyond no exceptions, and synthetic storage reports that may not cover all production volume edge cases.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/node/TestPendingContainerTracker.java -->
