# Research: subset-b-007539

This grouped report covers the requested Hadoop HDFS test sources. Each section is source-tree aligned and is intended to be split into the matching `Docs/researches/<source_path>_research.md` file.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestSortLocatedBlock.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestSortLocatedBlock.java

Purpose: this JUnit 5 test validates `DatanodeManager.sortLocatedBlocks` for replicated `LocatedBlock` instances when locations have mixed service states. It covers live, stale, slow, stale-and-slow, entering maintenance, decommissioning, and decommissioned DataNodes, with configuration switches controlling whether stale and slow nodes should be avoided for reads.

Important APIs and types: `DatanodeManager`, `DatanodeInfo`, `DatanodeInfoWithStorage`, `LocatedBlock`, `ExtendedBlock`, `DFSConfigKeys`, `DFSTestUtil`, `Time`, and mocked `FSNamesystem`/`BlockManager`. The helper `mockDatanodeManager(boolean avoidStaleDNForRead, boolean avoidSlowDNForRead)` builds a real `DatanodeManager` around mocked NameNode services and a `BlockReportLeaseManager`. `mockDatanodes` constructs seven deterministic DataNodes and mutates their admin, stale, and slow-peer state.

Control flow: each test creates a single located block with an ordered location array, calls `dm.sortLocatedBlocks(null, locatedBlocks)`, then asserts the post-sort location order. `testWithStaleDatanodes` checks live before stale before maintenance before decommissioned. `testAviodStaleAndSlowDatanodes`, `testAviodStaleDatanodes`, `testAviodSlowDatanodes`, and `testWithServiceComparator` exercise the four combinations of stale/slow avoidance flags. Where the comparator intentionally treats two classes equally, assertions allow either order within that equivalence class.

State and persistence: there is no disk persistence. State is held in mutable `DatanodeInfo` objects and the `DatanodeManager` slow-peer set. Staleness is simulated by old monotonic timestamps relative to `DFS_NAMENODE_STALE_DATANODE_INTERVAL`.

Dependencies and integration points: this is a focused integration test of NameNode block-location ordering logic, but it avoids a MiniDFSCluster. It depends on Hadoop test utilities for synthetic DataNode identities and Mockito for the minimal NameNode/BlockManager collaborators required by `DatanodeManager`.

Risks: the test uses `==` for some IP string comparisons instead of `equals`, which works only because the same objects usually flow through sorting. The method names contain `Aviod`, so searches for "Avoid" may miss them. The stale interval constant differs from the configured default units used in one test, so future staleness semantics could make the fixtures fragile.

Test signals: successful execution means the read-location comparator preserves the intended priority tiers and handles decommissioning states after service-state ordering. Failures usually indicate a regression in read avoidance configuration, slow-peer ordering, or admin-state demotion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestSortLocatedBlock.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestSortLocatedStripedBlock.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestSortLocatedStripedBlock.java

Purpose: this test validates sorting of `LocatedStripedBlock` locations when erasure-coded block groups include decommissioned and stale DataNodes. It specifically guards the extra bookkeeping needed for striped blocks: after sorting locations, the parallel block-index and block-token arrays must be reordered consistently with their DataNode entries.

Important APIs and types: `LocatedStripedBlock`, `LocatedBlock`, `DatanodeManager`, `DatanodeInfo.AdminStates`, `ErasureCodingPolicy`, `StorageType`, `BlockTokenIdentifier`, `Token`, `StripedFileTestUtil`, and `DFSTestUtil`. Static setup creates a real `DatanodeManager` with stale-node avoidance enabled. Helper methods build synthetic striped block groups from the default EC policy, with deterministic local DataNode ports matching logical block indices.

Control flow: each test prepares lists of decommissioned logical block indices and replacement target indices, creates two located striped block groups, snapshots each location's block index and token, calls `dm.sortLocatedBlocks(null, lbs)`, then checks two invariants. First, normal/stale-valid locations must appear before decommissioned entries. Second, the location-to-index and location-to-token mapping must remain unchanged even though arrays are permuted. Covered scenarios include multiple decommissioned nodes, duplicate decommissioning for the same block index, fewer-than-full-stripe groups, missing replacement targets, and extra in-service stale targets.

State and persistence: all state is in memory. The block group uses synthetic `ExtendedBlock` metadata, arrays of storage IDs/types, and mutable `DatanodeInfo` admin/timestamp state. No MiniDFSCluster or disk state is involved.

Dependencies and integration points: this test integrates the replicated block-location sorter with striped-block-specific arrays and EC policy dimensions. It relies on the production `DatanodeManager` comparator and on `LocatedStripedBlock` internal array layout staying aligned across locations, indices, and tokens.

Risks: the fixture mutates `List<Integer>` by removing boxed integers and relies on deprecated `new Integer(...)` style to force value removal; changing to index removal would break intent. The tests focus on decommissioned and stale placement, not slow peers for striped blocks. Token assertions are strong because the default block-token array values are identity-sensitive to position.

