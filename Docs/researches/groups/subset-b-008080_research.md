<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestFailureHandlingByClient.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestFailureHandlingByClient.java

Purpose: This integration test exercises Ozone RPC client write recovery when RATIS pipelines, containers, or datanodes fail while a key stream is open. It runs a 10-datanode `MiniOzoneCluster`, writes through `OzoneOutputStream`/`KeyOutputStream`, kills pipeline members or closes containers, and verifies that the client retries to new blocks while OM key length, data content, and exclude-list state remain correct.

Important APIs/types/functions: The fixture configures `RatisClientConfig`, `DatanodeRatisServerConfig`, `OzoneClientConfig`, SCM pipeline limits, and network-topology-aware reads. Tests use `TestHelper.createKey`, `TestHelper.validateData`, `ContainerTestHelper.getFixedLengthString`, `KeyOutputStream.getLocationInfoList`, `getStreamEntries`, `getExcludeList`, SCM `ContainerManager`/`PipelineManager`, and OM `lookupKey`. `testBlockCountOnFailures` opens datanode container RocksDB via `BlockUtils.getDB` and validates `BlockData` chunk count and size.

Control flow: `init` creates volume/bucket and disables stream-buffer flush delay. `restartDownDataNodes` restarts nodes queued by prior tests. `testBlockWritesWithDnFailures` writes 2.5 chunks, kills two replicas, closes the stream, then checks OM data size and physical block accounting. `testWriteSmallFile` forces replacement of a failed first block. `testContainerExclusionWithClosedContainerException` closes a container and expects only the container ID in the exclude list. `testDatanodeExclusionWithMajorityCommit` varies RATIS watch type and verifies datanode exclusion only for `ALL_COMMITTED`. `testPipelineExclusionWithPipelineFailure` kills two nodes and expects pipeline exclusion.

State and persistence behavior: The tests inspect OM key metadata, container metadata tables, block IDs, chunk lists, used block sizes, and client exclude-list contents. They confirm failed chunks do not corrupt committed length and that rewritten data lands in replacement blocks or pipelines.

Dependencies and integration points: Covers Ozone client streaming, SCM pipeline/container lookup, RATIS write/watch semantics, datanode lifecycle operations, container RocksDB block tables, and OM key finalization. It also depends on retry timing and leader election settings to make failures surface quickly.

Risks: The tests are timing-sensitive and one path is marked flaky. They rely on exact failure classification: closed containers, stopped datanodes, and broken pipelines must map to distinct exclude-list dimensions. Assertions that inspect datanode-local DB state can fail if commit-watcher timing changes valid chunk-count scenarios.

Test signals: Successful run proves key data remains readable after mid-stream failures, OM `dataSize` matches user bytes, failed blocks are discarded or rewritten, and exclude lists contain the expected container, datanode, or pipeline identifiers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestFailureHandlingByClient.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestFailureHandlingByClientFlushDelay.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestFailureHandlingByClientFlushDelay.java

Purpose: This variant retests pipeline failure handling with stream-buffer flush delay and tiny test sizes. It verifies client behavior when buffered writes, explicit flushes, and pipeline shutdown interact.

Important APIs/types/functions: The fixture uses `ClientConfigForTesting` to set `CHUNK_SIZE`, `FLUSH_SIZE`, `MAX_FLUSH_SIZE`, and `BLOCK_SIZE`, plus RATIS/SCM timeout knobs. The main test uses `KeyOutputStream`, `BlockOutputStreamEntry`, SCM pipeline lookup, datanode shutdown, `OmKeyArgs`, `OmKeyInfo`, and `TestHelper.validateData`.

Control flow: `init` builds a 10-datanode cluster, creates a volume and bucket, and configures static rack mapping. `testPipelineExclusionWithPipelineFailure` creates a RATIS key sized to one block, writes and flushes one chunk, discovers the backing container and pipeline, shuts down two nodes, writes and flushes again, checks that no container or datanode entries were recorded in the exclude list at that point, writes a third copy, and closes. OM lookup then verifies that a new block replaced the original failed block and the final key size is three chunks.

State and persistence behavior: The test is focused on visible client stream state and OM key metadata. It checks block ID replacement, final data size, and full readback, but does not inspect container RocksDB directly.

Dependencies and integration points: It integrates the client flush-delay buffering path with RATIS pipeline failure classification, SCM pipeline selection, datanode shutdown, and OM close-key commit handling.

Risks: Because failure is induced between flushes, the exact point where the stream observes the pipeline failure depends on buffering thresholds and asynchronous RATIS responses. The duplicated assertion on datanodes indicates this test primarily protects final rewrite/read correctness rather than every intermediate exclude-list dimension.

