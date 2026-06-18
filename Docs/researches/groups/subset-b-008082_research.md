# Research: subset-b-008082

Grouped research for Apache Ozone integration-test files under `hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone`. Each section preserves the source path and is intended to be split into the source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/container/ozoneimpl/TestOzoneContainerWithTLS.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/container/ozoneimpl/TestOzoneContainerWithTLS.java

Purpose: Integration coverage for secure gRPC container operations when datanode certificates, TLS trust managers, and optional container tokens are enabled. It exercises `OzoneContainer` directly rather than a full cluster, using test certificates and mock pipelines to validate create/close container, container download, checksum-info RPCs, and client trust-manager reload behavior around certificate expiry.

Important APIs, types, and functions: The test configures `OzoneConfiguration` with `OZONE_SECURITY_ENABLED_KEY`, `HDDS_GRPC_TLS_ENABLED`, `HDDS_GRPC_TLS_TEST_CERT`, short `HDDS_X509_DEFAULT_DURATION` and root CA lifetime, and container-token settings. It builds `CertificateClientTestImpl`, `SecretKeyTestClient`, `ContainerTokenSecretManager`, `XceiverClientGrpc`, `XceiverClientManager`, `DNContainerOperationClient`, `SimpleContainerDownloader`, and `ClientTrustManager`. Helper methods `createAndStartOzoneContainerInstance`, `createContainer`, `createAndCloseContainer`, `assertDownloadContainerFails`, `assertDownloadContainerWorks`, `letCertExpire`, `letCACertExpire`, and `aClientTrustManager` define the local secure DN harness and command flow.

Control flow: `setup` creates temp metadata/data/container DB directories, a random cluster ID, a test certificate client, token manager, mock datanode, and single-node pipeline. `testCertificateLifetime` proves the short leaf certificate expires. `createContainer` runs with container tokens off and on, starts an `OzoneContainer`, connects over TLS, and sends a secure create request. `downloadContainer` establishes a reusable client, creates closed containers before and after leaf certificate expiry, expects downloader failure while certs are expired, renews the cert, then expects all container downloads to succeed. `testDNContainerOperationClient` verifies checksum-info access through the higher-level DN operation client. `testGetContainerMerkleTree` verifies checksum info succeeds with a valid encoded container token and fails with `BLOCK_TOKEN_VERIFICATION_FAILED` for an invalid token. `testLongLivingClientWithCertRenews` captures `ClientTrustManager` logs to assert certificates are loaded once, retried after trust failure, fail while the CA remains expired, and succeed after root CA and leaf renewal.

State and persistence behavior: The test creates real Ozone container volume directories under JUnit temp storage and rewires each `HddsVolume` DB parent to the temp folder. Container state transitions are persisted through create and close commands. Certificate and CA expiry are time-based state in `CertificateClientTestImpl`; renewals mutate the certificate material used by server and clients. Checksum-info and download paths depend on on-disk closed container data and the container checksum tree.

Dependencies and integration points: The file integrates container command builders from `ContainerTestHelper`, Xceiver gRPC transport, client manager pooling, `SimpleContainerDownloader` replication download, DN checksum client, certificate client test implementation, token helpers, and Ozone datanode volume initialization utilities. It is a focused security/transport integration test, not a full SCM/OM cluster test.

Risks: Short certificate lifetimes and explicit waits can be timing-sensitive. The comment in `downloadContainer` notes low-probability flakiness from SSL renegotiation. Trust-manager assertions depend on log message text. Token paths rely on current user names and secret key IDs. Because the container is started manually, test failures can leave temp files until JUnit cleanup if `container.stop` is missed.

Test signals: Assertions cover certificate expiry exceptions, successful command responses, null/non-null downloader results, checksum-info non-empty results, exact `BLOCK_TOKEN_VERIFICATION_FAILED` outcomes, root-cause `CertificateExpiredException`, and log evidence for trust-manager reload/retry.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/container/ozoneimpl/TestOzoneContainerWithTLS.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/container/ozoneimpl/TestSecureOzoneContainer.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/container/ozoneimpl/TestSecureOzoneContainer.java

Purpose: Parameterized integration test for secure `OzoneContainer` command authorization. It validates how block/container token settings, token presence, and token expiry affect a create-container command sent over the gRPC xceiver client.

Important APIs, types, and functions: The class uses `OzoneContainer`, `XceiverClientGrpc`, `ContainerTokenSecretManager`, `ContainerTokenIdentifier`, `SecretKeyTestClient`, `CertificateClientTestImpl`, `MockPipeline`, `ContainerTestUtils`, and `StorageVolumeUtil`. `blockTokenOptions` enumerates combinations of `requireToken`, `hasToken`, and `tokenExpired`; `testCreateOzoneContainer` builds the container and sends the request; `testCase` provides diagnostic names.

Control flow: Static setup enables mini-cluster metrics mode. Per-test setup creates metadata paths, security cert and secret-key clients, token manager, and volume choosing policy. For each token combination, the test enables or disables `HDDS_BLOCK_TOKEN_ENABLED` and `HDDS_CONTAINER_TOKEN_ENABLED`, binds the container IPC port to the pipeline first node, creates and starts an `OzoneContainer`, and then impersonates `user1` via `UserGroupInformation.doAs`. If a token is requested, it creates a `ContainerTokenIdentifier` using the current secret key and either a future or past expiry. It sends `getCreateContainerSecureRequest` and compares response result or expected exception shape.

State and persistence behavior: Temporary metadata and data paths back real `OzoneContainer` storage. The token state is ephemeral but derived from the shared `SecretKeyTestClient`. Container lifecycle state is created only if authorization passes. Expired tokens are represented by an `Instant` in the past and may surface either as `SCMSecurityException` or a verification failure response, depending on where verification fails.

Dependencies and integration points: This is a lower-level secure container integration point between `HddsDispatcher` token verification, gRPC xceiver client, container command helpers, Hadoop UGI, certificate test client, and the local volume layout initializer.

Risks: The test depends on port binding from a mock pipeline and on different exception classes for missing versus expired tokens. Because it starts the container manually, state setup must stay aligned with real datanode layout initialization. Expiry behavior is sensitive to clock skew only at test-process scale.

Test signals: Expected outcomes are `SUCCESS` when tokens are not required or a valid token is supplied, `BLOCK_TOKEN_VERIFICATION_FAILED` when required tokens are missing or expired, `SCMSecurityException` for expired signed tokens, and `IOException` for missing-token authorization failures.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/container/ozoneimpl/TestSecureOzoneContainer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/container/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/container/package-info.java

Purpose: Package-level documentation for the integration-test package `org.apache.hadoop.ozone.container`.

Important APIs, types, and functions: There are no executable APIs. The only declaration is the package statement with a Javadoc summary, "Test container related classes."

Control flow: None. This file is compile-time package metadata.

State and persistence behavior: None. It creates no runtime state and persists no data.

Dependencies and integration points: The file anchors Javadoc/package metadata for neighboring container integration tests.

Risks: Only stale or overly broad package documentation risk. It has no runtime behavior.

