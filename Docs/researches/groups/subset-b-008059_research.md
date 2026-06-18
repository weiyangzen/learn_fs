# subset-b-008059 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/test/java/org/apache/hadoop/ozone/client/io/BlockStreamAccessor.java -->
# sources/object-store/apache-ozone/hadoop-ozone/client/src/test/java/org/apache/hadoop/ozone/client/io/BlockStreamAccessor.java

Purpose: test-only accessor for package-private `BlockOutputStreamEntry` state. APIs expose block ID, pipeline, security token, and current position through `getStreamBlockID`, `getStreamPipeline`, `getStreamToken`, and `getStreamCurrentPosition`. Control flow is direct delegation to the wrapped entry; no persistence or mutation is introduced. Dependencies are HDDS block, pipeline, and token types plus client IO internals. Integration point is unit tests that need observability without widening production visibility. Risk is tight coupling to `BlockOutputStreamEntry` internals. Test signal is indirect: failures surface when production getters or entry state semantics change.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/test/java/org/apache/hadoop/ozone/client/io/BlockStreamAccessor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/test/java/org/apache/hadoop/ozone/client/io/TestECBlockOutputStreamEntry.java -->
# sources/object-store/apache-ozone/hadoop-ozone/client/src/test/java/org/apache/hadoop/ozone/client/io/TestECBlockOutputStreamEntry.java

Purpose: validates EC block output stream client selection when multiple EC replica pipelines share hostnames/IPs. Important functions are two JUnit tests and helper `aNode`. Each test builds an `ECReplicationConfig`, a five-node `Pipeline`, constructs `ECBlockOutputStreamEntry`, then asks `XceiverClientManager` to acquire clients for per-replica single-EC pipelines. State is in the manager's client cache/refcounts, not persisted. Dependencies include `PipelineID`, `DatanodeDetails`, `XceiverClientManager`, and Ozone configuration. Risks covered: cache keys must distinguish ports, but coalesce identical host/port endpoints. Test signals assert either five distinct clients or three clients with expected refcounts.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/test/java/org/apache/hadoop/ozone/client/io/TestECBlockOutputStreamEntry.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/test/java/org/apache/hadoop/ozone/client/io/TestKeyInputStreamEC.java -->
# sources/object-store/apache-ozone/hadoop-ozone/client/src/test/java/org/apache/hadoop/ozone/client/io/TestKeyInputStreamEC.java

Purpose: regression test for reading a large EC block group through `KeyInputStream`. The test builds RS-10-4 EC metadata where logical block group length is dataBlocks times block size, mocks `BlockInputStreamFactory.create`, and returns a test `BlockExtendedInputStream`. Control flow constructs `OmKeyInfo` with one `OmKeyLocationInfoGroup`, enables checksum verification in `OzoneClientConfig`, obtains `LengthInputStream` via `KeyInputStream.getFromOmKeyInfo`, and reads 100 bytes. State is synthetic OM key metadata and mock pipeline replica indexes. Risk covered: EC block-group size arithmetic and stream construction for large groups. Test signal is successful read count.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/test/java/org/apache/hadoop/ozone/client/io/TestKeyInputStreamEC.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/test/java/org/apache/hadoop/ozone/client/io/TestKeyOutputStream.java -->
# sources/object-store/apache-ozone/hadoop-ozone/client/src/test/java/org/apache/hadoop/ozone/client/io/TestKeyOutputStream.java

