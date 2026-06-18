# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/resolver/order/TestLeaderFollowerResolver.java

## Purpose
This test verifies `LeaderFollowerResolver`, which preserves a configured leader destination as first choice for a multi-destination mount.

## Important APIs, Types, and Functions
The test uses `LeaderFollowerResolver`, `MultipleDestinationMountTableResolver`, `DestinationOrder.LEADER_FOLLOWER`, `MountTable`, `PathLocation`, and `RemoteLocation`.

## Control Flow
It creates a mocked router, constructs a multiple-destination resolver, registers the leader-follower ordering resolver, and adds `/local` with a `LinkedHashMap` destination order of subcluster2, subcluster0, subcluster1. Resolving `/local/file0.txt` must return subcluster2 as the first destination.

## State and Persistence
All state is local to the resolver and mount entry. There is no membership data, state store, or persistent filesystem.

## Dependencies and Integration Points
The test depends on insertion-order preservation through `LinkedHashMap` and destination ordering delegation from `MultipleDestinationMountTableResolver`.

## Risks and Test Signals
The test is intentionally narrow and does not inspect follower order beyond the first destination. Passing it signals that leader-follower mounts preserve the configured leader as the default route.