Test signals: Presence of the package declaration is validated by Java compilation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/container/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/container/replication/TestContainerReplication.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/container/replication/TestContainerReplication.java

Purpose: Integration tests for datanode container replication push and pull behavior across all `CopyContainerCompression` modes, including failure paths and edge cases around wrong ports, unknown containers, negative persisted bytes-used counters, and over-allocated container sizes.

Important APIs, types, and functions: The file uses `MiniOzoneCluster`, `XceiverClientManager`, `ReplicateContainerCommand`, `ReplicationSupervisor`, `DatanodeStateMachine`, `StateContext`, `KeyValueContainerData`, `BlockUtils`, `GrpcContainerUploader`, and `ContainerImporter`. Key helpers are `createConfiguration`, `createNewClosedContainer`, `createOverAllocatedContainer`, `queueAndWaitForCompletion`, `selectOtherNode`, `poisonBytesUsed`, and `getContainer`.

Control flow: `setup` builds a cluster with one datanode per compression mode, starts datanodes after applying compression config, and creates an xceiver client factory. Push tests create a closed container on the source and queue a `toTarget` command; pull tests create a closed container on another node and queue a `fromSources` command on the target. Failure tests queue a pull command with an invalid replication port or a push command for a nonexistent container and wait for the replication failure counter. Negative bytes-used testing creates an oversized container, writes a poison value into the container metadata DB and in-memory statistics, then verifies push import succeeds. Over-allocated tests write chunk/putBlock commands until the target size is reached, close the container, capture upload/import logs, and assert target import size matches source size.

State and persistence behavior: The tests create real containers in mini-cluster datanode storage. `poisonBytesUsed` directly mutates the RocksDB metadata table key for bytes used and updates in-memory statistics to prevent automatic correction. Replication commands are queued into the datanode `StateContext` with the current SCM leader term, and completion is observed through supervisor counters. Over-allocated container size is persisted through block/chunk writes and close.

Dependencies and integration points: This exercises SCM/datanode command handling, xceiver clients, replication supervisor execution, container downloader/uploader/importer code, RocksDB container metadata, container volume space reservation, and compression-specific replication configuration.

Risks: Counter-based waiting can hide the specific failure if another replication operation increments the same counter, though test isolation reduces this. Direct DB mutation is intentionally invasive and tied to key-value container metadata internals. Log-message assertions for over-allocation are brittle. Multi-datanode mini-cluster timing can be slow or flaky under load.

Test signals: Success/failure counters must increment within 30 seconds. Imported containers must exist on targets. Source and target `bytesUsed` must match. Logs must show upload size and double reservation size for over-allocated containers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/container/replication/TestContainerReplication.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/container/replication/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/container/replication/package-info.java

Purpose: Package-level documentation for `org.apache.hadoop.ozone.container.replication` integration tests.

Important APIs, types, and functions: No executable APIs are defined. The Javadoc describes the package as "Test container replication."

Control flow: None.

State and persistence behavior: None.

Dependencies and integration points: Provides package metadata for replication integration test classes.

Risks: Documentation can become stale, but no runtime behavior is affected.

Test signals: Java compilation validates only the package declaration.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/container/replication/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/container/server/TestContainerServer.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/container/server/TestContainerServer.java

Purpose: Smoke and integration tests for unsecured container xceiver servers over standalone gRPC and Ratis gRPC transports. It verifies client/server wiring with a trivial dispatcher and with a real `HddsDispatcher` stack.

Important APIs, types, and functions: The file uses `XceiverServerGrpc`, `XceiverServerRatis`, `XceiverClientGrpc`, `XceiverClientRatis`, `MockPipeline`, `RatisTestHelper`, `HddsDispatcher`, `ContainerController`, `Handler.getHandlerForContainerType`, `MutableVolumeSet`, `ContainerMetrics`, and `DNCertificateClient`. Core helpers are `runTestClientServer`, `runTestClientServerRatis`, `newXceiverServerRatis`, `createDispatcher`, and the inner `TestContainerDispatcher`.

Control flow: Static setup enables mini-cluster metrics, prepares metadata paths, disables Ratis datastream, and creates a datanode certificate client. `testClientServer` configures the standalone container IPC port from the mock pipeline, starts `XceiverServerGrpc` with a test dispatcher, connects a gRPC client, and sends a create-container request. `testClientServerRatisGrpc` runs the same pattern for 1-node and 3-node Ratis pipelines. `testClientServerWithContainerDispatcher` builds a full dispatcher with container set, volume set, handlers, and metrics, then verifies a create request through gRPC.

State and persistence behavior: Server tests create temporary datanode metadata and volume roots. The full dispatcher constructs actual handlers and volume sets and sets an SCM cluster ID, so create-container can touch persistent container metadata. The simple dispatcher returns a synthetic create-container response without storing container state.

Dependencies and integration points: Covers client/server transport constructors, Ratis server initialization, handler registration for container types, local datanode volume setup, metrics system, and xceiver command request tracing.

Risks: Uses a shared static `OzoneConfiguration`, so mutations across subtests must not conflict. Temporary Ratis storage paths are derived from datanode IDs. The simple dispatcher only validates transport plumbing, not container semantics. Full dispatcher setup must stay in sync with handler constructor requirements.

Test signals: Requests must carry a trace ID; clients must connect and send a create-container command without exception. Resource cleanup closes the client and stops all servers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/container/server/TestContainerServer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/container/server/TestSecureContainerServer.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/container/server/TestSecureContainerServer.java

Purpose: Secure xceiver server integration tests validating block-token and container-token enforcement over gRPC and Ratis gRPC transports. It ensures unauthenticated create/read/write/block operations fail and encoded tokens allow the same requests to succeed.

Important APIs, types, and functions: The test uses `CertificateClientTestImpl`, `SecretKeyTestClient`, `OzoneBlockTokenSecretManager`, `ContainerTokenSecretManager`, `TokenVerifier`, `HddsDispatcher`, `XceiverServerGrpc`, `XceiverServerRatis`, `XceiverClientGrpc`, `XceiverClientRatis`, and container request builders for write/read/get/put block paths. Helpers include `createDispatcher`, `newXceiverServerRatis`, `runTestClientServer`, `assertRequiresToken`, `assertSucceeds`, `assertFailsTokenVerification`, and `getToken`.

Control flow: Static setup enables security and block tokens, creates certificate and secret-key clients, and initializes token managers with one-hour lifetimes. The gRPC and Ratis tests create servers for a mock pipeline, connect clients, first assert a create-container request without a container token fails, then create the container with a valid container token. They generate an all-access block token and verify write chunk, put block, read chunk, get block, and get committed block length requests fail without the encoded token and succeed with it.

State and persistence behavior: A real dispatcher and volume set are built per datanode with temp data directories. Container creation persists state before block operations. Tokens are generated from in-memory secret keys, but verification happens through production `TokenVerifier` in the dispatcher. Cleanup deletes the configured datanode data path after each test.

Dependencies and integration points: This file integrates transport security with container command authorization, Ratis datastream settings, token managers, container handlers, and low-level protobuf request builders. It also normalizes different failure surfaces: gRPC/read-only requests return response messages, while some Ratis write failures throw exceptions with token-verification text in the root cause.

