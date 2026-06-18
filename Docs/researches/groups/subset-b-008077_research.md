# Research Group: subset-b-008077

This grouped report covers Apache Ozone integration-test sources under `hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone`. Each section is bounded for deterministic reconciliation into the requested source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/TestMiniOzoneCluster.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/TestMiniOzoneCluster.java

## Purpose
`TestMiniOzoneCluster` verifies core MiniOzoneCluster and datanode lifecycle behavior in a local integration-test environment. It checks that clusters can start multiple HDDS datanodes, clients can connect to datanode container endpoints, random container ports are assigned uniquely, datanode restarts preserve advertised ports, datanodes recover registration after SCM restarts, and a custom datanode factory creates multiple data volumes with configured reserved space.

## Important APIs, Types, and Functions
- `MiniOzoneCluster.newBuilder(conf)` drives cluster construction through `setNumDatanodes`, `setDatanodeFactory`, `build`, `waitForClusterToBeReady`, `restartHddsDatanode`, and `restartStorageContainerManager`.
- `HddsDatanodeService`, `DatanodeStateMachine`, `EndpointStateMachine`, and `StorageContainerManager` expose the datanode and SCM state inspected by the tests.
- `Pipeline.newBuilder`, `PipelineID.randomId`, `StandaloneReplicationConfig.getInstance(ReplicationFactor.ONE)`, and `XceiverClientGrpc` create a one-datanode standalone pipeline and validate gRPC connectivity.
- Configuration keys under `OzoneConfigKeys`, `HddsConfigKeys`, and `ScmConfigKeys` control metadata directories, pipeline limit, random IPC/Ratis/datastream ports, and SCM stale-node timing.
- `UniformDatanodesFactory` and `StorageVolume` are used to assert volume count and reserved capacity.

## Control Flow
`setup` builds a shared `OzoneConfiguration` rooted at a JUnit temp directory, lowers the datanode pipeline limit, enables random Ratis IPC ports, and shortens SCM stale-node detection. Each test creates or manipulates a cluster and `cleanup` shuts it down if present. `testStartMultipleDatanodes` starts three datanodes, builds a standalone one-node pipeline for each, connects with `XceiverClientGrpc`, and asserts the selected node is connected. `testContainerRandomPort` constructs raw `DatanodeStateMachine` instances outside a full cluster, starts their read and write channels to force actual port binding, stops the channels, and verifies all read/write ports are nonzero and unique; it then disables the random IPC port flag and confirms multiple state machines use the same configured default read port. `testKeepPortsWhenRestartDN` captures all `DatanodeDetails.Port` values before and after a persistent datanode restart. `testDNstartAfterSCM` stops SCM, restarts a datanode, observes `GETVERSION`, restarts SCM, waits for readiness, and expects `HEARTBEAT`. `testMultipleDataDirs` starts one datanode with three data volumes and a one-byte reserved-space setting, then checks cluster naming/base-dir conventions and volume reservations.

## State and Persistence Behavior
The file exercises both ephemeral process state and persistent identity state. Port preservation relies on datanode restart with persisted metadata. The SCM restart path checks endpoint-state transitions rather than persisted tables. The multiple-volume test validates datanode volume configuration materialized into the container volume set. Random-port checks explicitly start container channels because port values are finalized only after server bind.

## Dependencies and Integration Points
The tests integrate MiniOzoneCluster with the HDDS datanode state machine, container read/write channels, SCM lifecycle, pipeline/client connectivity, temporary metadata directories, and volume usage accounting. `SCMTestUtils.getConf` provides a separate configuration for raw datanode-state-machine port checks.

## Risks and Edge Cases
Random port uniqueness is sensitive to bind timing and local port availability. The GETVERSION loop has no sleep, so it is a tight state assertion over a nominal twenty iterations rather than a true twenty-second wait. `testContainerRandomPort` sets the datastream-enabled flag on the shared `conf` instead of `ozoneConf`, which may be intentional for global defaults but is a configuration coupling worth watching. The tests do not write user data through OM; they focus on datanode and container-service surfaces.

## Test Signals
Strong signals include successful `XceiverClientGrpc` connection to every datanode, nonzero and unique random container channel ports, stable datanode port maps after restart, transition from `GETVERSION` to `HEARTBEAT` after SCM recovery, and exact data-volume count/reserved bytes. Failures usually indicate lifecycle, port binding, endpoint registration, or datanode factory regressions.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/TestMiniOzoneCluster.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/TestOMSortDatanodes.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/TestOMSortDatanodes.java

