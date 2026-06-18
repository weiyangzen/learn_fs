# subset-b-007564 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/util/TestCombinedHostsFileReader.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/util/TestCombinedHostsFileReader.java

Purpose: JUnit 5 coverage for `CombinedHostsFileReader`, the JSON-based include/exclude hosts reader for datanode admin properties.

Important APIs/types/functions: `CombinedHostsFileReader.readFile`, `readFileWithTimeout`, `DatanodeAdminProperties[]`, `GenericTestUtils.getTestDir`, JUnit `assertThrows`, Mockito `Callable<DatanodeAdminProperties[]>` setup.

Control flow: setup initializes Mockito mocks; teardown deletes a generated temp hosts JSON file. The tests load legacy and current cached JSON fixtures and expect seven datanode admin records. An empty temp JSON file must deserialize to an empty array. Timeout tests call `readFileWithTimeout` with a normal fixture and with very small timeout values expecting `IOException` for timeout/interruption paths.

State and persistence behavior: test state is a temp JSON file under the generic test directory plus read-only fixtures under `test.cache.data`. No HDFS cluster is started. The mock `Callable` is configured but not passed directly to production code, so the timeout tests are primarily black-box timing/exception checks against `readFileWithTimeout`.

Dependencies and integration points: integrates with HDFS protocol `DatanodeAdminProperties`, local test JSON resources, and reader timeout handling likely backed by executor/future logic.

Risks: timing-sensitive assertions can be flaky if timeout behavior changes; the mocked callable does not appear to inject into the production call, so those stubs may be dead setup. Empty-file semantics are explicitly preserved.

Test signals: fixture cardinality checks, empty-file read, successful timeout-bounded read, and expected `IOException` on timeout/interruption scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/util/TestCombinedHostsFileReader.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/util/TestCyclicIteration.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/util/TestCyclicIteration.java

Purpose: validates `CyclicIteration<K,V>` over a sorted `NavigableMap`, especially wraparound ordering from arbitrary start keys.

Important APIs/types/functions: `TreeMap`, `NavigableMap`, `CyclicIteration<Integer,Integer>`, `Map.Entry`, helper `checkCyclicIteration`.

Control flow: the single test loops map sizes 0 through 4. For each size, it builds keys as even integers, then iterates start positions from `-1` through the last possible odd/even boundary. Each cyclic iteration is collected into a list and compared against the expected rotated key sequence using `((start + 2) / 2 + i) % size`.

State and persistence behavior: all state is in-memory. The test prints maps and iterations to stdout but performs no persistence or cluster work.

Dependencies and integration points: exercises the HDFS utility iterator against Java `TreeMap` ordering, making it a small contract test for consumers that need deterministic ring traversal.

Risks: for `numOfElements == 0`, the verification loop is skipped, so the test only verifies that iteration over an empty map produces no elements and does not throw. The arithmetic expectation encodes even-key spacing; behavior for non-uniform keys is indirectly covered only through `TreeMap` ceiling/wrap logic.

Test signals: confirms complete iteration order for small maps, start keys before/inside/after present keys, and wraparound traversal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/util/TestCyclicIteration.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/util/TestDiff.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/util/TestDiff.java

Purpose: randomized stress coverage for `Diff<byte[], INode>`, the utility used by NameNode snapshot/directory diff logic.

Important APIs/types/functions: `Diff.create/delete/modify`, undo methods, `combinePosterior`, `apply2Previous`, `apply2Current`, `accessPrevious`, `accessCurrent`, `Diff.search`, `Diff.Container`, `Diff.UndoInfo`, `INodeDirectory`.

Control flow: `testDiff` runs combinations of starting list size and modification count from 0 to 10000 using exponential steps. `runDiffTest` builds a sorted previous inode list, copies it into current, creates five incremental diffs, then randomly creates, deletes, or modifies inodes while recording each operation. It verifies that applying diffs forward reproduces current, applying them backward reproduces previous, combining all diffs preserves both directions, and key-based access returns the identical object expected from previous/current. Each mutation occasionally records `toString`, undoes, asserts original diff text, reapplies, and asserts restored diff text.