Risks: Static shared configuration and mutable datanode dir cleanup require careful isolation. The test is sensitive to the definition of `isReadOnly` and to whether transport paths return failure responses or throw. Token access mode coverage uses `EnumSet.allOf`, so changes in token access semantics can alter expected success.

Test signals: Expected failures must include `BLOCK_TOKEN_VERIFICATION_FAILED`, expected successes must return `SUCCESS`, and both 1-node and 3-node Ratis pipelines must pass the same token requirements.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/container/server/TestSecureContainerServer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/debug/TestLDBCli.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/debug/TestLDBCli.java

Purpose: Integration tests for the `ozone debug ldb` CLI parser and scanner against temporary RocksDB stores. It validates table scanning, range and filter options, schema-aware datanode block table keys, output splitting, empty table output, and value-schema inspection.

Important APIs, types, and functions: Uses `RDBParser` through picocli `CommandLine`, `DBStoreBuilder`, `DBStore`, `Table`, `BlockUtils.getUncachedDatanodeStore`, `DatanodeSchemaThreeDBDefinition`, `DBScanner.JsonSerializationHelper`, `OmKeyInfo`, and `BlockData`. `scanTestCases` is the main parameter matrix. Helpers `prepareTable`, `prepareKeyTable`, `assertContents`, and `toMap` create expected JSON-compatible maps from production codecs.

Control flow: `setup` creates a fresh `OzoneConfiguration`, command-line parser, captured stdout/stderr writers, and an ordered expected map. Parameterized scan tests create either OM `keyTable`, DN `block_data` in schema V2/V3, or invalid combinations, execute `scan --db ... --column-family ...` with extra flags, then compare exit code, stderr substring, and parsed JSON output against an expected sub-map. Dedicated tests cover scanning an empty `pipelines` table, writing records into multiple output files using `--max-records-per-file` and `-l`, and running `value-schema`.

State and persistence behavior: Each test builds a temporary RocksDB directory and closes it after execution. OM key table state is populated with serialized `OmKeyInfo` values. DN block table state is populated with serialized `BlockData` values and schema-specific keys: plain block IDs for V2 and container-prefixed fixed-length keys for V3. Output-file tests persist JSON shard files under temp scan directories.

Dependencies and integration points: The tests connect the CLI parser, RocksDB abstraction, Ozone protobuf serialization, JSON object mapping, DN schema definitions, and filter/range logic. They use stdout/stderr exactly as the CLI would expose them.

Risks: JSON comparison depends on `DBScanner.JsonSerializationHelper` output structure. Filter strings are parsed as text and can be sensitive to field names such as `keyName` and `dataSize`. The test intentionally checks invalid V2-as-V3 parsing, so schema defaults are important. Output directory file counts assume deterministic splitting.

Test signals: Exit codes and stderr substrings validate error paths; JSON parsed stdout maps validate scan content; empty table output must be `{  }\n`; output files must be valid JSON; `value-schema` output must mention `keyName`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/debug/TestLDBCli.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/debug/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/debug/package-info.java

Purpose: Package-level documentation for `org.apache.hadoop.ozone.debug` integration tests.

Important APIs, types, and functions: No executable code; the file declares the package and a Javadoc summary for debug-related tests.

Control flow: None.

State and persistence behavior: None.

Dependencies and integration points: Provides package metadata for debug CLI test classes.

Risks: No runtime risk.

Test signals: Java compilation validates package metadata.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/debug/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/dn/DatanodeTestUtils.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/dn/DatanodeTestUtils.java

Purpose: Test utility class for injecting and restoring datanode data, file, metadata directory, root directory, and volume failures. It supports integration tests that need deterministic local filesystem damage without permanently corrupting test workspaces.

Important APIs, types, and functions: Public static helpers include `injectDataDirFailure`, `restoreDataDirFromFailure`, `injectDataFileFailure`, `restoreDataFileFromFailure`, `injectContainerMetaDirFailure`, `restoreContainerMetaDirFromFailure`, `simulateBadRootDir`, `simulateBadVolume`, `restoreBadRootDir`, `restoreBadVolume`, `waitForHandleFailedVolume`, and `getHddsVolumeClusterDir`. It works with `StorageVolume`, `HddsVolume`, `MutableVolumeSet`, Apache Commons `FileUtils`, and `GenericTestUtils.waitFor`.

Control flow: Directory and file failure injection generally renames the target to a `.origin` backup path, then replaces it with an incompatible filesystem object: a file where a directory should be or a directory where a file should be. Restore methods delete the incompatible replacement and rename `.origin` back. Metadata directory failure manipulates writable permissions. Bad root/volume simulation removes write permission from root directories, and restore returns permissions. `waitForHandleFailedVolume` polls `MutableVolumeSet.getFailedVolumesList().size()` until the expected number appears.

State and persistence behavior: The utility mutates real filesystem state under datanode temp volumes. It preserves original content under the `.origin` suffix so tests can restore during cleanup. Permission changes alter the ability of `HddsVolume.check` and container IO paths to write, causing volume-health code to detect failures.

Dependencies and integration points: Used by volume failure detection/toleration tests and any datanode test that needs chunk, DB, container metadata, or root volume damage. It integrates with Ozone storage volume abstractions while relying on platform filesystem permission semantics.

Risks: If a test aborts before restore, `.origin` files or directories can remain. Permission behavior varies across platforms and user privileges, especially when tests run with elevated permissions. Renaming open RocksDB directories requires careful cache invalidation in callers. The methods are destructive by design and should stay confined to temp test data.

Test signals: The utility itself has no direct tests here, but callers observe IO exceptions, failed volume counts, and successful restore allowing cluster shutdown/cleanup.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/dn/DatanodeTestUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/dn/TestDatanodeMinFreeSpaceIntegration.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/dn/TestDatanodeMinFreeSpaceIntegration.java

Purpose: Integration test verifying datanode storage reports sent to SCM reflect configured soft minimum free-space reservation.

Important APIs, types, and functions: Uses `MiniOzoneCluster`, datanode/SCM storage reports, `OzoneConfiguration`, and SCM/datanode free-space config keys. The main test is `storageReportsAtScmMatchSoftMinFreeSpaceFromConfig`; helper `storageReportsMatchSoftMinFree` compares reported capacity/remaining values with the configured soft min free value.

Control flow: The test builds a mini cluster with datanode minimum free-space configuration, waits for readiness and reports, then polls SCM-visible storage reports until every reported storage location matches the expected capacity accounting. The helper evaluates storage report fields rather than client-visible object behavior.

State and persistence behavior: The cluster creates datanode volume directories and reports their capacity/free-space state through heartbeats. No object data is written; persistence is limited to volume initialization and SCM report state.

Dependencies and integration points: Covers datanode storage report generation, SCM report ingestion, and configuration plumbing for minimum free space. It indirectly validates datanode volume calculations used by placement and allocation decisions.

Risks: Storage capacity and remaining space depend on the host filesystem. Timing depends on report intervals and SCM processing. The test must compare soft-min-adjusted values without assuming exact absolute disk capacity beyond the configured relationship.

