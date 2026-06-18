# subset-b-007518 Research

Grouped research for HDFS test sources. Each section preserves the source path in its title and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/TestRefreshCallQueue.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/TestRefreshCallQueue.java

Purpose: Validates live NameNode IPC call queue refresh behavior and FairCallQueue queue-size reconfiguration in a MiniDFSCluster.
Important APIs/types/functions: `TestRefreshCallQueue`, `setUp(Class<?>)`, `MockCallQueue`, `canPutInMockQueue()`, `testRefresh()`, and `testRefreshCallQueueWithFairCallQueue()`.
Control flow: Setup picks a random NameNode RPC port, installs `ipc.<port>.callqueue.impl`, and starts the cluster. The first test verifies the mock queue is active, runs `DFSAdmin -refreshCallQueue`, then verifies RPC puts stop hitting the mock. The second starts with `FairCallQueue`, disables mini-cluster metrics mode to expose duplicate registration failures, calls `refreshCallQueue(config)`, and checks max queue size changes.
State and persistence behavior: The test mutates static counters for queue construction and puts, cluster lifecycle state, the default HDFS URI, and `DefaultMetricsSystem` mini-cluster mode. Persistence is limited to MiniDFSCluster metadata and metrics registrations during the test.
Dependencies and integration points: Integrates NameNode RPC server, `DFSAdmin`, `FileSystem.exists()`, `CommonConfigurationKeys` queue sizing, `FairCallQueue`, and metrics lifecycle.
Risks and edge cases: Random port selection can collide and has only five retries. Metrics mode restoration is crucial after failures. Static counters make parallel execution unsafe. The test assumes refresh swaps queues without dropping RPC availability.
Test signals: Successful signals are admin exit code 0, no new `MockCallQueue` construction after refresh, mock put counts no longer increasing, no duplicate `DecayRpcSchedulerMetrics2` source, and updated server max queue size.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/TestRefreshCallQueue.java -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/cli/CLITestCmdDFS.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/cli/CLITestCmdDFS.java

Purpose: Adds DFSAdmin support to the generic XML CLI test command abstraction.
Important APIs/types/functions: `CLITestCmdDFS` extends `CLITestCmd`; `getExecutor(String, Configuration)` recognizes `CLICommandDFSAdmin` and returns `FSCmdExecutor` with a `DFSAdmin` tool.
Control flow: The parser-created command keeps its raw string and command type. At execution time, matching DFSAdmin types are routed to `DFSAdmin`; all other command types fall back to the base command executor.
State and persistence behavior: No durable state; it stores command text/type in the inherited `CLITestCmd` fields and instantiates a fresh `DFSAdmin` per execution.
Dependencies and integration points: Integrated by `CLITestHelperDFS` and HDFS CLI tests that parse `<dfs-admin-command>` elements from XML.
Risks and edge cases: If the XML parser assigns the wrong command type, DFSAdmin commands fall through to generic execution. The executor depends on the caller passing the correct NameNode tag and configuration.
Test signals: Covered indirectly by HDFS CLI XML suites that include DFSAdmin commands and expect output/exit-code matches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/cli/CLITestCmdDFS.java -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/cli/CLITestCmdErasureCoding.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/cli/CLITestCmdErasureCoding.java

Purpose: Adds erasure-coding admin command execution to the XML CLI test framework.
Important APIs/types/functions: `CLITestCmdErasureCoding` extends `CLITestCmd`; `getExecutor()` recognizes `CLICommandErasureCodingCli` and returns `ErasureCodingCliCmdExecutor` wrapping `ECAdmin`.
Control flow: The XML parser supplies an erasure-coding command type, and execution dispatches to `ECAdmin` through a command executor. Non-EC command types use base behavior.
State and persistence behavior: No persistence. Runtime state is the inherited command string/type and the per-call `ECAdmin` instance.
Dependencies and integration points: Used by `TestErasureCodingCLI` for `<ec-admin-command>` XML entries and depends on `org.apache.hadoop.hdfs.tools.ECAdmin`.
Risks and edge cases: Mistyped command type or missing EC policies in the cluster setup will surface as generic executor use or admin failures. The command string placeholder expansion happens outside this class.
Test signals: Signals are XML CLI expectations around `ECAdmin` commands, policy enablement, and exit-code/output validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/cli/CLITestCmdErasureCoding.java -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/cli/CLITestHelperDFS.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/cli/CLITestHelperDFS.java

Purpose: Specializes the generic CLI XML parser so HDFS tests can include DFSAdmin commands.
Important APIs/types/functions: `CLITestHelperDFS` extends `CLITestHelper`; `getConfigParser()` returns `TestConfigFileParserDFS`; nested `endElement()` handles `dfs-admin-command`.
Control flow: During SAX parsing, closing a `dfs-admin-command` tag appends a `CLITestCmdDFS` to either test or cleanup command lists. Other tags defer to the base parser.
State and persistence behavior: Maintains parser-local `charString` and inherited command lists; no durable state.
Dependencies and integration points: Provides the common base for ACL, delete, HDFS, XAttr, and crypto CLI tests that need both normal shell commands and DFSAdmin commands.
Risks and edge cases: Parser behavior depends on exact XML tag spelling and on inherited list selection. Unknown tags must continue flowing to the superclass.
Test signals: Test signal is successful execution of XML files containing mixed DFSAdmin and base CLI command tags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/cli/CLITestHelperDFS.java -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/cli/TestAclCLI.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/cli/TestAclCLI.java

Purpose: Runs the ACL CLI XML suite against an HDFS cluster with ACLs enabled and POSIX ACL inheritance disabled.
Important APIs/types/functions: `TestAclCLI` extends `CLITestHelperDFS`; key methods are `initConf()`, `setUp()`, `tearDown()`, `getTestFile()`, `expandCommand()`, `execute()`, and `testAll()`.
Control flow: Setup initializes CLI helper state, enables NameNode ACLs, starts a one-Datanode cluster, captures NameNode URI and user name, then XML commands from `testAclCLI.xml` are expanded and executed. Teardown closes the FS and cluster.
State and persistence behavior: Cluster namespace and ACL metadata are transient per test. It stores `MiniDFSCluster`, `FileSystem`, `namenode`, and `username` fields for command expansion.
Dependencies and integration points: Integrates NameNode ACL feature flags, the common CLI XML harness, `FileSystem`, and HDFS command executors.
Risks and edge cases: Output expectations depend on username, line separator, and the disabled inheritance policy. Resource cleanup ordering matters because superclass teardown may inspect command results.
Test signals: Signals are `testAll()` XML cases for set/get/remove ACL commands, placeholder expansion, and exit-code/output comparisons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/cli/TestAclCLI.java -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/cli/TestAclCLIWithPosixAclInheritance.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/cli/TestAclCLIWithPosixAclInheritance.java

Purpose: Repeats the ACL CLI suite with POSIX ACL inheritance enabled.
Important APIs/types/functions: `TestAclCLIWithPosixAclInheritance` extends `TestAclCLI`, overrides `initConf()` and `getTestFile()`, and exposes `testAll()`.
Control flow: It calls the parent ACL configuration, flips `DFS_NAMENODE_POSIX_ACL_INHERITANCE_ENABLED_KEY` to true, and runs `testAclCLIWithPosixAclInheritance.xml` through the inherited cluster and command execution flow.
State and persistence behavior: Uses the parent cluster/FS fields; persistent effects are only transient ACL namespace changes inside MiniDFSCluster.
Dependencies and integration points: Depends on the parent ACL CLI harness and the POSIX ACL inheritance NameNode option.
Risks and edge cases: Regression risk is that parent setup changes could accidentally override the inheritance flag. XML expectations must track inheritance semantics exactly.
Test signals: Signals are XML expectations that default ACL inheritance follows POSIX rules under the enabled flag.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/cli/TestAclCLIWithPosixAclInheritance.java -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/cli/TestCacheAdminCLI.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/cli/TestCacheAdminCLI.java

