# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/ECBlockGroupStats.java

## Purpose
`ECBlockGroupStats` is the public/evolving statistics DTO for striped erasure-coded block groups returned by `ClientProtocol.getECBlockGroupStats()`.

## APIs and Behavior
It stores low-redundancy, corrupt, missing, bytes-in-future, and pending-deletion counts plus optional `badlyDistributedBlocks` and `highestPriorityLowRedundancyBlocks`. Getters and `has...` methods distinguish absent optional metrics from zero values. `equals`, `hashCode`, and `toString` include all fields. `merge(Collection<ECBlockGroupStats>)` sums all required counters and only includes optional counters if at least one input had them.

## State, Dependencies, and Integration
The class is immutable and depends on Apache Commons Lang builders. It is used by NameNode block-management metrics, client/admin reporting, and federation-style aggregation.

## Risks and Test Signals
`merge()` returns a constructor without optional counters unless both optional categories are present somewhere; if only one optional metric family is present, it drops both optional sums. Tests should cover merge with none, one, and both optional metrics, toString visibility, equality, and overflow assumptions for large clusters.