Test signals: The primary signal is that SCM storage reports eventually match datanode soft min free-space expectations; failure indicates config not applied, report not propagated, or incorrect accounting.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/dn/TestDatanodeMinFreeSpaceIntegration.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/dn/checksum/TestContainerCommandReconciliation.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/dn/checksum/TestContainerCommandReconciliation.java

Purpose: Large secure HA integration test for container checksum retrieval, checksum file handling, SCM-reported data checksums, and container reconciliation after block deletion or chunk corruption. Marked flaky for HDDS-13401.

Important APIs, types, and functions: Uses `MiniOzoneHAClusterImpl`, `MiniKdc`, secure OM/SCM/DN Kerberos config, `DNContainerOperationClient`, `ContainerChecksumTreeManager`, `ContainerMerkleTreeWriter`, `ContainerMerkleTreeTestUtils`, `StorageContainerLocationProtocolClientSideTranslatorPB`, `KeyValueHandler`, `BlockManager`, `BlockUtils`, `TestContainerCorruptions`, and `TestHelper`. Important helpers include `init`, `setSecureConfig`, `setSecretKeysConfig`, `startCluster`, `getDataAndContainer`, `writeChecksumFileToDatanodes`, and `waitForDataChecksumsAtSCM`.

Control flow: Class setup creates a secure Ozone HA cluster with three SCMs, one OM, Kerberos principals/keytabs, token settings, fast heartbeat/report intervals, and a DN checksum client using SCM certificate and secret-key clients. API tests verify checksum-info failure for open containers, nonexistent replicas, unreadable files, server IO errors, corrupt protobuf files, and empty checksum files. Success tests delete an existing checksum file and require on-demand creation, overwrite checksum trees on all replicas and require matching reads, and validate retrieval from every replica. Reconciliation tests write data to a closed Ratis-3 container, mutate one replica by deleting block metadata/files or corrupting blocks, force a scan, observe divergent SCM data checksums, call `reconcileContainer`, and wait until all replicas report one checksum again while the original key remains readable. The SCM checksum-reporting test also verifies non-zero data checksums after close, after reconcile, and after datanode/SCM restarts.

State and persistence behavior: This file heavily mutates real persisted state: key data, container metadata DB tables, block files, checksum tree files, Kerberos keytabs, SCM replica checksum records, and datanode restart state. It explicitly deletes block table entries in a batch and block files from chunk paths, writes corrupt bytes or empty bytes into checksum files, updates checksum files through checksum managers, and relies on container reports to persist data checksum signals in SCM.

Dependencies and integration points: Covers secure cluster bootstrap, Kerberos, secret key rotation config, Ozone client writes, DN checksum RPCs, datanode scanners, SCM replica reports, container reconciliation client API, checksum Merkle tree serialization, and end-to-end data validation after repair.

Risks: It is slow and timing-sensitive due to HA secure startup, large 20 MB writes, container close waits, reports, scans, and restarts. It depends on host filesystem permission behavior for unreadable files. Direct block DB/file deletion is invasive and version-sensitive. Static cluster/client state means setup failure can cascade. It is explicitly tagged flaky, so reconciliation/report convergence may vary.

Test signals: Expected `StorageContainerException` result codes include `UNCLOSED_CONTAINER_IO`, `CONTAINER_NOT_FOUND`, and `IO_EXCEPTION`; corrupt checksum files must throw `InvalidProtocolBufferException`; success paths require sorted Merkle trees to match; reconciliation requires unique SCM data checksum count to move from divergent to one; final key validation proves readable data after repair.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/dn/checksum/TestContainerCommandReconciliation.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/dn/ratis/TestDnRatisLogParser.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/dn/ratis/TestDnRatisLogParser.java

Purpose: Integration test for parsing datanode Ratis log segment files with the debug `RatisLogParser`.

Important APIs, types, and functions: Uses `MiniOzoneCluster`, `OzoneConfiguration`, `OZONE_SCM_RATIS_PIPELINE_LIMIT`, `HDDS_CONTAINER_RATIS_DATANODE_STORAGE_DIR`, and `RatisLogParser.parseRatisLogs` with `smToContainerLogString`.

Control flow: Setup builds a one-datanode mini cluster, redirects `System.out` and `System.err` to byte-array streams, and waits for readiness. The test locates the first SCM pipeline ID, derives the datanode Ratis pipeline `current/log_inprogress_0` file, waits for its existence, invokes the parser, and asserts stdout contains total entry statistics.

State and persistence behavior: The mini cluster persists Ratis logs under the datanode Ratis storage directory. The parser reads the in-progress segment file and emits text to stdout. The test mutates global process stdout/stderr and closes the capture streams during cleanup.

Dependencies and integration points: Bridges live datanode Ratis storage layout with the debug log parser. It depends on pipeline creation and Ratis log file naming.

Risks: Redirecting global stdout/stderr can affect parallel tests. In-progress log file creation is timing-sensitive. Ratis storage layout or segment naming changes would break path derivation.

Test signals: The log segment file must exist and be a file; parser output must contain `Num Total Entries:`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/dn/ratis/TestDnRatisLogParser.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/dn/scanner/TestBackgroundContainerDataScannerIntegration.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/dn/scanner/TestBackgroundContainerDataScannerIntegration.java

Purpose: Integration tests for `BackgroundContainerDataScanner`, which scans closed containers' data and metadata without client interaction and marks corrupted replicas unhealthy.

Important APIs, types, and functions: Extends `TestContainerScannerIntegrationAbstract`. Uses `ContainerScannerConfiguration`, `BackgroundContainerDataScanner`, `TestContainerCorruptions`, `ContainerChecksums`, `ContainerMerkleTreeTestUtils.readChecksumFile`, and `verifyAllDataChecksumsMatch`. Helper `assertReplicaChecksumMatches` compares SCM-reported checksum with the checksum tree written to disk.

Control flow: `init` enables container scrubbing, disables the metadata scanner to isolate data scanner behavior, shortens the data scan interval, and builds a one-datanode cluster. The parameterized test pauses scanning, writes and closes a container, verifies initial closed state and non-zero checksum, records the SCM-reported checksum, applies each corruption type, resumes scanning, waits for the container to become `UNHEALTHY`, and verifies SCM receives the unhealthy report. For missing metadata/container directories it expects the checksum to remain unchanged; for other corruption types it expects a new checksum, a rewritten checksum file, all data checksums to match, and corruption-specific log evidence.

State and persistence behavior: The scanner updates in-memory container state, writes checksum tree files for most corruptions, and updates SCM replica checksums via reports. Corruption mutates real container files, blocks, directories, or metadata under the temp datanode volume.

Dependencies and integration points: Integrates scanner scheduling, container state transitions, checksum file generation, SCM container replica reports, corruption helpers, and log validation.

Risks: Timing depends on scanner intervals and report propagation. Some corruptions intentionally prevent checksum tree writes, so expected behavior differs. Log assertion counts vary for block-level corruptions because multiple chunks can emit messages.