Purpose: Runs cache-admin CLI XML tests against a secured-policy HDFS cluster.
Important APIs/types/functions: `TestCacheAdminCLI`, nested `TestConfigFileParserCacheAdmin`, nested `CLITestCmdCacheAdmin`, `setUp()`, `tearDown()`, `execute()`, and `testAll()`.
Control flow: Setup configures `HDFSPolicyProvider`, forces replication 1, starts three Datanodes, captures user and NameNode, and asserts the FS is `DistributedFileSystem`. The parser turns `cache-admin-command` XML tags into typed commands that execute via `CacheAdminCmdExecutor`.
State and persistence behavior: State includes cluster namespace/cache directives and pools created by XML cases; teardown closes FS, shuts down the cluster, sleeps briefly, then delegates to base cleanup.
Dependencies and integration points: Integrates `CacheAdmin`, `CacheAdminCmdExecutor`, HDFS cache-management RPCs, service authorization policy, and the generic CLI test framework.
Risks and edge cases: The empty tag passed to `getExecutor()` means command text must carry all required NameNode replacement data. Sleep-based teardown can mask asynchronous cache-manager cleanup races.
Test signals: Signals are XML command exit codes and outputs for cache pool/directive management with HDFS replication normalized to 1.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/cli/TestCacheAdminCLI.java -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/cli/TestCryptoAdminCLI.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/cli/TestCryptoAdminCLI.java

Purpose: Runs crypto-admin CLI XML tests with an HDFS encryption key provider configured.
Important APIs/types/functions: `TestCryptoAdminCLI`, `createAKey()`, nested parser/command classes, `expandCommand()`, `execute()`, and `testAll()`.
Control flow: Setup configures service authorization, replication, trash interval, creates a temporary JavaKeyStoreProvider path, starts a one-Datanode cluster, creates `mykey` via the NameNode namesystem provider, then runs XML crypto-admin and DFS commands.
State and persistence behavior: State includes the temporary JKS file, encryption keys, cluster namespace, and per-test FS/cluster fields. Teardown closes FS and cluster but does not explicitly delete the tmpDir field.
Dependencies and integration points: Integrates `CryptoAdmin`, `CryptoAdminCmdExecutor`, `JavaKeyStoreProvider`, HDFS encryption-zone support, and the DFS CLI parser fallback.
Risks and edge cases: Key provider path formatting and provider flush are critical. The static `tmpDir` can be overwritten across parallel runs. XML output depends on trash and line-separator behavior.
Test signals: Signals are XML expectations for key/zone crypto admin flows, plus successful precreation of `mykey`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/cli/TestCryptoAdminCLI.java -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/cli/TestDeleteCLI.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/cli/TestDeleteCLI.java

Purpose: Runs delete CLI XML tests with HDFS safe-delete thresholds.
Important APIs/types/functions: `TestDeleteCLI` extends `CLITestHelperDFS`; key methods are `setUp()`, `tearDown()`, `getTestFile()`, `expandCommand()`, `execute()`, and `testAll()`.
Control flow: Setup fixes replication to 1, sets `HADOOP_SHELL_SAFELY_DELETE_LIMIT_NUM_FILES` to 5, starts a one-Datanode cluster, and executes expanded commands from `testDeleteConf.xml`.
State and persistence behavior: State is transient namespace content created and removed by XML commands. The NameNode URI is captured for placeholder expansion.
Dependencies and integration points: Depends on shell/FS delete command behavior, HDFS cluster semantics, and the DFS CLI helper parser.
Risks and edge cases: Safe-delete behavior is threshold-sensitive. The two-second teardown sleep suggests prior cleanup races. Output can vary if replication or trash defaults change.
Test signals: Signals are XML cases for delete, recursive delete, and safe-delete prompting/limits against HDFS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/cli/TestDeleteCLI.java -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/cli/TestErasureCodingCLI.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/cli/TestErasureCodingCLI.java

Purpose: Runs erasure-coding admin CLI XML tests against a cluster with selected EC policies enabled.
Important APIs/types/functions: `TestErasureCodingCLI`, nested `TestErasureCodingAdmin`, `setUp()`, `tearDown()`, `expandCommand()`, `execute()`, and `testAll()`.
Control flow: Setup starts three Datanodes, captures NameNode/user, obtains `DistributedFileSystem`, and enables RS-6-3, RS-3-2, and XOR policies before parsing `ec-admin-command` entries from XML.
State and persistence behavior: Cluster namespace and EC policy enablement are transient. The test is bounded by a 300 second timeout.
Dependencies and integration points: Integrates `ECAdmin`, `CLITestCmdErasureCoding`, HDFS erasure-coding policy APIs, and XML output validation.
Risks and edge cases: Only three Datanodes are started, so commands involving high-data/parity RS policies may validate metadata but not necessarily full placement. Timeout protects slow EC CLI operations.
Test signals: Signals are XML expectations for list/enable/disable/set/get/unset EC policy operations and error output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/cli/TestErasureCodingCLI.java -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/cli/TestHDFSCLI.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/cli/TestHDFSCLI.java

Purpose: Runs the broad HDFS CLI XML suite, including DFSAdmin topology behavior.
Important APIs/types/functions: `TestHDFSCLI` extends `CLITestHelperDFS`; setup builds an eight-Datanode rack/host topology, expands NameNode placeholders, and runs `testHDFSConf.xml`.
Control flow: Setup configures service authorization and replication 1, creates racks/hosts arrays, starts the cluster, validates `DistributedFileSystem`, then `testAll()` drives XML commands.
State and persistence behavior: Transient cluster topology, namespace, and command output state. Fields track cluster, FS, NameNode URI, and username.
Dependencies and integration points: Integrates DFS shell commands, DFSAdmin commands, HDFS policy provider, MiniDFSCluster rack awareness, and XML CLI comparison logic.
Risks and edge cases: Marked slow. Output from topology and admin commands depends on rack/host ordering and replication defaults. Teardown sleep implies asynchronous cleanup sensitivity.
Test signals: Signals are XML expected outputs for HDFS shell/admin commands, including topology printing and NameNode URI expansion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/cli/TestHDFSCLI.java -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/cli/TestXAttrCLI.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/cli/TestXAttrCLI.java

Purpose: Runs XAttr CLI XML tests with NameNode extended attributes enabled.
Important APIs/types/functions: `TestXAttrCLI` extends `CLITestHelperDFS`; methods configure xattrs, expand `NAMENODE` and `#LF#`, execute commands, and call `testAll()`.
Control flow: Setup enables `DFS_NAMENODE_XATTRS_ENABLED_KEY`, installs the HDFS policy provider, forces replication 1, starts one Datanode, and executes XML commands from `testXAttrConf.xml`.
State and persistence behavior: Namespace xattrs are transient. Cluster/FS/NameNode/user fields support command expansion and execution.
Dependencies and integration points: Integrates HDFS xattr feature flags, FS shell xattr commands, service authorization, and the CLI helper.
Risks and edge cases: Output is sensitive to line separators and xattr feature enablement. XML cleanup must remove xattrs/files to avoid cross-case leakage.
Test signals: Signals are XML cases for set/get/remove/list xattrs and expected errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/cli/TestXAttrCLI.java -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/cli/util/CLICommandCacheAdmin.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/cli/util/CLICommandCacheAdmin.java

