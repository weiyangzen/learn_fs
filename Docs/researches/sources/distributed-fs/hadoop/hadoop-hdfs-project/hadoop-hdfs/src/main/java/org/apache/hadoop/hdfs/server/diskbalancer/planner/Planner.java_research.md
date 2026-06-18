# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/diskbalancer/planner/Planner.java

Purpose: interface for diskbalancer planning algorithms.

Important APIs/types/functions: single method `NodePlan plan(DiskBalancerDataNode node) throws Exception`.

Control flow: `DiskBalancerCluster.computePlan()` obtains a planner and calls `plan()` per selected node. Implementations decide how to transform volume state into a sequence of `Step`s.

State and persistence behavior: none at interface level.

Dependencies and integration points: implemented by `GreedyPlanner`; constructed by `PlannerFactory`; output consumed as `NodePlan`.

Risks: broad exception signature pushes planner-specific failures into caller logging. Any future implementation must preserve `NodePlan` serialization and DataNode executor compatibility.

Test signals: planner factory and greedy planner tests indirectly cover the interface contract.