Test signals: Container state must move from `CLOSED` to `UNHEALTHY`; SCM replica state must match; data checksum must change or remain depending on corruption; checksum files and log messages provide secondary verification.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/dn/scanner/TestBackgroundContainerDataScannerIntegration.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/dn/scanner/TestBackgroundContainerMetadataScannerIntegration.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/dn/scanner/TestBackgroundContainerMetadataScannerIntegration.java

Purpose: Integration tests for `BackgroundContainerMetadataScanner`, the fast metadata-only scanner that detects obvious container metadata corruption in both open and closed containers.

Important APIs, types, and functions: Extends `TestContainerScannerIntegrationAbstract`. Uses `ReplicationManager.ReplicationManagerConfiguration`, `ContainerScannerConfiguration`, `BackgroundContainerMetadataScanner`, `TestContainerCorruptions`, and `ContainerLogger` log capture. `supportedCorruptionTypes` excludes missing/corrupt/truncated block data because this scanner checks metadata, not data contents.

Control flow: Setup shortens the replication manager interval, enables scrubbing, disables the data scanner to isolate metadata scanner behavior, shortens metadata scan interval, and builds the single-datanode cluster. The test writes one closed and one open container, records initial closed checksum and verifies open checksum is zero, applies each supported metadata corruption to both containers, waits for both local states to become `UNHEALTHY`, waits for SCM reports, asserts closed checksum did not change, checks whether the open container gets a checksum depending on whether metadata/container directory was missing, waits for SCM to close the open container, and verifies one log event for each container.

State and persistence behavior: Metadata corruption mutates container metadata files/directories. The metadata scanner changes container state to unhealthy but does not itself generate data checksums; checksum generation for open containers happens as a side effect of marking the container unhealthy when possible. SCM lifecycle state for the open container transitions away from open after unhealthy reporting.

Dependencies and integration points: Ties datanode metadata scanner, SCM replica/lifecycle state, replication manager closure behavior, checksum generation side effects, and corruption logging.

Risks: The test relies on disabled data scanner so data corruption does not mask metadata scanner signals. SCM lifecycle closure after unhealthy report is asynchronous. Missing metadata/container directory cases require special checksum expectations.

Test signals: Local container state and SCM replica state must become `UNHEALTHY`, closed checksum remains stable, open checksum behavior matches corruption type, SCM closes the open container, and logs contain exactly one corruption signal per container.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/dn/scanner/TestBackgroundContainerMetadataScannerIntegration.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/dn/scanner/TestContainerScannerIntegrationAbstract.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/dn/scanner/TestContainerScannerIntegrationAbstract.java

Purpose: Shared integration-test harness for datanode container scanner tests. It builds a one-datanode cluster, creates object store fixtures, writes/open/closes containers, waits for SCM state, and exposes helpers for checksum and corruption assertions.

Important APIs, types, and functions: Provides `buildCluster`, `pauseScanner`, `resumeScanner`, `waitForScmToSeeReplicaState`, `waitForScmToCloseContainer`, `getDnContainer`, `containerChecksumFileExists`, `writeDataThenCloseContainer`, `writeDataToOpenContainer`, `closeContainerAndWait`, `getTestData`, `getContainerReplica`, `readFromCorruptedKey`, `getContainerLogCapturer`, `getConf`, and `getDatanode`. Uses `MiniOzoneCluster`, `OzoneClient`, `ObjectStore`, `OzoneBucket`, `OzoneContainer`, `ContainerManager`, `ContainerReplica`, and `ContainerMerkleTreeTestUtils`.

Control flow: `buildCluster` configures one-second container reports, zero minimum scan gap, starts a one-DN mini cluster, waits for a Ratis ONE pipeline, creates a volume/bucket, and stores static handles. Write helpers create keys with `TestHelper.createKey`, write data larger than one chunk, close containers through SCM, wait until the datanode reports local closure, and wait until SCM sees a non-zero data checksum. Open-container helper writes without closing. Read helper attempts a key read and expects an `IOException`.

State and persistence behavior: Maintains static cluster/client/store/bucket state shared by subclasses. Writes real key/container data and relies on container close to generate persisted checksum tree files. Pause/resume directly affects the datanode `OzoneContainer` scrub scheduler.

Dependencies and integration points: Centralizes cluster setup for background and on-demand scanner tests, SCM state polling, Ozone object writes/reads, and checksum file checks.

Risks: Static shared fixtures mean subclasses must not run in ways that conflict. Wait timeouts are tuned for a single-datanode mini cluster. The log capturer captures broad Log4j output because targeted Log4j2 capture is unavailable.

Test signals: Helpers assert single-datanode replica counts, non-zero closed checksums, expected read failures from corrupted keys, and SCM/container state convergence.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/dn/scanner/TestContainerScannerIntegrationAbstract.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/dn/scanner/TestOnDemandContainerScannerIntegration.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/dn/scanner/TestOnDemandContainerScannerIntegration.java

Purpose: Integration tests for `OnDemandContainerScanner`, which runs when client interaction or dispatcher write failures expose container corruption.

Important APIs, types, and functions: Extends `TestContainerScannerIntegrationAbstract`. Uses `OnDemandContainerScanner`, `OnDemandScannerMetrics`, `ContainerDispatcher`, `TestContainerCorruptions`, `ContainerLogger`, `ContainerProtos`, `Checksum.getNoChecksumDataProto`, checksum tree readers, and `verifyAllDataChecksumsMatch`. It defines supported corruption sets for closed and open containers based on what the read path can detect.

Control flow: Setup enables scrubbing but disables both background scanners so only on-demand scans can mark corruption. Closed-container tests write and close a key, record initial SCM checksum, corrupt the container, read the key and expect failure, wait for `UNHEALTHY`, validate SCM state/logs, and compare updated checksum behavior. Open-container tests do the same for supported metadata/read-path corruptions on an open container. `testOnDemandScanTriggeredByUnhealthyContainer` builds a synthetic `PutBlock` request for an unwritten chunk, dispatches it directly, asserts failure and unhealthy state, then waits for `lastDataScanTime` and scanner metrics to advance.

State and persistence behavior: On-demand scans update container state, scan time, metrics, checksum files, and SCM replica checksums. Corruptions modify real container files/directories. The dispatcher-trigger test creates no valid block data for the synthetic request but still causes state and metric updates through error handling.

Dependencies and integration points: Links client read failures, dispatcher write failure handling, container-set scan-without-gap behavior, scanner metrics, checksum tree persistence, and SCM unhealthy reports.

Risks: Detection coverage is intentionally limited to paths touched by reads or dispatcher errors; unsupported corruption types are excluded. Timing depends on async scan execution after the read/dispatch failure. Missing metadata/container dir cases cannot write checksum files and require distinct expectations.

Test signals: Read/dispatch failures must occur, local state becomes `UNHEALTHY`, SCM replica state follows, log messages appear, checksum files and data checksum values change only for supported writable cases, and scanner metrics increase after direct dispatcher failure.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/dn/scanner/TestOnDemandContainerScannerIntegration.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/dn/volume/TestDatanodeHddsVolumeFailureDetection.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/dn/volume/TestDatanodeHddsVolumeFailureDetection.java