Purpose: Marker type for cache-admin CLI commands in the XML harness.
Important APIs/types/functions: `CLICommandCacheAdmin` implements `CLICommandTypes` and has no methods or fields.
Control flow: Parser code instantiates this marker when it sees `cache-admin-command`; executor dispatch uses `instanceof`.
State and persistence behavior: No state or persistence.
Dependencies and integration points: Consumed by `TestCacheAdminCLI.CLITestCmdCacheAdmin`.
Risks and edge cases: Its behavior relies entirely on type identity, so renaming or replacing it breaks dispatch.
Test signals: Indirectly covered by cache-admin XML command execution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/cli/util/CLICommandCacheAdmin.java -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/cli/util/CLICommandCryptoAdmin.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/cli/util/CLICommandCryptoAdmin.java

Purpose: Marker type for crypto-admin CLI commands in the XML harness.
Important APIs/types/functions: `CLICommandCryptoAdmin` implements `CLICommandTypes` and has no fields or behavior.
Control flow: Crypto parser creates this type; command dispatch recognizes it and wraps `CryptoAdmin`.
State and persistence behavior: No state or persistence.
Dependencies and integration points: Used by `TestCryptoAdminCLI` and `CryptoAdminCmdExecutor`.
Risks and edge cases: Pure marker classes are easy to miss in refactors but are dispatch-critical.
Test signals: Indirect coverage from crypto-admin XML tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/cli/util/CLICommandCryptoAdmin.java -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/cli/util/CLICommandDFSAdmin.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/cli/util/CLICommandDFSAdmin.java

Purpose: Marker type for DFSAdmin CLI commands in the XML harness.
Important APIs/types/functions: `CLICommandDFSAdmin` implements `CLICommandTypes`.
Control flow: The DFS XML parser attaches this marker, and `CLITestCmdDFS` routes it to `DFSAdmin`.
State and persistence behavior: No state or persistence.
Dependencies and integration points: Used by `CLITestHelperDFS`, HDFS CLI tests, ACL/delete/XAttr/crypto tests.
Risks and edge cases: Incorrect marker assignment causes commands to execute with the wrong tool.
Test signals: Indirectly covered wherever `<dfs-admin-command>` appears in XML.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/cli/util/CLICommandDFSAdmin.java -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/cli/util/CLICommandErasureCodingCli.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/cli/util/CLICommandErasureCodingCli.java

Purpose: Marker type for erasure-coding admin CLI commands.
Important APIs/types/functions: `CLICommandErasureCodingCli` implements `CLICommandTypes`.
Control flow: The EC parser creates this type and `CLITestCmdErasureCoding` routes it to `ECAdmin`.
State and persistence behavior: No state or persistence.
Dependencies and integration points: Used by `TestErasureCodingCLI` and `ErasureCodingCliCmdExecutor`.
Risks and edge cases: Dispatch depends on exact `instanceof` checks.
Test signals: Indirectly covered by EC CLI XML tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/cli/util/CLICommandErasureCodingCli.java -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/cli/util/CacheAdminCmdExecutor.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/cli/util/CacheAdminCmdExecutor.java

Purpose: Executes cache-admin command strings for CLI XML tests.
Important APIs/types/functions: `CacheAdminCmdExecutor` extends `CommandExecutor`, stores `namenode` and `CacheAdmin`, and overrides `execute(String)`.
Control flow: Execution converts a command string into argv with `getCommandAsArgs(cmd, "NAMENODE", namenode)` then calls `ToolRunner.run(admin, args)`.
State and persistence behavior: State is the configured NameNode replacement string and reusable `CacheAdmin` tool instance; no persistence beyond HDFS operations performed by the admin command.
Dependencies and integration points: Used by `TestCacheAdminCLI`; depends on `CommandExecutor` result capture and Hadoop `ToolRunner`.
Risks and edge cases: Argument parsing must preserve quoting and placeholder substitution. A reused admin instance carries its configuration between commands.
Test signals: Signals are exit codes and captured stdout/stderr in cache-admin XML tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/cli/util/CacheAdminCmdExecutor.java -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/cli/util/CryptoAdminCmdExecutor.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/cli/util/CryptoAdminCmdExecutor.java

Purpose: Executes crypto-admin command strings for CLI XML tests.
Important APIs/types/functions: `CryptoAdminCmdExecutor` extends `CommandExecutor`, stores `namenode` and `CryptoAdmin`, and overrides `execute(String)`.
Control flow: Command text is split through `getCommandAsArgs` with `NAMENODE` replacement, then run through `ToolRunner`.
State and persistence behavior: No local persistence; commands mutate key/encryption-zone state in the configured HDFS cluster.
Dependencies and integration points: Used by `TestCryptoAdminCLI`; integrates with `CryptoAdmin` and the configured key provider.
Risks and edge cases: Placeholder substitution and key-provider configuration are prerequisites. Reusing a `CryptoAdmin` instance assumes commands do not leave unexpected mutable tool state.
Test signals: Signals are XML output and exit-code checks for encryption zone/key operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/cli/util/CryptoAdminCmdExecutor.java -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/cli/util/ErasureCodingCliCmdExecutor.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/cli/util/ErasureCodingCliCmdExecutor.java

Purpose: Executes erasure-coding admin command strings for CLI XML tests.
Important APIs/types/functions: `ErasureCodingCliCmdExecutor` extends `CommandExecutor`, stores `namenode` and `ECAdmin`, and overrides `execute(String)`.
Control flow: It converts command text to argv using `NAMENODE` replacement and invokes `ToolRunner.run(admin, args)`.
State and persistence behavior: Local state is only the admin tool and NameNode string; persistent effects are EC policy settings in the MiniDFSCluster namespace.
Dependencies and integration points: Used by `CLITestCmdErasureCoding` in `TestErasureCodingCLI`.
Risks and edge cases: ECAdmin command behavior depends on enabled policies and HDFS cluster capability. Argument parsing must align with XML expectations.
Test signals: Signals are CLI XML cases around EC policy administration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/cli/util/ErasureCodingCliCmdExecutor.java -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/TestEnhancedByteBufferAccess.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/TestEnhancedByteBufferAccess.java

Purpose: Exercises HDFS enhanced byte-buffer reads, zero-copy mmap behavior, fallback reads, cached-data mmap anchoring, mmap disablement, and the 2GB mmap boundary.
Important APIs/types/functions: `initZeroCopyTest()`, `byteBufferToArray()`, `CountingVisitor`, `RestrictedAllocatingByteBufferPool`, `testFallbackImpl()`, `waitForReplicaAnchorStatus()`, and tests for zero-copy, short reads, no-fallback, mmap cache, cached data, client mmap disable, and large-file limits.
Control flow: Tests configure UNIX native short-circuit reads with a domain socket and mmap cache, create deterministic files in MiniDFSCluster, read through `FSDataInputStream`/`HdfsDataInputStream`, validate `ReadStatistics`, inspect `ShortCircuitCache`, and release buffers. Cached-data tests add/remove cache pools/directives and wait for replica anchor state. The large-file test seeks near 2GB boundaries.
State and persistence behavior: Global setup disables domain-socket path validation and temporarily replaces the POSIX cache manipulator. Runtime state includes mmap cache entries, short-circuit replicas, cache directives, DataNode locked memory accounting, and released/unreleased ByteBuffers.
Dependencies and integration points: Integrates native IO, domain sockets, HDFS short-circuit local reads, `ClientContext`, `ShortCircuitCache`, centralized cache management, `DFSTestUtil`, and byte-buffer fallback utilities.
Risks and edge cases: Tests assume native Unix support and skip otherwise. Buffer release discipline is critical to cache eviction and anchoring. Large-file coverage is gated by environment capability. Metrics and cache timing use waits with timeouts, so slow hosts can expose flakes.
Test signals: Signals include exact byte equality, zero-copy byte counters, expected `UnsupportedOperationException` when fallback is disallowed or mmap disabled, cache visitor counts, replica anchor transitions, cache usage accounting, and 2GB boundary read lengths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/TestEnhancedByteBufferAccess.java -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/TestFcHdfsCreateMkdir.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/TestFcHdfsCreateMkdir.java

