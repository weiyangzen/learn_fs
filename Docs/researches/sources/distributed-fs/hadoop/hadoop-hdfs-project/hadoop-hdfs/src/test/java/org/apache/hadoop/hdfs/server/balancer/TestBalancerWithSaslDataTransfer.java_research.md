# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/balancer/TestBalancerWithSaslDataTransfer.java

## Purpose
This wrapper verifies that the baseline balancer scenario works under SASL data-transfer protection modes: authentication, integrity, and privacy.

## Important APIs, Types, and Functions
The class extends `SaslDataTransferTestCase`, uses `createSecureConfig`, and delegates to a shared static `TestBalancer` instance through `testBalancer0Internal`.

## Control Flow
Each test creates a secure HDFS configuration for one SASL protection level and invokes the standard `TestBalancer` one-node/two-node balancing scenario. The delegated scenario initializes balancer defaults, builds MiniDFSClusters, creates files, starts empty nodes, runs balancer, and checks utilization.

## State and Persistence Behavior
The class itself has no cluster fields; state is delegated to the shared `TEST_BALANCER`. Because the instance is static, cleanup relies on the delegated test's internal `finally` and `@AfterEach` behavior when invoked through this wrapper is not automatic. The underlying methods do use cluster shutdown paths.

## Dependencies and Integration Points
Integration points include HDFS SASL data transfer setup, block access token/security settings from `SaslDataTransferTestCase`, and balancer block movement over secured transfer channels.

## Risks and Test Signals
Risks include shared static `TestBalancer` state, security configuration leakage, and inherited timing from balancer cluster tests. Signals are delegated balancer success and utilization convergence for all three SASL quality-of-protection modes.
