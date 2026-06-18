# subset-b-008089 Research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/shell/TestOzoneShellHA.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/shell/TestOzoneShellHA.java

Purpose: This is the main HA integration suite for `ozone sh`, `ozone admin`, and selected OFS shell behavior against a three-OM `MiniOzoneHAClusterImpl`. It validates command URI handling, volume/bucket/key operations, admin container and open-file commands, trash semantics, quotas, EC/RATIS replication options, bucket encryption keys, recursive delete, bucket links, JSON output, and bucket-layout validation.

Important APIs and types: The suite uses `OzoneShell`, `OzoneAdmin`, `OzoneFsShell`, `MiniOzoneHAClusterImpl`, `OzoneClient`, `ObjectStore`, `OzoneVolume`, `OzoneBucket`, `OzoneKeyDetails`, `OzoneFileStatus`, `OFSPath`, `OzoneTrashPolicy`, `MiniKMS`, `KeyProvider`, `ECKeyOutputStream`, `KeyOutputStream`, `CommandLine`, and OM/SCM config keys. Helpers inject OM HA `--set` values, parse JSON output, create volumes/buckets/keys, count output tokens, and build OFS client configurations.

Control flow: `init` starts MiniKMS, configures OM HA, KMS, filesystem paths, directory deletion, SCM container-list limit, and a five-datanode HA cluster. Each test captures stdout/stderr, executes shell commands through picocli with HA overrides, and then checks client-side API state or command output. Long flows create temporary keys, keep OFS streams open, force OM double-buffer flushes, suspend open-key cleanup, delete or overwrite hsynced files, and retry with `GenericTestUtils.waitFor`.

State and persistence behavior: The tests create real OM metadata for volumes, buckets, keys, open keys, hsync metadata, quota metadata, bucket encryption metadata, replication configs, linked buckets, trash trees, and recursive-deletion side effects. They also touch SCM container state through admin list/create commands and KMS-backed encryption key creation. Persistent test state is intentionally shared across ordered tests, with selective cleanup for some resources.

Dependencies and integration points: This file exercises shell parsing, HA OM address resolution, OM Ratis routing, KMS integration, SCM admin RPCs, OFS filesystem operations, OM open-key tables, trash policy behavior, bucket layout rules for FSO/OBS/LEGACY, quota enforcement, and replication-config resolution at bucket/key creation. It is a broad smoke and regression layer across CLI, client, OM, SCM, and filesystem APIs.

Risks: The suite is large, stateful, and timing-sensitive. It mutates global stdout/stderr, relies on HA leader discovery, waits for OM flushes, and shares a cluster across many tests. Several assertions count substrings in JSON output, so output shape changes can break tests. Recursive delete and list-open-files tests can interfere with open-key cleanup behavior, and external changes to `ozone.fs.hsync.enabled` are treated as failures.

Test signals: Signals include exact OM exception result codes, valid JSON arrays, container-count output caps, open-file pagination and continuation tokens, hsync/deleted/overwritten markers in text and JSON, trash move versus skip-trash behavior, quota metadata values and validation errors, EC versus RATIS stream class selection, encryption key persistence, bucket/link metadata flags, recursive delete disappearance of volumes/buckets, and key counts across bucket layouts.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/shell/TestOzoneShellHA.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/shell/TestOzoneShellHAWithFSO.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/shell/TestOzoneShellHAWithFSO.java

Purpose: This subclass reruns the broad `TestOzoneShellHA` command suite with FILE_SYSTEM_OPTIMIZED as the default bucket layout. It verifies that the inherited shell, admin, trash, quota, replication, and delete workflows continue to work when new buckets default to FSO semantics.

Important APIs and types: It uses `OzoneConfiguration`, `OMConfigKeys.OZONE_DEFAULT_BUCKET_LAYOUT`, `OZONE_BUCKET_LAYOUT_FILE_SYSTEM_OPTIMIZED`, `OzoneConfigKeys.OZONE_HBASE_ENHANCEMENTS_ALLOWED`, `OZONE_FS_HSYNC_ENABLED`, and the inherited `startKMS` and `startCluster` hooks from `TestOzoneShellHA`.

Control flow: The overridden `@BeforeAll init` creates a fresh configuration, sets the default bucket layout to FSO, enables HBase-style enhancements and hsync on both server and client-facing keys, starts MiniKMS, and then starts the inherited HA cluster. All actual test methods are inherited unchanged.

State and persistence behavior: The persistent behavior under test is inherited OM/SCM/KMS state, but bucket creation without explicit layout now persists FSO layout metadata by default. This changes key namespace and trash behavior for inherited tests that omit `--layout`, while explicit OBS/LEGACY/FSO cases still set their own layout.

Dependencies and integration points: This class is an integration point between the generic Ozone shell HA suite and the FSO bucket-layout configuration path. It depends on the inherited static cluster lifecycle and KMS setup, so it must run as an isolated subclass instance rather than alongside a started base class.

Risks: Because almost all behavior is inherited, failures need to be interpreted as layout-sensitive regressions in the base shell workflows. Static fields in the parent class make lifecycle isolation important. The class does not add direct assertions that default-created buckets are FSO; it relies on inherited operations succeeding under the configured default.

Test signals: The signal is the full inherited `TestOzoneShellHA` suite passing with FSO default layout and hsync/HBase enhancements enabled.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/shell/TestOzoneShellHAWithFSO.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/shell/TestOzoneShellHAWithFollowerRead.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/shell/TestOzoneShellHAWithFollowerRead.java

Purpose: This subclass runs the shell HA suite with follower-read support enabled and adds targeted tests for leader skip-linearizable-read metrics and follower local-lease consistency. It verifies that shell read commands can exercise OM follower-read paths without breaking inherited shell behavior.

Important APIs and types: It uses `OzoneManagerRatisServerConfig`, `RaftServerConfigKeys.Read.Option.LINEARIZABLE`, `OzoneManager`, `OzoneShell`, and OM metrics such as `getNumLeaderSkipLinearizableRead`, `getNumFollowerReadLocalLeaseSuccess`, and `getNumFollowerReadLocalLeaseFailTime`.