Purpose: Runs generic FileContext create/mkdir tests against HDFS.
Important APIs/types/functions: `TestFcHdfsCreateMkdir` extends `FileContextCreateMkdirBaseTest`, overrides `createFileContextHelper()`, and manages static MiniDFSCluster/FileContext setup.
Control flow: Before all tests, a two-Datanode HDFS cluster starts, `fc` is bound to its URI, and the current user's working directory is created. Inherited base tests exercise create and mkdir semantics; teardown delegates to the base class per test and shuts down the cluster at the end.
State and persistence behavior: Static cluster and default working directory are shared across inherited tests; filesystem mutations are cleaned by base helpers.
Dependencies and integration points: Integrates HDFS with the common FileContext create/mkdir contract tests.
Risks and edge cases: Shared static cluster means inherited tests must clean their roots. The local `defaultWorkingDirectory` is created but not overridden for base access in this class, so behavior depends on the base class's expectations.
Test signals: Signals are inherited assertions for recursive mkdir, create parent behavior, existing-path handling, and HDFS URI qualification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/TestFcHdfsCreateMkdir.java -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/TestFcHdfsPermission.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/TestFcHdfsPermission.java

Purpose: Runs generic FileContext permission tests against HDFS.
Important APIs/types/functions: `TestFcHdfsPermission` extends `FileContextPermissionBase`; overrides `getFileContextHelper()` and `getFileContext()`.
Control flow: A two-Datanode cluster and FileContext are created once, with a user working directory. Base permission tests then operate through the returned HDFS FileContext.
State and persistence behavior: Static `fc`, cluster, and working directory persist for the class; per-test cleanup is inherited.
Dependencies and integration points: Integrates HDFS permissions with `FileContextPermissionBase`.
Risks and edge cases: Permissions depend on cluster/user defaults and base cleanup. The class-local `fc` shadows similarly named base fields, so overrides are essential.
Test signals: Signals are inherited permission, owner/group, and status assertions under HDFS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/TestFcHdfsPermission.java -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/TestFcHdfsSetUMask.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/TestFcHdfsSetUMask.java

Purpose: Verifies FileContext umask behavior for HDFS mkdir and create, including recursive parent permissions.
Important APIs/types/functions: `TestFcHdfsSetUMask`, constants for open/blank/user-group permissions and umasks, helpers `testMkdirWithExistingDir()`, `testMkdirRecursiveWithNonExistingDir()`, `testCreateRecursiveWithExistingDir()`, and `testCreateRecursiveWithNonExistingDir()`.
Control flow: Setup starts HDFS with restrictive `fs.permissions.umask`, opens FileContext, and each test sets a specific umask before mkdir/create operations. Assertions compare final file, directory, and parent permissions.
State and persistence behavior: State is the FileContext umask and test-root namespace. Per-test setup resets to wide-open umask and creates the root; teardown deletes it.
Dependencies and integration points: Depends on HDFS permission application, `FileContextTestHelper`, and `FsPermission` semantics.
Risks and edge cases: Parent directory permissions for recursive creation are subtle, especially blank permissions that still need access bits to create children. Umask is mutable on the shared FileContext.
Test signals: Signals are exact `FsPermission` matches for clear/open/middle umasks across existing and non-existing parent scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/TestFcHdfsSetUMask.java -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/TestGlobPaths.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/TestGlobPaths.java

Purpose: Provides broad regression coverage for Hadoop glob expansion on HDFS and local FS, including literals, wildcards, sets, ranges, braces, filters, permissions, symlink scenarios, reserved paths, and sorting.
Important APIs/types/functions: `RegexPathFilter`, `AcceptAllPathFilter`, `AcceptPathsEndingInZ`, `prepareTesting()`, `checkStatus()`, `FSTestWrapperGlobTest`, and many `@Test` methods such as `testMultiGlob()`, `pTestCurlyBracket()`, `testGlobFillsInSchemeOnFS/FC()`, `testGlobAccessDeniedOnFS/FC()`, `testReservedHdfsPathsOnFS/FC()`, and `testLocalFilesystem()`.
Control flow: Class setup starts HDFS, opens privileged and unprivileged FileSystem/FileContext handles, makes root writable, and switches login user. Tests create deterministic directory trees, run `globStatus` with patterns and filters, normalize paths, and delete the user root. Wrapper-based tests execute the same glob behavior through FileSystem and FileContext.
State and persistence behavior: Persistent state is transient namespace content under the test user's home plus root permission/owner changes in some cases. Static privileged/unprivileged handles live for the class.
Dependencies and integration points: Integrates `FileSystem.globStatus`, `FileContext.util().globStatus`, glob pattern parsing, `PathFilter`, symlink wrappers, HDFS reserved inode paths, permission enforcement, and local FS ordering.
Risks and edge cases: The suite mutates global login user and root permissions, so isolation matters. Several symlink glob tests are disabled. Expected ordering is strict and assumes glob sorting. Windows escape behavior is skipped for backslash semantics.
Test signals: Signals include exact merged path order, null versus empty-array distinction, `AccessControlException` when listing forbidden dirs, reserved root inode visibility, scheme filling, relative working-directory expansion, and sorted local filesystem glob output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/TestGlobPaths.java -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/TestHDFSFileContextMainOperations.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/TestHDFSFileContextMainOperations.java

Purpose: Runs HDFS-specific FileContext main-operation tests beyond the generic base suite.
Important APIs/types/functions: `TestHDFSFileContextMainOperations` extends `FileContextMainOperationsBaseTest`; key tests cover truncate, quota-sensitive old/new rename, root rename errors, edits-log replay, invalid names, corrupted-block support, and cross-filesystem rename.
Control flow: Class setup starts a two-Datanode cluster and HDFS FileContext. Tests create files/directories via helper methods, manipulate quotas through `DistributedFileSystem`, execute `FileContext.rename` or legacy `FileSystem.rename`, restart the cluster without formatting to replay edits, and assert final namespace state.
State and persistence behavior: Static cluster and FileContext are shared; `restartCluster()` preserves storage with `format(false)` to validate edit-log persistence. Namespace and quota state are per-test helper roots where possible.
Dependencies and integration points: Integrates FileContext APIs with HDFS quota accounting, truncate, append verification, edit-log loading, `RemoteException` unwrapping, and URI scheme validation.
Risks and edge cases: Quota tests depend on exact namespace counts and overwrite semantics. Restarting the shared cluster can affect following tests if cleanup is incomplete. Root rename expectations rely on remote exception wrapping.
Test signals: Signals include file length/content after truncate, space consumed equals new length times replication, quota exceptions, src/dst existence after rename, successful edit-log replay after restart, invalid-name rejection, and IOException for cross-filesystem rename.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/TestHDFSFileContextMainOperations.java -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/TestHdfsNativeCodeLoader.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/TestHdfsNativeCodeLoader.java