Test signals: passing tests indicate decommissioned striped-block replicas are demoted without corrupting block-index/token alignment. Failures can imply client-side EC reads may contact poor targets or use a token/index for the wrong internal block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestSortLocatedStripedBlock.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestStorageBlockPoolUsageStdDev.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestStorageBlockPoolUsageStdDev.java

Purpose: this MiniDFSCluster test verifies that the NameNode's live-node JSON exposes `blockPoolUsedPercentStdDev` values that match the DataNode storage reports and `Util.getBlockPoolUsedPercentStdDev`.

Important APIs and types: `MiniDFSCluster`, `FileSystem`, `DFSTestUtil.createFile`, `DataNode`, `FSNamesystem`, `StorageReport`, `Util.getBlockPoolUsedPercentStdDev`, Jetty `JSON`, and HDFS capacity/block-size configuration keys.

Control flow: `setup` builds a five-DataNode cluster with three storages per DataNode and equal capacities. The test writes one single-block file to each DataNode using favored nodes and sizes 1000, 2000, 4000, 8000, and 16000 bytes. It triggers heartbeats, reads the NameNode live-node JSON, independently asks each DataNode dataset for storage reports for the current block pool, and asserts equality with a `0.01d` tolerance.

State and persistence: the cluster creates real temporary HDFS storage volumes. File placement is controlled by favored-node addresses so each DataNode gets a different block-pool usage distribution across its three storages. The observable state is propagated from DataNode datasets to NameNode heartbeat state and then serialized into live-node JSON.

Dependencies and integration points: this is an integration test across client write placement, DataNode storage accounting, heartbeat reporting, NameNode live-node aggregation, and JSON UI/JMX-style output. It assumes one block per file by keeping file sizes below the configured block size.

Risks: there is no explicit `@AfterEach` shutdown in this file, so cleanup relies on test harness behavior or JVM teardown if not handled elsewhere. Favored-node placement could become flaky if placement semantics change. The direct JSON cast assumes stable key types and the exact `DataNode.getDisplayName()` key used in `FSNamesystem.getLiveNodes()`.

Test signals: a failure indicates either standard deviation computation drift, heartbeat/report serialization mismatch, or a regression in storage-report visibility from DataNode to NameNode live-node output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestStorageBlockPoolUsageStdDev.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestUnderReplicatedBlocks.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestUnderReplicatedBlocks.java

Purpose: this test class exercises NameNode block-replication scheduling edge cases around under-replicated blocks and per-DataNode replication work limits.

Important APIs and types: `MiniDFSCluster`, `BlockManager`, `BlockManagerTestUtil`, `DFSTestUtil`, `FsShell`, `DatanodeDescriptor`, `DatanodeStorageInfo`, `DataNodeTestUtils`, and `Whitebox`. It uses direct block-map manipulation, invalidate scheduling, heartbeat triggering, and shell `-setrep`.

Control flow: `testSetRepIncWithUnderReplicatedBlocks` creates a replicated file, schedules invalidation for one replica, triggers DataNode heartbeat so deletion occurs, removes the same DataNode from `blocksMap`, and then runs `hdfs dfs -setrep -w` to increase replication. The test verifies client stats after each internal state mutation, ensuring a block that is under-replicated but not queued still tolerates replication-factor changes. `testNumberOfBlocksToBeReplicated` creates ten tiny blocks on two DataNodes, starts a third node, removes one source DataNode, computes replication work, and asserts the remaining source DataNode's queued replication count does not exceed the hard stream limit.

State and persistence: both tests use real MiniDFSCluster storage and NameNode metadata, then intentionally mutate in-memory NameNode `blocksMap`, invalidation queues, and DataNode descriptors. Heartbeat interval and replication-work multiplier are adjusted to keep pending work observable during the assertion window.

Dependencies and integration points: these tests are tightly coupled to `BlockManager` internals, DataNode heartbeat behavior, replication queues, and shell-facing replication changes. They are not pure black-box tests; they validate consistency under internal state that can occur during race windows.

Risks: direct use of `bm.blocksMap`, `removeNode`, `Whitebox.getInternalState`, fixed sleep, and DataNode lookup by IPC port makes the tests sensitive to implementation changes. The first test deletes metadata from the block map after a real invalidation flow, which is useful but nonstandard state.

Test signals: passing tests indicate robust handling of stale under-replicated accounting and enforcement of replication scheduling backpressure. Failures suggest NameNode replication work queues may over-assign, lose under-replication, or mishandle `setrep` after replica invalidation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestUnderReplicatedBlocks.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/common/StorageAdapter.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/common/StorageAdapter.java

Purpose: this small test adapter exposes package-private `Storage` internals to tests that need to replace a `StorageDirectory` with a Mockito spy.

Important APIs and types: `Storage`, `Storage.StorageDirectory`, and Mockito. The only public API is `spyOnStorageDirectory(Storage s, int idx)`.

Control flow: `spyOnStorageDirectory` retrieves the storage directory at the requested index, wraps it with `Mockito.spy`, replaces the element in `Storage.getStorageDirs()`, and returns the spy to the caller. There are no assertions or test methods here; it is a helper used by other test classes.