State and persistence behavior: all state is in-memory `INodeDirectory` objects with deterministic names and mutable modification time. Randomness drives operation choice and undo sampling; there is no fixed seed.

Dependencies and integration points: depends on NameNode inode classes, `PermissionStatus`, `DFSUtil.string2Bytes`, and snapshot diff container behavior. It is an integration-style unit test for low-level diff invariants relied on by snapshots.

Risks: randomized coverage can be non-reproducible; failures may need captured stdout parameters. Identity checks are stricter than equality and protect against object replacement bugs.

Test signals: forward/backward application equivalence, combined diff equivalence, previous/current key access, search insertion order, and undo/redo stability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/util/TestDiff.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/util/TestLightWeightHashSet.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/util/TestLightWeightHashSet.java

Purpose: behavioral and capacity tests for `LightWeightHashSet`, Hadoop's compact hash-set implementation.

Important APIs/types/functions: constructors with capacity/load factors, `add`, `addAll`, `contains`, `containsAll`, `remove`, `removeAll`, iterator removal, `pollAll`, `pollN`, `pollToArray`, `clear`, `toArray`, `getCapacity`, `getElement`.

Control flow: `setUp` creates 100 random integers and a default-capacity set. Tests cover empty iteration, single/multiple insertion, duplicate rejection, membership, removal by value and iterator, polling all or bounded subsets, array polling with undersized/exact/zero arrays, clearing, load-factor expansion/shrinkage, bulk remove/contains/toArray, and canonical element lookup. `TestObject` deliberately creates a distinct object equal to an inserted value to verify `getElement` returns the stored instance.

State and persistence behavior: in-memory only. Random integer data is seeded with `Time.now`, so element values vary, but assertions are set-membership based rather than fixed-order based.

Dependencies and integration points: uses SLF4J logging and Hadoop `Time`; validates collection semantics expected by HDFS internals that use memory-sensitive sets.

Risks: random duplicates in the input list could make `assertTrue(set.add(i))` fail if `rand.nextInt()` repeats, though probability is low. Capacity assertions encode power-of-two and load-factor implementation details.

Test signals: Java collection contract coverage, iterator remove safety, poll-drains-remove semantics, dynamic resizing, and canonical-object retrieval.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/util/TestLightWeightHashSet.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/util/TestLightWeightLinkedSet.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/util/TestLightWeightLinkedSet.java

Purpose: validates `LightWeightLinkedSet`, a compact set that preserves insertion/poll order and maintains a bookmark iterator.

Important APIs/types/functions: `add`, `addAll`, `remove`, `contains`, `iterator`, `pollFirst`, `pollAll`, `pollN`, `clear`, `toArray`, `getBookmark`, `resetBookmark`.

Control flow: setup mirrors the hash-set test with 100 random integers. Basic tests assert empty/single/multiple collection behavior and insertion-order iteration. Removal tests check removed membership and remaining order. Poll tests verify FIFO-like `pollFirst`, `pollN`, and order after re-adding previously polled elements. Clear resets size, polling, iterators, and bookmark behavior. Bookmark-specific tests verify that `getBookmark` resumes from the advanced position, advances when the bookmarked element is removed, initializes on add to empty, and resets to head.

State and persistence behavior: in-memory collection state only. Random input varies per run; order expectations use the generated list's order.

Dependencies and integration points: collection utility used by HDFS for ordered lightweight tracking; tests rely on JUnit timeouts for bookmark edge cases.

Risks: same low-probability duplicate risk as the hash-set test because random integers are expected to be unique in `add` assertions. Bookmark tests encode internal cursor semantics, so refactors must preserve that public behavior.

Test signals: ordered iteration/polling, removal consistency, empty behavior, array conversion, bookmark movement, and bookmark reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/util/TestLightWeightLinkedSet.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/util/TestMD5FileUtils.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/util/TestMD5FileUtils.java

Purpose: tests file digest computation and sidecar `.md5` verification utilities.

Important APIs/types/functions: `MD5FileUtils.computeMd5ForFile`, `saveMD5File`, `verifySavedMD5`, `getDigestFileForFile`, `MD5Hash.digest`, `DFSTestUtil.generateSequentialBytes`.