Control flow: `init` configures linearizable reads, leader lease, leader skip optimization, client follower read, hsync, and HBase enhancements before starting the inherited HA cluster. `testAllowLeaderSkipLinearizableRead` repeatedly runs `volume list` with follower read enabled, observes the leader skip metric, disables skip on the leader, repeats reads, and verifies the metric stops increasing. `testAllowFollowerReadLocalLease` selects two non-leader OMs, configures one with valid local lease and one with negative lease time, runs repeated `volume list` commands with `LOCAL_LEASE`, then changes the second follower to unlimited lease/log lag and verifies success.

State and persistence behavior: The tests mutate live OM configurations and restore them in `finally` blocks. Persistent object-store state is not central; runtime state is OM Ratis read configuration and metrics counters accumulated by shell read requests.

Dependencies and integration points: The file integrates shell command execution, OM HA leader/follower roles, Ratis read options, follower-read client configuration, dynamic OM configuration updates, and OM metrics. It depends on a stable leader and at least two followers.

Risks: Metrics-based assertions require enough repeated reads to hit intended servers and can be sensitive to routing changes. Follower selection checks `!om.isLeaderReady()`, so leader transitions during the test could affect which OMs are configured. Config restoration is critical for inherited tests.

Test signals: Signals are a positive leader-skip metric before disabling the feature, unchanged leader-skip metric after disabling, local-lease success on a configured follower, local-lease failure-time increments on the follower with negative lease time, and later local-lease success after allowing infinite lag.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/shell/TestOzoneShellHAWithFollowerRead.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/shell/TestOzoneTenantShell.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/shell/TestOzoneTenantShell.java

Purpose: This HA integration suite validates `ozone tenant` shell behavior with OM multi-tenancy enabled and Ranger calls skipped through the in-memory/dev controller. It covers tenant lifecycle, user access IDs, secrets, tenant admin and delegated-admin permissions, JSON/text output, audit logging, existing-volume takeover, and volume reference-count protection.

Important APIs and types: The file uses `TenantShell`, `OzoneShell`, `MiniOzoneHAClusterImpl`, `OzoneConfiguration`, `OMMultiTenantManagerImpl.OZONE_OM_TENANT_DEV_SKIP_RANGER`, `OZONE_OM_MULTITENANCY_ENABLED`, `OmVolumeArgs`, `UserGroupInformation`, `OMRangerBGSyncService`, `AuthorizerLockImpl`, and picocli `CommandLine`. Helpers inject HA OM config, append `--om-service-id`, capture command writers, validate exact or partial output, and delete backing volumes through `ozone sh`.

Control flow: `init` deletes prior audit logs, enables multi-tenancy, builds a three-OM HA cluster without datanodes, and prepares tenant and ozone shells. Tests create tenants, list them, assign users to multiple tenants, get and set generated or explicit secrets, assign/revoke admin roles, run commands as different UGIs, delete tenants and backing volumes, and check failure paths for duplicate tenants, duplicate access IDs, overlong IDs, non-empty tenants, and unauthorized secret/admin operations.

State and persistence behavior: Tenant creation persists tenant metadata and creates a backing volume. User assignment persists access IDs and S3 secrets. Admin operations persist `isAdmin` and `isDelegatedAdmin` flags. Tenant deletion updates volume reference counts and must precede volume deletion when tenant features reference the volume. The suite also reads `audit.log` to verify success audit entries and triggers Ranger background sync on every OM after a failed delete path.

Dependencies and integration points: It connects CLI command handling to OM multi-tenant manager logic, S3 secret management, audit logging, in-memory Ranger policy/role simulation, HA OM routing, volume metadata, and UGI-based authorization. The `USE_ACTUAL_RANGER` switch documents but disables real Ranger integration.

Risks: The test depends on exact output formatting and ordering for many text and JSON assertions. It shares static shells and cluster state, so cleanup is important. The in-memory Ranger controller differs from real Ranger behavior. HA leadership changes can require syncing all OMs, which the test explicitly handles after a failed delete.

Test signals: Signals include empty and populated tenant lists, exact JSON for verbose commands, access-key export output, expected stderr messages, audit lines containing success, backing volume existence, `volumeRefCount` protection, nonzero exit codes for invalid operations, UGI-specific authorization failures, and successful cleanup leaving no tenants.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/shell/TestOzoneTenantShell.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/shell/TestReconfigShell.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/shell/TestReconfigShell.java

Purpose: This abstract non-HA integration test validates the `ozone admin reconfig` command against datanodes, OM, and SCM. It checks property listing, starting a reconfiguration task, runtime update of OM directory-deleting interval, and the bulk in-service datanode command.

Important APIs and types: It uses `OzoneAdmin`, `ReconfigurationHandler`, `ReconfigurableBase`, `OzoneManager`, `StorageContainerManager`, `HddsDatanodeService`, `DirectoryDeletingService`, `NodeManager`, `HddsProtos.NodeOperationalState`, `GenericTestUtils.PrintStreamCapturer`, and `LogCapturer`.

Control flow: `capture` initializes an admin shell, output capturers, and the OM reconfiguration handler from the shared non-HA cluster. Property tests execute `reconfig --service <service> --address <host:port> properties` and compare output with each service's `getReconfigurableProperties`. The interval test first sets the OM interval to `1m`, starts reconfig, waits for completion logs, and verifies the value from `ozone-site.xml` (`2m`) is applied and reported in status. Datanode tests execute the bulk `--in-service-datanodes` path and temporarily mark one datanode decommissioning to verify filtering.

State and persistence behavior: Runtime configuration state is mutated through `ReconfigurationHandler.reconfigureProperty` and reloaded from XML resources. The datanode out-of-service test mutates SCM node operational state and restores it. No permanent user data is created.

Dependencies and integration points: The class is nested under `NonHATests`, depends on the shared mini cluster, and integrates admin CLI parsing with service RPC endpoints, reconfigurable property registries, OM background service restart logic, SCM node manager state, and test resource `ozone-site.xml`.

Risks: Log-based waits can be timing-sensitive. Output capture resets only stdout explicitly in `stopCapture`, while stderr is captured but not closed there. The directory-deleting interval assertion depends on the test resource value remaining `2m`.

