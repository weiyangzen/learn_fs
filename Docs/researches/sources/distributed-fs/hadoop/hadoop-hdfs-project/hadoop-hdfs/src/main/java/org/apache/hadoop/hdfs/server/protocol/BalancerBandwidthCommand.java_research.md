<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/BalancerBandwidthCommand.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/BalancerBandwidthCommand.java

## Purpose

`BalancerBandwidthCommand` is a `DatanodeCommand` instructing a DataNode to update the maximum bandwidth it may use for block balancing.

## Important APIs and types

- Package-private no-arg constructor defaults bandwidth to zero.
- Public constructor sets action `DatanodeProtocol.DNA_BALANCERBANDWIDTHUPDATE`.
- `getBalancerBandwidthValue()` returns bytes per second.

## Control flow

The NameNode/admin path creates this command after `dfsadmin -setBalancerBandwidth`; DataNodes receive it through heartbeat command processing and apply the new bandwidth limit.

## State and persistence behavior

The command is immutable and carries one `long` payload. Any lasting effect is in the receiving DataNode's runtime balancer bandwidth setting, not in this object.

## Dependencies and integration points

Extends `DatanodeCommand` and depends on `DatanodeProtocol` action constants. Covered by balancer/admin command flows.

## Risks and edge cases

There is no local validation for negative or extreme bandwidth; validation must occur before construction or on the receiver. The source comment misspells the admin command, but the class behavior is unaffected.

## Test signals

`TestBalancerBandwidth` and DFSAdmin tests should verify command creation, heartbeat delivery, and DataNode-side bandwidth update behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/BalancerBandwidthCommand.java -->
