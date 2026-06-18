# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestParallelShortCircuitReadUnCached.java

## Purpose
This subclass is a regression test for uncached short-circuit local reads, stale sockets, and encrypted-transfer configuration not interfering with short-circuit local reads.

## Important APIs, Types, And Functions
`setupCluster` creates a temporary socket directory, enables short-circuit reads and domain-socket data traffic, enables data-transfer encryption and block access tokens, disables short-circuit checksum skipping, sets a short DataNode socket reuse keepalive, configures client socket cache expiry/capacity, sets short-circuit streams cache size to zero, disables bind-path validation, disables TCP reads, and delegates to the base setup. `before` skips if domain sockets are unavailable.

## Control Flow
After setup, inherited parallel-read workloads repeatedly open and read files without using the FileInputStream cache. The config deliberately allows stale socket scenarios and domain socket traffic while forcing local read behavior.

## State And Persistence
State includes socket cache and streams cache settings, encrypted transfer and block token settings, temporary socket path, and inherited read workload state. No persistence is tested.

## Dependencies And Integration Points
It integrates HDFS short-circuit local reads, domain socket data traffic, client socket caching, DataNode socket reuse, data transfer encryption, block access tokens, and base DFSInputStream concurrency tests.

## Risks
The test is environment-sensitive to domain socket support. It intentionally combines features that can interact subtly: encryption, tokens, socket caching, and disabled local stream cache. Static TCP-disable state must be isolated by the broader test suite.

## Test Signals
Signals are inherited read correctness with no FileInputStream cache, no TCP fallback, and no failure caused by encryption/token settings when using short-circuit local reads.