## Purpose
`TestOMSortDatanodes` verifies network-topology-aware read ordering as exposed through `KeyManagerImpl.sortDatanodes(List, String)`. It builds a miniature SCM/OM manager stack with registered datanodes distributed across two racks and validates that datanodes are sorted nearest to either a datanode client or an edge client hostname.

## Important APIs, Types, and Functions
- `KeyManagerImpl.sortDatanodes` is the primary API under test.
- `StaticMapping` and `NET_TOPOLOGY_NODE_SWITCH_MAPPING_IMPL_KEY` provide deterministic host/IP-to-rack resolution.
- `OZONE_NETWORK_TOPOLOGY_AWARE_READ_KEY` enables topology-aware read sorting.
- `HddsTestUtils.getScm`, `SCMConfigurator`, `SCMHAManagerStub`, `SCMContext.emptyContext`, `NodeManager.register`, and `OmTestManagers` create the SCM and OM-side dependencies.
- Helpers `assertRackOrder` and `nodeAddress` encode expected ordering and hostname-vs-IP client addressing.

## Control Flow
`setup` creates ten random datanodes, alternates them between `/rack0` and `/rack1`, adds both hostname and IP mappings, and adds two synthetic edge nodes. SCM is started, safe mode is exited, all datanodes are registered with the SCM node manager, and `OmTestManagers` creates an OzoneManager, RPC client, and key manager. `sortDatanodesRelativeToDatanode` iterates every registered datanode and expects the source datanode to be first, followed by all same-rack nodes before other-rack nodes. `sortDatanodesRelativeToNonDatanode` uses the edge hostnames and checks same-rack-first ordering. `testSortDatanodes` covers valid datanode client address and invalid client strings, asserting the method remains total and returns the full node list.

## State and Persistence Behavior
The test registers datanodes into SCM's in-memory node manager and uses static topology mappings from configuration. It does not persist OM keys or blocks. Cleanup closes the Ozone client, stops and joins SCM, and stops OM.

## Dependencies and Integration Points
This is an integration point between Hadoop network topology mapping, SCM node registration, OM key-management read sorting, and Ozone client manager setup. It also checks that `DatanodeDetails` network levels are set to `ROOT_LEVEL + 2`, matching rack-level topology.

## Risks and Edge Cases
The rack-order assertion assumes an even split across exactly two racks and checks the first half versus second half, so changes to distribution or topology depth would require test changes. Invalid clients are tested only for result size, not stable order. Because datanodes are random, uniqueness and mapping correctness depend on generated host/IP values being stable enough for `StaticMapping`.

## Test Signals
The most important signal is that source-local reads rank the source datanode first, same-rack nodes before remote-rack nodes, and invalid client addresses do not drop datanodes. This protects topology-aware read performance and fallback behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/TestOMSortDatanodes.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/TestOzoneConfigurationFields.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/TestOzoneConfigurationFields.java

## Purpose
`TestOzoneConfigurationFields` enforces consistency between Java configuration constants and `ozone-default.xml`. It extends Hadoop's `TestConfigurationFieldsBase` and declares the Ozone, SCM, HDDS, Recon, S3 gateway, and S3 secret config classes whose public config constants should be represented in the XML defaults, while maintaining explicit skip lists for dynamic, deprecated, tested-elsewhere, or intentionally non-XML properties.

## Important APIs, Types, and Functions
- `initializeMemberVariables` sets `xmlFilename`, `configurationClasses`, `errorIfMissingConfigProps`, and `errorIfMissingXmlProps`.
- `xmlPropsToSkipCompare`, `xmlPrefixToSkipCompare`, `configurationPropsToSkipCompare`, and `configurationPrefixToSkipCompare` are inherited mutable sets that define exceptions.
- `addPropertiesNotInXml` centralizes the larger skip list for keys that are intentionally not documented in `ozone-default.xml`.
- Config classes include `OzoneConfigKeys`, `ScmConfigKeys`, `OMConfigKeys`, `HddsConfigKeys`, Recon keys, S3 gateway keys, and S3 secret keys.

## Control Flow
The test framework calls `initializeMemberVariables`, after which the inherited base test reflects over the listed classes and compares discovered property names with the XML file. The method first enables strict missing-property checks, then adds specific XML examples and prefixes to skip, excludes known client-side/default fields and deprecated values, skips Ranger prefixes pending finalization, and invokes `addPropertiesNotInXml` for generated, HA-template, internal, test-only, or otherwise non-defaulted keys.