Control flow: `setup` deletes and recreates a class-specific test directory, writes a 128 KiB deterministic byte sequence to `testMd5File.dat`, and stores the expected MD5. Tests verify computed digest equality, successful save-and-verify, failure when the digest file is missing, failure when the digest file contains the wrong digest, and failure when the digest sidecar has invalid text format.

State and persistence behavior: persists a temporary data file and `.md5` sidecar under `PathUtils.getTestDir`. Each test gets clean disk state from `FileUtil.fullyDelete`.

Dependencies and integration points: validates HDFS utility behavior used by image/edit-log/checkpoint style file integrity workflows; relies on Hadoop `MD5Hash` and local filesystem I/O.

Risks: bad-digest and bad-format tests catch broad `IOException` without asserting message/type, so they verify failure but not precise diagnostics. File streams are manually closed rather than try-with-resources.

Test signals: positive digest round trip and three negative verification cases: missing, mismatched digest, malformed sidecar.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/util/TestMD5FileUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/util/TestPipelineCloseRecoveryByteArrayLeak.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/util/TestPipelineCloseRecoveryByteArrayLeak.java

Purpose: regression test for HDFS-17916, ensuring pipeline-close recovery returns the final DFSPacket byte buffer to `ByteArrayManager`.

Important APIs/types/functions: `MiniDFSCluster`, `DFSClientFaultInjector.failPacket`, `DFSTestUtil.createFile`, `ByteArrayManager.Impl`, `ManagerMap.countAllocated`, `GenericTestUtils.waitFor`.

Control flow: the test enables the write `ByteArrayManager`, sets allocation tracking threshold to zero, lowers locate-following-block retries, and installs a fault injector that reports every last-in-block ack as failed. It starts a three-datanode cluster, writes a 1 MiB replicated file to force streamer recovery in `PIPELINE_CLOSE`, extracts the client's `ByteArrayManager`, and waits until all tracked buffers are released.

State and persistence behavior: creates a temporary MiniDFSCluster and a file `/pipelineCloseRecoveryLeak.dat`. Global `DFSClientFaultInjector` state is saved and restored in `finally`; the cluster is always shut down.

Dependencies and integration points: integrates DFSClient streamer fault injection, datanode pipeline recovery, client context byte-array pooling, and cluster write path behavior.

Risks: timing-sensitive due to asynchronous streamer release; `waitFor` allows 5 seconds. Because it modifies a global fault injector, failure to restore would affect later tests, but cleanup is explicit.

Test signals: `ByteArrayManager` is the bounded implementation and `ManagerMap.countAllocated()` reaches zero after close.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/util/TestPipelineCloseRecoveryByteArrayLeak.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/util/TestReferenceCountMap.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/util/TestReferenceCountMap.java

Purpose: verifies `ReferenceCountMap` counting and thread-safe behavior using `AclFeature` instances.

Important APIs/types/functions: `ReferenceCountMap.put`, `remove`, `getReferenceCount`, `getUniqueElementsSize`, inner `PutThread`, inner `RemoveThread`, `SubjectInheritingThread`.

Control flow: the single-thread test inserts two ACL features, repeats insertions to raise counts, removes once, and checks remaining counts and unique element size. The concurrent test starts two put threads, each adding both features 10000 times, joins them, verifies count `2 * LOOP_COUNTER`, then starts one remove thread that removes both features 10000 times and verifies counts drop to `LOOP_COUNTER`.

State and persistence behavior: in-memory counters only. The two `AclFeature` objects are shared across threads as fields.

Dependencies and integration points: models NameNode feature deduplication/reference counting, especially ACL feature sharing. `SubjectInheritingThread` preserves security subject context in Hadoop test infrastructure.

Risks: concurrent test only overlaps put-put, then remove after joins; it does not test simultaneous put/remove interleavings. It assumes `AclFeature` equality/hash behavior based on contained int arrays.

Test signals: count increments, decrements without removing unique entries too early, unique element cardinality, and concurrent add/remove totals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/util/TestReferenceCountMap.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/util/TestStripedBlockUtil.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/util/TestStripedBlockUtil.java