Purpose: unit test for `KeyOutputStream` request concurrency limiting. It sets `KeyOutputStreamSemaphore` logging, spies `KeyOutputStream`, injects a semaphore with one permit, counts calls to `write` and `handleWrite`, and blocks `handleWrite` with per-thread latches. Control flow starts two writer threads, waits until both entered `write`, verifies only one reaches `handleWrite`, releases it, then verifies the second proceeds. State is semaphore queue length and latch map; no persistence. Dependencies are Mockito, `GenericTestUtils`, concurrency primitives, and `KeyOutputStreamSemaphore`. Risk covered: concurrent writes must serialize around request semaphore. Test signals are wait conditions and `verify(times(...))`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/test/java/org/apache/hadoop/ozone/client/io/TestKeyOutputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/test/java/org/apache/hadoop/ozone/client/io/TestOzoneOutputStream.java -->
# sources/object-store/apache-ozone/hadoop-ozone/client/src/test/java/org/apache/hadoop/ozone/client/io/TestOzoneOutputStream.java

Purpose: validates `OzoneOutputStream` unwrapping, metadata access, and pre-commit forwarding. The file defines fake `KeyOutputStream` and cipher-wrapper classes, then tests plain key streams, Hadoop `CryptoOutputStream` wrapping, Ozone cipher wrapping, `setPreCommits`, and failure behavior for non-key or non-metadata streams. Control flow constructs `OzoneOutputStream` with different underlying streams and calls `getKeyOutputStream`, `getMetadata`, or `setPreCommits`. State is in fake metadata maps and pre-commit lists. Dependencies include crypto stream types, Ratis checked runnables, Mockito, and JUnit assertions. Risks covered: encryption wrappers must not hide key commit stream semantics.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/test/java/org/apache/hadoop/ozone/client/io/TestOzoneOutputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/test/java/org/apache/hadoop/ozone/client/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/client/src/test/java/org/apache/hadoop/ozone/client/package-info.java

Purpose: package documentation for Ozone client tests. It declares package `org.apache.hadoop.ozone.client` and describes the package as tests for Ozone client classes. There are no APIs, control flow, state, persistence, or runtime dependencies beyond Java package metadata and ASF license headers. Integration point is Javadoc/package discovery for test sources. Risks are minimal; drift would only affect generated documentation or package-level annotations if later added. Test signal is compile-time package validity.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/test/java/org/apache/hadoop/ozone/client/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/test/java/org/apache/hadoop/ozone/client/rpc/TestOzoneKMSUtil.java -->
# sources/object-store/apache-ozone/hadoop-ozone/client/src/test/java/org/apache/hadoop/ozone/client/rpc/TestOzoneKMSUtil.java

Purpose: tests KMS provider lookup error behavior. It initializes an `OzoneConfiguration` before each test, calls `OzoneKMSUtil.getKeyProvider(config, null)` without configuring the KMS provider URI, and asserts an `IOException` with the expected message. State is the empty configuration object; no persisted files or services are used. Dependencies are Ozone configuration, `OzoneKMSUtil`, and JUnit lifecycle/assertions. Integration point is client RPC encryption setup, where absent KMS configuration must fail clearly. Risk covered: silent null providers or ambiguous messages when encryption support is misconfigured. Test signal is exact exception type and message.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/test/java/org/apache/hadoop/ozone/client/rpc/TestOzoneKMSUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/test/java/org/apache/hadoop/ozone/client/rpc/TestRpcClient.java -->
# sources/object-store/apache-ozone/hadoop-ozone/client/src/test/java/org/apache/hadoop/ozone/client/rpc/TestRpcClient.java

Purpose: unit coverage for RPC client OM version validation and idempotent close. The enum `ValidateOmVersionTestCases` enumerates expected client version, first/second OM versions, and expected validation result. The parameterized test builds `ServiceInfo` records and asserts `RpcClient.validateOmVersion`; another test rejects `FUTURE_VERSION` as expected version. `testCloseTwiceDoesNotWarn` uses a subclass with mock OM transport and Xceiver factory, captures logs, closes twice, and checks no warnings. State is synthetic service info and logging capture. Dependencies include AssertJ, JUnit params, mock Ozone transport classes, and `GenericTestUtils`. Risks covered: upgrade compatibility and close idempotency.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/client/src/test/java/org/apache/hadoop/ozone/client/rpc/TestRpcClient.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/dev-support/findbugsExcludeFile.xml -->
# sources/object-store/apache-ozone/hadoop-ozone/common/dev-support/findbugsExcludeFile.xml

