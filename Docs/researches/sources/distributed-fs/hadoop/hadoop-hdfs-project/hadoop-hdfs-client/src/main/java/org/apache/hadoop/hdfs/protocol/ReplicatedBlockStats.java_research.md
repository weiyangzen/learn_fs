# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/ReplicatedBlockStats.java

## Purpose
`ReplicatedBlockStats` is the public/evolving statistics DTO for contiguous replicated blocks returned by `ClientProtocol.getReplicatedBlockStats()`.

## APIs and Behavior
It stores low-redundancy, corrupt, missing replica, missing replication-one, bytes-in-future, and pending-deletion counts, plus optional badly distributed and highest-priority low-redundancy counts. Getters and `has...` methods expose required and optional metrics. `toString()` renders present optional fields. `merge(Collection<ReplicatedBlockStats>)` sums counters across inputs and includes optional metrics only if both optional categories are present somewhere.

## State, Dependencies, and Integration
The class is immutable. It integrates with NameNode block manager statistics, admin reporting, and federation aggregation.

## Risks and Test Signals
Unlike `ECBlockGroupStats`, this class does not override `equals()`/`hashCode()`, so object identity is used in tests/collections. `merge()` can drop a single present optional category if the other optional category is absent. Tests should cover merge optional-field combinations, toString formatting, identity versus value comparison expectations, and large-count aggregation.