Test signals: Passing means delayed-flush writes survive two-node pipeline failure, are finalized in OM with correct length, and validate through normal Ozone reads.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestFailureHandlingByClientFlushDelay.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestHybridPipelineOnDatanode.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestHybridPipelineOnDatanode.java

Purpose: This test verifies that RATIS pipelines with different replication factors can coexist on overlapping datanodes and still serve client I/O correctly.

Important APIs/types/functions: It uses `MiniOzoneCluster`, `OzoneClientFactory`, `ObjectStore`, `OzoneVolume`, `OzoneBucket`, `TestDataUtil.createKey`, `OzoneKeyDetails.getOzoneKeyLocations`, SCM `getContainerInfo`, `PipelineManager.getPipeline`, and standard `bucket.readKey`.

Control flow: A 3-datanode cluster is started with SCM RATIS pipeline limit 5. The test creates a volume/bucket, writes one key with RATIS/ONE and another with RATIS/THREE, resolves each key's container and pipeline ID, and compares pipeline type, node membership, and identity. It asserts the RATIS/ONE pipeline has one node, the RATIS/THREE pipeline is a distinct RATIS pipeline, and the three-node pipeline contains the single-node pipeline's datanode. Finally it reads both keys and compares bytes with the original payload.

State and persistence behavior: Persistent state is limited to key objects, container location metadata, and SCM pipeline records. The test does not mutate local container files; it validates that metadata placement and stored bytes are consistent.

Dependencies and integration points: Integrates client key creation, SCM pipeline allocation for mixed factors, datanode membership accounting, and read path correctness across different replication factors.

Risks: The placement assertion depends on SCM choosing a three-replica pipeline that includes the node selected for the one-replica pipeline. Pipeline policy or limit changes can alter this without breaking client functionality.

Test signals: Passing confirms mixed RATIS factor placement is allowed on the same datanode set and both keys remain readable through the RPC client.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestHybridPipelineOnDatanode.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestMultiBlockWritesWithDnFailures.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestMultiBlockWritesWithDnFailures.java

Purpose: This class tests multi-block RATIS writes when datanodes fail after some blocks have already been allocated or preallocated. It ensures stream close reconciles successful and retried blocks into correct OM length and readable data.

Important APIs/types/functions: The fixture configures RATIS client/server timeouts, SCM stale-node interval, leader election timeout, pipeline limit, and a `MiniOzoneCluster`. Tests use `OzoneOutputStream`, `KeyOutputStream.getLocationInfoList`, `getStreamEntries`, `BlockOutputStreamEntry`, SCM container/pipeline lookup, `shutdownHddsDatanode`, OM `lookupKey`, and `TestHelper.validateData`.

Control flow: `testMultiBlockWritesWithDnFailures` writes data spanning more than one block, confirms two block locations, shuts down two nodes from the second block's pipeline, writes the same data again, closes, then checks OM size equals two writes. `testMultiBlockWritesWithIntermittentDnFailures` preallocates six blocks, writes two data spans, kills one pipeline node, writes again, kills a second node, writes a fourth span, closes, and validates final length/content.

State and persistence behavior: The tests observe client block-location state and OM key metadata after close. They do not inspect container-local RocksDB, but they depend on OM discarding failed preallocated locations and counting only successfully committed user bytes.

Dependencies and integration points: Covers KeyOutputStream retry and block-preallocation behavior, SCM pipeline lookup, datanode shutdown, RATIS failure handling, and OM key finalization.

Risks: The intermittent-failure case is marked flaky and is sensitive to exactly when failed pipelines are detected. Preallocation count and pipeline placement can change with SCM policy settings.

Test signals: Passing indicates multi-block client writes recover from one or two datanode failures, close without losing data, and persist the expected key size in OM.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestMultiBlockWritesWithDnFailures.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestOzoneAtRestEncryption.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestOzoneAtRestEncryption.java

Purpose: This integration test validates transparent data encryption at rest for normal keys, stream keys, OFS filesystem writes, link buckets, GDPR metadata deletion, encrypted multipart uploads, and key-provider cache lifecycle.

Important APIs/types/functions: Setup starts `MiniKMS`, enables secure OM/block tokens with `CertificateClientTestImpl` and `SecretKeyTestClient`, creates a KMS key through `KeyProvider`, starts the OM secret manager, and configures block/chunk sizes. Main APIs include `BucketArgs.setBucketEncryptionKey`, `OzoneBucket.createKey`, `createStreamKey`, `readKey`, `FileSystem` OFS writes, `OzoneKeyDetails.getFileEncryptionInfo`, `ClusterContainersUtil.verifyOnDiskData`, `bucket.initiateMultipartUpload`, `createMultipartKey`, `createMultipartStreamKey`, `completeMultipartUpload`, `MultipartInputStream`, OM deleted table scanning, and `RpcClient.getKeyProviderCache`.