Purpose: SpotBugs/FindBugs suppression list for the `ozone-common` module. It contains two `Match` rules: suppresses `URF_UNREAD_PUBLIC_OR_PROTECTED_FIELD` for `org.apache.hadoop.ozone.TestOmUtils` and `DLS_DEAD_LOCAL_STORE` for `org.apache.hadoop.ozone.security.TestGDPRSymmetricKey`. There is no runtime control flow or persistence beyond static analysis configuration. Dependencies are the FindBugs filter XML schema and Maven/static-analysis plugin wiring. Integration point is build quality gates. Risk: overly broad or stale suppressions can hide real test-code issues or fail when class names move. Test signal is static analysis passing without these known false positives.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/dev-support/findbugsExcludeFile.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/pom.xml -->
# sources/object-store/apache-ozone/hadoop-ozone/common/pom.xml

Purpose: Maven descriptor for the `ozone-common` jar under the Ozone parent dependency client. It declares artifact identity, packaging, module dependencies, test dependencies, resources, source/test-source layout, and build plugins. Important integration points include generated protobuf classes, HDDS/Ozone common libraries, Hadoop dependencies, security/KMS, Ratis, Jackson, Guava, Mockito/JUnit for tests, and dev-support exclusions. Control flow is Maven lifecycle driven: compile, test-compile, static analysis, and packaging use this metadata. State/persistence are build artifacts in Maven target directories. Risks include dependency version drift, missing generated sources, and static-analysis exclusions getting out of sync. Test signal is module build and test execution.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/pom.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/fs/ozone/OzoneTrashPolicy.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/fs/ozone/OzoneTrashPolicy.java

Purpose: Ozone-specific Hadoop trash policy. `initialize` stores the filesystem, converts config to `OzoneConfiguration`, and chooses deletion interval from Ozone-specific key falling back to Hadoop trash interval. `moveToTrash` validates the path, qualifies it, computes trash root/current, handles OFS path trimming of volume/bucket, creates trash directories, resolves file collisions by appending timestamps, and renames the source into trash. `validatePath` blocks root/bucket deletion, invalid names, and paths already in trash. State is filesystem-visible directories and renamed keys. Dependencies include Hadoop `TrashPolicyDefault`, `OFSPath`, `OzoneFSUtils`, OM config keys, and permissions. Risks: OFS/o3fs path compatibility, trash recursion checks, race handling around mkdir/rename. Test signal should cover bucket/root rejection, existing trash targets, and OFS URI behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/fs/ozone/OzoneTrashPolicy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/fs/ozone/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/fs/ozone/package-info.java

Purpose: package documentation for the Ozone Hadoop filesystem trash policy implementation. It declares `org.apache.hadoop.fs.ozone`. There are no exported APIs beyond package metadata, no control flow, and no persistent state. Integration is documentation and package-level organization for `OzoneTrashPolicy`. Risk is limited to documentation drift. Test signal is compile-time validity.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/fs/ozone/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/hdds/protocol/StorageType.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/hdds/protocol/StorageType.java

Purpose: Ozone storage media enum with values `RAM_DISK`, `SSD`, `DISK`, and `ARCHIVE`; `DEFAULT` is `DISK`. APIs convert to and from `HddsProtos.StorageTypeProto` via explicit switches. Control flow is deterministic enum mapping with `IllegalStateException` for unknown cases. There is no mutable state or persistence. Dependencies are HDDS protobuf enums. Integration points include protocol serialization, SCM/container placement metadata, and client/server storage-policy exchange. Risks: adding proto enum values without updating mappings will throw at runtime; ordinal assumptions should be avoided. Test signal should assert round-trip conversion for every value.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/hdds/protocol/StorageType.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/hdds/protocol/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/hdds/protocol/package-info.java