Purpose: tests erasure-coded striped block utility math for block parsing, internal block lengths, range-to-stripe division, and large offsets.

Important APIs/types/functions: `StripedBlockUtil.parseStripedBlockGroup`, `getInternalBlockLength`, `divideByteRangeIntoStripes`, `divideOneStripe`, `LocatedStripedBlock`, `AlignedStripe`, `StripingCell`, `StripingChunk`, default EC policy.

Control flow: setup builds representative block-group sizes and byte-range sizes using random deltas inside cells/stripes. Helpers create dummy located striped blocks with synthetic datanode ports and internal block buffers whose bytes are deterministic hashes of logical offsets. Tests verify `LocatedStripedBlock` type, parse a block group into non-striped internal blocks with expected indexes/offsets/ports, assert internal block lengths for small/partial/full stripe cases, divide many valid byte ranges into aligned stripes, fill requested chunks from internal buffers, and confirm the reassembled output matches logical bytes. A final regression test covers offsets beyond `Integer.MAX_VALUE` to avoid overflow.

State and persistence behavior: no persistence; all block and buffer state is synthetic in-memory.

Dependencies and integration points: touches HDFS erasure-coding policy, protocol block types, block ID index mapping, and striped read range planning.

Risks: random deltas mean some exact boundary combinations vary; parity block read logic is noted as TODO. `verifyInternalBlocks` starts at index 1, so index 0 expectations are not asserted there.

Test signals: EC block metadata parsing, internal length calculations, byte-accurate range assembly, and large-offset regression coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/util/TestStripedBlockUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/util/TestXMLUtils.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/util/TestXMLUtils.java

Purpose: validates XML-safe string mangling/unmangling for edit-log or metadata fields.

Important APIs/types/functions: `XMLUtils.mangleXmlString`, `unmangleXmlString`, `XMLUtils.UnmanglingError`, helper `testRoundTripImpl`.

Control flow: helpers mangle an input string, assert the exact encoded form, unmangle it, and assert original equality. Tests cover empty strings, plain ASCII strings, backslash escaping, forbidden control code points and surrogate code units, malformed escape sequences that must throw `UnmanglingError`, and optional entity reference encoding for ampersand, quotes, apostrophe, less-than, and greater-than.

State and persistence behavior: pure string transformations; no external state.

Dependencies and integration points: protects XML serialization/deserialization contracts used by HDFS metadata tooling.

Risks: expected strings encode exact escape format, so intentional format changes require coordinated fixture updates. Invalid sequence tests use try/fail/catch rather than `assertThrows`, but still assert the exception path.

Test signals: exact mangled output, round-trip equivalence, entity reference coverage, and malformed escape rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/util/TestXMLUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/web/TestAuthFilter.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/web/TestAuthFilter.java

Purpose: verifies WebHDFS HTTP authentication filter initialization from Hadoop configuration.

Important APIs/types/functions: `AuthFilterInitializer.initFilter`, `FilterContainer.addFilter`, `AuthFilter`, `PseudoAuthenticationHandler.ANONYMOUS_ALLOWED`, Mockito `doAnswer`.

Control flow: the test creates a configuration with `hadoop.http.authentication.*` Kerberos settings. A mocked `FilterContainer` intercepts `addFilter`; the answer asserts filter name/class and inspects the generated parameter map for cookie path, auth type, absent cookie domain, Kerberos principal/keytab, and anonymous allowed flag. Finally, `AuthFilterInitializer` is invoked.

State and persistence behavior: no persistence; all state is config and mocked call arguments.

Dependencies and integration points: connects HDFS Web auth initialization to Hadoop HTTP server filter registration and authentication-server constants.

Risks: raw Mockito `Answer` and unchecked map cast suppress type safety. It covers default cookie path/domain and anonymous flag but not alternate cookie domain or simple auth configurations.

Test signals: one filter registration with expected name/class and a correctly translated auth parameter map.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/web/TestAuthFilter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/web/TestFSMainOperationsWebHdfs.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/web/TestFSMainOperationsWebHdfs.java

