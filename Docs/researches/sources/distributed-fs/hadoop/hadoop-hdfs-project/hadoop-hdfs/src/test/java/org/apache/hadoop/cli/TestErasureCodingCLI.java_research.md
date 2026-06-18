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
