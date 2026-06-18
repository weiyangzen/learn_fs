# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/balancer/Matcher.java

## Purpose

`Matcher` is a small topology predicate interface used by balancer planning code to classify whether two nodes satisfy a desired locality relationship.

## Important APIs, Types, and Functions

The interface defines `match(NetworkTopology cluster, Node left, Node right)`. Built-in instances are `SAME_NODE_GROUP`, `SAME_RACK`, and `ANY_OTHER`, each with a descriptive `toString()`.

## Control Flow

`SAME_NODE_GROUP` delegates to `NetworkTopology.isOnSameNodeGroup`, `SAME_RACK` delegates to `isOnSameRack`, and `ANY_OTHER` returns true when the two `Node` references are not the same object.

## State and Persistence Behavior

The matchers are stateless singleton anonymous classes. There is no persistence or mutation.

## Dependencies and Integration Points

It depends on Hadoop `NetworkTopology` and `Node`. It integrates with balancer matching and source/target selection phases that need to try same-node-group, same-rack, then broader candidates.

## Risks and Edge Cases

`ANY_OTHER` uses reference inequality instead of `equals`, so two distinct objects representing the same logical node would match. Node-group matching only makes sense when the topology implementation supports node groups. Null inputs are not defended here and rely on callers/topology behavior.

## Test Signals

Tests should assert same-rack and same-node-group delegation on representative topologies, `ANY_OTHER` reference behavior, `toString()` values, and behavior when node-group awareness is absent or topology stubs return false.