Purpose: runs core `FSMainOperationsBaseTest` behavior through `WebHdfsFileSystem` and adds WebHDFS-specific operation tests.

Important APIs/types/functions: `MiniDFSCluster`, `WebHdfsTestUtil`, `FSMainOperationsBaseTest`, `concat`, `truncate`, `WebHdfsFileSystem.jsonParse`, `GetOpParam.Op.GETHOMEDIRECTORY`.

Control flow: a static cluster with two datanodes is started, root permissions are opened, and a non-superuser WebHDFS filesystem is created through UGI. `testConcat` creates three source files and one target, concatenates, verifies sources disappear and length grows. `testTruncate` truncates a two-block file to one block, checks content and space consumed. `testJsonParseClosesInputStream` spies an HTTP connection so `jsonParse` reads a wrapper stream and verifies it closes. The mkdirs override verifies that creating subdirectories below a file fails and leaves no visible subdirectory.

State and persistence behavior: static MiniDFSCluster, files under `/test/hadoop`, root permission mutation, non-superuser working directory. Cluster is shut down after all tests.

Dependencies and integration points: integrates WebHDFS client, NameNode HTTP endpoint, DFS permissions, content summary, append/truncate semantics, and HTTP connection handling.

Risks: shared static filesystem and mutable `closedInputStream` field may couple tests if failures leave state. Non-superuser behavior depends on root permission setup.

Test signals: file concat/truncate correctness, stream cleanup for connection reuse, and HDFS-specific mkdir failure semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/web/TestFSMainOperationsWebHdfs.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/web/TestHttpsFileSystem.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/web/TestHttpsFileSystem.java

Purpose: verifies secure WebHDFS (`swebhdfs`) works against an HTTPS-only MiniDFSCluster.

Important APIs/types/functions: `DFS_HTTP_POLICY_KEY`, HTTPS address keys, `KeyStoreTestUtil.setupSSLConfig`, `MiniDFSCluster`, `WebHdfsTestUtil.getWebHdfsFileSystem(conf, "swebhdfs")`.

Control flow: `setUp` configures HTTPS-only NameNode/DataNode endpoints on random ports, creates temporary keystore/SSL config files, starts a one-datanode cluster, writes `/test`, records the actual HTTPS NameNode address, and patches it into configuration. The test obtains an `swebhdfs` filesystem, creates `/testswebhdfs`, writes one byte, verifies existence, opens the file, and reads the expected byte. `tearDown` shuts down the cluster, deletes temp dirs, and cleans SSL config.

State and persistence behavior: temporary keystore directory and SSL config resources under the test temp path; MiniDFSCluster file state. Cleanup is class-level.

Dependencies and integration points: integrates WebHDFS over TLS, Hadoop SSL test utilities, NameNode HTTPS address publication, and filesystem open/create APIs.

Risks: SSL material setup/cleanup and port allocation can be environment-sensitive. The test validates basic create/read rather than certificate failure modes or DN redirect details.

Test signals: successful `swebhdfs` create, exists, open, and byte-level read through HTTPS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/web/TestHttpsFileSystem.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/web/TestJsonUtil.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/web/TestJsonUtil.java

Purpose: unit coverage for server/client WebHDFS JSON conversion helpers.

Important APIs/types/functions: `JsonUtil.toJsonString/toJsonMap`, `JsonUtilClient.toFileStatus`, `toDatanodeInfo`, `toAclStatus`, `toXAttrs`, `getXAttr`, `toSnapshotDiffReportListing`, `HdfsFileStatus.Builder`, `AclStatus`, `ContentSummary`, `SnapshotDiffReportListing`.

Control flow: file-status tests build `HdfsFileStatus` objects with and without EC policy and symlink data, serialize to JSON, parse with Jackson, reconstruct client-side status, and compare `FileStatus` equivalence. Datanode tests decode current and legacy `name`-based maps and assert invalid/missing address forms fail. ACL, content summary, and XAttr tests compare exact JSON strings or parsed structures. Snapshot diff listing tests round-trip empty and populated modify/create/delete entry lists and compare all fields/byte arrays.

