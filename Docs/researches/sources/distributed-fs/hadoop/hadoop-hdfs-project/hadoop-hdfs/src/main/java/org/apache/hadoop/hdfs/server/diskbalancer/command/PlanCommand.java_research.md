# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/diskbalancer/command/PlanCommand.java

Purpose: implements `hdfs diskbalancer -plan <node>`, generating a disk move plan for one DataNode and writing both a pre-plan cluster snapshot and the plan JSON to a diskbalancer output directory.

Important APIs/types/functions: constructor registers `-outfile`, `-bandwidth`, `-threshold`, `-maxerror`, `-verbose`, and `-plan`. `execute()` validates a target node, parses optional bandwidth/error limits, reads cluster state, creates output paths, resolves the DataNode, writes a `BEFORE_TEMPLATE` cluster JSON snapshot, computes plans via `DiskBalancerCluster.computePlan()`, applies per-step bandwidth/error parameters, writes `PLAN_TEMPLATE` JSON, and optionally prints a table of `Step` source/destination/size/type values. `getThresholdPercentage()` bounds CLI threshold to `(0,100]` or falls back to `DFS_DISK_BALANCER_PLAN_THRESHOLD`. `setPlanParams()` mutates generated `Step` settings.

Control flow: target selection is single-node. The command snapshots before planning, populates volume paths through DataNode RPC for readability, sets `nodesToProcess` on the cluster, asks the cluster to compute plans, and writes only the first resulting `NodePlan`. No plan is written if there are no `volumeSetPlans`.

State and persistence behavior: writes two durable artifacts into HDFS/local output: a full cluster snapshot before planning and a node-specific plan JSON. It stores threshold, bandwidth, and max error as command fields and mutates each generated step before persistence.

Dependencies and integration points: integrates `Command`, `DiskBalancerCluster`, `DiskBalancerDataNode`, planner `NodePlan`/`Step`, `DiskBalancerCLI` file templates, and DFS config defaults. Generated plan JSON is consumed by `ExecuteCommand` and DataNode diskbalancer executor logic.

Risks: bandwidth and max error are parsed with `Integer.parseInt()` without local range handling, so bad numeric strings fail the command. The output directory is created before node path population and planning, so later failures may leave a partial snapshot directory. Plan freshness depends on timestamp and later DataNode validation. Only the first plan is written, matching single-node invocation but important if future code broadens `nodesToProcess`.

Test signals: `TestDiskBalancerCommand` validates plan generation, output text, invalid nodes, report/plan option errors, and force/execute compatibility.