Control flow: The setup installs a KMS provider URI, starts a 10-datanode cluster, sets a 256 KiB minimum MPU part size, creates `TEST_KEY`, and configures OFS as default FS. Tests warm up OM EDEK cache after OM restart, create encrypted buckets for every `BucketLayout`, verify direct/stream/OFS writes, verify link buckets inherit encryption, and ensure overwrites get distinct encryption info. GDPR tests delete encrypted keys and assert deleted-table metadata no longer retains GDPR secret fields or file encryption info. MPU tests upload one to three encrypted parts through byte-array and stream paths, complete uploads, read through `MultipartInputStream`, and exercise seeks/reads around crypto buffer, chunk, and block boundaries. `testGetKeyProvider` checks cached key providers are reused and closed on client close.

State and persistence behavior: The tests verify OM key metadata includes `FileEncryptionInfo` while live, deleted table entries are scrubbed, KMS EDEK queues are populated, on-disk container data differs from plaintext, multipart part ETags are committed, and final multipart keys are readable at arbitrary offsets.

Dependencies and integration points: Integrates KMS, Hadoop crypto buffer sizing, secure OM flags, block tokens, SCM/container storage, OFS filesystem adapter, Object Store and FSO bucket layouts, OM metadata tables, deleted-table cleanup, and multipart read composition.

Risks: The test is expensive and timing-sensitive around KMS cache warmup and OM restart. Encryption assertions depend on local container disk inspection. MPU stream cases are marked flaky, likely due to stream finalization or multipart read timing.

Test signals: Passing proves encrypted buckets decrypt through client APIs, persist ciphertext on disk, avoid leaking sensitive deleted metadata, support encrypted multipart uploads, and manage key-provider cache resources.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestOzoneAtRestEncryption.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestOzoneClientMultipartUploadWithFSO.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestOzoneClientMultipartUploadWithFSO.java

Purpose: This abstract non-HA integration test covers S3-style multipart upload behavior in Ozone's file-system-optimized path mode. It validates initiation, part upload/overwrite, completion, abort, listing, pagination, EC quota accounting, part-name metadata, parent-directory namespace effects, and S3 part-specific key-detail lookup.

Important APIs/types/functions: The test uses `NonHATests.TestCase.cluster`, `ObjectStore`, `OzoneVolume`, `OzoneBucket`, `OmMultipartInfo`, `OmMultipartCommitUploadPartInfo`, `OmMultipartUploadCompleteInfo`, `OzoneMultipartUploadPartListParts`, `OzoneMultipartUploadList`, `OzoneMultipartUpload`, `OMMetadataManager`, `OmBucketInfo`, `OmMultipartKeyInfo`, `OmKeyInfo`, `BucketLayout`, `OzoneFSUtils`, `QuotaUtil`, `DefaultReplicationConfig`, and `ECReplicationConfig`. Helpers `initiateMultipartUploadWithAsserts`, `uploadPart`, `completeMultipartUpload`, `verifyUploadedPart`, `verifyPartNamesInDB`, and `generateData` centralize protocol and metadata checks.

Control flow: `init` enables OM filesystem path handling for the cluster and creates a client. Each test creates a fresh volume/bucket/key. Initiation tests confirm upload IDs are non-null and unique. Upload tests write parts with MD5 ETags and verify part names/ETags, including deterministic part-name reuse for overwrites. Completion tests validate minimum part-size rules, invalid part maps, missing parts, and commit after complete. Abort tests cover invalid upload IDs, abort with in-progress streams, empty uploads, uploads with parts, and missing parent directories. Listing tests check `listParts` continuation, invalid marker/max inputs, marker beyond part count, invalid upload ID, `listMultipartUploads` prefix behavior, and key/upload marker pagination. S3 lookup tests call `getS3KeyDetails` for all parts, a specific part, and a missing part.

State and persistence behavior: The tests directly read OM open key and multipart info tables, compare FSO multipart keys, assert part protobuf records hold expected part names, and validate quota counters (`usedBytes`, `usedNamespace`) after overwrite, abort, EC upload, and unused-part discard. They check aborted uploads remove open-key and multipart-info rows.

Dependencies and integration points: Integrates FSO namespace semantics, S3 MPU client APIs, OM metadata layout, bucket quota accounting, EC and RATIS replication configs, part-list pagination contracts, and S3 gateway key-detail semantics.

Risks: The file is large and covers many protocol edges; regressions may be data-layout-specific. It depends on OM path mode being restored after tests. Some assertions use exact quota multiplication and part-count expectations that can change if default block size or EC replicated-size accounting changes.