State and persistence: the helper mutates the in-memory list of storage directories inside a `Storage` instance. It does not touch disk directly, but callers generally use it to observe or alter behavior around filesystem-backed storage directories.

Dependencies and integration points: this file is in the same package as `Storage`, so it can access package-private state that downstream tests cannot reach directly. It is a bridge between HDFS storage internals and Mockito-based verification.

Risks: replacing a real storage directory with a spy can subtly affect identity comparisons, final method behavior, or serialization assumptions. Because it mutates shared storage state in place, callers must avoid leaking the spied object across unrelated tests.

Test signals: there are no local test signals. Its correctness is reflected by tests that can verify interactions on `StorageDirectory` without reimplementing storage internals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/common/StorageAdapter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/common/TestGetUriFromString.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/common/TestGetUriFromString.java

Purpose: this unit test validates `Util.stringAsURI(String)` for relative paths, absolute Unix paths, absolute Windows paths, and already-formed file URIs.

Important APIs and types: `Util.stringAsURI`, `URI`, JUnit assertions, and SLF4J logging. Constants encode representative path inputs and expected URI scheme/path values.

Control flow: `testRelativePathAsURI` only asserts that a relative string produces a non-null URI. `testAbsolutePathAsURI` feeds Windows and Unix absolute path strings and asserts that both become `file` scheme URIs. `testURI` passes valid Unix and Windows-style `file://` URIs and checks both scheme and decoded path, including `%20` decoding for spaces.

State and persistence: no persistent state exists. The tested utility may consult platform path behavior, but the test expects platform-independent handling for the supplied strings.

Dependencies and integration points: this is a narrow compatibility guard for common HDFS storage/config parsing code that accepts user-provided path or URI strings. It protects callers that pass checkpoint/name/data directory paths in either URI or local-path form.

Risks: the relative-path test does not assert scheme/path details, so regressions in relative-path normalization might slip through. Windows path behavior is tested on any OS using string shape rather than the host filesystem, which is useful but may not catch every Java URI edge case.

Test signals: failures indicate `Util.stringAsURI` no longer preserves file scheme expectations or decodes URI paths as callers expect.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/common/TestGetUriFromString.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/common/TestHostRestrictingAuthorizationFilter.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/common/TestHostRestrictingAuthorizationFilter.java

Purpose: this test checks `HostRestrictingAuthorizationFilter`, an HTTP filter that restricts WebHDFS operations by user, remote host/CIDR, and path rules while allowing unrelated NameNode HTTP requests through.

Important APIs and types: `HostRestrictingAuthorizationFilter`, servlet `Filter`, `FilterConfig`, `FilterChain`, `HttpServletRequest`, `HttpServletResponse`, `WebHdfsFileSystem.PATH_PREFIX`, and Hadoop `AuthenticationFilter` config. `DummyFilterConfig` supplies init parameters and a mocked servlet context.

Control flow: each test creates a mocked request/response pair and invokes the filter directly. `testAcceptAll` supplies a wildcard allow rule. `testAcceptGETFILECHECKSUM` checks that checksum GET is not treated like restricted file-open GET. `testRuleAllowedGet` configures a multi-rule allow string and sends a matching `op=OPEN` WebHDFS request. `testRejectsGETs` sends an OPEN request with no allow rule, exercising default denial behavior. `testUnexpectedInputMissingOpParameter` covers malformed/missing operation input. `testNotWebhdfsAPIRequest` verifies non-WebHDFS paths such as `/conf` pass through.

State and persistence: no persistent state is used. The filter stores parsed init parameters in memory. Request state comes entirely from Mockito stubs.

Dependencies and integration points: this is an HTTP-layer security test for WebHDFS. It integrates Hadoop authentication-filter settings with custom authorization logic, but uses direct servlet mocks rather than an embedded HTTP server.

Risks: several negative tests do not verify `sendError`, so they primarily ensure no crash rather than exact deny/allow status. Requests sometimes stub `getRemoteAddr` twice. Query-string parsing includes whitespace in `op=GETFILECHECKSUM `, making the test useful for tolerance but dependent on implementation trimming behavior.

Test signals: failures point to regressions in host allow-rule parsing, WebHDFS operation classification, or bypass behavior for non-WebHDFS endpoints.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/common/TestHostRestrictingAuthorizationFilter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/common/TestJspHelper.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/common/TestJspHelper.java

Purpose: this unit test covers `JspHelper` security and HTTP helper behavior: UGI construction from delegation tokens, SPNEGO-authenticated users, proxy users, startup-mode token verification, replica-state serialization, and trusted proxy remote-address resolution.

Important APIs and types: `JspHelper`, `UserGroupInformation`, `DelegationTokenIdentifier`, `Token`, `AbstractDelegationTokenSecretManager`, `NameNodeHttpServer`, `NameNode`, `ProxyUsers`, `ProxyServers`, `DefaultImpersonationProvider`, `HdfsServerConstants.ReplicaState`, `DataInputBuffer`, `DataOutputBuffer`, and servlet request/context mocks. `DummySecretManager` creates simple token passwords for test tokens.