Test signals: Signals include empty stderr, output containing all reconfigurable properties, reconfiguration completion logs, `DirectoryDeletingService` restart log with 120 seconds, status output reporting finished and success for the interval key, and bulk datanode output containing the expected in-service count.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/shell/TestReconfigShell.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/shell/TestReplicationConfigPreference.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/shell/TestReplicationConfigPreference.java

Purpose: This abstract non-HA integration test verifies the precedence order for replication configuration when creating keys through `ozone sh`. It exhaustively combines server defaults, client configuration overrides, bucket replication config, and key CLI replication options.

Important APIs and types: It uses `ReplicationConfig`, `RatisReplicationConfig`, `ECReplicationConfig`, `OzoneShell`, `MiniOzoneCluster`, `OzoneClient`, `OzoneVolume`, `OzoneBucket`, `OzoneKeyDetails`, `TestDataUtil`, `TestHelper.setConfig`, and config keys `OZONE_REPLICATION`, `OZONE_REPLICATION_TYPE`, `OZONE_SERVER_DEFAULT_REPLICATION_KEY`, and `OZONE_SERVER_DEFAULT_REPLICATION_TYPE_KEY`.

Control flow: `init` creates a client and test file, saves and unsets existing replication-related configuration, creates one volume, and stores the volume handle. The parameter source builds all 81 combinations from `null`, RATIS/THREE, and EC 3-2 configs for server, client, bucket, and key levels. Each test updates OM server defaults, creates an `OzoneShell` with optional client overrides and OM address override, creates a bucket with optional replication flags, puts a key with optional replication flags, then validates the actual key config.

State and persistence behavior: The test mutates live OM replication defaults and restores saved config in `@AfterAll`. It persists buckets and keys in a shared volume, with random names per combination. Bucket metadata stores the bucket-level replication config; key metadata stores the resolved final replication config.

Dependencies and integration points: It connects shell CLI flags, client-side config overrides, OM server default replication, bucket metadata, and key creation. It is exposed through `NonHATests.ReplicationConfigPreference`, so it runs in the shared non-HA cluster context.

Risks: The comment labels both client and bucket as precedence step 2, but the implemented order is key CLI, client config, bucket config, server default, then RATIS/THREE fallback. The test creates many objects and relies on random names rather than cleanup. Direct OM config mutation must be restored to avoid contaminating later tests.

Test signals: For every combination, the bucket's stored replication config equals the bucket CLI config, and the key's config matches the expected precedence. Assertion messages include the key, bucket, client, and server replication descriptions to diagnose failures.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/shell/TestReplicationConfigPreference.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/shell/TestSafeModeCheckSubcommandHA.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/shell/TestSafeModeCheckSubcommandHA.java

Purpose: This integration suite validates `ozone admin safemode status` against an HA cluster with three OMs and three SCMs. It verifies default leader selection, direct SCM targeting, all-node reporting, and verbose rule output.

Important APIs and types: It uses `MiniOzoneCluster.newHABuilder`, `MiniOzoneHAClusterImpl`, `StorageContainerManager`, `OzoneAdmin`, `OzoneConfiguration`, and `GenericTestUtils.PrintStreamCapturer`. Helper methods derive the SCM service ID and assert safe-mode rule names and SCM node output patterns.

Control flow: `init` builds an HA cluster with OM service `om-test`, SCM service `scm-test`, three OMs, and three SCMs, then waits for readiness. Each test captures stdout/stderr, copies the cluster configuration into the admin shell as overrides, executes a safemode status variant, and inspects text output. Variants cover no option, `--verbose`, `--scm <host:port>`, `--all`, and combinations with verbose.

State and persistence behavior: The suite does not mutate object-store state. Runtime state comes from SCM safe-mode status and the HA config entries used to map service/node IDs to client addresses. Captured output is closed after each test.

Dependencies and integration points: It integrates admin CLI parsing, SCM HA service discovery, leader lookup, SCM client addresses, and safe-mode rule reporting. It depends on configuration keys `ozone.scm.service.ids` and `ozone.scm.client.address.<service>.<node>`.

Risks: Text output assertions are format-sensitive, especially regexes around `[nodeId]: in/out of safe mode`. The rule list is hard-coded, so changes in safe-mode rule names require test updates. The class has no `@AfterAll` cluster shutdown, which may rely on test framework cleanup or process teardown.

Test signals: Signals include leader node ID in default output, service ID when targeting or listing all SCMs, every SCM node ID with an in/out safe-mode line, and verbose output containing DataNode, RatisContainer, HealthyPipeline, StateMachineReady, OneReplicaPipeline, and ECContainer safe-mode rules.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/shell/TestSafeModeCheckSubcommandHA.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/shell/TestScmAdminHA.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/shell/TestScmAdminHA.java

Purpose: This small abstract HA test verifies that the SCM admin roles command can execute against an SCM endpoint in a shared HA cluster. It is a command-smoke test for `ozone admin --scm <host:port> scm roles`.

Important APIs and types: It uses `OzoneAdmin`, `MiniOzoneCluster`, `StorageContainerManager.getClientRpcAddress`, and the `HATests.TestCase` interface for cluster injection.

Control flow: `init` creates the admin shell and stores the cluster reference from the enclosing HA test harness. `testGetRatisRoles` builds `host:port` from the current storage container manager client RPC address and executes the `scm roles` command with `--scm`.

State and persistence behavior: The test does not create or mutate persistent data. It only reads SCM HA/Ratis role state through the admin command path.

Dependencies and integration points: It is nested in `HATests`, so it shares a three-OM/three-SCM HA cluster. The integration point is admin CLI dispatch to SCM role-reporting RPCs over a specific SCM client endpoint.

Risks: There are no assertions on stdout or role content, so this test only catches command execution failures and uncaught exceptions. If role output regresses semantically but command exit remains successful, this file will not catch it.

Test signals: The sole signal is successful command execution without throwing from `ozoneAdmin.execute`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/shell/TestScmAdminHA.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/shell/TestTransferLeadershipShell.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/shell/TestTransferLeadershipShell.java