State and persistence behavior: pure in-memory maps, JSON strings, and protocol objects.

Dependencies and integration points: bridges WebHDFS REST JSON shape with HDFS protocol classes, ACL/XAttr helpers, erasure coding policy encoding, and snapshot diff pagination models.

Risks: exact JSON string assertions are order-sensitive and tightly coupled to serializer output. `checkDecodeFailure` accepts any exception, not a specific parse error. Some timestamps use `Time.now`, but equality is round-trip based.

Test signals: JSON round-trip fidelity, backward-compatible datanode decoding, ACL/XAttr/content summary encoding, and snapshot diff listing preservation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/web/TestJsonUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/web/TestJsonUtilClient.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/web/TestJsonUtilClient.java

Purpose: focused client-side JSON helper tests for simple array conversion and block-location decoding.

Important APIs/types/functions: `JsonUtilClient.toStringArray`, `toBlockLocationArray`, `JsonUtil.toJsonMap`, `JsonUtil.toJsonString`, `JsonSerialization.mapReader`, `BlockLocation`, `StorageType`.

Control flow: `testToStringArray` converts a three-element `List<String>` and asserts length/order. `testToBlockLocationArray` builds a `BlockLocation` with names, hosts, topology path, storage type, offset, and length, serializes it through WebHDFS JSON helpers, parses it back to a map, converts via `JsonUtilClient`, and compares the string representation to the original block location.

State and persistence behavior: in-memory only.

Dependencies and integration points: verifies client JSON utility behavior used by WebHDFS block location REST responses and simple list conversion.

Risks: block-location comparison uses `toString`, which may miss fields not included in the string representation. Only a single block and storage type are covered.

Test signals: ordered string-array conversion and one-block BlockLocation JSON round trip.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/web/TestJsonUtilClient.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/web/TestWebHDFS.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/web/TestWebHDFS.java

Purpose: broad slow integration suite for WebHDFS client/server behavior across file I/O, REST responses, snapshots, erasure coding, quotas, storage policies, retries, symlinks, trash, statistics, and compatibility.

Important APIs/types/functions: `MiniDFSCluster`, `WebHdfsTestUtil`, `WebHdfsFileSystem`, `DistributedFileSystem`, `DFSTestUtil`, `SnapshotTestHelper`, `HdfsAdmin`, `StoragePolicySatisfier`, `WebHdfsInputStream`, REST params `LengthParam`, `OffsetParam`, `NoRedirectParam`, JSON helpers, `RetryPolicy`.

Control flow: each test starts a cluster and `tearDown` shuts it down. Early tests write/read a 200 MiB file with seek and positional read verification, test NameNode restart retry, large paginated directory listing with non-superuser UGI, file-space quota failure, customized username/ACL regexes, no-datanode create failure, invalid path REST error, snapshot allow/disallow/create/delete/rename/diff/listing, EC file status flags and EC policy commands, insecure delegation token fallback behavior, offset/length HTTP open, content summary and quota usage/setters, pread/stream mixing, home directory per user, block locations via API and raw REST, read retry classification with spies, `noredirect=true` location JSON and CORS, trash roots including snapshot and encryption zone cases, storage policy operations and disabled-policy error, external SPS behavior, append failure with insufficient DNs, fs server defaults and backward compatibility, exception cause propagation, WebHDFS statistics counters, symlink target/status, filesystem status, EC policy/codecs listing, and multi-user trash roots.

State and persistence behavior: heavy MiniDFSCluster filesystem state, global static `cluster`, randomized file contents, UGI login-user mutation in one test, external SPS lifecycle, key-provider test file for encryption zones, and raw HTTP connections.

Dependencies and integration points: covers most WebHDFS public API and REST surface, comparing many results against `DistributedFileSystem` as oracle. It integrates NameNode web resources, DataNode redirects, HDFS client retry policy, EC, snapshots, quotas, storage policies, encryption-zone trash, and statistics.

Risks: broad and slow; several tests use randomness, large I/O, raw HTTP, sleeps/retries, global cluster state, and external services. Some helper assertions compare JSON/objects manually and can be sensitive to protocol shape. The EC normal-file check appears to fetch `normalDir` status while comparing `normalFile` expectations, which is worth rechecking if that test changes.