Test signals: Passing means FSO multipart uploads preserve S3-compatible behavior, correctly maintain OM tables and quotas, clean up aborted state, and expose part metadata through both Ozone and S3-facing client APIs.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestOzoneClientMultipartUploadWithFSO.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestOzoneClientRetriesOnExceptionFlushDelay.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestOzoneClientRetriesOnExceptionFlushDelay.java

Purpose: This flush-delay variant checks that a `GroupMismatchException` during a buffered block write is detected, translated through `HddsClientUtils.checkForException`, and recovered by allocating a replacement block.

Important APIs/types/functions: The fixture configures `OzoneClientConfig` checksum type and retry count, small `ClientConfigForTesting` buffer sizes, SCM close/scrub/destroy timing, `XceiverClientManager`, and `MiniOzoneCluster`. The test uses `ContainerTestHelper.getCreateContainerRequest` to deliberately create a duplicate container in the target RATIS group and provoke a group mismatch.

Control flow: `testGroupMismatchExceptionHandling` initiates a one-block key, resolves the first block's container and pipeline, sends a create-container command through an acquired xceiver client, writes data larger than the max flush size, extracts the first `BlockOutputStream`, waits for pipeline close, and flushes. It then asserts the underlying stream exception is `GroupMismatchException`, the failed pipeline ID is in the `KeyOutputStream` exclude list, a second stream entry has been allocated, close clears stream entries, and the key validates with the original bytes.

State and persistence behavior: Client state under test includes stream entries, pipeline exclude-list contents, and the stored `ioException`. Persistent validation is final OM key/readback state.

Dependencies and integration points: Covers delayed flush buffering, block-output retry, xceiver client commands, RATIS pipeline close detection, and OM finalization after retry.

Risks: Artificially sending create-container commands relies on low-level container protocol behavior. Timing around pipeline close and flush can be sensitive.

Test signals: Passing proves group mismatch in the flush-delay path does not lose data and correctly excludes the failing pipeline before retry.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestOzoneClientRetriesOnExceptionFlushDelay.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestOzoneClientRetriesOnExceptions.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestOzoneClientRetriesOnExceptions.java

Purpose: This class tests the non-flush-delay retry path in `BlockOutputStream` and `KeyOutputStream`, including recovery from group mismatch and failure after exceeding the configured client retry count.

Important APIs/types/functions: Setup sets `OzoneClientConfig.maxRetryCount`, disables checksums and stream flush delay, applies small block/chunk/flush sizes, and uses `RoundRobinPipelineChoosePolicy` to diversify allocated containers. It uses `XceiverClientManager`, `XceiverClientSpi`, `ContainerTestHelper.getCreateContainerRequest`, `BlockOutputStream.getIoException`, `HddsClientUtils.checkForException`, `GroupMismatchException`, and `ContainerNotOpenException`.

Control flow: `testGroupMismatchExceptionHandling` creates one key, provokes duplicate container creation on the selected pipeline, writes and flushes after pipeline close, verifies a `GroupMismatchException`, checks pipeline exclusion, confirms a second stream entry was allocated, closes, and validates data. `testMaxRetriesByOzoneClient` preallocates `MAX_RETRIES + 1` blocks, deliberately closes each candidate container, writes data, waits for close, and then expects a write/flush failure once retries exceed the configured max. A subsequent `flush` must report that the stream is closed.

State and persistence behavior: The tests inspect client stream entries before and after close, the exclude list, per-block stream exceptions, and final key readback for the recoverable case. The max-retry case validates fail-fast client state after exhausting replacement blocks.

Dependencies and integration points: Integrates SCM placement policy, low-level xceiver container commands, client retry counters, exception unwrapping, and OM/object-store validation.

Risks: Assumptions require enough distinct containers to exceed retry count; if placement reuses containers, the test can be skipped by `Assumptions.assumeTrue`. Exception class mapping is a brittle but important API contract.

Test signals: Passing means recoverable container/protocol failures retry to a new block, and unrecoverable repeated failures produce a clear max-retry IOException and close the stream.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestOzoneClientRetriesOnExceptions.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestOzoneRpcClient.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestOzoneRpcClient.java

Purpose: This is the baseline Ozone RPC client integration test class for a non-secure but ACL-enabled cluster. It inherits the shared test suite from `OzoneRpcClientTests`.

Important APIs/types/functions: The class configures `OzoneConfiguration`, enables test authorization, sets SCM pipeline owner container count to one, enables native ACLs, and calls inherited `startCluster(conf)` and `shutdownCluster()`.

Control flow: `init` builds the cluster configuration and delegates cluster startup to `OzoneRpcClientTests`. The inherited superclass supplies the actual client API tests for volumes, buckets, keys, ACLs, reads, writes, deletes, server defaults, and related RPC behavior. `shutdown` delegates cleanup.