Purpose: Checks whether native HDFS code loading is enforced when the test JVM requests it.
Important APIs/types/functions: `requireTestJni()` reads `require.test.libhadoop`; `testNativeCodeLoaded()` checks `NativeCodeLoader.isNativeCodeLoaded()`.
Control flow: If the property is absent or false, the test logs and returns. If required, it fails with `LD_LIBRARY_PATH` context when libhadoop is not loaded.
State and persistence behavior: No filesystem or cluster state; reads system properties and environment variables.
Dependencies and integration points: Integrates JUnit with Hadoop `NativeCodeLoader` and native-library test configuration.
Risks and edge cases: Behavior changes entirely based on a JVM property. Failure diagnostics depend on `LD_LIBRARY_PATH` rather than all native search paths.
Test signals: Signals are either a skip-like return when native code is optional or a hard failure when required native code is missing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/TestHdfsNativeCodeLoader.java -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/TestResolveHdfsSymlink.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/TestResolveHdfsSymlink.java

Purpose: Tests FileContext and DFSClient behavior around HDFS symlink resolution to other filesystems and delegation token APIs.
Important APIs/types/functions: `TestResolveHdfsSymlink`, `testFcResolveAfs()`, `testFcDelegationToken()`, `testLinkTargetNonSymlink()`, and `testLinkTargetNonExistent()`.
Control flow: Setup starts HDFS with delegation tokens always enabled. Tests create a local file, create an HDFS symlink to the local root, resolve abstract filesystems for a path through the link, obtain/renew/cancel HDFS delegation tokens, and assert DFSClient link-target errors for non-symlink and missing paths.
State and persistence behavior: State includes the MiniDFSCluster, local test file, HDFS symlink, and issued delegation token. Cleanup deletes the non-symlink file and shuts down the cluster.
Dependencies and integration points: Integrates `FileContext.resolveAbstractFileSystems`, local FS, HDFS symlinks, `DFSClient.getLinkTarget`, and HDFS delegation token renewal/cancellation.
Risks and edge cases: Cross-filesystem symlink resolution depends on FileContext URI construction. Token tests assume at least one token is returned. Some created symlink/local paths are not explicitly cleaned before cluster teardown.
Test signals: Signals are exactly two resolved AFS instances, successful token renew/cancel, error text for non-symlink, and `FileNotFoundException` text for missing paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/TestResolveHdfsSymlink.java -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/TestSWebHdfsFileContextMainOperations.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/TestSWebHdfsFileContextMainOperations.java

Purpose: Runs the WebHDFS FileContext main-operation suite over HTTPS (`swebhdfs`).
Important APIs/types/functions: `TestSWebHdfsFileContextMainOperations` extends `TestWebHdfsFileContextMainOperations`; overrides class setup, `createFileContextHelper()`, `getWebhdfsUrl()`, and teardown.
Control flow: Setup creates temporary SSL keystores, configures HTTPS-only HDFS endpoints on random localhost ports, starts two Datanodes, builds an `swebhdfs://` URI from the NameNode HTTPS address, and binds FileContext to it.
State and persistence behavior: State includes temporary keystore/config directories, static cluster, static HTTPS URI, and inherited FileContext test namespace. Teardown shuts down the cluster and deletes SSL materials.
Dependencies and integration points: Integrates `KeyStoreTestUtil`, `SSLFactory`, HDFS HTTPS policy, SWebHDFS scheme handling, and inherited FileContext operation tests.
Risks and edge cases: SSL setup failures are wrapped in `RuntimeException`. Hostname verifier and random HTTPS addresses are critical. Cleanup must remove both cluster and keystore artifacts.
Test signals: Signals are inherited WebHDFS/FileContext operation assertions executed over HTTPS plus successful SSL config setup/cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/TestSWebHdfsFileContextMainOperations.java -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/TestSymlinkHdfs.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/TestSymlinkHdfs.java

Purpose: Base class for HDFS symlink behavior tests shared by FileSystem and FileContext wrappers.
Important APIs/types/functions: `TestSymlinkHdfs` extends `SymlinkBaseTest`; overrides scheme/base dirs/URI/exception unwrapping and defines tests for cross-FS links, rename across FS, slash links, target-affecting metadata operations, partial URI rejection, replication through links, max path length, WebHDFS symlink creation, owner, and quota.
Control flow: Class setup starts HDFS with umask 000 and disabled max-component length, opens WebHDFS and DFS handles, and subclasses set the wrapper. Tests create files/links through wrapper APIs and verify reads/status/metadata. Quota and WebHDFS cases call HDFS-specific APIs directly.
State and persistence behavior: Static MiniDFSCluster, WebHDFS FS, and DFS handles persist across subclasses. Namespace changes occur under `/test1` and `/test2`; base class cleanup behavior is inherited.
Dependencies and integration points: Integrates HDFS symlink implementation, `SymlinkBaseTest`, FileSystem/FileContext wrappers, WebHDFS, quota enforcement, path-length limits, and RemoteException unwrapping.
Risks and edge cases: Subclass wrapper selection changes behavior; FileSystem disables some inherited tests. Cross-filesystem rename expects different exception classes by wrapper type. Shared static cluster can leak namespace/quota state if base cleanup misses a path.
Test signals: Signals include successful reads through symlinks, failed cross-FS renames, unchanged link metadata when target permissions/owner change, replication target updates, path too long failure, WebHDFS link behavior, and quota exception on excess symlink creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/TestSymlinkHdfs.java -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/TestSymlinkHdfsDisable.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/TestSymlinkHdfsDisable.java

Purpose: Verifies that disabling remote symlink resolution blocks both FileContext and DistributedFileSystem link opens.
Important APIs/types/functions: `TestSymlinkHdfsDisable.testSymlinkHdfsDisable()`.
Control flow: The test disables `FS_CLIENT_RESOLVE_REMOTE_SYMLINKS_KEY`, starts a MiniDFSCluster, creates a target file and HDFS symlink, then attempts `fc.open(link)` and `dfs.open(link)` expecting errors.
State and persistence behavior: State is a single cluster, one target file, and one symlink; the cluster is not shut down in a finally block in the visible code.
Dependencies and integration points: Depends on HDFS symlink resolution configuration, `DFSTestUtil`, FileContext, and DistributedFileSystem.
Risks and edge cases: Missing `finally` cleanup is a resource leak risk if assertions fail. The expected error is matched by substring `resolution is disabled`.
Test signals: Signals are IOException failures for both FileContext and DFS open paths when symlink resolution is disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/TestSymlinkHdfsDisable.java -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/TestSymlinkHdfsFileContext.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/TestSymlinkHdfsFileContext.java

Purpose: Runs the HDFS symlink base tests through a FileContext wrapper and adds AbstractFileSystem-specific link behavior.
Important APIs/types/functions: `TestSymlinkHdfsFileContext` extends `TestSymlinkHdfs`; `testSetup()` creates `FileContextTestWrapper`; `testAccessLinkFromAbstractFileSystem()` verifies AFS does not resolve links implicitly.
Control flow: Before all tests, the subclass binds FileContext to the shared cluster URI and installs the wrapper. The added test creates a file/link and calls `AbstractFileSystem.open(link)`, expecting `UnresolvedLinkException`.
State and persistence behavior: Uses the shared static cluster/DFS/WebHDFS state from the base class plus a static FileContext.
Dependencies and integration points: Integrates HDFS FileContext symlink behavior, AbstractFileSystem API, and inherited `SymlinkBaseTest` cases.
Risks and edge cases: Depends on base class `beforeClassSetup()` ordering. The AFS test must distinguish direct AFS behavior from FileContext's higher-level resolution.
Test signals: Signals are inherited symlink tests plus `UnresolvedLinkException` from raw AFS open.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/TestSymlinkHdfsFileContext.java -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/TestSymlinkHdfsFileSystem.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/TestSymlinkHdfsFileSystem.java

