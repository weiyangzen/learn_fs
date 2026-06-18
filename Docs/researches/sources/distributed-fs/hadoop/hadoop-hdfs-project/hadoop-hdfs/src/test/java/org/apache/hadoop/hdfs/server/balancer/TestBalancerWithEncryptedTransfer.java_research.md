# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/balancer/TestBalancerWithEncryptedTransfer.java

## Purpose
This wrapper test verifies that the standard balancer scenarios work when HDFS data transfer encryption and block access tokens are enabled.

## Important APIs, Types, and Functions
The file uses `HdfsConfiguration`, `DFSConfigKeys.DFS_ENCRYPT_DATA_TRANSFER_KEY`, `DFS_BLOCK_ACCESS_TOKEN_ENABLE_KEY`, and delegates to `TestBalancer.testBalancer0Internal`, `testBalancer1Internal`, and `testBalancer2Internal`.

## Control Flow
`setUpConf` enables encrypted data transfer and block access tokens on a shared configuration. Each test constructs a fresh `TestBalancer` and runs one of the core internal scenarios: balanced cluster plus new node, uneven distribution, and default-constructor balancing. The delegated tests initialize normal balancer configuration on top of the security settings.

## State and Persistence Behavior
This class owns only a configuration instance. Cluster creation, data files, token behavior, and shutdown are handled by the delegated `TestBalancer` methods and their internal `finally` blocks.

## Dependencies and Integration Points
The integration point is between balancer block movement and encrypted HDFS data transfer with block tokens. It ensures balancer copy paths can authenticate and move blocks under encryption rather than only in simple unencrypted clusters.

## Risks and Test Signals
Risks are inherited from `TestBalancer` plus encrypted transfer setup. Signals are delegated success: each scenario must complete within 60 seconds and satisfy `TestBalancer` exit-code and utilization checks.