State and persistence behavior: This file itself owns no persisted state beyond cluster lifecycle. Its effect is to run the inherited RPC client contract against a cluster with authorization and ACL behavior enabled.

Dependencies and integration points: Depends on `OzoneRpcClientTests` for behavior coverage, OM native ACL authorizer, SCM pipeline ownership settings, and MiniOzoneCluster startup.

Risks: Because this is a configuration subclass, behavioral regressions appear in inherited tests. Misconfiguring ACL or authorization flags would alter the inherited suite's expectations.

Test signals: Passing confirms the shared RPC client test suite works with native ACLs and the selected SCM pipeline/container settings.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestOzoneRpcClient.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestOzoneRpcClientForAclAuditLog.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestOzoneRpcClientForAclAuditLog.java

Purpose: This not-thread-safe integration test verifies audit log entries for Ozone client ACL APIs on volume objects, covering both successful and failed authorization paths.

Important APIs/types/functions: Setup enables audit log4j config, native ACLs, wildcard administrators, and starts a 3-datanode cluster. The test uses `OzoneAcl`, `OzoneObjInfo`, `ObjectStore.getAcl`, `addAcl`, `removeAcl`, `setAcl`, `VolumeArgs`, `OMAction`, `AuditEventStatus`, and `FileUtils` to read and clear `audit.log`.

Control flow: `testXXXAclSuccessAudits` creates a volume owned by the current user, verifies create/read audit records, constructs a volume `OzoneObj`, then performs get/add/remove/set ACL operations and verifies each audit line contains the expected action, volume, ACL identities, and `SUCCESS`. `testXXXAclFailureAudits` creates a volume owned by another user and attempts the same ACL operations; each caught exception is followed by a log assertion for `FAILURE`.

State and persistence behavior: The test mutates actual volume ACL metadata and the local `audit.log` file. `verifyLog` reads the first log line and clears the file after each assertion to isolate events.

Dependencies and integration points: Integrates ObjectStore ACL RPC APIs, native ACL authorization, OM audit logging, test log4j configuration, current `UserGroupInformation`, and filesystem log inspection.

Risks: Marked unhealthy because audit support for HA ACL code needed fixes. It is intentionally not thread-safe; any parallel audit-producing test can pollute `audit.log`. File path assumptions also depend on test working directory.

Test signals: Passing means ACL RPC success/failure paths emit audit records with expected action names, resource names, ACL identities, and statuses.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestOzoneRpcClientForAclAuditLog.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestOzoneRpcClientWithKeyLatestVersion.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestOzoneRpcClientWithKeyLatestVersion.java

Purpose: This abstract non-HA test verifies that the client option `OZONE_CLIENT_KEY_LATEST_VERSION_LOCATION` controls whether key location versions returned by listing include only the latest version or all versions when bucket versioning is enabled.

Important APIs/types/functions: It uses `NonHATests.TestCase.cluster`, `OzoneClientFactory.getRpcClient`, `ObjectStore`, `OzoneVolume`, `OzoneBucket`, `BucketArgs.setVersioning`, `TestDataUtil.createKey`, `assertKeyContent`, `bucket.listStatus`, and `bucket.listStatusLight`.

Control flow: The parameterized test runs with `getLatestVersionOnly` true and false. For each mode it creates a client using the cluster config plus the option override, creates a volume, then creates two buckets: one with versioning disabled and one enabled. It writes the same key multiple times, ending with known content, verifies read content, and asserts the number of `KeyLocationVersions` returned by `listStatus`: all versions only when bucket versioning is enabled and the client option asks not to limit to latest; otherwise one version. The light-listing API is checked for a single returned status entry.

State and persistence behavior: The test creates actual key versions in OM. It validates client-side projection of those persisted versions rather than physical block contents.

Dependencies and integration points: Integrates OM versioned-key metadata, client configuration propagation, listing APIs, and read-after-overwrite semantics.

Risks: Expected version count depends on overwrite preserving previous versions only for versioned buckets. Changes to `listStatusLight` version exposure are not deeply asserted here.

Test signals: Passing confirms latest-version filtering is honored without breaking key reads or list status shape.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestOzoneRpcClientWithKeyLatestVersion.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestReadRetries.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestReadRetries.java

Purpose: This test validates read retry behavior across a three-node RATIS pipeline and confirms FSO intermediate directory status remains accessible after data-node failures.

Important APIs/types/functions: It configures FSO paths with `configureFSOptimizedPaths`, uses `MiniOzoneCluster`, `OzoneClient`, `ObjectStore`, `OzoneVolume`, `OzoneBucket`, `TestDataUtil.createKey`, `OzoneClientTestUtils.assertKeyContent`, OM `lookupKey`, SCM `ContainerManager`/`PipelineManager`, and `bucket.getFileStatus`.

