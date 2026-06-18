# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestParallelShortCircuitReadNoChecksum.java

## Purpose
This subclass validates the modern short-circuit local read path when client short-circuit checksum verification is skipped.

## Important APIs, Types, And Functions
It mirrors `TestParallelShortCircuitRead` but sets `HdfsClientConfigKeys.Read.ShortCircuit.SKIP_CHECKSUM_KEY` to true. It uses `TemporarySocketDirectory`, `DomainSocket`, `DFS_DOMAIN_SOCKET_PATH_KEY`, `DFSInputStream.tcpReadsDisabledForTesting`, and inherited parallel-read tests.

## Control Flow
Setup is skipped if domain sockets cannot load. Otherwise the cluster is configured for short-circuit local reads over a temporary domain socket path, with TCP reads disabled and checksum skipping enabled. The inherited concurrent workloads verify returned bytes against known data.

## State And Persistence
State is short-lived client/cluster configuration plus the static TCP-disable test flag. No NameNode or DataNode restart persistence is exercised.

## Dependencies And Integration Points
The file integrates the short-circuit local reader, checksum-skip option, domain socket native support, and the base read utility.

## Risks
Because byte validation still happens in the test, corruption should be caught by comparison even when HDFS checksum verification is skipped. Platform domain socket absence skips the path. Static testing flags and socket cleanup remain shared-environment risks.

## Test Signals
Signals are successful inherited copying/direct/mixed/no-checksum workloads while short-circuit checksum skipping is enabled and TCP fallback is disabled.