Control flow: `testGetUgi` verifies delegation token service selection from URL `namenodeAddress`, servlet-context NameNode address, or preexisting token service. `testGetUgiFromToken` establishes that a delegation token overrides remote user, `user.name`, and `doas` parameters. `testGetNonProxyUgi` requires authenticated remote users under Kerberos and ignores conflicting user parameters. `testGetProxyUgi` configures proxy-user authorization and checks both valid impersonation and unauthorized failures. `testGetUgiDuringStartup` mocks a NameNode and expects `RetriableException` while token verification occurs during startup mode. The remaining tests validate replica-state read/write bounds and `X-Forwarded-For` handling when proxy servers are trusted.

State and persistence: the tests mutate global security configuration through `UserGroupInformation.setConfiguration`, proxy-user refresh, and Kerberos system properties. No disk persistence is involved.

Dependencies and integration points: this file is a high-value integration point between HDFS HTTP servlets, delegation token identity, Hadoop security auth methods, proxy-user authorization, and NameNode startup behavior.

Risks: global UGI/proxy configuration can leak across tests if not reset by the wider suite. Assertions are sensitive to exact exception messages. The token secret manager is deliberately minimal and should not be treated as production token verification coverage.

Test signals: failures indicate identity construction, impersonation authorization, token service assignment, or trusted proxy address logic changed in ways that can affect WebHDFS/JSP security.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/common/TestJspHelper.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/common/blockaliasmap/impl/TestInMemoryLevelDBAliasMapClient.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/common/blockaliasmap/impl/TestInMemoryLevelDBAliasMapClient.java

Purpose: this test validates the RPC client/server path for the in-memory LevelDB-backed provided-storage alias map. It checks read/write, iteration, batching, concurrent reads after writes, service bind host configuration, and missing/null block handling.

Important APIs and types: `InMemoryLevelDBAliasMapServer`, `InMemoryLevelDBAliasMapClient`, `InMemoryAliasMap`, `BlockAliasMap.Reader/Writer`, `FileRegion`, `Block`, `ProvidedStorageLocation`, `DFSConfigKeys`, `GenericTestUtils`, `LambdaTestUtils`, and Java executor/future concurrency utilities.

Control flow: `setUp` configures an RPC address, creates a temporary LevelDB root with a BPID subdirectory, and constructs server/client objects. Tests start the server and configure the client before exercising operations. `writeRead` stores and resolves one `FileRegion`. `iterateSingleBatch` and `iterateThreeBatches` write multiple regions and assert iteration order, with batch size forced to two in the latter. `multipleReads` prepares random regions, schedules delayed readers and earlier writers on a cached thread pool, then verifies all resolved regions match expected values in any order. `testServerBindHost` sets the NameNode service RPC bind host and reuses `writeRead`. `testNonExistentBlock` rejects a region with null `ProvidedStorageLocation` and confirms unresolved blocks return an empty optional.

State and persistence: alias data is backed by a temporary LevelDB directory under the test dir and removed in `tearDown`. Server/client lifecycle is explicit; resources are closed after each test.

Dependencies and integration points: this is the main integration test for alias-map RPC, provided-storage metadata serialization, LevelDB persistence, batch iteration, and bind-address handling.

Risks: fixed ports `9876` can collide in parallel test environments. The random input can include duplicate block IDs, which may reduce unique coverage. The executor is not explicitly shut down in `multipleReads`, relying on task completion and JVM cleanup.

Test signals: failures indicate breakage in alias-map RPC wiring, LevelDB-backed storage, iterator batching, or optional/error behavior for invalid mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/common/blockaliasmap/impl/TestInMemoryLevelDBAliasMapClient.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/common/blockaliasmap/impl/TestLevelDBFileRegionAliasMap.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/common/blockaliasmap/impl/TestLevelDBFileRegionAliasMap.java

Purpose: this test verifies the local `LevelDBFileRegionAliasMap` implementation for direct file-backed alias-map reads, writes, and iteration.

Important APIs and types: `LevelDBFileRegionAliasMap`, `LevelDBOptions`, `BlockAliasMap.Reader/Writer`, `FileRegion`, `Block`, `Path`, and Java `Iterator`.

Control flow: `testReadBack` creates a temporary directory, opens a writer for BPID `BPID-0`, stores one region, closes the writer, opens a reader, resolves the block, and asserts equality. `testIterate` stores ten deterministic regions across several paths, closes the writer, iterates all reader results, and checks that each block ID maps back to the expected array slot while adjacent duplicates are not observed.

State and persistence: test data is persisted to a temporary LevelDB directory and deleted in a `finally` block. The writer is closed before reader construction, making persistence and reopen behavior part of the test.

Dependencies and integration points: this is lower-level than the in-memory RPC client test. It validates the local alias-map contract used by provided storage and bootstrap metadata flows without server/client RPC.

Risks: `dbFile.delete()` only deletes empty directories, so LevelDB contents may remain if not cleaned elsewhere; recursive delete would be stronger. The iteration test assumes ordering by block ID and contiguous block IDs from 1 to 10.