Purpose: This HA integration suite validates OM and SCM leadership transfer commands. It tests explicit target transfer with `-n` and randomized transfer with `-r`, and verifies Ratis peer priorities are reset after transfer.

Important APIs and types: The file uses `MiniOzoneHAClusterImpl`, `MiniOzoneCluster.newHABuilder`, `OzoneAdmin`, `OzoneManager`, `StorageContainerManager`, `RatisHelper.NEUTRAL_PRIORITY`, `RaftPeer`, and `ScmConfigKeys.OZONE_SCM_HA_RATIS_SNAPSHOT_THRESHOLD`.

Control flow: `init` configures a low SCM HA Ratis snapshot threshold, builds a three-OM/three-SCM fully active HA cluster, and waits for readiness. `testOmTransfer` finds the OM leader, selects a follower, executes `om transfer -n`, sleeps, verifies the selected OM is leader, checks priorities, then executes `om transfer -r` and expects a different leader. `testScmTransfer` performs the same explicit and random flow for SCM using `scm transfer`.

State and persistence behavior: The tests mutate runtime Ratis leadership and peer priorities. No user object data is created. The snapshot threshold configuration affects SCM Ratis behavior during the cluster lifetime. Cluster shutdown is explicit in `@AfterAll`.

Dependencies and integration points: It integrates admin CLI commands with OM and SCM HA Ratis servers, leader election/transfer APIs, cluster leader-discovery helpers, and Ratis peer group priority metadata.

Risks: `Thread.sleep(3000)` for OM transfer is timing-sensitive; SCM uses `waitForClusterToBeReady`. Random transfer only asserts leader inequality and may be sensitive if transfer fails or leadership changes concurrently. Priority assertions assume all peers are visible from the new leader and should be neutral after command completion.

Test signals: Signals include equality with the requested new leader after explicit transfer, inequality after randomized transfer, non-null SCM leader lookup, and every OM/SCM Ratis peer priority equal to `NEUTRAL_PRIORITY`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/shell/TestTransferLeadershipShell.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/shell/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/shell/package-info.java

Purpose: This package descriptor documents `org.apache.hadoop.ozone.shell` in the integration-test tree as containing test utilities for Ozone shell-related tests.

Important APIs and types: It declares the Java package and carries only package Javadoc. There are no classes, methods, fields, or annotations beyond the package declaration.

Control flow: There is no executable control flow.

State and persistence behavior: There is no state or persistence.

Dependencies and integration points: Its only integration point is Java package documentation for the shell integration-test package. The package contains large CLI integration suites such as Ozone shell, tenant shell, SCM admin, safemode, and leadership-transfer tests.

Risks: The Javadoc is generic and says "Test utils" even though the package also contains full integration tests. This is documentation-only and does not affect runtime behavior.

Test signals: None directly; package-info files are compile/documentation artifacts.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/shell/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/tools/contract/AbstractContractDistCpTest.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/tools/contract/AbstractContractDistCpTest.java

Purpose: This abstract contract suite validates a filesystem implementation's compatibility with Hadoop DistCp in both local-to-remote and remote-to-local directions. It covers deep directory copies, incremental update/delete behavior, missing-file tracking, large files, direct versus rename-based writes, iterator listing mode, single-file copies, update of existing files, zero-byte skip logic, modification-time-based update decisions, and DistCp job ID propagation.

Important APIs and types: It extends `AbstractFSContractTestBase` and uses `FileSystem`, `Path`, `DistCp`, `DistCpOptions`, `Job`, `CopyMapper.Counter`, `SimpleCopyListing`, `CopyListingFileStatus`, `SequenceFile.Reader`, `RemoteIterator`, `LocatedFileStatus`, `ContractTestUtils`, `RemoteIterators`, and `ToolRunner`. Override hooks include `shouldUseDirectWrite`, `getDefaultDistCPSizeKb`, `getDepth`, and `getWidth`.

Control flow: `setup` creates isolated fully qualified local and remote paths per concrete class and test method. Helper methods initialize a fixed input/output tree, create files with deterministic datasets, run DistCp with standard list-status thread settings, and verify contents. Update tests first perform a baseline copy, mutate the source by deleting files/subtrees and adding a new file, then run DistCp with `syncFolder`, `deleteMissing`, or `trackMissing`. File update tests manipulate modification times to force skip versus copy decisions.

State and persistence behavior: The suite writes real files/directories on the local filesystem and the filesystem under contract. It persists DistCp tracking listings as sequence files, modifies file timestamps, and inspects MapReduce counters from completed local jobs. Teardown logs remote IO statistics.

Dependencies and integration points: This file integrates Hadoop filesystem contract tests, DistCp copy listing and mapper logic, local MapReduce execution, object-store-specific direct-write options, and filesystem metadata semantics such as rename, listFiles recursion, timestamps, zero-byte files, and content reads.

Risks: Large-file tests can be expensive for object stores; size is configurable by `scale.test.distcp.file.size.kb`. Modification-time tests use a fixed offset and are sensitive to timestamp precision. The helper calculating `Math.min(modTimeSourceUpd - offset, 0)` can set a very old or zero timestamp, which assumes target filesystem accepts it. Direct-write behavior depends on subclass overrides.

Test signals: Signals include successful completed DistCp jobs, verified copied byte contents, expected destination tree existence/nonexistence, `COPY`, `SKIP`, and `BYTESCOPIED` counter ranges, presence of tracking sequence files, iterator-mode log output, expected recursive file counts, non-null DistCp job ID config, and exact content replacement or skip decisions after timestamp manipulation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/tools/contract/AbstractContractDistCpTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/utils/FaultInjectorImpl.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/utils/FaultInjectorImpl.java

Purpose: This is a test `FaultInjector` implementation that can pause an execution point until the test resumes it and can carry an injected exception and container command type.

Important APIs and types: It extends `org.apache.hadoop.hdds.utils.FaultInjector`, uses `CountDownLatch`, `IOException`, `ContainerProtos.Type`, AssertJ `Fail`, and JUnit assertions. Test-visible methods override `setException`, `getException`, `setType`, and `getType`.