Control flow: A 3-datanode cluster is started with one pipeline owner container. The test creates an FSO bucket, writes a nested key under `a/b/c/` with RATIS/THREE, verifies client key details match OM block location, resolves the backing pipeline, and confirms it has three datanodes. It then shuts down datanodes one by one: after the first and second shutdowns, full key content must still read; after the third, reading must throw `IOException`. Finally it verifies the intermediate directory `a/b/c` is returned as a directory with the expected trimmed name.

State and persistence behavior: The test observes OM key block metadata, SCM pipeline membership, datanode process state, and FSO directory metadata.

Dependencies and integration points: Integrates read retry/failover in `KeyInputStream`/client read path, RATIS replicated container reads, SCM metadata lookup, and FSO directory status APIs.

Risks: Sequential datanode shutdown assumes no replacement replicas are created during the short test. Timing changes in replication manager could alter availability expectations.

Test signals: Passing means reads survive loss of up to two replicas in a three-node pipeline and fail only when all replicas are unavailable, while FSO directory metadata remains queryable.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestReadRetries.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestSecureOzoneRpcClient.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestSecureOzoneRpcClient.java

Purpose: This secure subclass of `OzoneRpcClientTests` validates RPC client behavior with block tokens, native ACL authorization, S3 authentication, secure server defaults, and FSO lease recovery.

Important APIs/types/functions: Setup enables secure OM test mode, block tokens, ACLs, native authorizer, HBase enhancements, hsync, test authorization, certificate and secret-key test clients, KMS provider URI, and inherited cluster startup. The class uses `OzoneOutputStream.hsync`, `RootedOzoneFileSystem.recoverLease`, `OMMetrics`, OM metadata/deleted tables, `S3SecretManager`, signed `OMRequest` messages, `UserGroupInformation` proxy users, and inherited `verifyReplication`.

Control flow: `testPutKeySuccessWithBlockToken` writes and reads multiple keys in object-store and FSO buckets, verifies committed-byte metrics, and asserts block tokens are not persisted in OM key location metadata or cache. `testFileRecovery` writes and hsyncs an FSO key, optionally forces lease recovery through a system property, and expects close failure only after forced recovery has committed the key. `testPreallocateFileRecovery` creates a preallocated key, writes less than reserved size, recovers the lease, then checks file length, committed bytes, quota, and deleted-table entries for unused preallocated blocks. `testS3Auth` stores an S3 secret, submits signed create/read volume OM requests, verifies OK responses, then changes the secret and expects invalid-token responses. `testRemoteException` checks unauthorized proxy-user volume listing raises `AccessControlException`. It overrides an unhealthy-container read test because DN restart is incompatible with security enabled and verifies server defaults expose the KMS URI.

State and persistence behavior: State assertions include OM metrics, key tables/cache entries without tokens, FSO committed file metadata, bucket namespace/byte quota, deleted-table reclaimed block records, S3 secret table authentication behavior, and server defaults.

Dependencies and integration points: Integrates block-token security, OM native ACL authorizer, secure datanode/container access, OFS filesystem lease recovery, KMS server-default propagation, S3 auth validation, and inherited broad RPC client tests.

Risks: Security setup is configuration-heavy. System property `FORCE_LEASE_RECOVERY_ENV` and FS cache disabling can leak if not isolated. Preallocation recovery uses large data sizes and asynchronous quota/deleted-table updates.

Test signals: Passing confirms secure client writes/readbacks work, tokens are not persisted in metadata, recovery commits correct sizes and reclaims unused blocks, S3 signatures are enforced, and secure server defaults are exposed.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestSecureOzoneRpcClient.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestValidateBCSIDOnRestart.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestValidateBCSIDOnRestart.java

Purpose: This test validates datanode restart behavior when container block-commit sequence ID state is missing or inconsistent. It protects container state-machine recovery and corruption detection around BCSID.

Important APIs/types/functions: Setup disables stream flush delay, shortens heartbeat/report/stale/destroy intervals, configures RATIS client/server timeouts, starts a 2-datanode cluster, and waits for a RATIS/ONE pipeline. The test uses `OzoneOutputStream`, `KeyOutputStream`, `OmKeyLocationInfo`, `TestHelper.getDatanodeService`, `OzoneContainer`, `ContainerStateMachine`, `SimpleStateMachineStorage`, `StatemachineImplTestUtil.findLatestSnapshot`, `HddsDispatcher.getMissingContainerSet`, `BlockUtils.getDB`, and `KeyValueContainerData.getBcsIdKey`.