Purpose: package documentation for common HDDS protocol objects in Ozone. It declares `org.apache.hadoop.hdds.protocol`. No functions, control flow, state, or persistence are present. Integration is documentation/package organization for protocol helpers such as `StorageType`. Risk is only documentation/package drift. Test signal is successful compilation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/hdds/protocol/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/OFSPath.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/OFSPath.java

Purpose: parser/reconstructor for Rooted Ozone Filesystem paths. State fields hold authority, volume, bucket, mount, key, and configuration. Constructors parse Hadoop `Path` or string URI, accepting only `ofs` scheme and preserving trailing slash for keys. Special `/tmp` mount maps to volume `tmp` and either shared bucket `tmp` or MD5 of current user. APIs classify root/volume/bucket/key/snapshot paths, compare bucket identity, generate non-key paths, compute per-user trash root, and derive temp bucket names. Dependencies include Hadoop `Path`, UGI, Ozone constants/config, `OzoneObjInfo`, and MD5. Risks: URI scheme rejection, user lookup failure, slash normalization, temp mount privacy/shared mode, and runtime exceptions for trash root on non-key paths. Tests should cover OFS URI forms, snapshots, `/tmp`, and trash roots.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/OFSPath.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/OmUtils.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/OmUtils.java

Purpose: broad static utility hub for Ozone Manager addressing, request classification, validation, IDs, path normalization, and display helpers. Key APIs resolve OM RPC/HTTP/HTTPS addresses, list active/listener/decommissioned OM node IDs, classify `OMRequest` as read-only or follower-readable, generate SHA digests, prepare deleted-key metadata, validate volume/bucket/snapshot/key names, encode object IDs with epoch bits, discover OM service IDs, normalize keys/paths, format service info, and resolve OM hosts. State is mostly stateless except static secure random bytes and logs; persistence occurs indirectly when prepared metadata is later stored. Dependencies are OM config keys, protobuf request types, HDDS config/network utilities, Hadoop `Path`, OM helper models, and exceptions. Risks: large switch statements must track new proto commands, follower-read eligibility differs from read-only classification, object ID bit limits, and address fallback rules. Tests should cover command categorization, HA config permutations, validation failures, and normalization.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/OmUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/OzoneAcl.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/OzoneAcl.java

Purpose: immutable ACL value object for Ozone resources. It stores identity type, normalized name, scope, and ACL rights as integer bits, with memoized string and hash forms. APIs include factories, `parseAcl`, `parseAcls`, protobuf conversion, scope change, access checks, add/remove bit operations, byte/list/set views, and equality. Control flow validates world/anonymous names, requires user/group names, parses optional `[ACCESS|DEFAULT]` scope, and encodes rights into up to two bytes. State is immutable after construction. Dependencies are Ozone ACL authorizer enums, protobuf `OzoneAclInfo`, Guava/Ratis helpers, and Jackson annotations. Risks: bit layout compatibility with protobuf, special handling for WORLD/ANONYMOUS names, `NONE` overriding `ALL`, and parser format strictness. Test signals should include parse/protobuf round trips and add/remove semantics.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/OzoneAcl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/OzoneFsServerDefaults.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/OzoneFsServerDefaults.java

Purpose: Ozone implementation of Hadoop `FsServerDefaults` focused on key provider URI propagation. Constructors either default or call superclass with mostly zero/default filesystem values and an optional `keyProviderUri`. APIs `getProtobuf` and `getFromProtobuf` serialize/deserialize `FsServerDefaultsProto`, only setting the key provider URI when present. State is the inherited immutable/default fields. Dependencies are Hadoop FS defaults and Ozone Manager protobufs. Integration point is client discovery of server defaults, especially encryption/KMS URI. Risks: omitted inherited fields mean future defaults may need explicit protobuf support. Test signal should assert null and non-null key provider URI round trips.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/OzoneFsServerDefaults.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/OzoneIllegalArgumentException.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/OzoneIllegalArgumentException.java