Control flow: Construction calls `init`, which creates a `ready` latch and a `wait` latch. `pause` counts down `ready` to signal that the injected point has been reached, then waits on `wait` until `resume` releases it. `resume` first waits for `ready`, failing the test if interrupted, then counts down `wait`. `reset` reinitializes the latches.

State and persistence behavior: State is entirely in memory: two latches, a `Throwable`, and an optional container proto command type. There is no persistence or filesystem interaction.

Dependencies and integration points: It plugs into production/test code that accepts an HDDS `FaultInjector`, especially container protocol paths where tests need deterministic blocking or metadata about the affected `ContainerProtos.Type`.

Risks: If `pause` is never reached, `resume` blocks indefinitely. If `resume` is never called, the paused worker blocks indefinitely. `setException` stores an exception but `pause` does not throw it, so callers must know how the base `FaultInjector` contract consumes `getException`.

Test signals: Signals are deterministic synchronization between test and worker threads, stored exception identity, stored command type, and reset latch behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/utils/FaultInjectorImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/ozone/test/AclTests.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/ozone/test/AclTests.java

Purpose: This abstract integration harness runs selected OM ACL tests with native Ozone ACL authorization enabled on a shared non-HA mini cluster.

Important APIs and types: It extends `ClusterForTests<MiniOzoneCluster>`, uses `OzoneConfiguration`, `UserGroupInformation`, `OZONE_TEST_AUTHORIZATION_ENABLED`, `OZONE_ACL_ENABLED`, `OZONE_ACL_AUTHORIZER_CLASS_NATIVE`, and `OMConfigKeys.OZONE_OM_ENABLE_FILESYSTEM_PATHS`. Nested classes extend `TestBucketOwner`, `TestOzoneManagerListVolumes`, and `TestRecursiveAclWithFSO`.

Control flow: `newClusterBuilder` sets three datanodes. `createOzoneConfig` logs in the admin user, enables test authorization, native ACLs, and filesystem paths, then returns the configuration. `loginAdmin` resets the login user before each test. Nested test classes override `cluster()` to return the shared cluster from the harness.

State and persistence behavior: The harness persists cluster state created by nested ACL tests and globally changes the Hadoop login user to `om` in group `ozone` before config creation and before each test. ACL metadata and filesystem-path behavior are exercised by nested test suites.

Dependencies and integration points: It integrates Ozone native ACL authorizer configuration with existing OM ACL test classes while sharing one mini cluster. It depends on test security mode to avoid Kerberos while still enforcing ACL checks.

Risks: Global `UserGroupInformation.setLoginUser` can affect tests if not reset by the harness. The nested tests share a cluster, so cleanup and unique names are important. The harness only covers the selected nested ACL suites.

Test signals: Signals are inherited from the nested ACL suites: bucket owner behavior, list-volume authorization, and recursive ACL behavior in FSO mode under native ACL enforcement.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/ozone/test/AclTests.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/ozone/test/ClusterForTests.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/ozone/test/ClusterForTests.java

Purpose: This generic base class manages lifecycle and common configuration for integration tests that share a `MiniOzoneCluster` instance across nested test suites.

Important APIs and types: It uses `MiniOzoneCluster`, `OzoneConfiguration`, `DatanodeRatisServerConfig`, `RatisClientConfig.RaftConfig`, `OzoneClientConfig`, `IOUtils`, JUnit `@BeforeAll`, `@AfterAll`, and `@TestInstance(PER_CLASS)`.

Control flow: `createBaseConfiguration` sets shorter Ratis request/watch timeouts, disables stream buffer flush delay, enables HBase enhancements, hsync, client HBase enhancements, and sets OM lease soft limit to zero. Subclasses can override `createOzoneConfig`, `newClusterBuilder`, `createCluster`, and `onClusterReady`. `startCluster` creates the cluster, waits for readiness, and calls the hook; `shutdownCluster` closes it quietly.

State and persistence behavior: The class owns a single cluster field for the test instance. Persistent state is whatever the mini cluster creates and what nested tests write. Configuration objects are created before cluster startup and applied through builders.

Dependencies and integration points: It is the foundation for `NonHATests`, `HATests`, `FreonTests`, and `AclTests`, and centralizes client/server timeout and hsync settings used by many integration suites.

Risks: Shared cluster state can cause interactions between nested tests. PER_CLASS lifecycle means subclasses must avoid relying on per-test cluster recreation. The default builder uses five datanodes unless subclasses override it.

Test signals: This file has no direct tests; its signal is successful startup, readiness, optional hook execution, and quiet shutdown for subclasses.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/ozone/test/ClusterForTests.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/ozone/test/ConfigAssumptions.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/ozone/test/ConfigAssumptions.java

Purpose: This small interface provides a reusable AssertJ assumption helper for skipping tests based on boolean configuration values.

Important APIs and types: It uses `ConfigurationSource` and `org.assertj.core.api.Assumptions.assumeThat`.

Control flow: The static `assumeConfig` method reads `conf.getBoolean(key, defaultValue)` and applies an assumption that the actual value equals the expected value. If not, AssertJ marks the test as skipped/aborted rather than failed.

State and persistence behavior: It has no state and does not mutate configuration.

Dependencies and integration points: Test classes can call it to gate scenarios that require optional features to be enabled or disabled. It relies on the configuration abstraction used by Ozone and HDDS.

Risks: It handles only boolean keys. Misusing the default value can hide a misconfiguration by making missing keys look like expected values.

Test signals: The signal is an assumption pass or test skip based on the resolved boolean value.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/ozone/test/ConfigAssumptions.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/ozone/test/FreonTests.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/ozone/test/FreonTests.java

Purpose: This abstract harness groups data-writing Freon generator tests so they can run against one shared non-HA mini cluster with smaller test-oriented client block/chunk settings.

Important APIs and types: It extends `ClusterForTests<MiniOzoneCluster>`, uses `ClientConfigForTesting`, `StorageUnit.MB`, and nested test classes from `org.apache.hadoop.ozone.freon`: `TestDNRPCLoadGenerator`, `TestHadoopDirTreeGenerator`, `TestHadoopNestedDirGenerator`, `TestHsyncGenerator`, `TestOmBucketReadWriteFileOps`, `TestOmBucketReadWriteKeyOps`, and `TestRandomKeyGenerator`.