Control flow: The test writes and flushes a key to create a container, captures the datanode and container data, closes the key, deletes the container path, removes the container from the in-memory container set, takes a state-machine snapshot, and calls `buildMissingContainerSet`. It asserts the latest snapshot exists and the dispatcher missing-container set contains the deleted container ID. It then writes another key, locates its container, opens the container DB, corrupts the stored BCSID by writing `0L`, restarts the datanode, and asserts the container state becomes `UNHEALTHY`.

State and persistence behavior: It deliberately mutates on-disk container directories and RocksDB metadata. It validates snapshot-derived missing-container state and restart-time comparison between container file state and DB BCSID.

Dependencies and integration points: Covers datanode container set rebuild, RATIS state machine snapshots, dispatcher missing-container tracking, KeyValueContainer metadata, DB handle access, and datanode restart.

Risks: This is invasive: it deletes container files and corrupts RocksDB inside a live test cluster. Timing of snapshots and container reports must match the shortened intervals.

Test signals: Passing means missing containers are discovered from snapshots and BCSID mismatches are detected by marking containers unhealthy after restart.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestValidateBCSIDOnRestart.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/package-info.java

Purpose: This package descriptor documents that `org.apache.hadoop.ozone.client.rpc` contains test classes for the Ozone RPC client library.

Important APIs/types/functions: It declares the Java package only. There are no classes, methods, fields, annotations, or executable logic.

Control flow: None. The file is compile-time package documentation.

State and persistence behavior: None. It does not create runtime state or persistent data.

Dependencies and integration points: It integrates with JavaDoc/package documentation for the integration-test package and shares the package namespace with the RPC client integration tests in this directory.

Risks: Low. The main risk is stale or overly broad package documentation if package contents change substantially.

Test signals: Compilation of the test source tree is the only signal; there are no direct tests for this descriptor.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/read/TestChunkInputStream.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/read/TestChunkInputStream.java

Purpose: This class validates `ChunkInputStream` buffering behavior, especially checksum-boundary caching and buffer release, across container layout versions.

Important APIs/types/functions: It extends `TestInputStreamBase`, runs under `ContainerLayoutTestInfo.ContainerTest`, and uses `TestBucket`, `KeyInputStream`, `BlockInputStream`, `ChunkInputStream`, `ByteBuffer`, `IOUtils.readFully`, and layout updates through the base class.

Control flow: `testAll` opens a client, applies the requested container layout, creates a test bucket, and runs three private tests. `testChunkReadBuffers` writes multi-block data, initializes the first block stream, reads one byte and larger spans from the first chunk, performs seeks across checksum boundaries, checks cached buffer counts/capacities/null slots, and verifies buffers are released after EOF. `testBufferRelease` reads up to the last byte of a checksum buffer, confirms it remains cached, reads the last byte, confirms release, then reads more data and checks a new buffer is used. `testCloseReleasesBuffers` confirms explicit close clears cached buffers.

State and persistence behavior: Persistent state is random key data in a test bucket. Runtime state under test is `ChunkInputStream.getCachedBuffers`, positions, remaining bytes, and cached `ByteBuffer` identity.

Dependencies and integration points: Integrates client read streams, block/chunk stream hierarchy, checksum sizing from `OzoneClientConfig`, container layouts, and `TestBucket` data validation.

Risks: The test asserts internal buffer-array shape, nulling, and capacity. Legitimate buffer implementation refactors may require test updates even if external reads remain correct.

Test signals: Passing means chunk reads fetch checksum-sized buffers, release consumed buffers promptly, preserve data correctness after seek/read, and free buffers on close or EOF.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/read/TestChunkInputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/read/TestInputStreamBase.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/read/TestInputStreamBase.java

Purpose: This abstract base class provides a shared MiniOzoneCluster and read-stream configuration for chunk, key, and stream-block input tests.

Important APIs/types/functions: Constants define `CHUNK_SIZE`, `FLUSH_SIZE`, `MAX_FLUSH_SIZE`, `BLOCK_SIZE`, and `BYTES_PER_CHECKSUM`. `newCluster` configures bytes per checksum, SCM stale/dead intervals, datanode pipeline limit, RATIS pipeline limit, SCM block size, replication-manager interval, and client block/chunk/flush sizes through `ClientConfigForTesting`. `updateConfig` changes datanode container layout and closes open containers. `setup` and `cleanup` manage cluster lifecycle.

Control flow: Before all tests, `setup` starts a five-datanode cluster and waits for readiness. Subclasses call `getCluster` and `updateConfig` to run layout-specific cases. `closeContainers` scans SCM containers and closes open ones via `TestHelper.waitForContainerClose` so subsequent writes use the new layout. After all tests, the cluster is closed quietly.

State and persistence behavior: Owns the shared cluster and mutates datanode configuration for container layout. It also forces open container closure, which changes SCM/container persistent state to isolate layout tests.