Test signals: failures indicate local LevelDB encoding, lookup, or iterator ordering no longer matches `FileRegion` alias-map expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/common/blockaliasmap/impl/TestLevelDBFileRegionAliasMap.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/common/blockaliasmap/impl/TestLevelDbMockAliasMapClient.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/common/blockaliasmap/impl/TestLevelDbMockAliasMapClient.java

Purpose: this test isolates client error handling for `InMemoryLevelDBAliasMapClient` by backing the server with a mocked `InMemoryAliasMap` that throws storage-layer exceptions.

Important APIs and types: `InMemoryLevelDBAliasMapServer`, `InMemoryLevelDBAliasMapClient`, mocked `InMemoryAliasMap`, `Block`, `ProvidedStorageLocation`, `FileRegion`, AssertJ exception assertions, Mockito `doThrow`, and `DBException`.

Control flow: `setUp` creates a mock alias map with a BPID, starts an alias-map server using a factory that returns the mock, configures a client, and points LevelDB config at a temporary directory. `readFailure` configures the mock `read` method to throw `IOException` and then `DBException`, verifying both surface to the client caller as `IOException`. `writeFailure` configures the mock `write` method to throw `IOException` and verifies repeated writer `store` calls propagate `IOException`.

State and persistence: temporary directories and server/client resources are cleaned in `tearDown`, but the core alias state is mocked and not persisted.

Dependencies and integration points: the test exercises RPC client/server exception translation rather than LevelDB storage correctness. It is useful for ensuring storage exceptions do not leak as unchecked or protocol-specific failures to alias-map callers.

Risks: fixed port `9877` can collide under parallel runs. The second `writeFailure` assertion depends on Mockito behavior after a single `doThrow` setup; Mockito repeats the throwable for subsequent invocations, which is intended but implicit. The test does not verify server-side logging or status codes.

Test signals: failures indicate read/write exception translation or RPC error wrapping changed in the alias-map client stack.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/common/blockaliasmap/impl/TestLevelDbMockAliasMapClient.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/common/blockaliasmap/impl/TestTextBlockAliasMap.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/common/blockaliasmap/impl/TestTextBlockAliasMap.java

Purpose: this test covers the text-based `TextFileRegionAliasMap` format used for provided-storage block maps. It validates writer/reader option resolution, compression codec selection, CSV/TSV serialization, multiple independent iterators, and iterator invalidation after reader close.

Important APIs and types: `TextFileRegionAliasMap`, `TextReader`, `TextWriter`, `WriterOptions`, `ReaderOptions`, `FileRegion`, `DataOutputBuffer`, `DataInputBuffer`, `CompressionCodecFactory`, `GzipCodec`, and `fileNameFromBlockPoolID`.

Control flow: overloaded `check` helpers subclass `TextFileRegionAliasMap` and intercept `createWriter` or `createReader` to assert resolved path and codec. `testWriterOptions` checks default output dir, no default codec, BPID-derived filename, and gzip suffix/codec behavior. `testReaderOptions` checks explicit filenames with and without gzip. `testCSVReadWrite` and `testCSVReadWriteTsv` write three `FileRegion` rows into an in-memory buffer using comma or tab delimiters, create a custom reader over that buffer, interleave two iterators to prove independence, and confirm an iterator obtained before close throws `IllegalStateException` afterward.

State and persistence: all data is in memory; no filesystem writes occur. Options are mutable objects, so tests mutate and reuse them deliberately.

Dependencies and integration points: this file guards the human-readable alias-map interchange format, including codec detection by path suffix and delimiter handling. It complements LevelDB tests by covering text import/export style flows.

Risks: tests use simple paths and offsets and do not cover delimiters embedded in path text. The reader/writer factory interception returns null intentionally, so only option resolution is tested there, not actual stream creation.

Test signals: failures suggest path/codec option derivation, file-region text serialization, or iterator lifecycle semantics changed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/common/blockaliasmap/impl/TestTextBlockAliasMap.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/common/sps/TestBlockDispatcher.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/common/sps/TestBlockDispatcher.java

Purpose: this test validates a retry-path detail in SPS `BlockDispatcher`: when SASL block movement fails due to `InvalidEncryptionKeyException`, the dispatcher must clear the cached data-encryption key before retrying.

Important APIs and types: `BlockDispatcher`, `BlockMovingInfo`, `SaslDataTransferClient`, `DataEncryptionKeyFactory`, `InvalidEncryptionKeyException`, `ExtendedBlock`, `Token<BlockTokenIdentifier>`, `DatanodeInfo`, `StorageType`, and a fake `Socket`.

Control flow: the test constructs source/target DataNodes, a block movement command, a `CountingKeyFactory`, and an `InvalidKeySaslClient` whose `socketSend` always throws `InvalidEncryptionKeyException` while counting attempts. A custom `BlockDispatcher` overrides `newSocket` to return `FakeSocket`. The call to `moveBlock` is expected to throw after retry; assertions require one key clear and two SASL send attempts.