Purpose: Integration tests proving datanodes detect failed HDD volumes when chunk files, container metadata, or RocksDB directories are corrupted under both schema V3 and older schema modes.

Important APIs, types, and functions: Uses `MiniOzoneCluster`, `OzoneClient`, `ContainerOperationClient`, `DatanodeTestUtils`, `HddsVolume`, `MutableVolumeSet`, `DatanodeStoreCache`, `HddsVolume.checkDbHealth`, and `VolumeCheckResult`. Helpers are `newCluster`, `createKey`, and `readKeyToTriggerCheckVolumeAsync`.

Control flow: Each parameterized test builds a one-datanode cluster with replication one, container cache size one, zero min free space, failed volume tolerance one, and zero disk-check min gap. `corruptChunkFile` writes a key, locates chunk files under the volume cluster/current/container/chunks path, replaces chunk files with directories, makes the volume bad, reads the key to trigger async volume check, and waits for one failed volume. `corruptContainerFile` creates a standalone container, makes its metadata dir unwritable, makes the volume bad, attempts close and expects `IOException`, then waits for failed volume detection. `corruptDbFile` writes/closes a container, evicts it from cache by creating another container, replaces DB directory with a file, invalidates schema V3 cache if needed, triggers read failure, and waits for failed volume detection. `corruptDbFileWithoutDbHandleCacheInvalidation` directly exercises `HddsVolume.checkDbHealth` for schema V3, expecting first observed failure to still return healthy and subsequent failure to return failed.

State and persistence behavior: The tests create keys, containers, chunk files, container metadata, and RocksDB directories on real temp datanode volumes. Failure injection renames or permission-mutates those paths and later restores them. Volume failure state is stored in `MutableVolumeSet` failed volume lists and DB health failure counters.

Dependencies and integration points: Integrates client read path, container close path, volume health checks, datanode store cache, schema-specific DB locations, SCM container creation, and helper failure injection.

Risks: Filesystem permission and rename semantics can vary by OS and user. RocksDB cache behavior is schema-dependent and must be explicitly invalidated for some tests. Tests rely on cleanup restoration in `finally` blocks to avoid poisoning cluster shutdown.

Test signals: Expected client read or close operations throw `IOException`; `waitForHandleFailedVolume` observes exactly one failed volume; direct DB health returns `HEALTHY` then `FAILED` in the no-cache-invalidation scenario.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/dn/volume/TestDatanodeHddsVolumeFailureDetection.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/dn/volume/TestDatanodeHddsVolumeFailureToleration.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/dn/volume/TestDatanodeHddsVolumeFailureToleration.java

Purpose: Integration test for startup-time datanode tolerance of failed data volumes. It verifies one failed volume is tolerated when configured, while a second failed volume triggers datanode shutdown.

Important APIs, types, and functions: Uses `MiniOzoneCluster`, `UniformDatanodesFactory` with three data volumes, `DatanodeConfiguration.setFailedDataVolumesTolerated`, `DatanodeTestUtils`, `ExitUtil`, `DatanodeStateMachine`, and log capture.

Control flow: Per-test setup builds a one-datanode cluster with three data volumes, replication one, fast heartbeat/report intervals, and tolerated failed data volumes set to one. The test marks the first volume root bad and restarts the datanode successfully. It then marks a second volume root bad, disables JVM exit, captures datanode and exit logs, restarts without waiting for full success, waits for `ExitException` logging, asserts datanode shutdown due to too many bad volumes, and restores both roots.

State and persistence behavior: Volume root permissions are changed to simulate startup failure. Restarting the datanode reloads volume health state. Exceeding tolerance invokes process-exit logic, intercepted by `ExitUtil.disableSystemExit`.

Dependencies and integration points: Covers volume initialization during datanode startup, failed-volume tolerance config, datanode state machine shutdown behavior, and process-exit handling.

Risks: Relies on filesystem permission changes and log messages. Because system exit is disabled, the failed datanode may not actually terminate exactly as production would. Timed wait allows up to 60 seconds for restart/shutdown logging.

Test signals: First restart with one bad volume must not throw. Second restart must log an exit with status 1 and `DatanodeStateMachine Shutdown due to too many bad volumes`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/dn/volume/TestDatanodeHddsVolumeFailureToleration.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/freon/OmBucketTestUtils.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/freon/OmBucketTestUtils.java

Purpose: Shared test utility for OM bucket read/write Freon tests, primarily carrying parameter defaults for mixed read/write workloads and assertions on OM lock metrics.

Important APIs, types, and functions: Contains nested `ParameterBuilder` with default volume/bucket path, counts, data/buffer sizes, thread mix, operation counts, bucket args, description, fluent setters, getters, `getExpectedWriteCount`, and `toString`. Public `verifyOMLockMetrics` asserts `OMLockMetrics` read/write waiting and held sample counts are greater than zero.

Control flow: ParameterBuilder setters mutate fields and return `this` for test-case construction. `getExpectedWriteCount` derives write operations from total threads minus read-thread percentage, write count, and write operation count. `verifyOMLockMetrics` reads formatted metric stat strings, logs them, parses the third whitespace-separated token as sample count, and asserts all four lock metric sample counts are positive.

State and persistence behavior: Builder state is in-memory and per instance. `verifyOMLockMetrics` observes metrics accumulated elsewhere in OM lock instrumentation and does not reset them.

Dependencies and integration points: Depends on `BucketArgs` for bucket creation parameters and `OMLockMetrics` for metrics verification. Used by Freon bucket read/write workload tests outside this subset.

Risks: Metric stat parsing is brittle because it assumes token position. Expected write count truncates integer percentage math. Defaults are tuned for tests and may be expensive if reused accidentally.

Test signals: Positive read/write lock waiting and held sample counts indicate the workload exercised OM lock instrumentation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/freon/OmBucketTestUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/freon/TestDNRPCLoadGenerator.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/freon/TestDNRPCLoadGenerator.java

Purpose: Non-HA Freon integration test for `DNRPCLoadGenerator`, validating direct datanode RPC load generation against a real allocated container in read/write and Ratis/non-Ratis modes.

Important APIs, types, and functions: Implements `NonHATests.TestCase`. Uses `StorageContainerLocationProtocolClientSideTranslatorPB.allocateContainer`, `XceiverClientCreator`, `ContainerProtocolCalls.createContainer`, `DNRPCLoadGenerator`, and picocli `CommandLine`. Parameter provider covers `(readOnly, ratis)` booleans.

Control flow: `init` allocates a standalone replication-one container through SCM, opens an xceiver client to the pipeline, and creates the container on the datanode. The parameterized test builds the generator with cluster config, supplies container ID, five clients, ten threads/operations via `-t 10`, and optional `--read-only` and `--ratis` flags, then asserts command exit code zero.

State and persistence behavior: The allocated container is persisted in the mini cluster during setup. Load generator calls perform direct DN RPCs that may read or write container data depending on flags. No explicit post-run container content validation is performed beyond exit code.

Dependencies and integration points: Exercises SCM container allocation, xceiver client factory, datanode container creation, Freon CLI parsing, and direct DN RPC load code.