Dependencies and integration points: Supports `TestChunkInputStream`, `TestKeyInputStream`, and `TestStreamBlockInputStream`; integrates with SCM container layout config, replication manager, and client stream sizing.

Risks: Shared cluster lifecycle improves speed but can introduce state coupling between subclass tests. `updateConfig` changes datanode configs at runtime and assumes closing existing containers is sufficient layout isolation.

Test signals: Subclass success implicitly validates this base configuration; failures in cluster setup, container close, or layout switching surface across all read-stream tests.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/read/TestInputStreamBase.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/read/TestKeyInputStream.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/read/TestKeyInputStream.java

Purpose: This class verifies `KeyInputStream` composition, seeking, skipping, byte-array reads, direct `ByteBuffer` reads, EC reads, and continued reads after replica loss.

Important APIs/types/functions: It extends `TestInputStreamBase`, uses `ContainerLayoutTestInfo.ContainerTest`, `TestBucket`, `KeyInputStream`, `BlockInputStream`, `ChunkInputStream`, `BlockExtendedInputStream`, `ECReplicationConfig`, `XceiverClientMetrics`, `BufferUtils.getNumberOfBins`, OM `getKeyInfo`, and `TestHelper.countReplicas`/`waitForContainerClose`.

Control flow: `testNonReplicationReads` runs multiple cases in one layout-specific test. `testInputStreams` verifies key data is split into expected block streams and chunk streams with correct lengths. Random seek helpers repeatedly seek/read and validate slices against original data. `testECSeek` writes EC data and reads across EC chunk/block boundaries. `testSeek` and `testSkip` reset xceiver metrics, write three chunks, assert seek/skip do not issue `ReadChunk`, then read and verify exactly two chunks are fetched for a boundary-crossing read. Byte-array and `ByteBuffer` cases read full keys with many buffer sizes. `readAfterReplication` reads one byte, optionally `unbuffer`s, shuts down one pipeline datanode, and verifies remaining data can still be read.

State and persistence behavior: Persistent test state includes random keys with RATIS or EC replication and closed containers for replica tests. Runtime state includes stream position, internal part streams, xceiver read/write metrics, and client buffer contents.

Dependencies and integration points: Integrates Ozone key input stream logic, block/chunk stream generation, EC layout, SCM replica state, xceiver metrics, datanode shutdown, and buffer APIs.

Risks: Tests inspect internal stream structure and exact operation counts, so stream implementation changes can require updates. The replication read test shuts down a datanode and is ordered last to avoid shared-cluster side effects.

Test signals: Passing confirms key reads are correctly segmented, seeks/skips are lazy, all read APIs return exact bytes, EC offsets work, and open reads can continue after one replica disappears.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/read/TestKeyInputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/read/TestStreamBlockInputStream.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/read/TestStreamBlockInputStream.java

Purpose: This class tests the gRPC streaming block read path enabled by `OzoneClientConfig.setStreamReadBlock(true)`, including sequential reads, positioned reads, ByteBuffer reads, seeking, checksum-disabled reads, and empty-key behavior.

Important APIs/types/functions: It extends `TestInputStreamBase`, uses `MiniOzoneCluster`, `OzoneClientFactory`, `TestBucket`, `KeyInputStream`, `StreamBlockInputStream`, `ByteBuffer`, `OzoneClientConfig`, and `ContainerProtos.ChecksumType.NONE`. It also lowers noisy logger levels for common Ozone/Ratis components.

Control flow: `testReadKey` starts a fresh cluster, enables stream-read-block on a copied config, writes random keys of fixed and random lengths, validates positioned reads, and reads full data with many buffer sizes and optional random starting offsets. `runTestPositionedRead` compares ordinary seek/read with `readFully(position, ByteBuffer)` for edge and random positions. `testAll` writes data with checksums enabled, verifies full reads by byte array, one-byte loop, and ByteBuffer, validates random seek behavior and invalid block-stream seeks, checks zero-length key behavior, then repeats read/seek with checksum type `NONE`.

State and persistence behavior: Persistent state is random keys in temporary test buckets. Runtime state includes stream positions, duplicated ByteBuffers, and `StreamBlockInputStream` block length/position.

Dependencies and integration points: Integrates the stream-block read implementation, key-level read APIs, positioned read contract, checksum handling, empty-key OM metadata, and gRPC xceiver service.

Risks: The test creates separate clusters instead of using the base shared cluster for its main methods, increasing runtime. Random offsets and sizes broaden coverage but can make failures harder to reproduce without logged parameters.

Test signals: Passing means streaming block reads return exact bytes for sequential and positioned reads, maintain position after failed seeks, work with and without checksums, and represent empty keys as no part streams with EOF on read.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/read/TestStreamBlockInputStream.java -->
