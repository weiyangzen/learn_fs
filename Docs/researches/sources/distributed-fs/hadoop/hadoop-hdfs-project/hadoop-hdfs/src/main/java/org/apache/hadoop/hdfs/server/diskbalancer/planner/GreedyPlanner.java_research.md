# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/diskbalancer/planner/GreedyPlanner.java

Purpose: greedy diskbalancer planner that repeatedly schedules the largest feasible move between the most over-utilized and most under-utilized volumes within each storage-type volume set.

Important APIs/types/functions: implements `Planner.plan(DiskBalancerDataNode)`. `plan()` creates a `NodePlan`, loops while the node needs balancing, and calls `balanceVolumeSet()` for each set. `balanceVolumeSet()` copies a volume set, removes skipped/failed volumes, picks low/high volumes from the sorted queue, computes a `MoveStep`, applies it to simulated usage, and appends the step. `computeMove()` calculates `maxLowVolumeCanReceive` and `maxHighVolumeCanGive` relative to ideal usage and returns a `MoveStep` with source high volume and destination low volume. `applyStep()` mutates simulated used bytes and recomputes density.

Control flow: planning is iterative simulation. It stops only when all volume sets report no balancing needed under threshold. After finishing a set, it writes node name, UUID, timestamp, and port into the `NodePlan`.

State and persistence behavior: planner holds only threshold. It creates `MoveStep` objects that serialize into plan JSON. The simulation mutates the copied volume set's volume objects and skip flags to model future state; no HDFS data moves happen here.

Dependencies and integration points: depends on diskbalancer data model, `NodePlan`, `MoveStep`, `Step`, and `Time`. Constructed by `PlannerFactory`, called by `DiskBalancerCluster.computePlan()`, output consumed by `PlanCommand` and DataNode execution.

Risks: no explicit iteration cap; bad density/queue behavior could loop. `printQueue()` assumes non-empty queue in debug mode. The `DiskBalancerVolumeSet` copy is shallow, so simulations may share volume objects with the source model depending on construction path. Equal density comparator behavior can remove queue entries. Threshold semantics depend on `DiskBalancerVolumeSet.isBalancingNeeded()`.

Test signals: diskbalancer planner tests and command plan tests validate generated step counts, source/destination choices, and no-plan cases.
