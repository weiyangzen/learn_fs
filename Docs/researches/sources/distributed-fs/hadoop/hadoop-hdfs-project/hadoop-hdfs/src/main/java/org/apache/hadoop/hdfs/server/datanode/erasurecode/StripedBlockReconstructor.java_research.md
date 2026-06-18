<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/erasurecode/StripedBlockReconstructor.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/erasurecode/StripedBlockReconstructor.java

## Purpose

`StripedBlockReconstructor` is the runnable task that reconstructs missing striped internal blocks and streams the reconstructed bytes to target DataNodes.

## Important APIs, Types, And Functions

- Constructor creates a `StripedWriter` for target handling.
- `hasValidTargets()` delegates target validation to the writer.
- `run()` initializes decoder, optional validator, reader, writer, runs reconstruction, sends end packets, updates metrics, decrements xmits, and cleans resources.
- `reconstruct()` loops over target length: throttle reads, read minimum sources, decode, throttle writes, transfer to targets, update metrics, advance position, and clear buffers.
- `reconstructTargets` performs decode and optional validation for current outputs.

## Control Flow

The task runs in the worker reconstruction pool. Each loop reconstructs up to the striped read buffer size or remaining target length. If all target transfers fail, it throws. The `finally` block always decrements xmits submitted, records task and byte metrics, closes reader/writer buffers, and releases decoder resources.

## State And Persistence

State is inherited reconstructor state plus the `StripedWriter`. Persistent effects are network writes that create reconstructed internal block replicas on target DataNodes. Metrics record read, remote-read, write, decode, validation, and task counts.

## Dependencies And Integration Points

It integrates `ErasureCodingWorker`, `StripedReader`, `StripedWriter`, raw EC decoder, optional `DecodingValidator`, DataNode read/write throttlers, `DataNodeMetrics`, and `DataNodeFaultInjector`.

## Risks And Edge Cases

Packet acknowledgements from targets are not checked, matching block replication behavior but leaving a window where reconstruction appears sent without confirmation. Validation can detect bad decoding but costs time. Xmit accounting must match enqueue accounting even after constructor or runtime failures.

## Test Signals

Tests should cover successful reconstruction, read and write throttling, partial final buffers, all-target failure, validation failure, metric updates, xmit decrement, resource cleanup, and target buffer limit adjustment for short internal blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/erasurecode/StripedBlockReconstructor.java -->