Control flow: `createOzoneConfig` starts from the base cluster config and applies a 4 MB chunk size and 256 MB block size through `ClientConfigForTesting`. Each nested Freon test class overrides `cluster()` to return the shared cluster.

State and persistence behavior: Nested generator tests create substantial volumes, buckets, directories, keys, and hsync state in the mini cluster. The harness itself only alters client config and provides shared cluster access.

Dependencies and integration points: It connects Freon load/generator tests to the common cluster lifecycle. Grouping these tests separately from `NonHATests` keeps heavier data-writing tests out of the general non-HA suite.

Risks: Shared cluster state and heavier IO can make runtime and cleanup more expensive. Configuration values are tuned for tests, so performance or layout behavior may not match production defaults.

Test signals: Signals come from nested Freon tests: successful DN RPC load generation, Hadoop directory tree generation, nested directory creation, hsync generation, OM bucket read/write key and file operations, and random key generation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/ozone/test/FreonTests.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/ozone/test/HATests.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/ozone/test/HATests.java

Purpose: This abstract harness groups HA integration tests under one shared three-OM/three-SCM `MiniOzoneHAClusterImpl`.

Important APIs and types: It extends `ClusterForTests<MiniOzoneHAClusterImpl>`, uses `MiniOzoneCluster.newHABuilder`, random UUID-based OM/SCM service IDs, and nested suites including `TestOzoneFsHAURLs`, `TestStorageContainerManagerHAWithAllRunning`, `TestScmApplyTransactionFailure`, `TestGetClusterTreeInformation`, `TestDatanodeQueueMetrics`, and `TestScmAdminHA`.

Control flow: `newClusterBuilder` creates an HA builder from the common config, assigns random service IDs, and configures three OMs and three SCMs. The `TestCase` interface defines a `cluster()` method for nested HA suites. Each nested class extends an existing test and overrides `cluster()` to use the shared harness cluster.

State and persistence behavior: The harness owns shared HA cluster state. Nested tests exercise OM/SCM HA metadata, Ratis groups, datanode queues, cluster tree information, and filesystem HA URLs. Random service IDs prevent cross-run naming conflicts.

Dependencies and integration points: It links common cluster lifecycle to HA-specific tests across filesystem, SCM, OM, metrics, and shell admin areas. It also includes `TestScmAdminHA` from this subset as a nested command test.

Risks: HA tests can influence leadership, node state, and metrics for later nested tests. Shared cluster execution improves performance but makes ordering and cleanup more important. Random IDs improve isolation but can make logs less deterministic.

Test signals: Signals come from nested HA suites: URL resolution, SCM HA behavior, transaction failure handling, cluster-tree information, datanode queue metrics, and SCM admin roles command execution.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/ozone/test/HATests.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/ozone/test/NonHATests.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/ozone/test/NonHATests.java

Purpose: This abstract harness groups many non-HA integration suites so they run against a single shared `MiniOzoneCluster`. It is the main non-HA aggregation point for filesystem, SCM, pipeline, client RPC, OM, reconfiguration, shell/debug, and replication preference tests.

Important APIs and types: It extends `ClusterForTests<MiniOzoneCluster>` and defines a `TestCase` interface. Nested classes adapt test suites such as `TestOzoneClientMultipartUploadWithFSO`, Ozone FS tests, SCM container/pipeline/MXBean/metrics tests, `TestReplicationConfigPreference`, client RPC tests, CPU metrics, lease recovery, OM list/status/object-store/block-versioning tests, datanode/OM/SCM reconfiguration tests, `TestOzoneDebugShell`, `TestReconfigShell`, and `TestOzoneDebugReplicasVerify`.

Control flow: The harness relies on inherited cluster startup/shutdown. Each nested class extends an existing test class and overrides `cluster()` to return `getCluster()`. There are no test methods directly in this file; JUnit discovers and runs nested suites in the same cluster context.

State and persistence behavior: The shared cluster persists all data created by nested suites during the class lifecycle: keys, buckets, containers, pipelines, multipart uploads, metrics, reconfiguration state, and debug-shell artifacts. State isolation depends on nested tests using unique names and cleanup.

Dependencies and integration points: This file stitches together broad subsystem coverage under one mini cluster. It is a key integration point for tests that implement the local `NonHATests.TestCase` contract, including `TestReconfigShell` and `TestReplicationConfigPreference` in this subset.

Risks: The breadth of nested tests raises cross-test contamination risk. Reconfiguration and debug tests can mutate runtime settings visible to later tests. Failures may be harder to localize because the harness only provides cluster injection and shared lifecycle.

Test signals: The file's signal is successful execution of all nested suites against the shared non-HA cluster, covering FS behavior, SCM/container/pipeline behavior, client RPC behavior, OM metadata behavior, reconfiguration, debug shell, and replication-config precedence.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/ozone/test/NonHATests.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/ozone/test/TestFreon.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/ozone/test/TestFreon.java

Purpose: This concrete test class instantiates the `FreonTests` harness with a default non-HA mini cluster.

Important APIs and types: It extends `FreonTests`, uses `MiniOzoneCluster`, and JUnit `@TestInstance(PER_CLASS)`.

Control flow: `createCluster` calls `newClusterBuilder().build()`. Cluster configuration and nested Freon test discovery come from the parent class.

State and persistence behavior: Persistent state is generated by nested Freon tests inherited from `FreonTests`. This class itself only chooses the standard cluster builder.

Dependencies and integration points: It is the runnable entry point for the Freon grouped integration suite. It binds the abstract harness to a real non-HA mini cluster.

Risks: Runtime and IO volume are inherited from Freon tests. There are no local assertions or cleanup beyond inherited lifecycle.

Test signals: Signals are inherited Freon generator test results on a built mini cluster.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/ozone/test/TestFreon.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/ozone/test/TestOzoneIntegrationHA.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/ozone/test/TestOzoneIntegrationHA.java