Purpose: Ozone-specific `IllegalArgumentException` subclass used to distinguish errors originating in Hadoop/Ozone implementation from JDK argument errors. API is a single message constructor; state is the inherited exception message and serial version UID. No control flow or persistence beyond exception construction. Dependencies are HDDS audience/stability annotations. Integration point is public API error handling where callers may want to catch Ozone-originated invalid arguments. Risks are minimal; misuse could fragment exception handling if ordinary `IllegalArgumentException` would suffice. Test signal is constructor/message preservation if needed.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/OzoneIllegalArgumentException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/client/checksum/CompositeCrcFileChecksum.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/client/checksum/CompositeCrcFileChecksum.java

Purpose: Hadoop `FileChecksum` implementation representing a composed CRC. Fields store CRC int, `DataChecksum.Type`, and bytes-per-CRC. APIs return algorithm name `COMPOSITE-<type>`, fixed length 4, big-endian bytes via `CrcUtil`, checksum options, writable read/write of the CRC int, and formatted string. Control flow is simple serialization/deserialization; only `crc` is read from `DataInput`, while type/options are constructor-supplied. Dependencies are Hadoop checksum APIs and local CRC utilities. Risks: deserialization without crc type/bytes-per-crc requires external construction context; algorithm string compatibility matters for clients. Test signal should cover bytes, string, and writable round trips.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/client/checksum/CompositeCrcFileChecksum.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/client/checksum/CrcComposer.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/client/checksum/CrcComposer.java

Purpose: stateful composer that combines per-chunk CRC32/CRC32C values into one digest or striped digests for concatenated data. Factories create non-striped or striped composers; `getModFunction` selects polynomial mod implementation. `update` accepts byte arrays, `DataInputStream`, or single CRC ints, validates CRC byte alignment, composes via precomputed monomial when possible, advances stripe position, flushes at stripe boundaries, and rejects overrun. `digest` emits any partial stripe, resets internal digest stream, and returns bytes. State includes current composite CRC, position in stripe, output buffer, precomputed monomial, and hints. Dependencies are pure Java CRC implementations and `CrcUtil`. Risks: stripe alignment, zero CRC sentinel behavior, unsupported checksum types, and digest reset semantics. Tests should cover variable bytes-per-CRC and stripe boundaries.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/client/checksum/CrcComposer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/client/checksum/CrcUtil.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/client/checksum/CrcUtil.java

Purpose: low-level CRC algebra and byte-format helpers. APIs multiply CRC polynomials modulo a provided function, compute monomials for byte lengths, compose two CRCs with or without precomputed monomial, write/read big-endian ints, and render single or multiple CRC byte arrays as hex. Control flow uses bit decomposition/squaring for `getMonomial`, explicit bounds checks for read/write, and length validation for debug formatting. State is none; all methods are static. Dependencies are `LongToIntFunction` mod callbacks from checksum implementations. Risks: polynomial bit order is subtle, negative lengths and buffer bounds must fail loudly, and endian compatibility with Hadoop checksum formats matters. Test signals should verify known CRC composition vectors and byte conversions.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/client/checksum/CrcUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/client/checksum/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/client/checksum/package-info.java

Purpose: package documentation for Ozone client checksum classes. It declares `org.apache.hadoop.ozone.client.checksum` and names the package as checksum-related. There are no APIs, runtime control flow, or persistent state. Integration is package/Javadoc organization for `CompositeCrcFileChecksum`, `CrcComposer`, and `CrcUtil`. Risk is documentation drift only. Test signal is compile-time validity.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/client/checksum/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/client/io/LengthInputStream.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/client/io/LengthInputStream.java