## State and Persistence Behavior
There is no runtime service state or persistence. The file mutates inherited test configuration collections before the base-class comparison executes.

## Dependencies and Integration Points
The file integrates with `ozone-default.xml`, Java config-key classes across Ozone/HDDS/Recon/S3 packages, and `HttpServer2.HTTP_IDLE_TIMEOUT_MS_KEY`, which is excluded because another test owns it. It is a documentation/configuration contract test rather than a service behavior test.

## Risks and Edge Cases
The skip lists can hide real documentation gaps if keys remain there after becoming user-facing. There is a duplicate skip for `ozone.scm.nodes.EXAMPLESCMSERVICEID`. Strict `errorIfMissingConfigProps` and `errorIfMissingXmlProps` make the test sensitive to both new Java constants and stale XML properties, which is intentional but can cause broad failures during config refactors.

## Test Signals
Passing means the configured key classes and `ozone-default.xml` are synchronized except for documented exceptions. Failures are strong signals that a new config key lacks XML documentation, an XML property lacks a matching constant, or an exception list needs deliberate review.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/TestOzoneConfigurationFields.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/TestSecureOzoneCluster.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/TestSecureOzoneCluster.java

## Purpose
`TestSecureOzoneCluster` is a broad secure-mode integration test for Ozone SCM and OM. It validates Kerberos startup, SCM security protocol authentication, admin authorization, OM secure initialization, delegation-token renewal, S3 secret authorization, OM certificate initialization and rotation, cross-secret-key token renewal, and gRPC TLS certificate renewal behavior.

## Important APIs, Types, and Functions
- Security setup uses `MiniKdc`, `UserGroupInformation`, Kerberos principals/keytabs, `HADOOP_SECURITY_AUTHENTICATION`, and Ozone/SCM/OM Kerberos config keys.
- SCM setup uses `StorageContainerManager.scmInit`, `HddsTestUtils.getScmSimple`, `ScmInfo`, `SCMSecurityProtocolClientSideTranslatorPB`, `HAUtils.getScmContainerClient`, and `StorageContainerLocationProtocol`.
- OM setup uses `OMStorage`, `OzoneManager.createOm`, `OzoneManager.omInit`, `OzoneManager.setTestSecureOmFlag`, `OzoneManagerProtocolClientSideTranslatorPB`, `OmTransportFactory`, and `ScmTopologyClient`.
- Certificate paths use `SecurityConfig`, `OMCertificateClient`, `DefaultCertificateClient`, `CertificateCodec`, `CertificateClientTestImpl`, `SelfSignedCertificate`, `DefaultApprover`, `CertificateSignRequest`, and `SCMGetCertResponseProto`.
- Token and secret paths use `Token<OzoneTokenIdentifier>`, `ManagedSecretKey`, `SecretKeyTestClient`, `S3SecretValue`, `DELEGATION_TOKEN_MAX_LIFETIME_KEY`, and `HDDS_SECRET_KEY_EXPIRY_DURATION`.
- Helper methods `setSecureConfig`, `createCredentialsInKDC`, `initSCM`, `setupOm`, `initializeOmStorage`, `validateCertificate`, `generateSelfSignedX509Cert`, and `signX509Cert` define the reusable secure test environment.

## Control Flow
`init` allocates random ports, enables security and Kerberos, sets certificate-renewal/grace timers and delegation-token lifetime, creates MiniKdc principals, generates an OM key pair, and builds OM details. `stop` shuts down KDC, SCM, OM, and OM client. SCM tests initialize SCM storage and assert secure startup, security-protocol success for a keytab-authenticated user, failure for token-only users, and admin-command denial for non-admin or unauthenticated users. Kerberos failure tests deliberately clear or corrupt principal/authentication settings and reuse `testCommonKerberosFailures`.

OM tests start secure SCM, initialize OM storage, and then validate successful login/startup, secure client volume creation, no retry on access-control authentication failure, and secret-manager lifetime validation. Delegation-token tests obtain a token over Kerberos, renew it, then assert expiration, renewer mismatch, and tampered-token failures. S3 secret tests cover get, duplicate get, revoke, set after revoke, admin access to other users, and non-admin `USER_MISMATCH` failures.