Test signals: end-to-end WebHDFS parity with DFS APIs, REST status/error codes, redirect/noredirect behavior, retry/no-retry decisions, metadata serialization, and feature-specific regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/web/TestWebHDFS.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/web/TestWebHDFSAcl.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/web/TestWebHDFSAcl.java

Purpose: runs the shared NameNode ACL base test suite through WebHDFS.

Important APIs/types/functions: `FSAclBaseTest`, `WebHdfsTestUtil.createConf`, `startCluster`, `createFileSystem`, `createFileSystem(UserGroupInformation)`, `WebHdfsConstants.WEBHDFS_SCHEME`.

Control flow: class initialization creates WebHDFS test configuration and starts the inherited ACL test cluster. It overrides filesystem factories so base ACL tests operate via `WebHdfsFileSystem` as superuser or a specified UGI. One inherited test, `testDefaultAclNewSymlinkIntermediate`, is disabled because WebHDFS cannot currently resolve symlinks for that scenario.

State and persistence behavior: cluster and filesystem state are managed by `FSAclBaseTest`. This subclass contributes WebHDFS client selection and class-level configuration.

Dependencies and integration points: integrates WebHDFS with the generic HDFS ACL conformance suite, including user-specific clients.

Risks: most behavior is inherited, so this file's direct content is small but its executed surface is broad. The disabled symlink ACL case documents a known WebHDFS limitation and prevents false failure.

Test signals: all enabled base ACL operations must pass over WebHDFS, confirming parity with direct HDFS ACL behavior except the explicitly skipped symlink intermediate case.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/web/TestWebHDFSAcl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/web/TestWebHDFSForHA.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/web/TestWebHDFSForHA.java

Purpose: WebHDFS high-availability behavior across logical nameservice failover, delegation tokens, stale standby credentials, open streams, multi-namespace config, and startup retry.

Important APIs/types/functions: `MiniDFSNNTopology`, `DFSTestUtil.newHAConfiguration`, `HATestUtil.setFailoverConfigurations`, `WebHdfsFileSystem`, `DelegationTokenSecretManager`, `ExceptionHandler`, `JsonUtilClient.toRemoteException`, `Whitebox.setInternalState`, `SubjectInheritingThread`.

Control flow: tests build a two-NameNode HA topology under logical URI `webhdfs://minidfs`. `testHA` writes before and after active NN shutdown/failover. `testSecureHAToken` gets a delegation token, fails over, renews/cancels it, and verifies WebHDFS token methods were used. The stale-credentials test forces the old NameNode's secret manager to fail token lookup and verifies the server-side security exception is serialized back as a `StandbyException` client can unwrap. `testFailoverAfterOpen` opens an output stream before failover and writes/closes after. Multi-namespace config checks only the selected nameservice resolves two NN addresses. Startup retry nulls `NameNode.rpcServer`, starts a background mkdir via WebHDFS, restores the server, and waits for success.

State and persistence behavior: temporary HA clusters per test, files/directories under `/test`, token state in NameNode secret managers, and reflective mutation of NameNode internals.

Dependencies and integration points: HA failover proxy configuration, WebHDFS token lifecycle, server exception serialization, client retry, and startup race handling.

Risks: reflective `Whitebox` changes and threaded wait can be timing-sensitive. Token tests rely on secret-manager internals and mocked/spied filesystem registration.

Test signals: successful operation after failover, token renew/cancel routing, stale credential unwrapping, stream survival across failover, address resolution, and retry during startup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/web/TestWebHDFSForHA.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/web/TestWebHDFSXAttr.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/web/TestWebHDFSXAttr.java

Purpose: runs the shared extended-attribute base suite through WebHDFS.

Important APIs/types/functions: `FSXAttrBaseTest`, `createFileSystem`, `WebHdfsTestUtil.getWebHdfsFileSystem`, `WebHdfsConstants.WEBHDFS_SCHEME`.

Control flow: the subclass only overrides `createFileSystem` to return a `WebHdfsFileSystem` for the inherited configuration. All actual XAttr operation tests are inherited from `FSXAttrBaseTest`.