Purpose: Runs HDFS symlink tests through a FileSystem wrapper and adds DFS-only symlink operation coverage.
Important APIs/types/functions: `TestSymlinkHdfsFileSystem` extends `TestSymlinkHdfs`; disables two inherited tests; adds `testRecoverLease()`, `testIsFileClosed()`, `testConcat()`, and `testSnapshot()`.
Control flow: Setup installs `FileSystemTestWrapper`. Added tests create symlinks to files or directories, then call DFS-only APIs through link paths: lease recovery, file-closed status, concat target/srcs, and snapshot allow/create/rename/delete.
State and persistence behavior: Uses shared HDFS cluster and DFS handle. Snapshot and concat tests mutate namespace under symlinked directories.
Dependencies and integration points: Integrates symlink resolution with `DistributedFileSystem` lease, concat, and snapshot APIs.
Risks and edge cases: Two inherited tests are disabled because FileSystem fills URI authority and creates parents differently. DFS-only operations must resolve links consistently without changing link status.
Test signals: Signals are true lease/file-closed results and no exception during concat and snapshot operations through link paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/TestSymlinkHdfsFileSystem.java -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/TestUnbuffer.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/TestUnbuffer.java

Purpose: Tests `FSDataInputStream.unbuffer()` behavior for HDFS TCP readers and capability policy failures.
Important APIs/types/functions: `TestUnbuffer`, `testUnbufferClosesSockets()`, `testOpenManyFilesViaTcp()`, and `testUnbufferException()`.
Control flow: Tests disable short-circuit reads to force TCP block readers, create files in MiniDFSCluster, read bytes, call `unbuffer()`, inspect `PeerCache`, and reopen/read many streams. The exception test mocks a stream that advertises unbuffer capability but does not implement `CanUnbuffer`.
State and persistence behavior: State includes a dedicated DFS client context peer cache, open input streams, and MiniDFSCluster namespace. Cleanup closes streams and clusters in finally blocks.
Dependencies and integration points: Integrates HDFS block readers, `PeerCache`, client context configuration, `FSDataInputStream`, `StreamCapabilitiesPolicy`, and Mockito.
Risks and edge cases: Socket-cache assertions depend on disabled short-circuit reads and long cache timeouts. The 500-open test is resource-sensitive. Mocked capability behavior must match policy strings.
Test signals: Signals are peer cache size changes after unbuffer, successful many-stream reads without socket exhaustion, and expected `UnsupportedOperationException` text for a buggy stream.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/TestUnbuffer.java -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/TestUrlStreamHandler.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/TestUrlStreamHandler.java

Purpose: Validates Hadoop URL stream handler support for HDFS and file URLs while leaving unrelated protocols to default handlers.
Important APIs/types/functions: `TestUrlStreamHandler`, static `FsUrlStreamHandlerFactory`, `setupHandler()`, `testDfsUrls()`, `testFileUrls()`, and protocol handler tests.
Control flow: Before all tests, the JVM-global URL stream handler factory is installed. HDFS test creates a file through `FileSystem`, builds an `hdfs://` URL from cluster URI, opens it as a stream, and compares bytes. File test does the same for a local `file://` URL. HTTP/HTTPS/unknown protocols should return null handlers from the Hadoop factory.
State and persistence behavior: State includes a JVM-global URL handler factory that can be set only once, a MiniDFSCluster for HDFS URL testing, and a local temp file.
Dependencies and integration points: Integrates Java `URL`, Hadoop `FsUrlStreamHandlerFactory`, HDFS FileSystem, local FileSystem, and MiniDFSCluster.
Risks and edge cases: Global factory installation can conflict with other tests in the same JVM. Byte reads assume the first read returns all 1024 bytes. Local temp directory creation and cleanup must succeed.
Test signals: Signals are non-null URL streams, exact byte equality for HDFS and file URLs, and null handlers for http, https, and unknown protocols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/TestUrlStreamHandler.java -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/TestWebHdfsFileContextMainOperations.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/TestWebHdfsFileContextMainOperations.java

Purpose: Runs FileContext main-operation tests through WebHDFS.
Important APIs/types/functions: `TestWebHdfsFileContextMainOperations` extends `FileContextMainOperationsBaseTest`; key methods are `clusterSetupAtBeginning()`, `setUp()`, `testUnsupportedSymlink()`, `testSetVerifyChecksum()`, and `ClusterShutdownAtEnd()`.
Control flow: Setup starts two-Datanode HDFS, builds a `webhdfs://` URI from the NameNode HTTP address, binds FileContext, and creates the user working directory. Per-test setup builds a randomized root URI under the WebHDFS endpoint. The checksum test writes data, enables verify checksum, reads it back, and compares bytes.
State and persistence behavior: Static cluster, WebHDFS URI, FileContext, and test data persist for the class. Per-test roots are randomized; symlink test is intentionally empty because support is partial.
Dependencies and integration points: Integrates WebHDFS scheme handling with the generic FileContext main-operation test suite.
Risks and edge cases: WebHDFS differs from direct HDFS for checksum timing and corrupted-block support. The empty symlink test documents unsupported behavior but provides no assertion.
Test signals: Signals are inherited FileContext operation results over WebHDFS and byte-for-byte checksum readback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/TestWebHdfsFileContextMainOperations.java -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/HDFSContract.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/HDFSContract.java

Purpose: Defines the HDFS filesystem contract used by Hadoop's generic contract test suite.
Important APIs/types/functions: `HDFSContract`, `CONTRACT_HDFS_XML`, `BLOCK_SIZE`, static `createCluster()`, `destroyCluster()`, `getCluster()`, and overrides `init()`, `getTestFileSystem()`, `getScheme()`, `getTestPath()`.
Control flow: The contract loads `contract/hdfs.xml`, starts a two-Datanode MiniDFSCluster with block size equal to the abstract test file length, asserts contract options loaded, and returns the cluster FileSystem for tests.
State and persistence behavior: A static MiniDFSCluster is shared by contract test classes and destroyed after each class. Test path root is `/test`.
Dependencies and integration points: Integrates contract option XML, `AbstractFSContract`, MiniDFSCluster, and HDFS FileSystem.
Risks and edge cases: Static cluster lifecycle requires every contract test class to pair create/destroy. Block-size override affects tests that assume normal HDFS defaults.
Test signals: Signals are inherited contract tests creating the cluster, loading case-sensitivity options, and operating against `hdfs` scheme.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/HDFSContract.java -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/TestDFSWrappedIO.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/TestDFSWrappedIO.java

Purpose: Runs WrappedIO tests against HDFS, especially ByteBuffer positioned reads.
Important APIs/types/functions: `TestDFSWrappedIO` extends `TestWrappedIO` and overrides `createContract()` while using `HDFSContract.createCluster()/destroyCluster()`.
Control flow: Before all tests it starts the shared HDFS contract cluster, base tests run WrappedIO cases, and after all it destroys the cluster.
State and persistence behavior: State is the static HDFSContract cluster and test namespace.
Dependencies and integration points: Integrates `org.apache.hadoop.io.wrappedio.impl.TestWrappedIO` with HDFS contract.
Risks and edge cases: Failures can come from the generic WrappedIO suite or HDFS contract cluster lifecycle.
Test signals: Signals are inherited WrappedIO assertions for HDFS reads and positioned ByteBuffer behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/TestDFSWrappedIO.java -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/TestHDFSContractAppend.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/TestHDFSContractAppend.java

