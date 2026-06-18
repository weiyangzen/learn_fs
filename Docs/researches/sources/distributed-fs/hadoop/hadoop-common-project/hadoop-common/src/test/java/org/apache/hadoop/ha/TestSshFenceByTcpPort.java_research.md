# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ha/TestSshFenceByTcpPort.java

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ha/TestSshFenceByTcpPort.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ha/TestSshFenceByTcpPort.java

Purpose: this test covers SSH-based fencing through `SshFenceByTcpPort`, especially argument parsing and timeout behavior. The real fencing test is gated by system properties for host, port, and key file.

Important APIs and types: uses `SshFenceByTcpPort`, nested `Args`, `BadFencingConfigurationException`, `DummyHAService`, and JUnit assumptions. Configuration keys include identity file and connect timeout.

Control flow: `testFence()` runs only when configured and expects `tryFence()` to return true for the configured target. `testConnectTimeout()` points at an unfenceable address and verifies a false result within timeout. Parsing tests construct `Args` for null, empty, user-only, port-only, and user:port forms; bad parsing cases assert configuration exceptions.

State and persistence: test configuration comes from system properties. No persistent state is modified; network behavior depends on external host reachability for the gated real SSH case.

Dependencies and integration points: integrates JSch/SSH fencing behavior indirectly, Hadoop configuration, service target address extraction, and local user-name defaults.

Risks: the real SSH test is environment-sensitive and skipped unless properties are set. The timeout case uses a public IP and fixed port, so network policy can influence duration or result.

Test signals: confirms default user/port parsing, custom user and port parsing, bad arg rejection, configured identity use, and graceful false return on connection timeout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ha/TestSshFenceByTcpPort.java -->
