# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/resolver/order/LeaderFollowerResolver.java

Purpose: ordering policy for disaster-tolerant leader/follower mount entries where the first configured destination is the leader.

Important API: `getFirstNamespace` returns `loc.getDefaultLocation().getNameserviceId`, logging and returning null on failure.

Control flow and state: stateless; all ordering meaning comes from administrator-provided destination order in the mount table.

Dependencies and integration points: registered for `DestinationOrder.LEADER_FOLLOWER` in `MultipleDestinationMountTableResolver`. Directory creation semantics include this order in `FOLDER_ALL`.

Risks: no health or space check is performed; failover is left to later sequential invocation behavior. Misordered mount entries make the wrong cluster leader.

Test signals: first destination selection, empty destination failure, and preservation of configured order after prioritization.
