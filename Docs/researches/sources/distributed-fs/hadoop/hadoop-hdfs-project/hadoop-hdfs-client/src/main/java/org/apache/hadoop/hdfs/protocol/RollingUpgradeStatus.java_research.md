# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/RollingUpgradeStatus.java

## Purpose
`RollingUpgradeStatus` is the base status object for rolling upgrade state, carrying block pool ID and finalized flag.

## APIs and Behavior
The constructor initializes final fields. `getBlockPoolId()` and `isFinalized()` expose state. Equality compares block pool ID and finalized flag, while hash code uses block pool ID only. `toString()` renders the block pool ID.

## State, Dependencies, and Integration
The object is immutable and used as the superclass for `RollingUpgradeInfo`. It integrates with NameNode rolling-upgrade RPC responses.

## Risks and Test Signals
Hash code omits finalized status while equality includes it, which is legal but can increase collisions. Null block pool IDs will break hash/equality. Tests should cover equality/hash contract, finalized differences, null handling if protocol conversion allows it, and status display.