Purpose: `FilterInputStream` wrapper that carries known stream length and optionally supports Hadoop `ByteBufferReadable`. APIs expose `getLength`, `getWrappedStream`, and `read(ByteBuffer)`. Control flow delegates byte-buffer reads only if the wrapped stream implements `ByteBufferReadable`; otherwise it throws `UnsupportedOperationException`. State is the immutable length plus inherited wrapped stream reference. Dependencies are Java IO, `ByteBuffer`, and Hadoop `ByteBufferReadable`. Integration point is Ozone key input streams returning both data and logical length. Risks: callers must not assume ByteBuffer support for all wrapped streams; length is informational and not enforced. Test signal should cover delegation and unsupported case.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/client/io/LengthInputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/client/io/SelectorOutputStream.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/client/io/SelectorOutputStream.java

Purpose: output stream that buffers initial bytes, then selects the real underlying stream based on total bytes written/required. `ByteArrayBuffer` manages byte array capacity, writes, and `selectAndClose`; `Underlying` holds the selector function and chosen stream. Writes either stay buffered or go to selected output. `flush`, `hflush`, `hsync`, `hasCapability`, and `close` force selection; sync methods require underlying `Syncable`. State includes buffer contents until selection and then the underlying stream reference. Dependencies are Hadoop `Syncable`/`StreamCapabilities`, Jakarta `Nonnull`, and Ratis `CheckedFunction`. Risks: not thread-safe, selector invoked during capability checks, buffer overflow validation, and sync errors for non-syncable streams. Tests should cover threshold transitions and forced selection.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/client/io/SelectorOutputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/client/io/WrappedOutputStream.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/client/io/WrappedOutputStream.java

Purpose: pure delegating `OutputStream` wrapper. It stores one underlying `OutputStream` and forwards all `write` overloads, `flush`, and `close`. There is no selection, buffering, synchronization, or persistence beyond effects performed by the wrapped stream. Dependencies are Java IO only. Integration point is APIs that need a distinct wrapper type while preserving standard output behavior. Risks are minimal; null underlying stream is not checked in constructor, so misuse produces later `NullPointerException`. Test signal is straightforward delegation behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/client/io/WrappedOutputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/client/io/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/client/io/package-info.java

Purpose: package documentation for common Ozone client IO classes. It declares `org.apache.hadoop.ozone.client.io`. No executable code, state, or persistence exists. Integration is documentation/package organization for stream wrappers and related client IO helpers. Risk is documentation drift. Test signal is compile-time validity.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/client/io/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/conf/OMClientConfig.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/conf/OMClientConfig.java

Purpose: typed configuration bean for OM client settings under prefix `ozone.om.client`. Annotated fields define RPC timeout (`ozone.om.client.rpc.timeout`, default 15m, milliseconds) and trash emptier pool size (`ozone.om.client.trash.core.pool.size`, default 5). APIs are getters/setters. State is held in config object populated by HDDS configuration reflection. Dependencies are `@Config`, `@ConfigGroup`, config tags/types, and `TimeUnit`. Integration points are `OmUtils.getOMClientRpcTimeOut` and trash emptier pool sizing. Risk: `setRpcTimeOut` appears to compare the old field before assigning `timeOut`, so intended clamping can be bypassed. Test signal should include timeout parsing and integer-limit behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/conf/OMClientConfig.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/conf/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/conf/package-info.java

Purpose: package documentation for Ozone configuration classes. It declares `org.apache.hadoop.ozone.conf`. There are no APIs, control flow, state, or persistence. Integration is documentation/package organization for `OMClientConfig`. Risk is documentation drift. Test signal is compile-time validity.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/conf/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/IOmMetadataReader.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/IOmMetadataReader.java

