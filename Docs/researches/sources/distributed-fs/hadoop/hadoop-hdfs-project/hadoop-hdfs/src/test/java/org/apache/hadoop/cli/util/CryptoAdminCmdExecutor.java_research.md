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
