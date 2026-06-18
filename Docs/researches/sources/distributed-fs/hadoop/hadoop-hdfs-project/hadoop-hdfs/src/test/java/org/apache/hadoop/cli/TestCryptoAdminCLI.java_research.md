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