Purpose: interface contract for Ozone Manager metadata read operations. APIs include key lookup, key info with volume context, file/directory status listing in full and lightweight forms, file status and lookup, key listing in full and lightweight forms, ACL retrieval, and object tagging retrieval. Control flow is defined by implementers; default method delegates `listStatus` without partial prefixes. State/persistence are OM metadata DB concerns outside the interface. Dependencies are OM helper DTOs, `OzoneAcl`, `OzoneObj`, and `OMException`. Integration point is OM read path for client RPC, filesystem APIs, and ACL/tag consumers. Risks: interface expansion affects all metadata reader implementations; lightweight/full variants must remain semantically aligned. Test signals come from implementation-level list/lookup/ACL/tag tests.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/IOmMetadataReader.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/OMConfigKeys.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/OMConfigKeys.java

Purpose: central constant registry for Ozone Manager configuration keys and defaults. It spans OM addresses/ports, HA service/node settings, HTTP/HTTPS/grpc, Ratis, snapshots, trash, KMS/EDEK cache, compaction, quotas, filesystem paths, ACL defaults, follower reads, listeners, decommissioning, upgrade/finalization, and operational limits. APIs are public static final constants plus private constructor. There is no runtime state or persistence, but these strings control persisted configuration files and cross-component compatibility. Dependencies are constants from HDDS/Ozone and time/size defaults. Integration is broad: clients, OM servers, tests, and docs reference these keys. Risks: renaming breaks config compatibility; defaults influence production behavior; duplicated or deprecated keys require careful migration. Test signal is config loading and grep-based references.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/OMConfigKeys.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/OmConfig.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/OmConfig.java

Purpose: typed reconfigurable OM configuration bean. Annotated fields cover filesystem-path semantics, key character checks, max server list size, user volume count, upgrade finalization timeout, default user/group ACL rights, ignoring client ACLs, list-all-volumes, leader linearizable-read optimization, and follower-read local lease settings. APIs are getters/setters, `validate`, `copy`, `setFrom`, and nested key/default constants. `validate` repairs nonpositive list size, enforces positive max user volume count, and parses default ACL rights. State is mutable config object populated from configuration; persistence is external config files. Dependencies are HDDS config annotations, Guava preconditions, and ACL enums. Risks: `setFrom` omits some fields such as ignoreClientACLs and follower-read lease settings; cached ACL sets must refresh on validation. Test signal should cover reconfiguration and copy semantics.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/OmConfig.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/exceptions/OMException.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/exceptions/OMException.java

Purpose: checked exception for Ozone Manager failures carrying a structured `ResultCodes` enum. Constructors accept result only, message/result, message/cause/result, or cause/result. `getResult` exposes the code and `toString` prefixes the code before the IOException string. State is immutable result plus inherited exception fields. Dependencies are Java IO only. Integration point is OM RPC error propagation and client-side status decoding; `STATUS_CODE` constant supports textual encoding elsewhere. Risks: enum order/name compatibility with protocol mapping, broad result set maintenance, and code-specific handling in clients. Test signal should verify result preservation and mapping from server errors to expected codes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/exceptions/OMException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/exceptions/OMLeaderNotReadyException.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/exceptions/OMLeaderNotReadyException.java

Purpose: specialized `IOException` indicating the OM leader exists but is not ready to serve. API is a message constructor. State is the inherited message only. Dependencies are Java IO. Integration point is HA retry/failover logic, especially follower-read and leader failover providers that detect leader-not-ready and retry appropriately. Risk: callers relying on exact type need server-side exception translation to preserve it. Test signal should assert retry policies treat it differently from non-retriable errors.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/exceptions/OMLeaderNotReadyException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/exceptions/OMNotLeaderException.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/exceptions/OMNotLeaderException.java

Purpose: specialized `IOException` for requests sent to a non-leader OM. It carries the current OM node ID and optional suggested leader node ID/address, with constructors for message-only and structured current/leader context. APIs expose current and suggested leader IDs and build messages that guide clients to retry on the leader when known. State is immutable exception context. Dependencies are Java IO/string handling. Integration point is HA failover and follower-read fallback; follower-read disables itself when this appears from a supposed follower-read path. Risks: message parsing compatibility if downstream code extracts leader info from text; null leader suggestions must be handled. Test signal should cover message forms and failover handling.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/exceptions/OMNotLeaderException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/exceptions/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/exceptions/package-info.java