Purpose: Adapts generic append contract tests to HDFS.
Important APIs/types/functions: `TestHDFSContractAppend` extends `AbstractContractAppendTest` and returns `new HDFSContract(conf)`.
Control flow: Starts HDFSContract before the class, executes inherited append tests, and destroys the cluster afterward.
State and persistence behavior: Uses static contract cluster and inherited test paths.
Dependencies and integration points: Integrates HDFS with the append contract suite.
Risks and edge cases: Append behavior depends on contract XML features and MiniDFSCluster lifecycle.
Test signals: Signals are inherited append success/error semantics on HDFS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/TestHDFSContractAppend.java -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/TestHDFSContractBulkDelete.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/TestHDFSContractBulkDelete.java

Purpose: Adapts generic bulk-delete contract tests to HDFS.
Important APIs/types/functions: `TestHDFSContractBulkDelete` extends `AbstractContractBulkDeleteTest` and overrides `createContract()`.
Control flow: Cluster setup/teardown bracket inherited bulk delete tests.
State and persistence behavior: State is the shared HDFSContract cluster and files created by inherited tests.
Dependencies and integration points: Integrates HDFS with bulk delete contract coverage.
Risks and edge cases: Bulk delete semantics must match HDFS capabilities advertised in contract options.
Test signals: Signals are inherited bulk delete result and error assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/TestHDFSContractBulkDelete.java -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/TestHDFSContractConcat.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/TestHDFSContractConcat.java

Purpose: Adapts concat contract tests to HDFS and verifies the cluster is usable after startup.
Important APIs/types/functions: `TestHDFSContractConcat` extends `AbstractContractConcatTest`; setup calls `getDefaultBlockSize()` after creating the cluster.
Control flow: Before all it starts HDFSContract and performs a simple FS operation, then inherited concat tests run and teardown destroys the cluster.
State and persistence behavior: Uses static contract cluster and inherited test files.
Dependencies and integration points: Integrates HDFS concat implementation with generic contract tests.
Risks and edge cases: Concat is sensitive to block sizes and file closure state; startup smoke operation catches early cluster failures.
Test signals: Signals are inherited concat tests plus successful default block size query.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/TestHDFSContractConcat.java -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/TestHDFSContractCreate.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/TestHDFSContractCreate.java

Purpose: Adapts create contract tests to HDFS.
Important APIs/types/functions: `TestHDFSContractCreate` extends `AbstractContractCreateTest` and creates `HDFSContract`.
Control flow: HDFSContract cluster brackets inherited create tests.
State and persistence behavior: Static contract cluster; created files live under contract test path until cleanup.
Dependencies and integration points: Integrates HDFS FileSystem with generic create semantics.
Risks and edge cases: Create flags, overwrite behavior, and parent handling depend on contract options.
Test signals: Signals are inherited create/open/status assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/TestHDFSContractCreate.java -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/TestHDFSContractDelete.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/TestHDFSContractDelete.java

Purpose: Adapts delete contract tests to HDFS.
Important APIs/types/functions: `TestHDFSContractDelete` extends `AbstractContractDeleteTest`.
Control flow: Cluster setup/teardown surrounds inherited delete tests.
State and persistence behavior: Shared HDFSContract cluster and inherited namespace.
Dependencies and integration points: Integrates HDFS delete semantics with contract suite.
Risks and edge cases: Recursive and missing-path delete semantics must align with advertised contract.
Test signals: Signals are inherited delete behavior assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/TestHDFSContractDelete.java -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/TestHDFSContractGetFileStatus.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/TestHDFSContractGetFileStatus.java

Purpose: Adapts get-file-status contract tests to HDFS.
Important APIs/types/functions: `TestHDFSContractGetFileStatus` extends `AbstractContractGetFileStatusTest`.
Control flow: Starts contract cluster, runs inherited status tests, destroys cluster.
State and persistence behavior: Static cluster and test paths.
Dependencies and integration points: Integrates HDFS `FileStatus` behavior with generic contract tests.
Risks and edge cases: Owner, directory/file distinctions, and missing path exceptions are contract-sensitive.
Test signals: Signals are inherited status metadata and error assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/TestHDFSContractGetFileStatus.java -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/TestHDFSContractLeaseRecovery.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/TestHDFSContractLeaseRecovery.java

Purpose: Adapts lease-recovery contract tests to HDFS.
Important APIs/types/functions: `TestHDFSContractLeaseRecovery` extends `AbstractContractLeaseRecoveryTest`.
Control flow: HDFSContract cluster wraps inherited lease recovery cases.
State and persistence behavior: State includes open files/leases created by base tests.
Dependencies and integration points: Integrates HDFS lease recovery with generic filesystem contracts.
Risks and edge cases: Lease timing and recovery can be asynchronous; cluster cleanup must close outstanding clients.
Test signals: Signals are inherited lease recovery and file visibility assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/TestHDFSContractLeaseRecovery.java -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/TestHDFSContractMkdir.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/TestHDFSContractMkdir.java

Purpose: Adapts mkdir contract tests to HDFS.
Important APIs/types/functions: `TestHDFSContractMkdir` extends `AbstractContractMkdirTest`.
Control flow: Creates HDFSContract cluster, runs inherited mkdir tests, tears down.
State and persistence behavior: Shared static cluster and contract test directory.
Dependencies and integration points: Integrates HDFS mkdir behavior with the contract suite.
Risks and edge cases: Parent creation, root handling, and existing-file collisions are key risks.
Test signals: Signals are inherited mkdir status and exception assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/TestHDFSContractMkdir.java -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/TestHDFSContractMultipartUploader.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/TestHDFSContractMultipartUploader.java

Purpose: Adapts multipart uploader contract tests to HDFS with HDFS-specific capability overrides.
Important APIs/types/functions: `TestHDFSContractMultipartUploader` extends `AbstractContractMultipartUploaderTest`; overrides `partSizeInBytes()`, `finalizeConsumesUploadIdImmediately()`, and `supportsConcurrentUploadsToSamePath()`.
Control flow: Cluster setup/teardown wraps inherited multipart upload tests. The class reports 1KB part size, immediate upload-id consumption on finalize, and concurrent uploads to the same path as supported.
State and persistence behavior: State includes multipart upload session metadata and the static HDFSContract cluster.
Dependencies and integration points: Integrates HDFS multipart upload implementation with generic contract coverage.
Risks and edge cases: Incorrect capability overrides would make inherited tests assert the wrong semantics. Concurrent upload support is explicitly advertised and should stay true only if HDFS behavior supports it.
Test signals: Signals are inherited multipart upload completion, abort, conflict, and concurrent-upload tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/TestHDFSContractMultipartUploader.java -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/TestHDFSContractOpen.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/TestHDFSContractOpen.java

Purpose: Adapts open contract tests to HDFS.
Important APIs/types/functions: `TestHDFSContractOpen` extends `AbstractContractOpenTest`.
Control flow: Starts HDFSContract, runs inherited open/read tests, destroys cluster.
State and persistence behavior: Static cluster and files from inherited tests.
Dependencies and integration points: Integrates HDFS open/read semantics with contract suite.
Risks and edge cases: EOF, missing files, directory opens, and buffer sizes are contract-sensitive.
Test signals: Signals are inherited open and read assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/TestHDFSContractOpen.java -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/TestHDFSContractPathHandle.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/TestHDFSContractPathHandle.java