Risks: Exit-code-only validation may miss partial operation failures if the generator swallows them. Shared setup container is reused across parameter cases. Load generation can be timing-sensitive under constrained CI.

Test signals: `cmd.execute` must return `0` for all four read-only/Ratis combinations.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/freon/TestDNRPCLoadGenerator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/freon/TestDataValidate.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/freon/TestDataValidate.java

Purpose: Abstract base integration test for Freon `RandomKeyGenerator` write-validation behavior on a five-datanode Ratis cluster.

Important APIs, types, and functions: Provides static `startCluster` and `shutdownCluster`, and tests `ratisTestLargeKey` and `validateWriteTest`. Uses `MiniOzoneCluster`, `DatanodeRatisServerConfig`, `RatisClientConfig.RaftConfig`, `OZONE_SCM_RATIS_PIPELINE_LIMIT`, `RandomKeyGenerator`, and picocli `CommandLine`.

Control flow: `startCluster` shortens Ratis request/watch timeouts, sets pipeline limit to eight, starts five datanodes, waits for readiness, and waits for a Ratis THREE pipeline. `ratisTestLargeKey` writes one 20 MB key with `--validate-writes` and asserts one volume, one bucket, one key, and zero validation failures. `validateWriteTest` writes 2 volumes * 5 buckets * 10 keys with Ratis THREE validation and asserts expected creation counts, validation enabled, non-zero validated/success counts, and zero unsuccessful validations.

State and persistence behavior: Tests create real volumes, buckets, keys, and replicated Ratis containers. `RandomKeyGenerator` stores counters for created volumes/buckets/keys and validation outcomes. Cluster state is static and shared by concrete subclasses.

Dependencies and integration points: Integrates Freon CLI, Ozone object store writes, Ratis replication, client/datanode timeouts, and read-back validation of generated data.

Risks: Large-key and multi-key tests can be slow. Static cluster lifecycle is controlled by subclasses, so missing shutdown would leak resources. Counter assertions depend on `RandomKeyGenerator` semantics.

Test signals: Exact creation counts, `getValidateWrites` true, positive validation counts, and zero unsuccessful validation count.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/freon/TestDataValidate.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/freon/TestDataValidateWithDummyContainers.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/freon/TestDataValidateWithDummyContainers.java

Purpose: Concrete `TestDataValidate` variant for non-persistent dummy containers, where write validation is intentionally unsupported.

Important APIs, types, and functions: Extends `TestDataValidate`. `init` sets `HDDS_CONTAINER_PERSISTDATA=false` and disables unsafe byte operations before starting the inherited cluster. Overrides `validateWriteTest` as a logged no-op. `shutdown` delegates to `shutdownCluster`.

Control flow: Before all tests, it starts a cluster configured to avoid persisting container data. The inherited `ratisTestLargeKey` can still exercise generator behavior, but write-validation test is skipped because non-persistent containers cannot validate writes. After all tests, it shuts down the shared cluster.

State and persistence behavior: Container data persistence is disabled, so data is not durable on disk. This is the core reason validation is not meaningful in this mode.

Dependencies and integration points: Validates Freon behavior under `ChunkManagerDummyImpl`/non-persistent container configuration while sharing the base RandomKeyGenerator cluster harness.

Risks: The no-op override has no assertion, intentionally suppressing the inherited validation contract. If non-persistent behavior changes, this skip may need revisiting.

Test signals: Startup/shutdown and inherited tests are the main signals; overridden validation emits a log message and no assertion.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/freon/TestDataValidateWithDummyContainers.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/freon/TestDataValidateWithSafeByteOperations.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/freon/TestDataValidateWithSafeByteOperations.java

Purpose: Concrete `TestDataValidate` variant that runs Freon write-validation tests with unsafe byte operations disabled.

Important APIs, types, and functions: Extends `TestDataValidate`. `init` creates `OzoneConfiguration`, sets `OZONE_UNSAFEBYTEOPERATIONS_ENABLED=false`, and calls `startCluster`. `shutdown` calls `shutdownCluster`.

Control flow: Before all tests, starts the inherited five-datanode Ratis cluster in safe byte-operation mode. It inherits `ratisTestLargeKey` and `validateWriteTest`, which run `RandomKeyGenerator` with write validation. After all tests, it shuts down the cluster.

State and persistence behavior: Uses normal persistent containers and safe byte handling for generated key data. State and validation counters are inherited from the base test.

Dependencies and integration points: Verifies Freon validation works when Ozone avoids unsafe byte operations, covering the safer data path.

Risks: Thin wrapper, so most behavioral risk is in base class. It only toggles one config key and assumes inherited tests fully cover the mode.

Test signals: Inherited creation-count and validation-count assertions must pass under safe byte operations.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/freon/TestDataValidateWithSafeByteOperations.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/freon/TestDataValidateWithUnsafeByteOperations.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/freon/TestDataValidateWithUnsafeByteOperations.java

Purpose: Concrete `TestDataValidate` variant that runs Freon write-validation tests with unsafe byte operations enabled.

Important APIs, types, and functions: Extends `TestDataValidate`. `init` sets `OZONE_UNSAFEBYTEOPERATIONS_ENABLED=true` and starts the inherited cluster. `shutdown` calls `shutdownCluster`.

Control flow: Starts a five-datanode Ratis cluster configured for unsafe byte operations, then inherits large-key and multi-key RandomKeyGenerator validation tests. Shuts down after all tests.

State and persistence behavior: Uses persistent replicated key data, but byte-buffer handling follows the unsafe optimized path. Counters and validation data are maintained by `RandomKeyGenerator`.

Dependencies and integration points: Verifies Freon validation and Ozone write/read data handling work with the unsafe byte operation optimization enabled.

Risks: Thin wrapper; failures indicate either base Freon validation issues or unsafe byte path regressions. Does not add mode-specific assertions beyond inherited validation success.

Test signals: Inherited tests must produce expected object counts, positive validation counts, and zero failed validations.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/freon/TestDataValidateWithUnsafeByteOperations.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/freon/TestFreonWithDatanodeFastRestart.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/freon/TestFreonWithDatanodeFastRestart.java

Purpose: Freon integration test for datanode fast restart without waiting for pipeline closure, with Ratis snapshot verification. Marked unhealthy for HDDS-1160.

Important APIs, types, and functions: Uses `MiniOzoneCluster`, `RandomKeyGenerator`, `StateMachine`, `SimpleStateMachineStorage`, `SingleFileSnapshotInfo`, `TermIndex`, and `TestHelper.getStateMachine`. Helper `startFreon` runs one 20 MB Ratis THREE validated write.

Control flow: Setup starts a three-datanode mini cluster with one-second SCM heartbeat processing. The test runs Freon once, records the Ratis state machine last applied term/index, restarts datanode 0 without waiting, obtains the restarted state machine storage, verifies the latest snapshot file corresponds to the pre-restart term/index, checks post-restart term index is not behind, sleeps five seconds for datanode SCM registration, then runs Freon again.

State and persistence behavior: Freon writes replicated data and advances Ratis state. Datanode restart creates or exposes a snapshot in state machine storage. The test checks snapshot file path and term/index persistence across restart.