Purpose: package documentation for OM exception classes. It declares `org.apache.hadoop.ozone.om.exceptions`. There are no APIs, control flow, state, or persistence beyond package metadata. Integration is documentation/package organization for `OMException`, `OMNotLeaderException`, and `OMLeaderNotReadyException`. Risk is documentation drift. Test signal is compile-time validity.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/exceptions/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/ha/GrpcOMFailoverProxyProvider.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/ha/GrpcOMFailoverProxyProvider.java

Purpose: gRPC OM failover proxy provider reusing the OM failover base for S3 gateway/OM transport. It initializes proxies from active non-listener OM node configs, deriving host from OM RPC address and port from node-specific gRPC config or `GrpcOmTransportConfig`, shuffles proxies, and lazily returns current proxy from the map. It overrides `shouldFailover` to avoid failover for gRPC `RESOURCE_EXHAUSTED` and `DATA_LOSS`, leaves close as no-op, and exposes address lookup by node ID. State is the inherited proxy map/current node state. Dependencies include gRPC status exceptions, HDDS config helpers, `OmUtils`, `GrpcOmTransport`, and UGI. Risks: missing host config is fatal, no-op close assumes proxy lifecycle elsewhere, and status-code filtering affects retry behavior. Test signal should cover config resolution and non-failover statuses.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/ha/GrpcOMFailoverProxyProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/ha/HadoopRpcOMFailoverProxyProvider.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/ha/HadoopRpcOMFailoverProxyProvider.java

Purpose: Hadoop RPC OM failover provider for clients configured with multiple OMs. It builds `OMProxyInfo` entries from active non-listener node IDs and suffixed OM address keys, shuffles them, lazily creates RPC proxies for the current node, computes a HA delegation token service as sorted comma-separated proxy token services, and closes all opened proxies. State is inherited current proxy/proxy map plus computed delegation token service. Dependencies are Hadoop RPC, `Text`, UGI, `OmUtils`, and HA config helpers. Integration point is `RpcClient` and leader-based OM request retry/failover. Risks: unresolved addresses can produce null delegation token service and later connection failures; randomized order affects initial target; close must handle Closeable and RPC proxies. Test signal should cover lazy creation, token service ordering, and close idempotency.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/ha/HadoopRpcOMFailoverProxyProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/ha/HadoopRpcOMFollowerReadFailoverProxyProvider.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/ha/HadoopRpcOMFollowerReadFailoverProxyProvider.java

Purpose: wrapper `FailoverProxyProvider` that can route eligible read OM RPCs to followers/listeners while preserving leader failover for writes and fallback. It owns a leader `HadoopRpcOMFailoverProxyProvider`, a dynamic proxy with `FollowerReadInvocationHandler`, current follower index, last proxy for tests, and read consistency hints. Invocation parses `OMRequest`, injects default follower or leader consistency hint when absent, checks `OmUtils.shouldSendToFollower`, iterates OM proxies on retriable follower failures, disables follower read on `OMNotLeaderException`, propagates leader-not-ready for retry, and falls back to leader proxy when needed. State is volatile follower-read flag, current index, and underlying leader proxies. Dependencies include Hadoop retry/RPC, protobuf, OM HA exception extraction, Ratis read exceptions, and `ReadConsistency`. Risks: concurrency around proxy rotation, mutation of args array, command eligibility drift, disabling follower reads globally after one error, and correct exception wrapping as `ServiceException`. Test signal should cover routing, fallback, consistency hints, and failover exceptions.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/ha/HadoopRpcOMFollowerReadFailoverProxyProvider.java -->