Purpose: Verifies HDFS compliance with generic PathHandle semantics.
Important APIs/types/functions: `TestHDFSContractPathHandle` extends `AbstractContractPathHandleTest` and has an explicit empty constructor.
Control flow: Cluster setup/teardown surrounds inherited PathHandle tests.
State and persistence behavior: State includes path handles and files in the HDFSContract cluster.
Dependencies and integration points: Integrates HDFS path handle implementation with contract tests.
Risks and edge cases: Path handles must remain valid/invalid according to file identity and mutation semantics.
Test signals: Signals are inherited PathHandle stability and invalidation assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/TestHDFSContractPathHandle.java -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/TestHDFSContractRename.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/TestHDFSContractRename.java

Purpose: Adapts rename contract tests to HDFS.
Important APIs/types/functions: `TestHDFSContractRename` extends `AbstractContractRenameTest`.
Control flow: Starts the HDFSContract cluster, runs inherited rename cases, then destroys it.
State and persistence behavior: Shared cluster namespace under the contract test path.
Dependencies and integration points: Integrates HDFS rename behavior with generic contracts.
Risks and edge cases: Overwrite, directory, root, and cross-path rename semantics are high-risk contract areas.
Test signals: Signals are inherited rename existence/status/error assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/TestHDFSContractRename.java -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/TestHDFSContractRootDirectory.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/TestHDFSContractRootDirectory.java

Purpose: Adapts root-directory contract tests to HDFS.
Important APIs/types/functions: `TestHDFSContractRootDirectory` extends `AbstractContractRootDirectoryTest`.
Control flow: Cluster setup/teardown brackets inherited root directory tests.
State and persistence behavior: State is the root and test path of the HDFSContract cluster.
Dependencies and integration points: Integrates HDFS root behavior with contract suite.
Risks and edge cases: Root listing/status/deletion protections must match contract expectations.
Test signals: Signals are inherited root directory operation assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/TestHDFSContractRootDirectory.java -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/TestHDFSContractSafeMode.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/TestHDFSContractSafeMode.java

Purpose: Adapts safe-mode contract tests to HDFS.
Important APIs/types/functions: `TestHDFSContractSafeMode` extends `AbstractContractSafeModeTest`.
Control flow: Starts HDFSContract, runs inherited safe-mode interface tests, and destroys cluster.
State and persistence behavior: Static cluster safe-mode state is manipulated by inherited tests.
Dependencies and integration points: Integrates HDFS safe mode APIs with generic filesystem contract tests.
Risks and edge cases: Safe mode transitions can be timing-sensitive and must leave the cluster usable afterward.
Test signals: Signals are inherited safe-mode enter/leave and operation behavior assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/TestHDFSContractSafeMode.java -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/TestHDFSContractSeek.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/TestHDFSContractSeek.java

Purpose: Adapts seek contract tests to HDFS.
Important APIs/types/functions: `TestHDFSContractSeek` extends `AbstractContractSeekTest`.
Control flow: HDFSContract lifecycle wraps inherited seek tests.
State and persistence behavior: State includes test files and input stream positions.
Dependencies and integration points: Integrates HDFS seek/read semantics with generic contracts.
Risks and edge cases: Boundary seeks, negative seeks, EOF, and closed-stream behavior are key risks.
Test signals: Signals are inherited seek position and read-content assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/TestHDFSContractSeek.java -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/TestHDFSContractSetTimes.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/TestHDFSContractSetTimes.java

Purpose: Adapts set-times contract tests to HDFS.
Important APIs/types/functions: `TestHDFSContractSetTimes` extends `AbstractContractSetTimesTest`.
Control flow: Starts HDFSContract, runs inherited timestamp mutation tests, destroys cluster.
State and persistence behavior: State includes file metadata timestamps in the MiniDFSCluster namespace.
Dependencies and integration points: Integrates HDFS mtime/atime behavior with contract tests.
Risks and edge cases: Timestamp precision and unsupported atime settings can cause contract mismatches.
Test signals: Signals are inherited setTimes metadata assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/TestHDFSContractSetTimes.java -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/TestHDFSContractUnbuffer.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/TestHDFSContractUnbuffer.java

Purpose: Adapts unbuffer contract tests to HDFS.
Important APIs/types/functions: `TestHDFSContractUnbuffer` extends `AbstractContractUnbufferTest`.
Control flow: Contract cluster wraps inherited unbuffer tests.
State and persistence behavior: State includes streams and client resources created by the base tests.
Dependencies and integration points: Integrates HDFS stream unbuffer support with generic contract coverage.
Risks and edge cases: Resource cleanup and capability advertisement must be consistent.
Test signals: Signals are inherited unbuffer support and post-unbuffer read behavior assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/TestHDFSContractUnbuffer.java -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/TestHDFSContractVectoredRead.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/TestHDFSContractVectoredRead.java

Purpose: Adapts vectored-read contract tests to HDFS across parameterized buffer types.
Important APIs/types/functions: `TestHDFSContractVectoredRead` is a JUnit `@ParameterizedClass` over `params`, extends `AbstractContractVectoredReadTest`, and passes `bufferType` to the superclass.
Control flow: For each buffer type, HDFSContract cluster setup/teardown brackets inherited vectored-read tests that issue ranged reads and compare results.
State and persistence behavior: State includes the static contract cluster and per-parameter test files/buffers.
Dependencies and integration points: Integrates HDFS vectored read implementation with generic contract coverage and JUnit parameterized class support.
Risks and edge cases: Parameterized cluster lifecycle can be expensive. Buffer-type support must match inherited expectations, and range coalescing errors can be subtle.
Test signals: Signals are inherited vectored-read content, range, EOF, and buffer-management assertions for each buffer type.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/TestHDFSContractVectoredRead.java -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/loadGenerator/TestLoadGenerator.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/loadGenerator/TestLoadGenerator.java

Purpose: Tests HDFS load-generator support utilities: structure generation, data generation, probabilistic load generation, argument validation, and scripted operations.
Important APIs/types/functions: `TestLoadGenerator` extends `Configured` and implements `Tool`; tests `StructureGenerator`, `DataGenerator`, `LoadGenerator`, `main()`, and `run()`.
Control flow: Static configuration sets tiny block/checksum sizes and heartbeat interval. `testStructureGenerator()` runs with deterministic args/seed, verifies generated directory/file structure files, then mutates arguments to assert validation failures. `testLoadGenerator()` writes structure files, starts a three-Datanode cluster, generates data under `/test`, runs load generation, validates bad probabilities/delays/thread/time args, and tests good/bad script files.
State and persistence behavior: State includes files under `PathUtils.getTestDir`, generated HDFS namespace under `/test`, and temporary script files. Cleanup deletes structure/script files and shuts down the cluster.
Dependencies and integration points: Integrates `StructureGenerator`, `DataGenerator`, `LoadGenerator`, MiniDFSCluster, `ToolRunner`, and Hadoop `Time`.
Risks and edge cases: Generated output is seed-sensitive. Argument index constants must match the argv arrays; one restore line assigns `args[READ_PROBABILITY] = oldArg` after mutating write probability, which is suspicious but in-test. Long-running load operations depend on timing.
Test signals: Signals include exact generated file lines, zero return for valid generation/load/script runs, -1 for invalid args and malformed scripts, and successful `Tool` wrapper execution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/loadGenerator/TestLoadGenerator.java -->