Purpose: This concrete class instantiates the `HATests` harness as a runnable HA integration suite.

Important APIs and types: It extends `HATests` and returns `MiniOzoneHAClusterImpl` from `createCluster`.

Control flow: `createCluster` simply calls `newClusterBuilder().build()`. The HA builder is configured by the parent with random OM/SCM service IDs and three OMs/SCMs.

State and persistence behavior: Persistent and runtime state comes from the shared HA cluster and nested suites inherited from `HATests`. This class does not add state of its own.

Dependencies and integration points: It is the executable bridge between the abstract HA grouping harness and the JUnit runner.

Risks: All risks are inherited from `HATests`: shared HA state, leadership changes, metrics state, and cleanup interactions among nested tests.

Test signals: Signals are inherited nested HA suite outcomes after the cluster builds and reaches readiness.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/ozone/test/TestOzoneIntegrationHA.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/ozone/test/TestOzoneIntegrationNonHA.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/ozone/test/TestOzoneIntegrationNonHA.java

Purpose: This concrete class instantiates the broad `NonHATests` harness as a runnable non-HA integration suite.

Important APIs and types: It extends `NonHATests`, returns `MiniOzoneCluster`, and uses JUnit `@TestInstance(PER_CLASS)`.

Control flow: `createCluster` calls the inherited `newClusterBuilder().build()`, using the common base configuration and default five-datanode non-HA cluster unless parent hooks change it.

State and persistence behavior: Runtime and persistent state are created by the nested non-HA suites inherited from `NonHATests`. This class has no additional state.

Dependencies and integration points: It is the runnable entry point for the aggregated non-HA integration suite.

Risks: The class inherits the large shared-cluster contamination surface of `NonHATests`. There are no local assertions to narrow failures.

Test signals: Signals are successful execution of all nested non-HA suites on the built mini cluster.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/ozone/test/TestOzoneIntegrationNonHA.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/ozone/test/TestOzoneNonHAWithNativeACL.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/ozone/test/TestOzoneNonHAWithNativeACL.java

Purpose: This concrete class instantiates the `AclTests` harness as a runnable non-HA native-ACL integration suite.

Important APIs and types: It extends `AclTests`, returns `MiniOzoneCluster`, and uses JUnit `@TestInstance(PER_CLASS)`.

Control flow: `createCluster` builds the cluster from the ACL-configured builder inherited from `AclTests`, which enables native ACLs, test authorization, filesystem paths, and three datanodes.

State and persistence behavior: Persistent state comes from nested ACL tests and the ACL-enabled OM metadata they create. This class adds no state of its own.

Dependencies and integration points: It is the executable entry point for native ACL tests in a non-HA mini cluster.

Risks: It inherits global UGI mutation and shared cluster-state concerns from `AclTests`.

Test signals: Signals are inherited ACL test results for bucket ownership, volume listing, and recursive FSO ACL behavior under native ACL authorization.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/ozone/test/TestOzoneNonHAWithNativeACL.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/ozone/test/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/ozone/test/package-info.java

Purpose: This package descriptor documents `org.apache.ozone.test` as containing test cluster definitions.

Important APIs and types: It declares only the package and package-level Javadoc.

Control flow: There is no executable control flow.

State and persistence behavior: There is no state or persistence.

Dependencies and integration points: It documents the package that contains shared integration-test harnesses such as `ClusterForTests`, `NonHATests`, `HATests`, `FreonTests`, and ACL-specific cluster wrappers.

Risks: Documentation-only; the summary is accurate but brief.

Test signals: None directly.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/ozone/test/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/ratis/statemachine/impl/StatemachineImplTestUtil.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/ratis/statemachine/impl/StatemachineImplTestUtil.java

Purpose: This interface exposes a package-local test helper for finding the latest snapshot in a Ratis `SimpleStateMachineStorage`.

Important APIs and types: It uses `SimpleStateMachineStorage`, `SingleFileSnapshotInfo`, `File`, and `IOException`.

Control flow: The static `findLatestSnapshot` method retrieves the state machine directory from storage and delegates to `SimpleStateMachineStorage.findLatestSnapshot(dir.toPath())`.

State and persistence behavior: It reads filesystem state from the Ratis state machine directory to locate snapshot files. It does not mutate storage.

Dependencies and integration points: The interface lives in `org.apache.ratis.statemachine.impl`, matching the package of Ratis implementation classes so tests can access package-scoped functionality where needed. It is an integration helper for snapshot-related tests.

Risks: It depends on Ratis snapshot filename/layout semantics. If Ratis changes `SimpleStateMachineStorage.findLatestSnapshot`, callers inherit the new behavior.

Test signals: Signals are the returned `SingleFileSnapshotInfo` for the newest snapshot or any propagated `IOException` from storage scanning.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/ratis/statemachine/impl/StatemachineImplTestUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/resources/contract/ozone.xml -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/resources/contract/ozone.xml

Purpose: This Hadoop filesystem contract file declares Ozone/OFS object-store semantics for contract tests.

Important APIs and types: It is an XML `<configuration>` resource consumed by Hadoop contract tests. Keys include `fs.contract.test.root-tests-enabled`, random seek count, blobstore classification, delayed create visibility, case sensitivity, rename behavior, append/concat/block-locality support, getFileStatus/seek/unbuffer support, strict exceptions, permissions support, hsync, and hflush.

Control flow: There is no code flow. Test harnesses load the XML as configuration and use the properties to enable, skip, or adjust contract tests.

State and persistence behavior: The file is static test configuration. It does not persist runtime state.

Dependencies and integration points: It integrates Ozone with Hadoop FS contract suites and tells tests which filesystem features should or should not be expected from an object store. It directly affects assertions in contract tests such as seek, rename, append, delete, and sync tests.

Risks: Incorrect flags can either hide real regressions by skipping/weakening tests or cause false failures by claiming unsupported semantics. Rename and create-visibility flags are especially important for object-store behavior.

Test signals: Contract tests use these properties as expected behavior signals: Ozone is a blobstore, case-sensitive, create visibility may be delayed, append/atomic directory delete/atomic rename/block locality/concat/Unix permissions are unsupported, while getFileStatus, seek, seek-on-closed, strict exceptions, unbuffer, hsync, and hflush are supported.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/resources/contract/ozone.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/resources/core-site.xml -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/resources/core-site.xml

