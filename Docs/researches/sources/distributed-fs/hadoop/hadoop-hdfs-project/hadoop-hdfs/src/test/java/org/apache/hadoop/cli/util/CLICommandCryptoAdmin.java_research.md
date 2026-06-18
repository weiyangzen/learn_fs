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