State and persistence: there is no persistent state. Counters in fake collaborators capture retry behavior. The fake socket uses in-memory byte streams and no network connection.

Dependencies and integration points: the test sits at the data-transfer/SPS boundary, where storage policy satisfaction moves blocks between DataNodes and must handle encrypted data-transfer key expiry. It verifies `BlockDispatcher` retry side effects without requiring a real cluster or real SASL negotiation.

Risks: because the SASL client always throws, the test only validates the invalid-key retry path, not successful second-attempt movement. It also assumes exactly two attempts for this error class.

Test signals: failures mean encryption-key cache invalidation or retry count changed, which can affect block movement under encrypted data transfer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/common/sps/TestBlockDispatcher.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/BlockReportTestBase.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/BlockReportTestBase.java

Purpose: this abstract JUnit base class defines a comprehensive block-report test suite. Subclasses provide `sendBlockReports`, allowing the same scenarios to run against different block-report batching/splitting strategies.

Important APIs and types: `MiniDFSCluster`, `DistributedFileSystem`, `DataNode`, `BlockManager`, `StorageBlockReport`, `BlockListAsLongs`, `BlockReportReplica`, `DatanodeRegistration`, `DatanodeProtocolClientSideTranslatorPB`, `DelayAnswer`, `Replica`, `HdfsServerConstants.ReplicaState`, and many `DFSTestUtil`/`BlockManagerTestUtil` helpers. `getBlockReports` builds reports from the DataNode dataset and can corrupt one replica's generation stamp or length.

Control flow: setup creates a one-DataNode cluster with small block/checksum sizes; teardown closes filesystem and cluster. The numbered tests cover stale length changes ignored by block reports, missing block files producing missing/under-replicated accounting, bad generation stamps producing corrupt replicas, extra unknown blocks producing pending deletion, replication completion after adding a DataNode, older/bad replicas on a second DataNode, temporary replicas during replication being ignored, RBW reports arriving after block completion, and concurrent/interleaved block reports preserving DataNode storage identity. Helpers write files, start extra DataNodes, locate blocks, wait for temporary replicas, recursively delete block files, and print NameNode block stats.

State and persistence: the class uses real MiniDFSCluster disks and NameNode metadata, then intentionally mutates block files, in-memory block reports, replica states, and timing. Static `conf` and `REPL_FACTOR` are reset in controlled places; tests that change block size restart the cluster.

Dependencies and integration points: this is a central integration fixture for DataNode-to-NameNode block reporting, replica state handling, storage report identity, replication scheduling, corruption detection, and race windows around file close and block report RPCs.

Risks: tests are timing-sensitive, with sleeps, polling loops, concurrent RPCs, and a 40-second temporary-replica wait. They depend on internal file naming, block-map behavior, and exact NameNode counters. There are duplicate annotations and duplicated local code snippets in the source, but intent remains clear.

Test signals: failures indicate regressions in block report interpretation, corrupt/missing/pending-deletion accounting, handling of temporary/RBW replicas, or thread safety of concurrent reports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/BlockReportTestBase.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/DataNodeTestUtils.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/DataNodeTestUtils.java

Purpose: this utility exposes package-private or operational DataNode behavior to tests while deliberately avoiding Mockito imports so downstream projects can still start MiniDFSCluster with limited dependencies.

Important APIs and types: `DataNode`, `MiniDFSCluster`, `BPOfferService`, `FsDatasetSpi`, `FsVolumeSpi`, `FsVolumeImpl`, `FsDatasetTestUtil`, `DatanodeRegistration`, `InterDatanodeProtocol`, `StorageLocation`, and `GenericTestUtils.waitFor`.

Control flow: simple helpers get a DataNode registration, toggle heartbeat/cache-report/IBR test flags, trigger deletion reports, heartbeats, and block reports across all block-pool offer services, create inter-DataNode protocol proxies with hostname-setting assertions, expose the DataNode dataset, and fetch replica info. Disk-failure helpers rename data directories to `.origin`, create files in their place, and restore the original directories later. Reconfiguration builds a comma-separated data-dir list and calls `reconfigurePropertyImpl`, swallowing `ReconfigurationException` for tests that intentionally hit failed volumes. Volume helpers locate an `FsVolumeImpl` by base URI and wait for async disk-error checks to complete.

State and persistence: several methods mutate real filesystem directories and DataNode runtime flags. `injectDataDirFailure` and `restoreDataDirFromFailure` are persistent on disk until restored, so callers must use cleanup reliably.

Dependencies and integration points: this is a shared white-box bridge for tests of DataNode heartbeats, block reports, volume failures, dynamic volume reconfiguration, and dataset internals. It integrates with production DataNode APIs but remains in test scope.

Risks: directory failure injection is destructive if restore is skipped or if `.origin` already exists. Reconfiguration intentionally hides some exceptions, which is useful for tests but can obscure unexpected failures. The "no Mockito" constraint is important and documented in the source.

Test signals: no local tests exist; downstream tests using this helper signal whether DataNode internals remain reachable and controllable for test scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/DataNodeTestUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/FsDatasetImplTestUtilsFactory.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/FsDatasetImplTestUtilsFactory.java

