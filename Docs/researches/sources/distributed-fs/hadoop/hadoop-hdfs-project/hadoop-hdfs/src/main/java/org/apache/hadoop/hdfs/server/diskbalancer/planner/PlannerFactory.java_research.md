# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/diskbalancer/planner/PlannerFactory.java

Purpose: factory for planner implementations.

Important APIs/types/functions: constant `GREEDY_PLANNER = "greedyPlanner"`. `getPlanner(plannerName, node, threshold)` returns a new `GreedyPlanner` for that name and logs node details in debug mode; otherwise throws `IllegalArgumentException`. Constructor is private.

Control flow: `DiskBalancerCluster.computePlan()` always requests `GREEDY_PLANNER`, so this factory is the extension point for future algorithms.

State and persistence behavior: stateless.

Dependencies and integration points: depends on `DiskBalancerDataNode` for logging and `GreedyPlanner` construction.

Risks: string comparison has no null guard for `plannerName`; callers must pass a valid constant. Adding planners requires updating factory and likely plan compatibility tests.

Test signals: planner tests cover recognized/unrecognized planner names and greedy planner creation.
