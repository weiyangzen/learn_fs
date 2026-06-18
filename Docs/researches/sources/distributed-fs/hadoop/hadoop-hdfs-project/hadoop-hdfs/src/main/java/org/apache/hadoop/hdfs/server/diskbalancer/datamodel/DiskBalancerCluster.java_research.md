# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/diskbalancer/datamodel/DiskBalancerCluster.java

Purpose: top-level diskbalancer model representing DataNodes, inclusion/exclusion selections, node lookup indexes, output metadata, and plan computation for selected nodes.

Important APIs/types/functions: constructors initialize node lists and lookup maps or bind a `ClusterConnector`. `parseJson()`/`toJson()` serialize cluster snapshots. `readClusterInfo()` pulls nodes from the connector and builds IP, lowercase hostname, and UUID maps. Inclusion/exclusion setters accumulate sets. `setNodesToProcess()` defines the planning scope. `createSnapshot()` writes JSON to a local path. `computePlan()` creates a bounded thread pool, gets `GreedyPlanner` instances from `PlannerFactory`, submits one `Callable<NodePlan>` per node, and collects plans. `computePoolSize()` uses a one-thread-per-100-nodes heuristic capped at 100 and rounded in tens.

Control flow: commands read cluster info, resolve nodes by lookup maps, set nodes to process, and call `computePlan()`. Each planner is isolated to a node, enabling parallel planning. Exceptions in planner futures are logged and skipped rather than aborting the full plan list.

State and persistence behavior: JSON serialization persists cluster state for plan snapshots. `nodesToProcess`, lookup maps, and connector are ignored by Jackson. `outputpath` supports local snapshot writing. Inclusion/exclusion lists are stored but this file does not apply them during `readClusterInfo()` or `computePlan()`.

Dependencies and integration points: uses Jackson, `JsonUtil`, `ClusterConnector`, planner interfaces, `FileUtils`, and executor services. It is the bridge from connector data to planner output consumed by `PlanCommand`.

Risks: `computePlan()` never shuts down its `ExecutorService`, which can leak threads in long-lived callers. `computePoolSize(0)` can return 0; currently guarded by `nodesToProcess` use but worth protecting if empty lists are passed. Inclusion/exclusion semantics are documented but not enforced in visible code. Future exceptions are swallowed after logging, so partial planning may look successful.

Test signals: diskbalancer model/planner tests and `TestDiskBalancerCommand` validate JSON snapshots, node lookup, and plan computation on test clusters.
