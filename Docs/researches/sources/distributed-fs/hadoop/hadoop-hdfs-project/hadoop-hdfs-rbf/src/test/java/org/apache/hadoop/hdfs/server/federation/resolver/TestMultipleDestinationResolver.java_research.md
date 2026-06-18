# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/resolver/TestMultipleDestinationResolver.java

## Purpose
This test validates `MultipleDestinationMountTableResolver`, especially destination ordering strategies for mounts with more than one subcluster.

## Important APIs, Types, and Functions
The setup uses `MultipleDestinationMountTableResolver`, `MountTable.setDestOrder()`, `DestinationOrder` values `HASH`, `HASH_ALL`, `LOCAL`, `RANDOM`, and `LEADER_FOLLOWER`, `PathLocation`, `RemoteLocation`, `PathLocation.prioritizeDestination()`, and `HashResolver.extractTempFileName()`.

## Control Flow
Setup registers single-destination `/tmp`, default multi-destination `/`, hash mounts `/hash` and `/hashall`, local and random mounts, read-only multi-destination `/readonly`, and a leader-follower mount with insertion order. Tests assert even distribution for hash-all and random paths, first-level stickiness for hash, hard-coded hash-all examples, single-destination passthrough, same-subcluster resolution for files below a chosen parent directory, temp-file-name extraction for copy/speculation patterns, read-only hashing behavior, leader-follower first destination selection, local default selection, random resolver variability across repeated calls, and explicit destination prioritization.

## State and Persistence
State is the in-memory mount table and resolver cache. There is no router, membership store, or filesystem persistence in this test.

## Dependencies and Integration Points
The test integrates all built-in destination-order resolvers through the multiple-destination resolver. It is a behavioral contract for router routing decisions when a mount table entry has multiple `RemoteLocation` targets.

## Risks and Test Signals
Hash expectations encode deterministic hashing details and may need updates if the hash algorithm changes. Random distribution tests depend on probability but use enough iterations to expect all three subclusters. Passing tests signal stable destination selection, parent-child stickiness where required, temp-file canonicalization, and correct ordering delegation for local/random/leader-follower modes.