Dependencies and integration points: Exercises Freon writes, datanode restart behavior, Ratis state machine snapshotting, SCM heartbeat registration, and post-restart pipeline usability.

Risks: Explicit `Thread.sleep(5000)` documents a known race with SCM registration and possible `scmId cannot be null` crash. The test is marked unhealthy. Snapshot path expectations are tightly coupled to Ratis storage naming.

Test signals: Freon counters must show one volume/bucket/key and zero validation failures before and after restart; snapshot file and term index must match pre-restart last applied term/index; post-restart index must be greater than or equal to before.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/freon/TestFreonWithDatanodeFastRestart.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/freon/TestFreonWithPipelineDestroy.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/freon/TestFreonWithPipelineDestroy.java

Purpose: Freon integration test verifying RandomKeyGenerator can write successfully before and after an active Ratis pipeline is closed/destroyed and a new pipeline becomes ready.

Important APIs, types, and functions: Uses `MiniOzoneCluster`, `RandomKeyGenerator`, Ratis timeout configs, `XceiverServerSpi.getPipelineReport`, `PipelineID`, `PipelineManager`, and picocli `CommandLine`. Helpers are `startFreon` and `destroyPipeline`.

Control flow: Setup configures short pipeline destroy timeout, pipeline report interval, heartbeat processing, Ratis timeouts, and starts a three-datanode cluster. The test runs one validated 20 MB Freon write, closes the pipeline reported by datanode 0 through SCM `PipelineManager.closePipeline`, waits for a new Ratis THREE pipeline, then runs the same Freon write again.

State and persistence behavior: Freon writes persistent replicated data. Closing a pipeline changes SCM pipeline state and datanode pipeline reports. New pipeline readiness is required before the second write.

Dependencies and integration points: Exercises Freon object writes, SCM pipeline manager, datanode pipeline reports, Ratis pipeline recreation, and validation after topology disruption.

Risks: Pipeline report ordering assumes the first report is suitable. Pipeline closure and recreation are asynchronous and can be timing-sensitive. Freon uses generic object names, so repeated runs rely on generator uniqueness or clean cluster state.

Test signals: Both Freon runs must create exactly one volume, one bucket, one key, and zero failed validations; cluster must provide a ready Ratis THREE pipeline after closure.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/freon/TestFreonWithPipelineDestroy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/freon/TestHadoopDirTreeGenerator.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/freon/TestHadoopDirTreeGenerator.java

Purpose: Integration tests for Freon Hadoop directory tree generator command `dtsg`, validating generated directory depth, span, file count, and file size through the Ozone Hadoop filesystem.

Important APIs, types, and functions: Implements `NonHATests.TestCase`. Uses `Freon.getCmd`, `OzoneClient`, `ObjectStore`, `BucketArgs`, `BucketLayout`, `OzoneFileSystemTestUtils.setPageSize`, Hadoop `FileSystem`, `FileStatus`, and `StorageSize`. Helpers include `verifyDirTree`, `traverseToLeaf`, and `verifyActualSpan`.

Control flow: Per-test setup opens an Ozone client; cleanup closes it. The parameterized test runs for `FILE_SYSTEM_OPTIMIZED` and `LEGACY` bucket layouts and verifies several volume/bucket trees with different depth, span, file count, and per-file-size combinations, including page-size-plus-half span. `verifyDirTree` creates the volume and bucket, invokes `freon dtsg` with root `o3fs://bucket.volume`, then lists the filesystem with a small page size. It checks root span, recursively follows one directory path to the leaf, validates intermediate span counts, validates leaf file sizes, and ensures duplicate names are not seen in a directory.

State and persistence behavior: Creates real volumes, buckets, directories, and files in the test cluster. The Hadoop filesystem listing reflects OM namespace state for both bucket layouts. Page size configuration affects listing pagination behavior.

Dependencies and integration points: Covers Freon CLI, Ozone object store bucket layout variants, Hadoop Ozone filesystem URI handling, OM address injection, directory listing pagination, and file size generation.

Risks: The traversal follows the first directory path rather than exhaustively validating all branches. Listing order may affect which path is checked, though span/file assertions still catch many regressions. The duplicate-name assertion message is awkward but functional.

Test signals: Expected depth, subdirectory span, file count, and file length must match for each scenario and bucket layout.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/freon/TestHadoopDirTreeGenerator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/freon/TestHadoopNestedDirGenerator.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/freon/TestHadoopNestedDirGenerator.java

Purpose: Integration tests for Freon Hadoop nested directory generator command `ddsg`, validating generated nested directory depth and span through the Ozone filesystem.

Important APIs, types, and functions: Implements `NonHATests.TestCase`. Uses `Freon.getCmd`, `OzoneClient`, `ObjectStore`, Hadoop `FileSystem`, `FileStatus`, and helpers `verifyDirTree`, `depthBFS`, and `spanCheck`.

Control flow: Per-test setup opens a cluster client and object store; cleanup closes it. The test invokes `verifyDirTree` with several depth/span combinations, including span zero. Each invocation creates a volume/bucket, runs `freon ddsg` against `o3fs://bucket.volume`, lists the root through Hadoop FS, computes depth with breadth-first traversal, then counts child directories at the last parent/leaf parent and compares with expected span.

State and persistence behavior: Creates Ozone volumes, buckets, and directory keys. The filesystem view is read after generation to validate namespace state.

Dependencies and integration points: Covers Freon nested directory generation, Ozone FS URI access, OM address configuration, and Hadoop filesystem directory listings.

Risks: `depthBFS` assumes at least one root status and uses the last visited path to check span. It validates structural shape but not naming or all branches exhaustively. Span zero has special path/depth handling.

Test signals: BFS-computed depth must equal expected depth, and `spanCheck` on the selected path must equal expected span.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/freon/TestHadoopNestedDirGenerator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/freon/TestHsyncGenerator.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/freon/TestHsyncGenerator.java

Purpose: Non-HA integration test for Freon `HsyncGenerator`, ensuring the generator command succeeds against an OFS bucket path in a mini cluster.

Important APIs, types, and functions: Implements `NonHATests.TestCase`. Uses `HsyncGenerator`, picocli `CommandLine`, `OzoneClient`, `ObjectStore`, `OzoneVolume`, `OZONE_OFS_URI_SCHEME`, and `OZONE_OM_ADDRESS_KEY`.

Control flow: The test creates a random volume and `bucket1`, constructs an OFS root path of the form `ofs://<om-address>/<volume>/<bucket>/`, executes the generator with 8 bytes per write, 64 writes per transaction, five threads, and 100 operations, then asserts exit code zero.

State and persistence behavior: Creates real volume/bucket namespace and writes data through hsync workload operations. The test does not inspect generated files afterward; persistence is implied by command success.

Dependencies and integration points: Covers Freon CLI parsing, OFS URI handling, hsync write path, and Ozone client/object-store setup.

Risks: Exit-code-only validation may miss subtle durability or content issues. Workload timing can vary with cluster performance. The path depends on OM address config being populated.

Test signals: The generator command must return exit code `0`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/freon/TestHsyncGenerator.java -->