State and persistence behavior: inherited test cluster and filesystem state; this file contributes only WebHDFS client construction.

Dependencies and integration points: ties WebHDFS REST XAttr operations to the same expectations as native HDFS XAttr behavior.

Risks: because behavior is inherited, regressions may surface in this class without code here changing. The file does not override user-specific filesystem creation, so coverage depends on what `FSXAttrBaseTest` requires.

Test signals: inherited XAttr create/get/list/remove and permission behavior must pass via WebHDFS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/web/TestWebHDFSXAttr.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/web/TestWebHdfsFileSystemContract.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/web/TestWebHdfsFileSystemContract.java

Purpose: WebHDFS implementation of the generic filesystem contract plus direct REST edge-case tests.

Important APIs/types/functions: `FileSystemContractBaseTest`, static `MiniDFSCluster`, `WebHdfsTestUtil.getWebHdfsFileSystemAs`, `WebHdfsFileSystem.toUrl`, REST params (`LengthParam`, `OffsetParam`, `DoAsParam`, `NamenodeAddressParam`), `WebHdfsTestUtil.sendRequest/getAndParseResponse`.

Control flow: a static two-datanode cluster starts once and root permissions are opened. Each test uses a non-superuser WebHDFS client. Tests validate mkdir failure below files, block-location parity with DFS, case-insensitive `op` query handling, missing file open errors, seek and positional reads, root path behavior, `OPEN` length/offset truncation to actual content, many HTTP response codes and content types, bad doAs, empty set-owner/permission params, append, missing `namenoderpcaddress` on DN create redirect, JSON parse failure on non-JSON content, create paths with spaces, datanode create redirects missing optional params, and `access` permission/not-found behavior.

State and persistence behavior: persistent static cluster state across methods, per-test non-superuser UGI, files under `/test` and permission changes.

Dependencies and integration points: generic filesystem contract, WebHDFS URL generation, raw HTTP requests, NameNode/DataNode two-step create, access-control checks, and block-location JSON path.

Risks: static cluster has no explicit class teardown in this file, so lifecycle depends on test framework/JVM cleanup. Raw URL string manipulation is sensitive to parameter ordering and encoding. Case-insensitive op test notes Jersey2 URL-change support caveat.

Test signals: contract parity, raw REST response codes, redirect parameter handling, range reads, permissions, and block-location equivalence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/web/TestWebHdfsFileSystemContract.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/web/TestWebHdfsTimeouts.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/web/TestWebHdfsTimeouts.java

Purpose: verifies WebHDFS sets finite connect/read timeouts for normal, auth, redirect, and two-step write HTTP paths.

Important APIs/types/functions: `WebHdfsFileSystem`, `URLConnectionFactory`, `ConnectionConfigurator`, timeout config keys, `ServerSocket`, `SocketChannel`, `SubjectInheritingThread`, parameterized `TimeoutSource`.

Control flow: each parameterized test runs with timeouts supplied either by a custom connection factory or configuration. Setup binds a bogus server socket on the NameNode HTTP address; read-timeout tests let it accept no useful response, while connect-timeout tests fill the server backlog with nonblocking sockets. Redirect tests start one background thread that accepts the first request, switches the filesystem to short timeouts, optionally consumes backlog, and sends an HTTP 307 redirect back to the bogus server. Tests call `listFiles`, `getDelegationToken`, `getFileChecksum`, or `create/close` and expect `SocketTimeoutException` with connect/read messaging.

State and persistence behavior: local sockets, client channel list, WebHDFS client, and one server thread per redirect test. `tearDown` closes channels, filesystem, server socket, and joins the thread.

Dependencies and integration points: covers WebHDFS URL open paths including auth URLs, redirect handling, and DataNode write follow-up connections.

Risks: backlog saturation is OS-dependent; the test aborts when unable to prove backlog consumption. Timing is bounded by short 200 ms socket timeouts and JUnit 100-second method timeouts.

Test signals: timeout exceptions for all relevant HTTP paths and both timeout configuration sources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/web/TestWebHdfsTimeouts.java -->