Purpose: This test `core-site.xml` provides proxy-user permissions for integration tests.

Important APIs and types: It is a Hadoop XML configuration resource with `hadoop.proxyuser.proxyuser.users`, `hadoop.proxyuser.proxyuser.groups`, and `hadoop.proxyuser.proxyuser.hosts`, all set to wildcard values.

Control flow: There is no executable code. Hadoop configuration loading makes these keys available to tests and services.

State and persistence behavior: Static configuration only; it does not persist runtime state.

Dependencies and integration points: It supports tests involving proxy user impersonation by allowing the test user named `proxyuser` to proxy any user, group, and host. It is loaded alongside other site XML resources in the integration-test classpath.

Risks: Wildcard proxy settings are appropriate for test isolation but insecure for production. Tests depending on proxy-user behavior may fail if this file is not on the classpath.

Test signals: The signal is successful authorization of proxy-user scenarios that require permissive users, groups, and hosts.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/resources/core-site.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/resources/hdfs-site.xml -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/resources/hdfs-site.xml

Purpose: This placeholder `hdfs-site.xml` exists on the integration-test classpath for Hadoop configuration compatibility.

Important APIs and types: It is an XML `<configuration>` with no properties.

Control flow: There is no executable flow.

State and persistence behavior: It is static and empty; no runtime state is persisted.

Dependencies and integration points: Some Hadoop components expect `hdfs-site.xml` to be present even when tests are not configuring HDFS-specific settings. This file supplies an empty override layer.

Risks: Because it contains no properties, any test requiring HDFS-specific configuration must set it elsewhere. Accidental assumptions that this file configures HDFS behavior would be incorrect.

Test signals: None directly, other than successful resource loading without HDFS overrides.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/resources/hdfs-site.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/resources/mapred-site.xml -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/resources/mapred-site.xml

Purpose: This placeholder `mapred-site.xml` exists on the integration-test classpath for MapReduce configuration compatibility.

Important APIs and types: It is an XML `<configuration>` with no properties.

Control flow: There is no executable flow.

State and persistence behavior: Static empty configuration only.

Dependencies and integration points: Hadoop MapReduce and DistCp tests may load `mapred-site.xml`; this file supplies a no-op resource so defaults or programmatic settings control behavior. For example, `AbstractContractDistCpTest` sets local job tracker configuration programmatically rather than through this file.

Risks: Tests requiring MapReduce-specific overrides must not assume this file provides them.

Test signals: None directly, other than resource availability and absence of mapred overrides.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/resources/mapred-site.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/resources/ozone-site.xml -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/resources/ozone-site.xml

Purpose: This integration-test `ozone-site.xml` defines common Ozone/HDDS settings used by mini-cluster and shell tests.

Important APIs and types: Configuration keys include mock datanode disk-usage factory, OM transport class, disabled S3 gRPC server, datanode write chunk threads, SCM/OM handler counts, datastream settings, heartbeat intervals, SCM pipeline limit, close-container wait duration, snapshot diff wait time, Ratis log appender byte limits, SCM chunk/block sizes, client stream/datastream buffers, readonly/admin users, and `ozone.directory.deleting.service.interval=2m`.

Control flow: No executable flow. Ozone and Hadoop configuration loaders merge these properties into test configurations. `TestReconfigShell` specifically relies on the directory-deleting interval value when reloading configuration.

State and persistence behavior: Static configuration only; it shapes runtime cluster behavior but does not persist dynamic state itself.

Dependencies and integration points: It integrates with mini-cluster startup, OM/SCM/datanode thread sizing, datastream tests, admin-user authorization tests, snapshot diff tests, and reconfiguration tests. Smaller block/chunk/buffer values make integration tests faster and lower resource consumption.

Risks: The property name for `hdds.container.ratis.log.appender.queue.byte-limit` includes a line break before `</name>`, which may be intentional tolerance or an XML formatting hazard. Changing `ozone.directory.deleting.service.interval` breaks `TestReconfigShell` expectations. Admin user settings are test-only and not production-safe.

Test signals: Signals are indirect: clusters start with mock DU, expected handler/heartbeat/buffer behavior, reconfiguration reloads `2m`, and admin-related tests see `admin` as configured administrator/readonly administrator.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/resources/ozone-site.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/resources/ssl/generate.sh -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/resources/ssl/generate.sh

Purpose: This helper script generates local SSL/TLS test materials: a CA key/certificate, server key/certificate/PKCS8 private key, and client key/certificate/PKCS8 private key for mutual TLS scenarios.

Important APIs and types: It is a shell script invoking `openssl genrsa`, `openssl req`, `openssl x509`, `openssl rsa`, and `openssl pkcs8`. Variables `SERVER_CN` and `CLIENT_CN` default to `localhost`. Generated files include `ca.key`, `ca.crt`, `server.key`, `server.csr`, `server.crt`, `server.pem`, `client.key`, `client.csr`, `client.crt`, and `client.pem`.

Control flow: The script creates a passphrase-protected CA key, self-signed CA cert, passphrase-protected server key, server CSR, CA-signed server certificate, unencrypted server key, passphrase-protected client key, client CSR, CA-signed client certificate, unencrypted client key, and PKCS8 PEM private keys.

State and persistence behavior: It writes key, CSR, certificate, and PEM files into the current working directory and overwrites existing files with the same names. Certificates are valid for 365 days and use serial `01` for both server and client certs.

Dependencies and integration points: It supports SSL test resources consumed by Ozone/HDDS tests that need certificate chains, trust cert collections, server private keys, and optional mutual-TLS client credentials.

Risks: Hard-coded passphrase `1111`, duplicate serial numbers, localhost CN, no subjectAltName, and overwriting behavior make this suitable only for tests. Modern TLS clients may require SANs instead of CN-only certificates.

Test signals: The expected signal is successful generation of all certificate and key artifacts with OpenSSL and their later loadability by SSL-enabled tests.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/resources/ssl/generate.sh -->
