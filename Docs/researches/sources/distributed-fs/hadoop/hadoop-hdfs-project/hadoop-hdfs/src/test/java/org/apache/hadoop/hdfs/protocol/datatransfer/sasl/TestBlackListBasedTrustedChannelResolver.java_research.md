<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/protocol/datatransfer/sasl/TestBlackListBasedTrustedChannelResolver.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/protocol/datatransfer/sasl/TestBlackListBasedTrustedChannelResolver.java

Purpose: Tests blacklist-file behavior for `BlackListBasedTrustedChannelResolver` on client and server trust decisions.

Important APIs/types/functions: `BlackListBasedTrustedChannelResolver`, client/server fixed blacklist config keys, `isTrusted()`, `isTrusted(InetAddress)`, Apache `FileUtils`, and `GenericTestUtils.getTestDir`.

Control flow: `setup` writes a temporary blacklist file containing two IPs and creates a resolver. Client test appends the local host address, sets the client blacklist path, and expects the current channel to be untrusted. Server test sets the server blacklist path, verifies default local trust, and verifies a listed remote address is untrusted. `cleanUp` deletes the file.

State and persistence behavior: Persists a temporary text blacklist file under the test directory.

Dependencies and integration points: Covers data-transfer SASL trust-bypass decisions driven by fixed IP blacklist files.

Risks: Client test depends on resolving `InetAddress.getLocalHost().getHostAddress()` and matching resolver behavior. File append uses platform default charset through `FileUtils`.

Test signals: Passing means configured blacklist files are loaded and trusted-channel decisions change for listed client/server addresses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/protocol/datatransfer/sasl/TestBlackListBasedTrustedChannelResolver.java -->