Certificate tests cover multiple phases: reinitializing a previously insecure OM into secure mode; first secure OM certificate acquisition from SCM and trust-chain persistence; periodic certificate rotation with mocked SCM responses; recoverable rotation failure where an invalid response leaves the old cert in place until a valid response arrives; unrecoverable rollback failure where OM termination is expected; and gRPC TLS renewal where old and new clients continue to connect after OM certificate renewal and old certificate expiry. The cross-secret-key token test injects `SecretKeyTestClient`, rotates the current secret key, obtains a new token with the new key id, and proves an older token remains renewable while the old key is still valid.

## State and Persistence Behavior
The suite writes SCM and OM metadata under temp directories through `SCMStorageConfig` and `OMStorage`, including cluster IDs, SCM IDs, OM IDs, certificate serial IDs, keys, and certificates. Certificate rotation writes certificates through `CertificateCodec` and checks serial-number changes in the active certificate client. Token state lives in OM's delegation-token/secret-key machinery, while `SecretKeyTestClient` keeps generated keys in memory by UUID. Kerberos state is externalized in MiniKdc keytab files. Several tests intentionally share or override principals because SCM and OM run in the same JVM and Hadoop UGI state can otherwise conflict.

## Dependencies and Integration Points
This file ties together MiniKdc, Hadoop RPC/SASL, SCM security service, OM RPC/gRPC transports, Ozone Manager storage, SCM certificate authority behavior, token renewal logic, S3 secret APIs, certificate file layout, and process-exit paths. It also uses log capture from `OzoneManager`, `OMCertificateClient`, `Client`, and `ExitUtil` as observable integration signals.

## Risks and Edge Cases
Timing-sensitive tests depend on sleeps, certificate lifetimes, renewal grace periods, and `GenericTestUtils.waitFor`; slow hosts can make rotation and expiry checks flaky. `testGetSetRevokeS3Secret` is marked flaky for HDDS-9349 and `testOMGrpcServerCertificateRenew` is marked unhealthy for HDDS-8764. Same-JVM UGI behavior is a known risk; `initSCM` rewrites the SCM Kerberos principal to the OM principal to let OM contact SCM. Several tests assert specific exception messages and log strings, making them sensitive to message changes even if behavior remains correct. Exit-path tests disable system exits and inspect logs, so cleanup and global static state such as `OzoneManager.setUgi` and `GrpcOmTransport.setCaCerts` must be restored.

## Test Signals
Strong signals include trust-chain sizes, successful CA certificate retrieval only with Kerberos, exact admin/authentication failures, OM login log output, single no-retry access-control log occurrence, correct token kind/service/secret-key id, `TOKEN_EXPIRED` and `USER_MISMATCH` result codes, S3 secret changes after revoke, certificate subject/issuer/validity checks, certificate serial changes after renewal, old-token renewal across secret-key rotation, and gRPC client success before and after OM certificate renewal.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/TestSecureOzoneCluster.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/admin/om/lease/TestLeaseRecoverer.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/admin/om/lease/TestLeaseRecoverer.java

## Purpose
`TestLeaseRecoverer` verifies the OM admin lease-recovery CLI against an FSO bucket in a non-HA Ozone cluster. It creates an open file, writes and syncs data, runs `LeaseRecoverer --path`, and then confirms the recovered file is visible, closed, immutable through the old output stream, and safely recoverable a second time.

## Important APIs, Types, and Functions
- The abstract test implements `NonHATests.TestCase`, using `cluster()` supplied by the concrete non-HA test harness.
- `TestDataUtil.createVolumeAndBucket(client, BucketLayout.FILE_SYSTEM_OPTIMIZED)` creates the target FSO bucket.
- `FileSystem`, `FSDataOutputStream`, `FileStatus`, `LeaseRecoverable`, and `Path` exercise the OFS filesystem path.
- `CommandLine(new LeaseRecoverer()).setOut(...).setErr(...)` invokes the picocli admin command in-process.
- Constants `OZONE_OFS_URI_SCHEME`, `OZONE_URI_DELIMITER`, and `OZONE_OM_ADDRESS_KEY` build the OFS URI.

## Control Flow
`init` creates an Ozone client and an FSO bucket. `testCLI` builds an `ofs://<om-address>/<volume>/<bucket>/file` path and opens a Hadoop `FileSystem` for the OFS root. `testWithFS` writes random bytes to a new file, calls `hsync`, executes the lease-recovery command with `--path`, checks stderr is empty, and asserts the visible file length equals the first write. It then attempts another write through the old stream; `flush` and `hsync` must throw `IOException`, length must remain unchanged, `isFileClosed` must report true, close must succeed, and a second CLI recovery call must also succeed without stderr.

