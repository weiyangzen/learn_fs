# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/diskbalancer/planner/package-info.java

Purpose: package-level documentation for diskbalancer planners.

Important APIs/types/functions: documents the conceptual loop over `DiskBalancerVolumeSet`: plan a move, add a step, apply the step to current state, repeat until balanced.

Control flow: documentation mirrors `GreedyPlanner` simulation, where each step modifies the modeled state before computing the next step.

State and persistence behavior: none directly; contextualizes `NodePlan` and `Step` artifacts.

Dependencies and integration points: frames planner package as the bridge between data model and DataNode-executable plan.

Risks: pseudocode names differ from concrete API (`planner.plan(current, threshold)` vs current `Planner.plan(node)`), so readers should inspect actual classes.

Test signals: not directly tested.