Purpose: this factory adapts the default `FsDatasetImplTestUtils` implementation to the generic `FsDatasetTestUtils.Factory` contract.

Important APIs and types: `FsDatasetTestUtils.Factory`, `FsDatasetTestUtils`, `FsDatasetImplTestUtils`, and `DataNode`.

Control flow: `newInstance(DataNode datanode)` returns a new `FsDatasetImplTestUtils` bound to the supplied DataNode. `getDefaultNumOfDataDirs()` returns `FsDatasetImplTestUtils.DEFAULT_NUM_OF_DATA_DIRS`.

State and persistence: the factory has no state and performs no persistence. The returned utility operates on a real DataNode dataset and may perform persistent operations, but this class only constructs it.

Dependencies and integration points: it is the default test-utility factory selected by `FsDatasetTestUtils.Factory.getFactory` when the configured dataset factory resolves to the normal `FsDatasetFactory`. It keeps tests generic across real and simulated datasets.

Risks: class-name convention matters: `FsDatasetTestUtils.Factory.getFactory` derives `...TestUtilsFactory` from the configured dataset factory name, so renaming this class or changing package placement would break reflective lookup. The implementation is intentionally small and should remain aligned with `FsDatasetImplTestUtils`.

Test signals: no direct tests live here. Successful dataset white-box tests using the default dataset factory confirm that reflective selection and default data-dir counts still work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/FsDatasetImplTestUtilsFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/FsDatasetTestUtils.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/FsDatasetTestUtils.java

Purpose: this private unstable test interface defines white-box operations for manipulating and inspecting DataNode `FsDataset` replicas in tests, abstracting over real and simulated dataset implementations.

Important APIs and types: `ExtendedBlock`, `Replica`, `ReplicaInPipeline`, `ReplicaBeingWritten`, `ReplicaWaitingToBeRecovered`, `ReplicaUnderRecovery`, `FsVolumeSpi`, `Configuration`, `DFSConfigKeys`, `ReflectionUtils`, and `FsDatasetFactory`. The nested `Factory` derives a corresponding `TestUtilsFactory` class from the configured dataset factory class name.

Control flow: `Factory.getFactory` reads `dfs.datanode.fsdataset.factory`, asserts the name contains `Factory`, replaces the suffix with `TestUtilsFactory`, and instantiates it as a `Factory`. Implementations then create utility instances for a DataNode and report default data-dir counts. The interface exposes methods to create replicas in finalized/RBW/pipeline/recovery states, corrupt/truncate/delete block and metadata files via `MaterializedReplica`, inspect stored lengths and generation stamps, change persisted generation stamps, iterate stored replicas, query pending async deletion count, and verify block-pool presence/absence.

State and persistence: this is a contract for persistent dataset mutation. Implementations may write files, corrupt files, delete metadata, or alter generation stamps, and those changes may survive MiniDFSCluster shutdown depending on the underlying dataset.

Dependencies and integration points: many HDFS tests use this abstraction to avoid hard-coding `FsDatasetImpl` layout. It is also the hook that allows `SimulatedFSDataset` to provide compatible behavior where possible.

Risks: reflective factory naming is convention-based and brittle. Methods intentionally permit destructive corruption, so tests must scope blocks and cleanup carefully. Because the interface is marked unstable, implementations and callers must evolve together.

Test signals: no local assertions exist. The interface is validated indirectly by block recovery, corruption, scanner, and dataset tests that use it across dataset implementations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/FsDatasetTestUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/InternalDataNodeTestUtils.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/InternalDataNodeTestUtils.java

Purpose: this Mockito-enabled DataNode test utility contains internal helpers that should not leak to downstream MiniDFSCluster users. It complements `DataNodeTestUtils` by allowing spies and mocks.

Important APIs and types: `DataNode`, `FsDatasetSpi`, `DatanodeProtocolClientSideTranslatorPB`, `BPOfferService`, `BPServiceActor`, `NameNode`, `NamespaceInfo`, `HeartbeatResponse`, `NNHAStatusHeartbeat`, `StorageLocation`, Mockito spies/mocks/answers, and `Preconditions`.

Control flow: `mockDatanodeBlkPinning` wraps `dn.data` in a spy and overrides `getPinning` to return a fixed value. `spyOnBposToNN` finds the `BPOfferService` for a NameNode block pool, locates the service actor connected to the NameNode service RPC address, spies on the existing NameNode proxy, installs the spy, and returns it for call interception. `startDNWithMockNN` configures a fake HDFS URI, creates a local storage directory, mocks the NameNode protocol, returns registrations unchanged, supplies namespace info and active heartbeat responses, constructs a `DataNode` overriding `connectToNN`, and triggers an initial heartbeat.

State and persistence: helpers mutate DataNode internals by replacing dataset/proxy references. `startDNWithMockNN` deletes and recreates a supplied data directory and starts a real DataNode against mocked NameNode RPC.