## State and Persistence Behavior
The test persists a volume, FSO bucket, and file through the cluster's OM and filesystem implementation. Lease recovery transitions the key/file from an open lease to closed state, after which the old stream can no longer extend committed length. The second command execution validates idempotence.

## Dependencies and Integration Points
The file connects the admin CLI, OFS URI parsing, Hadoop `FileSystem`, FSO bucket layout, OM lease recovery, and stream failure handling. It uses picocli output redirection to assert CLI cleanliness without spawning a separate process.

## Risks and Edge Cases
The test is non-HA only and focuses on FSO layout, not object-store bucket layout. It assumes `flush` after recovery will call writeChunk/putBlock and fail; changes in stream buffering could alter where the exception appears. It checks stderr but does not inspect stdout or command exit code. Random content validates length, not byte-for-byte data after recovery.

## Test Signals
Passing means the lease-recovery CLI closes an open OFS file, preserves the last synced length, rejects further writes through the stale stream, reports the file as closed, and remains idempotent on repeated recovery.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/admin/om/lease/TestLeaseRecoverer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/SecretKeyTestClient.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/SecretKeyTestClient.java

## Purpose
`SecretKeyTestClient` is a small test implementation of `SecretKeyClient` used to model OM secret-key rotation for delegation-token tests. It generates HMAC secret keys, exposes the current key, retains older keys by UUID, and lets tests rotate to a new current key while old keys remain retrievable.

## Important APIs, Types, and Functions
- Implements `SecretKeyClient.getCurrentSecretKey()` and `SecretKeyClient.getSecretKey(UUID)`.
- `rotate()` creates a new `ManagedSecretKey` and stores it in `keysMap`.
- `generateKey()` uses `KeyGenerator.getInstance("HmacSHA256")`, `UUID.randomUUID()`, `Instant.now()`, and `Instant.now().plus(Duration.ofHours(1))`.
- `ManagedSecretKey` carries key id, creation time, expiry time, and the generated `SecretKey`.

## Control Flow
The constructor immediately calls `rotate`, so a usable current key exists after construction. Each later `rotate` replaces `current` with a newly generated one and inserts it into the map. Lookup by ID returns either the matching current or older key, if it has been generated in this client instance.

## State and Persistence Behavior
State is in-memory only. There is no expiry enforcement or removal of old keys; the one-hour expiry timestamp is metadata consumed by downstream code. Because older keys remain in `keysMap`, tests can validate renewal of tokens signed by a previous key after rotation.

## Dependencies and Integration Points
The class is used by secure OM tests that inject a custom secret-key client into `OzoneManager`. It integrates with HDDS symmetric-key abstractions and Java cryptography but has no Ozone service dependencies of its own.

## Risks and Edge Cases
The implementation is intentionally minimal and not thread-safe. It does not simulate key deletion, expiry rejection, persistence, or failed key generation beyond wrapping the impossible missing `HmacSHA256` algorithm in `RuntimeException`. Tests using it should not infer production rotation cleanup behavior.

## Test Signals
Useful signals are distinct UUIDs after rotation, stable retrieval of old keys by ID, and token identifiers reflecting the current key id at creation time while old tokens can still be validated with retained keys.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/SecretKeyTestClient.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/package-info.java

## Purpose
`package-info.java` supplies package-level documentation for `org.apache.hadoop.ozone.client` integration tests. Its only semantic content is the Javadoc sentence identifying the package as Ozone client tests, followed by the package declaration.

## Important APIs, Types, and Functions
There are no classes, methods, constants, or runtime APIs. The file declares the `org.apache.hadoop.ozone.client` package and provides package Javadoc.

## Control Flow
No executable control flow exists.

## State and Persistence Behavior
No state is created, mutated, or persisted.

## Dependencies and Integration Points
The file integrates with Java package documentation tooling and the compiler's package-info convention. It sits beside client integration-test helpers such as `SecretKeyTestClient`.

## Risks and Edge Cases
The only practical risk is documentation drift if the package contents broaden beyond client tests. There is no behavioral risk.

## Test Signals
Compilation of package metadata is the only signal. There are no direct assertions tied to this file.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/package-info.java -->
