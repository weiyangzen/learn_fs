# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/resolver/FederationNamenodeServiceState.java

Purpose: enum representing Namenode service state in federation. Its declaration order is the resolver priority order.

Important APIs: states include high-priority routable states such as `ACTIVE`, `OBSERVER`, and `STANDBY`, plus degraded/admin states such as `UNAVAILABLE`, `EXPIRED`, and `DISABLED`. `getState(HAServiceState)` maps HA protocol states to federation states, returning `ACTIVE`, `OBSERVER`, or `STANDBY`.

Control flow and state: stateless enum. `NamenodePriorityComparator` uses enum ordering directly, so any reordering changes routing behavior.

Dependencies and integration points: bridges HA service state from Namenode monitoring into State Store membership records and router selection.

Risks: declaration order is behavioral. Missing or new HA states default to standby-style handling unless mapping is updated. `EXPIRED` and `DISABLED` need explicit filtering/marking in resolver logic.

Test signals: assert HA mapping and priority comparator ordering, especially observer-read behavior and disabled namespace marking.