Dependencies and integration points: this file is used for race and protocol tests that need to delay, assert, or fake DataNode-to-NameNode traffic. It directly integrates with BP service actor internals and should track those implementations closely.

Risks: replacing internal fields with spies can change behavior if methods are final or if concurrency expects the original object. `startDNWithMockNN` performs filesystem deletion on the provided path. Exact NameNode service address matching must remain consistent with BP actor setup.

Test signals: downstream tests using delayed block reports, mocked pinning, or mock NameNode startup provide coverage. Failures usually indicate DataNode protocol wiring or internal field layout changed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/InternalDataNodeTestUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/SimpleBlocksMovementsStatusHandler.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/SimpleBlocksMovementsStatusHandler.java

Purpose: this simple test implementation of `BlocksMovementsStatusHandler` collects completed storage-policy-satisfier block movement attempts so tests can inspect and remove them later.

Important APIs and types: `BlocksMovementsStatusHandler`, `BlockMovementAttemptFinished`, Hadoop `Block`, `List`, and `Collections.unmodifiableList`.

Control flow: `handle` extracts the block from a completed movement event and appends it to `blockIdVsMovementStatus` under synchronization. `getMoveAttemptFinishedBlocks` returns an empty mutable list if no blocks are present, otherwise an unmodifiable view of the backing list. `remove` removes supplied blocks from the tracking list if the argument is non-null. `removeAll` clears the list under synchronization.

State and persistence: state is an in-memory `ArrayList<Block>`. There is no disk or network persistence. Synchronization is partial: add, read, and clear synchronize on the list, but `remove` calls `removeAll` without the same lock.

Dependencies and integration points: this class plugs into DataNode/SPS tests that need a lightweight movement-status sink instead of the production heartbeat path to the NameNode.

Risks: `getMoveAttemptFinishedBlocks` can return an unmodifiable view of the live backing list, so later mutations are visible and concurrent iteration may still be unsafe. `remove` is not synchronized, unlike other mutating operations. The field name says status but stores only block IDs, so it does not preserve success/failure detail.

Test signals: no local tests exist. It is validated indirectly when SPS/DataNode tests can observe expected movement-completion blocks and clear them.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/SimpleBlocksMovementsStatusHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/SimulatedFSDataset.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/SimulatedFSDataset.java

Purpose: this test-scope `FsDatasetSpi` implementation simulates DataNode storage without storing block bytes. It records block metadata, returns deterministic synthetic bytes on reads, tracks capacity/usage per simulated storage and block pool, and supports enough replica lifecycle behavior for MiniDFSCluster tests that prefer fast in-memory storage.

Important APIs and types: `FsDatasetSpi`, `FsVolumeSpi`, `ReplicaInPipeline`, `ReplicaHandler`, `ReplicaState`, `Block`, `ExtendedBlock`, `BlockListAsLongs`, `DatanodeStorage`, `StorageReport`, `VolumeFailureSummary`, `DataNodeVolumeMetrics`, `FSDatasetMBean`, `MBeans`, `DataChecksum`, and `DataNodeLockManager`. Nested types include `Factory`, `TestUtilsFactory`, `BInfo`, `SimulatedBPStorage`, `SimulatedStorage`, `SimulatedVolume`, `SimulatedInputStream`, and `SimulatedOutputStream`.

Control flow: `setFactory` installs the simulated dataset factory and matching test-utils factory in configuration. Construction determines storage count from `DataStorage` or configured storage locations, creates simulated storages with capacity/state/non-DFS-used values, and registers an FSDataset MBean. Blocks are assigned to storages by `blockId mod storageCount`. `injectBlocks`, `createTemporary`, `createRbw`, `append`, `recoverAppend`, `recoverClose`, `recoverRbw`, and `finalizeBlock` manipulate `BInfo` records in per-block-pool maps. Reads use `SimulatedInputStream`, whose bytes are derived from block ID and offset; metadata reads return a null-checksum header. Block reports include only finalized replicas. Invalidation frees capacity, removes block metadata, and optionally notifies the DataNode.

State and persistence: all block maps and usage counters are in memory and are explicitly not remembered across restarts. Capacity accounting is persistent only for the life of the dataset object. MBean registration is process-global and must be unregistered in `shutdown`.

Dependencies and integration points: this dataset integrates with DataNode storage, block reports, recovery, volume references, metrics, storage reports, cache API stubs, and pinning. Many advanced features are unsupported or no-op, such as trash, lazy persist, local path info, cache operations, volume add/remove, and scanner check/update.

Risks: synchronization is coarse and not universal across nested storage structures. Several interface methods return null or throw `UnsupportedOperationException`, so tests must stay within the supported subset. It does not persist across restart, which is intentional but can invalidate tests expecting real disk semantics. Capacity accounting depends on correct finalize/unfinalize/invalidate paths.

Test signals: tests using simulated storage validate DataNode protocol and block-management logic without physical block files. Failures usually indicate lifecycle incompatibility with `FsDatasetSpi`, incorrect usage accounting, unsupported method reachability, or replica-state mismatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/SimulatedFSDataset.java -->
