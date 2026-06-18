# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestParallelUnixDomainRead.java

## Purpose
This subclass runs the shared parallel-read workload over UNIX domain socket data transfer while short-circuit local reads are disabled.

## Important APIs, Types, And Functions
`setupCluster` skips if domain sockets are unavailable, disables TCP reads, creates a `TemporarySocketDirectory`, configures `DFS_DOMAIN_SOCKET_PATH_KEY`, disables `Read.ShortCircuit.KEY`, enables `DFS_CLIENT_DOMAIN_SOCKET_DATA_TRAFFIC`, disables bind-path validation, and delegates to the base setup with replication one. `before` skips when domain sockets failed to load.

## Control Flow
The subclass sets transport options only. Inherited tests then perform multi-threaded positional and seek/read workloads; because TCP is disabled and short-circuit is off, data transfer should use UNIX domain sockets.

## State And Persistence
State is transport configuration, temporary socket path, and inherited static cluster/client state. No persistence behavior is involved.

## Dependencies And Integration Points
It integrates HDFS domain socket data traffic, `DomainSocket`, `TemporarySocketDirectory`, and common DFSInputStream read paths.

## Risks
Domain socket availability determines whether tests run. The static TCP-disable flag and socket directory cleanup need external lifecycle hygiene. Because short-circuit is disabled, failures distinguish domain socket data-transfer regressions from local short-circuit reader regressions.

## Test Signals
Signals are inherited parallel-read byte correctness and successful workload completion using domain socket data traffic without short-circuit local reads.
