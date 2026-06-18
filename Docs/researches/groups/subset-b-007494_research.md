# subset-b-007494 research

Grouped research for the requested Hadoop HDFS diskbalancer, mover, ACL, and BackupNode source files. Each section is delimited for reconciliation into the corresponding source-tree-aligned per-file report.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/diskbalancer/command/Command.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/diskbalancer/command/Command.java

Purpose: abstract base for `hdfs diskbalancer` subcommands. It centralizes CLI option validation, cluster discovery, output directory management, DataNode RPC proxy creation, node lookup, node-list parsing, plan/snapshot file IO, and human-facing output recording.

Important APIs/types/functions: `execute(CommandLine)` and `printHelp()` are abstract command hooks. `readClusterInfo()` selects a `ClusterConnector` through `ConnectorFactory` and builds a `DiskBalancerCluster`. `setOutputPath()`, `create()`, and `open()` manage HDFS/local filesystem paths. `getNode()`, `getNodeList()`, and `getNodes()` resolve hostnames, IPs, UUIDs, comma lists, and `file://` host files. `getDataNodeProxy()` creates `ClientDatanodeProtocol` clients using the DataNode Kerberos principal. `parseTopNodes()` implements common `-top` validation. `populatePathNames()` asks the DataNode for the diskbalancer volume-name map and attaches physical paths to `DiskBalancerVolume` objects.

Control flow: concrete commands construct with valid option names, call `verifyCommandOptions()`, call `readClusterInfo()` if they need cluster state, optionally call `setOutputPath()`, and then use the shared lookup/RPC/IO helpers. `readClusterInfo()` starts from `FileSystem.getDefaultUri(getConf())`; `file` schemes become JSON model connectors and non-file schemes become NameNode connectors. `populatePathNames()` short-circuits for local/file model clusters and otherwise performs a DataNode RPC.

State and persistence behavior: the command keeps mutable `clusterURI`, `FileSystem`, `DiskBalancerCluster`, `topNodes`, `PrintStream`, and `diskBalancerLogs`. `setOutputPath()` creates a timestamped default under `/system/diskbalancer` or a user-supplied output path, and refuses an existing target directory to avoid overlapping runs. `close()` closes the `FileSystem`; comments tie this to cleanup around balancer id-file usage.

Dependencies and integration points: integrates with Commons CLI, Hadoop `FileSystem`, `ClientDatanodeProtocol`, `DFSUtilClient`, `UserGroupInformation`, `HostsFileReader`, diskbalancer data model/planner command stack, and `DiskBalancerCLI` constants. DataNode RPCs depend on `DFS_DATANODE_KERBEROS_PRINCIPAL_KEY` and socket factory setup.

Risks: command option validation only checks long option names registered by each subclass, so new options must be explicitly added. `parseTopNodes()` dereferences `cluster`, so callers must read cluster info first. `getNodeByName()` lowercases in the cluster but `getNode()` passes user input as-is to cluster lookup, relying on `DiskBalancerCluster` to normalize. `populatePathNames()` trusts DataNode JSON and only fills paths for known UUIDs. Output path collision is treated as another instance and aborts even for stale directories.

Test signals: `TestDiskBalancerCommand` exercises CLI option validation, report behavior, query behavior, execute plan validity, host-file parsing, and JSON connector-backed node lookup. Diskbalancer integration tests also validate generated plans and DataNode RPC paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/diskbalancer/command/Command.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/diskbalancer/command/ExecuteCommand.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/diskbalancer/command/ExecuteCommand.java

Purpose: implements `hdfs diskbalancer -execute <planfile>`, reading a serialized `NodePlan` and submitting it to the target DataNode for asynchronous diskbalancer execution.

Important APIs/types/functions: constructor registers `-execute` and `-skipDateCheck`. `execute()` validates options, opens the plan file through `Command.open()`, reads UTF-8 JSON, checks `-skipDateCheck`, and calls `submitPlan()`. `submitPlan()` parses `NodePlan`, derives `<nodeName>:<port>`, computes a SHA-1 plan hash, creates a `ClientDatanodeProtocol` proxy, and invokes `submitDiskBalancerPlan(planHash, PLAN_VERSION, planFile, planData, skipDateCheck)`.

Control flow: the command is intentionally thin: local file/HDFS read, optional warning for forced old-plan execution, DataNode RPC submit, and immediate return. `DiskBalancerException` from the DataNode is logged with result code and rethrown for the CLI.

State and persistence behavior: no durable local state is held beyond inherited command state. The DataNode receives the entire JSON plan and hash and owns execution state after submission. The input plan file path is passed through to the DataNode as identifying metadata.

Dependencies and integration points: depends on `NodePlan.parseJson()` for safe plan deserialization, Commons Codec SHA-1, Hadoop FS streams, and `ClientDatanodeProtocol`. It is paired with `PlanCommand` output and `QueryCommand` status checks.

Risks: plan freshness is enforced by the DataNode unless `-skipDateCheck` is used; the command logs but does not otherwise guard against stale plans. DataNode address comes from plan fields, so malformed or hostile plan JSON must be rejected by `NodePlan.parseJson()` and DataNode-side validation. The SHA-1 hash is an identity/check value rather than a modern collision-resistant security primitive.

Test signals: `TestDiskBalancerCommand` includes execute-plan validity, invalid plan content, force execute, and DataNode exception cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/diskbalancer/command/ExecuteCommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/diskbalancer/command/HelpCommand.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/diskbalancer/command/HelpCommand.java

Purpose: implements top-level and command-specific help for the diskbalancer CLI.

Important APIs/types/functions: constructor registers `-help`. `execute()` accepts null or blank help arguments for generic help, validates options otherwise, normalizes the requested subcommand to lowercase, constructs the corresponding command (`PlanCommand`, `ExecuteCommand`, `QueryCommand`, `CancelCommand`, `ReportCommand`), and delegates `printHelp()`. `printHelp()` uses `HelpFormatter` with `DiskBalancerCLI.getHelpOptions()`.

Control flow: help resolution is a switch over `DiskBalancerCLI` command constants; unknown subcommands fall back to the generic help command. No cluster IO or RPCs occur.

State and persistence behavior: stateless apart from inherited configuration and print stream. It only writes to standard output via Commons CLI formatting.

Dependencies and integration points: depends on all command classes whose help it delegates to, plus `DiskBalancerCLI` option builders. Adding a new diskbalancer command requires updating this switch to expose command-specific help.

Risks: if command constants or option definitions drift, help text can become incomplete. Instantiating real command objects only for help is cheap here but means command constructors must avoid side effects.

Test signals: CLI command tests cover help argument handling indirectly through `DiskBalancerCLI` command parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/diskbalancer/command/HelpCommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/diskbalancer/command/PlanCommand.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/diskbalancer/command/PlanCommand.java

Purpose: implements `hdfs diskbalancer -plan <node>`, generating a disk move plan for one DataNode and writing both a pre-plan cluster snapshot and the plan JSON to a diskbalancer output directory.

Important APIs/types/functions: constructor registers `-outfile`, `-bandwidth`, `-threshold`, `-maxerror`, `-verbose`, and `-plan`. `execute()` validates a target node, parses optional bandwidth/error limits, reads cluster state, creates output paths, resolves the DataNode, writes a `BEFORE_TEMPLATE` cluster JSON snapshot, computes plans via `DiskBalancerCluster.computePlan()`, applies per-step bandwidth/error parameters, writes `PLAN_TEMPLATE` JSON, and optionally prints a table of `Step` source/destination/size/type values. `getThresholdPercentage()` bounds CLI threshold to `(0,100]` or falls back to `DFS_DISK_BALANCER_PLAN_THRESHOLD`. `setPlanParams()` mutates generated `Step` settings.

Control flow: target selection is single-node. The command snapshots before planning, populates volume paths through DataNode RPC for readability, sets `nodesToProcess` on the cluster, asks the cluster to compute plans, and writes only the first resulting `NodePlan`. No plan is written if there are no `volumeSetPlans`.

State and persistence behavior: writes two durable artifacts into HDFS/local output: a full cluster snapshot before planning and a node-specific plan JSON. It stores threshold, bandwidth, and max error as command fields and mutates each generated step before persistence.

Dependencies and integration points: integrates `Command`, `DiskBalancerCluster`, `DiskBalancerDataNode`, planner `NodePlan`/`Step`, `DiskBalancerCLI` file templates, and DFS config defaults. Generated plan JSON is consumed by `ExecuteCommand` and DataNode diskbalancer executor logic.

Risks: bandwidth and max error are parsed with `Integer.parseInt()` without local range handling, so bad numeric strings fail the command. The output directory is created before node path population and planning, so later failures may leave a partial snapshot directory. Plan freshness depends on timestamp and later DataNode validation. Only the first plan is written, matching single-node invocation but important if future code broadens `nodesToProcess`.

Test signals: `TestDiskBalancerCommand` validates plan generation, output text, invalid nodes, report/plan option errors, and force/execute compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/diskbalancer/command/PlanCommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/diskbalancer/command/QueryCommand.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/diskbalancer/command/QueryCommand.java

Purpose: implements `hdfs diskbalancer -query <node[,node...]>`, reporting the current diskbalancer plan status from one or more DataNodes.

Important APIs/types/functions: constructor registers `-query` and `-verbose`. `execute()` validates node input, deduplicates/sorts node strings through `TreeSet`, fills a default DataNode IPC port when no `host:port` is supplied, gets a `ClientDatanodeProtocol`, calls `queryDiskBalancerPlan()`, and prints `Plan File`, `Plan ID`, and result. With `-verbose`, it appends `DiskBalancerWorkStatus.currentStateString()`.

Control flow: the command performs no NameNode cluster discovery; it connects directly to each requested DataNode. On the first `DiskBalancerException`, it logs and rethrows rather than continuing to later nodes.

State and persistence behavior: no durable state. It emits status text to the command print stream and logs progress.

Dependencies and integration points: depends on `DFS_DATANODE_IPC_ADDRESS_KEY` default port, `NetUtils`, `ClientDatanodeProtocol`, and DataNode `DiskBalancerWorkStatus`. It is the operational counterpart to `ExecuteCommand`.

Risks: the host:port regex requires two to five digits and treats anything else as a bare host, so unusual address formats may get the default port appended. Partial failures abort the whole multi-node query. It does not use `Command.getNodes()` cluster resolution, so UUIDs are not resolved unless usable as network names.

Test signals: `TestDiskBalancerCommand` includes query without submit and multiple-node query cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/diskbalancer/command/QueryCommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/diskbalancer/command/ReportCommand.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/diskbalancer/command/ReportCommand.java

Purpose: implements `hdfs diskbalancer -report`, either listing the top DataNodes that would benefit from diskbalancer or printing detailed volume information for specified DataNodes.

Important APIs/types/functions: constructor registers `-report`, `-top`, and `-node`. `execute()` reads cluster info and dispatches to `handleNodeReport()` when `-node` is present or `handleTopReport()` otherwise. `handleTopReport()` reverse-sorts nodes by `DiskBalancerDataNode.compareTo()` and prints density summaries. `handleNodeReport()` resolves node names/IPs/UUIDs or `file://` host files through `Command.getNodes()`, catches invalid-node `DiskBalancerException` for user-friendly output, and calls `recordNodeReport()`. `recordNodeReport()` populates volume paths, formats usage/free ratios, capacity, failed/read-only/skip/transient flags, sorts volume lines, and appends them.

Control flow: top report is cluster-only and avoids DataNode path-name RPCs. Detailed node report does a DataNode RPC per resolved node to make volume paths human-readable. Invalid node lists are reported into output and return without throwing further.

State and persistence behavior: no durable files. It updates inherited `topNodes` and writes a text report. Cluster node density is computed during connector/model population and re-used for sorting.

Dependencies and integration points: connects `Command` node-list parsing, `DiskBalancerCluster`, `DiskBalancerVolumeSet`, `DiskBalancerVolume`, and `DiskBalancerCLI` option formatting. It is often used before planning to select candidates.

Risks: `parseTopNodes()` requires cluster initialization and throws for non-positive values. Detailed report output depends on DataNode volume-name support; without it, paths may remain UUID-like/null. Catching invalid nodes and returning can produce a successful CLI process with an error message in output depending on outer handling.

Test signals: `TestDiskBalancerCommand` has top report, default top, node report, invalid node, and host-file report tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/diskbalancer/command/ReportCommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/diskbalancer/command/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/diskbalancer/command/package-info.java

Purpose: package-level documentation for diskbalancer CLI command implementations.

Important APIs/types/functions: declares package `org.apache.hadoop.hdfs.server.diskbalancer.command`; no executable API.

Control flow: none. It documents that the package contains commands for the diskbalancer command-line tool.

State and persistence behavior: none.

Dependencies and integration points: gives JavaDoc context to `Command`, `PlanCommand`, `ExecuteCommand`, `QueryCommand`, `ReportCommand`, help/cancel commands, and downstream generated docs.

Risks: minimal; package docs can become stale if command set changes.

Test signals: not directly tested.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/diskbalancer/command/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/diskbalancer/connectors/ClusterConnector.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/diskbalancer/connectors/ClusterConnector.java

Purpose: small abstraction hiding where diskbalancer cluster information comes from.

Important APIs/types/functions: `getNodes()` returns `List<DiskBalancerDataNode>` and may throw `Exception`; `getConnectorInfo()` returns a descriptive string for logs.

Control flow: implementations populate diskbalancer-native data model objects from a backing source, such as NameNode RPC storage reports or JSON files.

State and persistence behavior: the interface owns no state. Implementations may hold URIs, RPC clients, or parsed files.

Dependencies and integration points: consumed by `DiskBalancerCluster.readClusterInfo()` and constructed by `ConnectorFactory`. Implemented here by `DBNameNodeConnector` and `JsonNodeConnector`; tests also use in-memory/null connectors.

Risks: broad `throws Exception` simplifies implementations but pushes error classification to callers. Callers assume returned nodes already have volume density computed by `DiskBalancerDataNode.addVolume()`.

Test signals: diskbalancer command and data model tests use real, JSON, and test connectors to exercise this boundary.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/diskbalancer/connectors/ClusterConnector.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/diskbalancer/connectors/ConnectorFactory.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/diskbalancer/connectors/ConnectorFactory.java

Purpose: factory for selecting the diskbalancer cluster connector from a cluster URI.

Important APIs/types/functions: `getCluster(URI clusterURI, Configuration conf)` logs URI/scheme and returns `JsonNodeConnector` when `scheme.startsWith("file")`, otherwise `DBNameNodeConnector`. Constructor is private.

Control flow: binary dispatch on URI scheme. File URIs are treated as serialized cluster models; all other schemes are treated as live HDFS NameNode endpoints.

State and persistence behavior: stateless; returns new connector instances each call.

Dependencies and integration points: used by `Command.readClusterInfo()`. Depends on URI-to-URL conversion for file connectors and `DBNameNodeConnector` construction for live clusters.

Risks: `startsWith("file")` is permissive; unexpected schemes starting with that prefix would be treated as JSON. Non-file URIs must be acceptable to `NameNodeConnector`.

Test signals: command tests create JSON connectors and live mini-cluster connectors; connector selection is indirectly covered by plan/report tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/diskbalancer/connectors/ConnectorFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/diskbalancer/connectors/DBNameNodeConnector.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/diskbalancer/connectors/DBNameNodeConnector.java

Purpose: live-cluster connector that reads DataNode and storage-volume information from the NameNode for diskbalancer.

Important APIs/types/functions: constructor disables `NameNodeConnector` id-file writing and creates a `NameNodeConnector` named `DiskBalancer` with `/system/diskbalancer.id`. `getNodes()` calls `getLiveDatanodeStorageReport()`, maps each `DatanodeInfo` to `DiskBalancerDataNode`, maps each `StorageReport` to `DiskBalancerVolume`, and adds volumes to the node. `getConnectorInfo()` identifies the NameNode URI.

Control flow: for each live DataNode storage report, the connector sets node UUID/IP/hostname/IPC port, then iterates storage reports to set capacity, failed flag, DFS used, storage ID as UUID, skip flag for read-only-shared or failed volumes, storage type name, transient flag, and finally updates node density via `addVolume()`.

State and persistence behavior: holds `clusterURI` and a `NameNodeConnector`. It does not persist output but uses `NameNodeConnector` for NameNode RPC state. The static id path is configured but id-file writing is disabled because DataNode admission controls concurrent diskbalancer execution.

Dependencies and integration points: depends on HDFS balancer `NameNodeConnector`, `DatanodeStorageReport`, `StorageReport`, `DatanodeStorage`, and diskbalancer data model classes. Feeding this connector into `DiskBalancerCluster` powers report and plan commands on real clusters.

Risks: only live DataNodes are considered. `reserved` is not populated from storage reports here, so effective-capacity behavior depends on defaults or JSON/test data. Volume path is not available until later DataNode RPC path population. A failure connecting to NameNode aborts command execution.

Test signals: mini-cluster diskbalancer command tests exercise live storage report mapping; `DiskBalancerTestUtil` builds imbalanced DataNodes used by plan/execute tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/diskbalancer/connectors/DBNameNodeConnector.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/diskbalancer/connectors/JsonNodeConnector.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/diskbalancer/connectors/JsonNodeConnector.java

Purpose: file-backed connector that reads a serialized `DiskBalancerCluster` JSON model and returns its nodes.

Important APIs/types/functions: constructor stores a `URL`. `getNodes()` reads `clusterURI.getPath()` with Jackson `ObjectReader` for `DiskBalancerCluster`, logs the node count, and returns `cluster.getNodes()`. `getConnectorInfo()` describes the JSON cluster source.

Control flow: there is no transformation beyond Jackson deserialization. The JSON model must already contain the diskbalancer data model shape.

State and persistence behavior: holds only the source URL. It performs read-only local file access and returns in-memory model objects.

Dependencies and integration points: selected by `ConnectorFactory` for file URIs. Used for offline planning/reporting tests and hand-crafted cluster models under test resources.

Risks: deserialized nodes may not have lookup maps populated until `DiskBalancerCluster.readClusterInfo()` iterates them. Bad/missing JSON file errors propagate. The connector returns the model's existing nodes without recomputing density unless volume-set/node constructors and JSON data preserve needed state.

Test signals: `TestDiskBalancerCommand` uses JSON connector scenarios; package docs mention test resource JSON cluster samples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/diskbalancer/connectors/JsonNodeConnector.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/diskbalancer/connectors/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/diskbalancer/connectors/package-info.java

Purpose: package-level documentation for diskbalancer cluster data source connectors.

Important APIs/types/functions: declares package `org.apache.hadoop.hdfs.server.diskbalancer.connectors`; describes `DBNameNodeConnector`, `JsonNodeConnector`, and a test-oriented `NullConnector`.

Control flow: none.

State and persistence behavior: none.

Dependencies and integration points: frames the connector package as the source-normalization layer feeding `DiskBalancerCluster`.

Risks: mentions a `NullConnector` not in this specific source subset, so readers should look in tests or neighboring source for that implementation.

Test signals: aligns with test connector usage in diskbalancer tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/diskbalancer/connectors/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/diskbalancer/datamodel/DiskBalancerCluster.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/diskbalancer/datamodel/DiskBalancerCluster.java

Purpose: top-level diskbalancer model representing DataNodes, inclusion/exclusion selections, node lookup indexes, output metadata, and plan computation for selected nodes.

Important APIs/types/functions: constructors initialize node lists and lookup maps or bind a `ClusterConnector`. `parseJson()`/`toJson()` serialize cluster snapshots. `readClusterInfo()` pulls nodes from the connector and builds IP, lowercase hostname, and UUID maps. Inclusion/exclusion setters accumulate sets. `setNodesToProcess()` defines the planning scope. `createSnapshot()` writes JSON to a local path. `computePlan()` creates a bounded thread pool, gets `GreedyPlanner` instances from `PlannerFactory`, submits one `Callable<NodePlan>` per node, and collects plans. `computePoolSize()` uses a one-thread-per-100-nodes heuristic capped at 100 and rounded in tens.

Control flow: commands read cluster info, resolve nodes by lookup maps, set nodes to process, and call `computePlan()`. Each planner is isolated to a node, enabling parallel planning. Exceptions in planner futures are logged and skipped rather than aborting the full plan list.

State and persistence behavior: JSON serialization persists cluster state for plan snapshots. `nodesToProcess`, lookup maps, and connector are ignored by Jackson. `outputpath` supports local snapshot writing. Inclusion/exclusion lists are stored but this file does not apply them during `readClusterInfo()` or `computePlan()`.

Dependencies and integration points: uses Jackson, `JsonUtil`, `ClusterConnector`, planner interfaces, `FileUtils`, and executor services. It is the bridge from connector data to planner output consumed by `PlanCommand`.

Risks: `computePlan()` never shuts down its `ExecutorService`, which can leak threads in long-lived callers. `computePoolSize(0)` can return 0; currently guarded by `nodesToProcess` use but worth protecting if empty lists are passed. Inclusion/exclusion semantics are documented but not enforced in visible code. Future exceptions are swallowed after logging, so partial planning may look successful.

Test signals: diskbalancer model/planner tests and `TestDiskBalancerCommand` validate JSON snapshots, node lookup, and plan computation on test clusters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/diskbalancer/datamodel/DiskBalancerCluster.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/diskbalancer/datamodel/DiskBalancerDataNode.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/diskbalancer/datamodel/DiskBalancerDataNode.java

Purpose: data model for one DataNode, including identity, network address, volume sets grouped by storage type, volume count, and node data density used for report ranking.

Important APIs/types/functions: constructors initialize UUID and `volumeSets`. Standard getters/setters expose DataNode IP/name/port/UUID. `addVolume()` groups a `DiskBalancerVolume` into a `DiskBalancerVolumeSet` by storage type, creating the set with matching transient flag as needed, then recomputes node density. `computeNodeDensity()` sums absolute volume data densities across all volumes and updates volume count. `isBalancingNeeded()` delegates to all volume sets. `compareTo()` orders by node data density.

Control flow: connectors call setters and `addVolume()` for each storage report. Planner/report code reads volume sets and density. Sorting report output uses `Comparable` and reverse order to select high-density nodes.

State and persistence behavior: plain Java bean state serialized as part of cluster JSON. Density is derived but stored; every added volume recomputes set density and node density.

Dependencies and integration points: uses `DiskBalancerVolumeSet`, `DiskBalancerVolume`, and Hadoop `Preconditions`. Consumed by cluster lookup, report formatting, and greedy planning.

Risks: empty constructor does not initialize `volumeSets`, relying on Jackson to populate it; direct use must call setters or use UUID constructor. `equals()` compares UUID, but `hashCode()` delegates to `Object`, violating the equals/hashCode contract for hash collections. `compareTo()` subtracts doubles before comparing to zero, which is less direct than `Double.compare(this.nodeDataDensity, that.nodeDataDensity)`.

Test signals: data model tests and command tests validate node density sorting, volume grouping, and balancing need checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/diskbalancer/datamodel/DiskBalancerDataNode.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/diskbalancer/datamodel/DiskBalancerVolume.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/diskbalancer/datamodel/DiskBalancerVolume.java

Purpose: data model for a physical DataNode storage volume in diskbalancer planning and reporting.

Important APIs/types/functions: `parseJson()`/`toJson()` provide Jackson/JsonUtil serialization. Getters/setters cover path, capacity, storage type, used bytes, reserved bytes, UUID, failed, transient, skip, read-only, and volume data density. Derived methods include `getFreeSpace()`, `getUsedRatio()`, `getFreeRatio()`, `computeEffectiveCapacity()`, and `computeUsedPercentage()`. `setUsed()` clamps used bytes to capacity with a warning.

Control flow: connectors populate capacity/used/failure/storage identity; `DiskBalancerVolumeSet.computeVolumeDataDensity()` computes and writes `volumeDataDensity`; `GreedyPlanner` mutates `used` and `skip` on copied sets during simulation; reports read ratios and flags.

State and persistence behavior: most fields serialize into cluster and plan JSON; derived ratios and effective capacity are `@JsonIgnore`. Equality and hash code are UUID-based, so UUID is identity for set membership.

Dependencies and integration points: used by connector mapping, volume-set calculations, plan `Step` objects, DataNode executor plan JSON, and command reports.

Risks: ratio methods divide by capacity without zero checks. `equals()` and `hashCode()` assume `uuid` is non-null. `setUsed()` clamping can mask invalid upstream storage report values. `setTransient()` and `setIsTransient()` both exist, which can confuse bean conventions.

Test signals: diskbalancer data model and planner tests cover volume density, skip behavior, and JSON plan/cluster serialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/diskbalancer/datamodel/DiskBalancerVolume.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/diskbalancer/datamodel/DiskBalancerVolumeSet.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/diskbalancer/datamodel/DiskBalancerVolumeSet.java

Purpose: groups homogeneous DataNode volumes by storage type and transient property, computes ideal usage/density, and maintains a sorted queue used by the greedy planner.

Important APIs/types/functions: constructors initialize set ID, volume set, and `TreeSet` sorted by `MinHeap`. `addVolume()` enforces matching transient and storage type, inserts the volume, and recomputes density. `computeVolumeDataDensity()` ignores failed/skipped volumes, skips misconfigured negative effective capacity, calculates `idealUsed = totalUsed / totalEffectiveCapacity` truncated to four decimals, writes each volume's `idealUsed - used/effectiveCapacity`, and rebuilds `sortedQueue`. `isBalancingNeeded()` checks more than one volume and any non-failed, non-transient, non-skipped volume whose absolute density exceeds threshold. `removeVolume()` removes without recompute.

Control flow: connectors build sets incrementally; planners copy sets, repeatedly remove skipped volumes, inspect `sortedQueue.first()`/`last()`, and recompute after simulated moves. Reports iterate `getVolumes()`.

State and persistence behavior: serializes storage type, set ID, transient flag, ideal usage, and volumes while ignoring sorted queue, volume count, and ideal-used getter. The copy constructor shallow-copies volume objects into a new set and new queue, so planner simulation mutates copied set membership but still shares volume objects with the original unless the source set already contained distinct deserialized objects.

Dependencies and integration points: used by `DiskBalancerDataNode`, `GreedyPlanner`, and `ReportCommand`. Depends on Jackson annotations and `Preconditions`.

Risks: empty constructor does not initialize `volumes` or `sortedQueue`, relying on Jackson; direct use must select the boolean constructor. `TreeSet` comparator compares only density, so equal-density distinct volumes can collapse in the sorted queue. `isBalancingNeeded()` excludes transient volumes but density calculation includes non-skipped transient volumes, which must match planner expectations. Planner calls `queue.first()`/`last()` after removals; empty queues would fail.

Test signals: planner/data-model tests validate density computation, misconfigured skip behavior, threshold balancing, and queue order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/diskbalancer/datamodel/DiskBalancerVolumeSet.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/diskbalancer/datamodel/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/diskbalancer/datamodel/package-info.java

Purpose: package documentation for the diskbalancer data model.

Important APIs/types/functions: declares the package and describes the hierarchy: `DiskBalancerCluster` contains `DiskBalancerDataNode`; nodes contain `DiskBalancerVolumeSet`; volume sets contain `DiskBalancerVolume`.

Control flow: none.

State and persistence behavior: documents that model information is read from NameNode or user-supplied JSON.

Dependencies and integration points: provides high-level context for connector output and planner input.

Risks: documentation-only; it should stay aligned with model hierarchy if classes evolve.

Test signals: not directly tested.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/diskbalancer/datamodel/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/diskbalancer/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/diskbalancer/package-info.java

Purpose: top-level package documentation for diskbalancer.

Important APIs/types/functions: no executable code. It explains diskbalancer as a DataNode-local volume balancing feature that computes average data distribution per storage type and moves data from above-average to below-average volumes on live DataNodes.

Control flow: describes the conceptual three-step algorithm: calculate ideal per-volume usage, move from high-load to low-load volumes, and operate against live DataNodes.

State and persistence behavior: none directly; contextualizes generated plan files and DataNode execution state.

Dependencies and integration points: frames the command, connector, data model, planner, and DataNode executor packages.

Risks: docs can lag implementation details such as skip flags, thresholds, and storage-policy interactions.

Test signals: not directly tested.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/diskbalancer/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/diskbalancer/planner/GreedyPlanner.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/diskbalancer/planner/GreedyPlanner.java

Purpose: greedy diskbalancer planner that repeatedly schedules the largest feasible move between the most over-utilized and most under-utilized volumes within each storage-type volume set.

Important APIs/types/functions: implements `Planner.plan(DiskBalancerDataNode)`. `plan()` creates a `NodePlan`, loops while the node needs balancing, and calls `balanceVolumeSet()` for each set. `balanceVolumeSet()` copies a volume set, removes skipped/failed volumes, picks low/high volumes from the sorted queue, computes a `MoveStep`, applies it to simulated usage, and appends the step. `computeMove()` calculates `maxLowVolumeCanReceive` and `maxHighVolumeCanGive` relative to ideal usage and returns a `MoveStep` with source high volume and destination low volume. `applyStep()` mutates simulated used bytes and recomputes density.

Control flow: planning is iterative simulation. It stops only when all volume sets report no balancing needed under threshold. After finishing a set, it writes node name, UUID, timestamp, and port into the `NodePlan`.

State and persistence behavior: planner holds only threshold. It creates `MoveStep` objects that serialize into plan JSON. The simulation mutates the copied volume set's volume objects and skip flags to model future state; no HDFS data moves happen here.

Dependencies and integration points: depends on diskbalancer data model, `NodePlan`, `MoveStep`, `Step`, and `Time`. Constructed by `PlannerFactory`, called by `DiskBalancerCluster.computePlan()`, output consumed by `PlanCommand` and DataNode execution.

Risks: no explicit iteration cap; bad density/queue behavior could loop. `printQueue()` assumes non-empty queue in debug mode. The `DiskBalancerVolumeSet` copy is shallow, so simulations may share volume objects with the source model depending on construction path. Equal density comparator behavior can remove queue entries. Threshold semantics depend on `DiskBalancerVolumeSet.isBalancingNeeded()`.

Test signals: diskbalancer planner tests and command plan tests validate generated step counts, source/destination choices, and no-plan cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/diskbalancer/planner/GreedyPlanner.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/diskbalancer/planner/MoveStep.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/diskbalancer/planner/MoveStep.java

Purpose: concrete `Step` describing one planned data movement from a source volume to a destination volume.

Important APIs/types/functions: fields include source/destination `DiskBalancerVolume`, `idealStorage`, `bytesToMove`, `volumeSetID`, `maxDiskErrors`, `tolerancePercent`, and `bandwidth`. Implements all `Step` getters and setters for tunable execution parameters. `getSizeString()` formats bytes via `StringUtils.TraditionalBinaryPrefix`. `toString()` prints source path, destination path, human-readable size, and destination storage type. Jackson `@JsonInclude(NON_DEFAULT)` omits default tunables from JSON.

Control flow: created by `GreedyPlanner.computeMove()`, optionally modified by `PlanCommand.setPlanParams()`, serialized in `NodePlan`, deserialized by executor-side plan handling.

State and persistence behavior: fully serializable bean with default constructor for JSON. Non-default bandwidth/error/tolerance settings persist only when explicitly set.

Dependencies and integration points: implements `Step`; embeds volume objects so plan JSON carries volume identity/path/type information needed by DataNode executor.

Risks: source/destination volume objects are mutable model objects, so callers must avoid modifying them after plan persistence in ways that invalidate the step. Typo-level docs do not affect behavior. No range checks on bytes, bandwidth, tolerance, or max errors.

Test signals: planner and plan-command tests validate step serialization, text formatting, and bandwidth/max-error injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/diskbalancer/planner/MoveStep.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/diskbalancer/planner/NodePlan.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/diskbalancer/planner/NodePlan.java

Purpose: serializable plan for one DataNode, containing a polymorphic list of diskbalancer `Step` objects plus node identity, port, and creation timestamp.

Important APIs/types/functions: `volumeSetPlans` uses Jackson `@JsonTypeInfo` with `@class`. `parseJson()` first reads a tree, recursively validates all `@class` values with `checkNodes()`, and then deserializes. `stepClassIsAllowed()` checks configured package prefixes from `SUPPORTED_PACKAGES_CONFIG_NAME` in a static `HdfsConfiguration`. `toJson()` writes the plan. Accessors manage node name, UUID, port, timestamp, and step list; package-private `addStep()` appends non-null steps.

Control flow: planners build `NodePlan`, `PlanCommand` writes JSON, `ExecuteCommand` parses JSON before submission, and DataNode-side execution parses/validates again. The recursive class check traverses nested objects and arrays to reject unexpected polymorphic classes before Jackson binds them.

State and persistence behavior: plan JSON is a durable artifact under diskbalancer output directories and is submitted unchanged to DataNodes. Allowed package prefixes are loaded statically from configuration, so runtime config changes after class load may not affect validation.

Dependencies and integration points: depends on Jackson, `HdfsConfiguration`, `DFSConfigKeys.SUPPORTED_PACKAGES_CONFIG_NAME`, and `Step` implementations such as `MoveStep`. This is the main security boundary for plan deserialization.

Risks: allowed-package configuration must include diskbalancer planner classes or parsing fails. Prefix checks must be configured narrowly enough to avoid unsafe polymorphic deserialization. `setURI()` actually sets `nodeName`, a legacy naming oddity. `toList()` usage in `getAllowedPackages()` requires a Java version supporting stream `toList()`.

Test signals: tests include sample `Step` classes and plan validity checks, covering allowed/disallowed `@class` handling and execute-plan validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/diskbalancer/planner/NodePlan.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/diskbalancer/planner/Planner.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/diskbalancer/planner/Planner.java

Purpose: interface for diskbalancer planning algorithms.

Important APIs/types/functions: single method `NodePlan plan(DiskBalancerDataNode node) throws Exception`.

Control flow: `DiskBalancerCluster.computePlan()` obtains a planner and calls `plan()` per selected node. Implementations decide how to transform volume state into a sequence of `Step`s.

State and persistence behavior: none at interface level.

Dependencies and integration points: implemented by `GreedyPlanner`; constructed by `PlannerFactory`; output consumed as `NodePlan`.

Risks: broad exception signature pushes planner-specific failures into caller logging. Any future implementation must preserve `NodePlan` serialization and DataNode executor compatibility.

Test signals: planner factory and greedy planner tests indirectly cover the interface contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/diskbalancer/planner/Planner.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/diskbalancer/planner/PlannerFactory.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/diskbalancer/planner/PlannerFactory.java

Purpose: factory for planner implementations.

Important APIs/types/functions: constant `GREEDY_PLANNER = "greedyPlanner"`. `getPlanner(plannerName, node, threshold)` returns a new `GreedyPlanner` for that name and logs node details in debug mode; otherwise throws `IllegalArgumentException`. Constructor is private.

Control flow: `DiskBalancerCluster.computePlan()` always requests `GREEDY_PLANNER`, so this factory is the extension point for future algorithms.

State and persistence behavior: stateless.

Dependencies and integration points: depends on `DiskBalancerDataNode` for logging and `GreedyPlanner` construction.

Risks: string comparison has no null guard for `plannerName`; callers must pass a valid constant. Adding planners requires updating factory and likely plan compatibility tests.

Test signals: planner tests cover recognized/unrecognized planner names and greedy planner creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/diskbalancer/planner/PlannerFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/diskbalancer/planner/Step.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/diskbalancer/planner/Step.java

Purpose: interface for one executable diskbalancer plan action.

Important APIs/types/functions: exposes bytes to move, source/destination `DiskBalancerVolume`, ideal storage, volume set ID, human-readable size formatting, maximum disk errors, tolerance percentage, bandwidth, and setters for tunable execution parameters.

Control flow: planners create `Step` instances, commands print and tune them, `NodePlan` serializes/deserializes them, and DataNode execution consumes them.

State and persistence behavior: none at interface level; implementations are expected to be JSON-serializable because `NodePlan` uses polymorphic typing.

Dependencies and integration points: implemented by `MoveStep`; test package includes `SampleStep` for deserialization validation.

Risks: interface exposes mutable settings but no validation policy; callers and DataNode execution must enforce ranges and semantics. Future step types must be permitted by `NodePlan` allowed-package configuration.

Test signals: plan serialization/security tests and `TestDiskBalancerCommand` exercise concrete `MoveStep` behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/diskbalancer/planner/Step.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/diskbalancer/planner/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/diskbalancer/planner/package-info.java

Purpose: package-level documentation for diskbalancer planners.

Important APIs/types/functions: documents the conceptual loop over `DiskBalancerVolumeSet`: plan a move, add a step, apply the step to current state, repeat until balanced.

Control flow: documentation mirrors `GreedyPlanner` simulation, where each step modifies the modeled state before computing the next step.

State and persistence behavior: none directly; contextualizes `NodePlan` and `Step` artifacts.

Dependencies and integration points: frames planner package as the bridge between data model and DataNode-executable plan.

Risks: pseudocode names differ from concrete API (`planner.plan(current, threshold)` vs current `Planner.plan(node)`), so readers should inspect actual classes.

Test signals: not directly tested.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/diskbalancer/planner/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/mover/Mover.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/mover/Mover.java

Purpose: HDFS storage-policy migration tool. It scans one or more HDFS namespace paths, detects block replicas or striped block pieces whose storage types do not satisfy the file's storage policy, and schedules block moves through the balancer `Dispatcher`.

Important APIs/types/functions: constructor builds a `Dispatcher`, storage maps, retry settings, target paths, policy array, pinned-block exclusion map, and metrics. `init()` loads storage policies and DataNode storage reports, creating `Source` and target `StorageGroup`s per movable storage type. `run()` initializes, processes namespace, maps exceptions to `ExitStatus`, and shuts down dispatcher. `newDBlock()` creates `DBlock` or `DBlockStriped` and adjusts striped indices when locations are missing. Inner `Processor` lists directories, handles snapshots, processes files, derives expected storage types from `BlockStoragePolicy`, computes `StorageTypeDiff`, and schedules moves. `scheduleMoveReplica()` tries same-node, same node group, same rack, then any other target, respecting pinned blocks. `Cli` parses `-p` paths or `-f` local path files into NameNode-to-path maps for federation/HA. Static `run()` loops over NameNode connectors until all succeed or an error exit occurs. `Result` maps remaining/no-progress/retry state to exit status.

Control flow: command-line entry parses targets, creates `NameNodeConnector`s, initializes metrics and keytab login, then repeatedly runs a `Mover` per connector. Each iteration scans configured paths, schedules pending moves asynchronously via `Dispatcher`, waits for completion, checks block pinning failures/success, and either exits success, retries, reports no progress, or sleeps for heartbeat plus redundancy intervals before another pass. Directory traversal handles paginated listings and snapshottable directories; snapshot paths that still exist in current namespace are skipped to avoid duplicate work.

State and persistence behavior: uses NameNodeConnector id path `HdfsServerConstants.MOVER_ID_PATH` to prevent conflicting movers/SPS behavior. Move progress lives in dispatcher pending move state and NameNode/DataNode block movement counters. Metrics are registered per block pool as `Mover-<blockpoolID>`. Local path files are read but not persisted. Retry count is process-local and shared across connectors in the top-level run.

Dependencies and integration points: deeply integrates with balancer `Dispatcher`, `NameNodeConnector`, DFSClient listing APIs, storage policy suite, erasure coding policy manager, metrics system, Kerberos login, network topology matchers, and HDFS protocol block/location types. Related tests cover Storage Policy Satisfier interactions through the mover id file.

Risks: namespace scans can be expensive and run under live cluster conditions. Pinned-block exclusion map has a TODO about unbounded memory. Storage policy suitability for EC striped files is limited; unsupported policies cause skips. Retry counting is global for the run. `targetPaths` may be null depending on connector behavior, so callers rely on `NameNodeConnector` normalizing it. Mover intentionally ignores many per-directory listing errors and continues, which favors progress but may hide incomplete migration.

Test signals: `TestMover` covers CLI parsing, HA/federation path resolution, move scheduling, retry failure behavior, striped files, maintenance/decommission cases, keytab login, pinned blocks, unset storage policy, metrics, and max-iteration interactions. SPS tests cover mover id-file coexistence behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/mover/Mover.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/mover/MoverMetrics.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/mover/MoverMetrics.java

Purpose: metrics source for an HDFS mover instance scoped to one block pool.

Important APIs/types/functions: `create(Mover)` registers a `MoverMetrics` instance with `DefaultMetricsSystem`. `getName()` returns `Mover-<blockpoolID>`. Gauges/counters include `processingNamespace`, `blocksScheduled`, and `filesProcessed`. Metrics getters expose bytes moved, blocks moved, and blocks failed from `NameNodeConnector` counters. Package-private mutators update namespace-processing state and increment scheduled/processed counters.

Control flow: `Mover` constructs metrics, `Processor.processNamespace()` toggles processing gauge, file processing increments occur per processed file, and scheduling increments occur when a pending move is accepted.

State and persistence behavior: metrics are in-process mutable counters/gauges registered into Hadoop metrics. They are not persisted except through external metrics sinks.

Dependencies and integration points: uses Hadoop metrics annotations, `DefaultMetricsSystem`, and `NameNodeConnector` counters.

Risks: metric source naming depends on blockpool ID uniqueness. If a mover instance is created repeatedly for the same block pool without metrics-system cleanup, registration collisions are possible depending on metrics system behavior. It is package-private and tightly coupled to `Mover`.

Test signals: `TestMover.testMoverMetrics` validates metric registration/counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/mover/MoverMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/mover/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/mover/package-info.java

Purpose: package documentation for HDFS Mover.

Important APIs/types/functions: declares package `org.apache.hadoop.hdfs.server.mover`; explains mover as a tiered-storage migration tool that scans paths, checks block placement against storage policy, and moves replicas to satisfy policy.

Control flow: documentation matches `Mover.Processor`: scan paths, detect violations, schedule replica moves.

State and persistence behavior: none directly.

Dependencies and integration points: contextualizes `Mover` and `MoverMetrics` and their relationship to storage policies.

Risks: documentation does not cover EC-specific or pinned-block behavior present in implementation.

Test signals: not directly tested.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/mover/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/AclEntryStatusFormat.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/AclEntryStatusFormat.java

Purpose: packs and unpacks HDFS ACL entries into the 32-bit integer format used both in memory and on disk.

Important APIs/types/functions: enum fields define bit layout: `PERMISSION` 3 bits, `TYPE` 2 bits, `SCOPE` 1 bit, and `NAME` 24 bits. `getScope()`, `getType()`, `getPermission()`, and `getName()` decode fields. `toInt(AclEntry)` encodes scope/type/permission and, for named users/groups, stores a serial number from `SerialNumberManager.USER` or `.GROUP`. `toAclEntry()` rebuilds `AclEntry` objects, optionally using a string table. `toInt(List<AclEntry>)` converts lists.

Control flow: ACL storage converts feature entries into int arrays via this class; reads convert int arrays back into logical `AclEntry` instances. Named entries go through serial-number managers; mask/other/unnamed entries have no name ID.

State and persistence behavior: the bit layout is explicitly compatibility-sensitive because it is persisted in fsimage/edit state. Serial-number IDs tie ACL names to NameNode string tables.

Dependencies and integration points: used by `AclFeature`/`AclStorage`, `LongBitFormat`, `FsAction`, `AclEntryScope`, `AclEntryType`, and `SerialNumberManager`.

Risks: changing field width/order is on-disk incompatible. Enum ordinal dependence means changing enum ordering in Hadoop permission classes would break decoding. Name IDs are limited to 24 bits.

Test signals: ACL fsimage/offline image and NameNode ACL tests cover persistence, named ACL entries, and string-table decoding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/AclEntryStatusFormat.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/AclFeature.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/AclFeature.java

Purpose: inode feature storing the explicit ACL entries that cannot be represented directly in `FsPermission` bits.

Important APIs/types/functions: holds final `int[] entries` encoded by `AclEntryStatusFormat`. `getEntriesSize()` and `getEntryAt()` expose packed entries. `equals()`/`hashCode()` are array-content based for deduplication. Implements `ReferenceCountMap.ReferenceCounter` with synchronized `getRefCount()`, `incrementAndGetRefCount()`, and `decrementAndGetRefCount()`. `EMPTY_ENTRY_LIST` provides a shared empty immutable ACL entry list constant.

Control flow: `AclStorage.createAclFeature()` builds instances; `INode` attaches/removes them; `AclStorage.UNIQUE_ACL_FEATURES` interns them by equality and manages reference counts.

State and persistence behavior: packed int array is persisted as part of inode features. Reference count is in-memory only and supports deduplicating identical ACL features across inodes.

Dependencies and integration points: implements `INode.Feature`; used by NameNode namespace, fsimage serialization, snapshots, and ACL modification APIs.

Risks: `entries` array is stored directly without defensive copy, so caller mutation would break immutability assumptions and reference-map hashing. Reference count methods are synchronized but broader lifecycle correctness depends on all attach/remove paths using `AclStorage`.

Test signals: `TestFSImageWithAcl`, `TestAclWithSnapshot`, and NameNode ACL tests exercise ACL persistence and feature sharing behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/AclFeature.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/AclStorage.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/AclStorage.java

Purpose: utility class defining how HDFS logical ACLs are stored on inodes by splitting data between `FsPermission` bits and `AclFeature` entries.

Important APIs/types/functions: `copyINodeDefaultAcl()` inherits parent default ACLs to new files/directories, filtering by child mode and copying default ACLs only to directories. `readINodeAcl()` reads explicit feature entries for an inode or inode attributes. `getEntriesFromAclFeature()` decodes packed ints. `readINodeLogicalAcl()` reconstructs full logical ACL from permission bits plus feature access/default entries. `updateINodeAcl()` stores a new full ACL, validating default ACLs only on directories, replacing/removing features, and updating permissions. Private `createAclFeature()` stores named access entries and all defaults while omitting owner/mask/other entries represented in permission bits. Permission constructors preserve sticky bit and map ACL mask to group permission. `addAclFeature()` and `removeAclFeature()` intern features in `UNIQUE_ACL_FEATURES`.

Control flow: ACL modification code first uses `AclTransformation` to produce sorted validated logical ACLs, then calls `updateINodeAcl()`. Reads reconstruct logical views for API responses. New inode creation calls `copyINodeDefaultAcl()` to inherit directory defaults.

State and persistence behavior: extended ACL presence is represented by an inode ACL feature plus permission bits. Minimal ACLs remove the feature. Identical `AclFeature`s are reference-counted in a static map to reduce memory. Snapshot-aware updates pass `snapshotId` to inode feature/permission mutation methods.

Dependencies and integration points: central to NameNode ACL APIs, `INode`, `INodeDirectory`, `INodeAttributes`, snapshots, quota checks, `FsPermission`, `AclUtil`, and `AclTransformation`.

Risks: methods assume ACL lists are already validated and sorted; bypassing `AclTransformation` can corrupt storage layout. Default ACLs on files are rejected only in update. Feature interning depends on immutable entry arrays. Copying default ACLs uses child creation mode to mask permissions, so subtle POSIX inheritance behavior must stay covered by tests.

Test signals: `TestAclTransformation`, `TestNameNodeAcl`, `TestExtendedAcls`, `TestAclsEndToEnd`, `TestAclWithSnapshot`, `TestFSImageWithAcl`, WebHDFS/ViewFS ACL tests, and CLI ACL tests cover transformations, inheritance, persistence, snapshots, and API views.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/AclStorage.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/AclTransformation.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/AclTransformation.java

Purpose: implements NameNode ACL mutation algorithms: merge ACL entries, replace ACL entries, remove selected entries, and remove default ACLs while preserving POSIX/HDFS ACL invariants.

Important APIs/types/functions: public static operations are `filterAclEntriesByAclSpec()`, `filterDefaultAclEntries()`, `mergeAclEntries()`, and `replaceAclEntries()`. `ACL_ENTRY_COMPARATOR` enforces order by scope, type, and nullable name. `buildAndValidateAcl()` trims, sorts, rejects duplicates and invalid names for mask/other, checks max entries, and ensures required user/group/other entries for access and default scopes. `calculateMasks()` preserves, rejects deletion of required masks, or recalculates masks as the union of group and named-entry permissions. `copyDefaultsIfNeeded()` fills missing default user/group/other from corresponding access entries. Inner `ValidatedAclSpec` sorts/prevalidates untrusted user specs and supports key lookup by scope/type/name.

Control flow: every mutation starts by wrapping the user ACL spec in `ValidatedAclSpec`, combines it with existing sorted ACL entries according to operation semantics, copies defaults if needed, calculates masks, then validates and returns an unmodifiable sorted ACL. Removal tracks dirty scopes/masks to detect invalid mask deletion. Replacement operates independently for access and default scopes.

State and persistence behavior: stateless transformer. It returns logical ACL lists later stored by `AclStorage`; no direct inode mutation happens here.

Dependencies and integration points: used by NameNode ACL RPC implementations before `AclStorage.updateINodeAcl()`. Depends on Hadoop permission ACL types, `ScopedAclEntries`, and Guava comparison/order helpers.

Risks: maximum entry validation is per access/default scope and must account for automatically inserted masks/defaults. Input list is sorted in place in `ValidatedAclSpec`, so callers should not rely on original order. Mask semantics are subtle and security-sensitive; accidental changes could grant/deny access incorrectly.

Test signals: `TestAclTransformation` is the direct unit suite; broader NameNode/WebHDFS/ViewFS/CLI ACL tests verify integration behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/AclTransformation.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/AuditLogger.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/AuditLogger.java

Purpose: public evolving interface for pluggable NameNode audit logging.

Important APIs/types/functions: `initialize(Configuration conf)` configures the logger. `logAuditEvent(boolean succeeded, String userName, InetAddress addr, String cmd, String src, String dst, FileStatus stat)` records an audit event including authorization result, user, remote address, command, source/destination paths, and optional file status.

Control flow: NameNode audit paths call `logAuditEvent()` during request handling, including critical sections, so implementations must return quickly.

State and persistence behavior: interface has no state; implementations may write logs, metrics, or external events. The contract explicitly encourages low-latency behavior to avoid NameNode stalls.

Dependencies and integration points: public API annotated `InterfaceAudience.Public` and `InterfaceStability.Evolving`; used by NameNode audit logging configuration and custom audit logger plugins.

Risks: slow or blocking implementations can harm NameNode throughput. The evolving annotation permits API changes across versions. Implementations need to handle null `dst`/`stat` values depending on command.

Test signals: audit logging tests in the broader NameNode suite usually validate default and configured audit logger behavior; this interface itself is compile-time contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/AuditLogger.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/BackupImage.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/BackupImage.java

Purpose: `FSImage` specialization for BackupNode, managing local backup storage and the state machine for receiving, spooling, and applying NameNode edit log batches.

Important APIs/types/functions: enum `BNState` has `DROP_UNTIL_NEXT_ROLL`, `JOURNAL_ONLY`, and `IN_SYNC`. Constructor disables pre-upgradable layout checks and starts in drop-until-roll. `recoverCreateRead()` analyzes/formats/recovers backup storage directories without loading image/edits. `journal()` handles remote edit batches: drop before first roll, apply and journal when in sync, or only journal when catching up. `applyEdits()` validates contiguous txid batches, feeds bytes through `EditLogBackupInputStream`, uses `FSEditLogLoader`, advances `lastAppliedTxId`, and updates quota counts under FS write lock. `convergeJournalSpool()` and `tryConvergeJournalSpool()` replay finalized and in-progress local logs until current, then transition to `IN_SYNC`. `namenodeStartedLogSegment()` starts local segments, transitions from drop to journal-only, and optionally freezes namespace. `freezeNamespaceAtNextRoll()` and `waitUntilNamespaceFrozen()` coordinate checkpoints. `close()` aborts current edit log segment instead of finalizing.

Control flow: BackupNode initially drops edits until the active NameNode rolls. It then journals incoming edits locally without applying them, catches up from local spool, loads the in-progress stream, transitions to in-sync, and thereafter applies incoming edit batches to its namespace while journaling them. For checkpoints, it requests freeze on the next roll, transitions back to journal-only, and waits until namespace application stops.

State and persistence behavior: persists local edit logs and storage directories; in-memory namespace is advanced through edit replay. `bnState`, `stopApplyingEditsOnNextRoll`, `lastAppliedTxId`, and current edit log segment ID govern consistency. It intentionally aborts current segments on close because BackupNode is not the authoritative finalizer.

Dependencies and integration points: used by `BackupNode`, `BackupNodeRpcServer`, `Checkpointer`, `FSNamesystem`, `FSEditLog`, `FSEditLogLoader`, storage inspectors, and quota code. It receives journal data through `JournalProtocol` implemented by BackupNode RPC server.

Risks: state transitions are synchronization-sensitive. `applyEdits()` enforces contiguous txids; gaps abort with IO errors. Catch-up loops may repeat if logs roll concurrently. Quota recount after every batch can be costly but preserves namespace accounting. Incorrect close/finalization behavior could corrupt backup edit logs.

Test signals: `TestBackupNode` covers tailing edits, synchronization, checkpoints, storage dir matching, startup behavior, and BackupNode/CheckpointNode read/write restrictions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/BackupImage.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/BackupJournalManager.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/BackupJournalManager.java

Purpose: `JournalManager` implementation on the active NameNode side that writes edit log transactions to a registered BackupNode through RPC.

Important APIs/types/functions: constructor stores BackupNode registration and creates `JournalInfo` from the active NameNode registration. `startLogSegment()` creates an `EditLogBackupOutputStream`, starts a segment at the given txid, and returns it. `matchesRegistration()` compares BackupNode addresses. Most local-storage lifecycle methods (`format`, upgrade, rollback, input stream selection, purge) are unsupported, no-op, or intentionally empty because this manager is output-only.

Control flow: when the active NameNode rolls or writes edits, its edit log infrastructure can use this manager to create output streams targeting a BackupNode. It never provides input streams for recovery/replay.

State and persistence behavior: holds remote registration and journal identity. Persistence happens remotely through BackupNode RPC and local BackupNode edit logs, not in this manager.

Dependencies and integration points: uses `NamenodeRegistration`, `JournalInfo`, `EditLogBackupOutputStream`, and NameNode `JournalManager` plumbing.

Risks: unsupported methods must not be called in normal paths; accidental use for input/recovery would fail. `finalizeLogSegment()` is empty because BackupNode stream behavior differs from local journals, so callers must tolerate that.

Test signals: BackupNode integration tests exercise remote journaling and registration, indirectly covering this manager.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/BackupJournalManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/BackupNode.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/BackupNode.java

Purpose: NameNode subclass implementing BackupNode and CheckpointNode roles. A checkpoint node periodically downloads/merges/uploads checkpoints; a backup node also keeps a local namespace synchronized by receiving journal edits from the active NameNode.

Important APIs/types/functions: overrides RPC/service/HTTP address getters/setters to use backup-node config keys. `loadNamesystem()` configures backup safe mode, creates `BackupImage` and `FSNamesystem`, disables quota checks during load, and recovers storage. `initialize()` disables async edit logging, configures trash, performs handshake, initializes NameNode services, enters safe mode, disables lease hard-limit expiry, registers with active NameNode, and starts `Checkpointer`. `createRpcServer()` returns `BackupNodeRpcServer`. `stop()` reports fatal shutdown to active NameNode, stops proxy/checkpointer, aborts current edit log segment, and stops NameNode services. `setSafeMode()` is unsupported. Inner `BackupNodeRpcServer` implements `JournalProtocol`, verifies layout/namespace/cluster IDs, forwards `startLogSegment()` and `journal()` to `BackupImage`, and rejects fencing. `handshake()` and `registerWith()` validate version/storage and register subordinate NameNode. `BNHAContext` restricts supported operations to unchecked, checkpoint, journal, and reads for Backup role, and starts/stops active services in the backup context.

Control flow: construction follows NameNode startup but with backup-specific configuration. It first contacts active NameNode for namespace info, initializes local services, registers as subordinate, then receives journal RPCs and periodically checkpoints. Shutdown attempts to remove the backup stream from active NameNode before stopping local services.

State and persistence behavior: persists backup/checkpoint storage through `BackupImage` and checkpoint manager. Runtime state includes active NameNode proxy/address, HTTP address, checkpoint thread, and local `FSNamesystem`. Backup role stays in safe mode for mutating operations and allows reads; CheckpointNode disallows reads except allowed categories.

Dependencies and integration points: integrates with NameNode base class, `NamenodeProtocol`, `JournalProtocolPB`, protobuf translator, `BackupImage`, `Checkpointer`, HA state/context, storage namespace validation, Kerberos UGI, and DFS backup configuration keys.

Risks: BackupNode depends on non-HA proxy creation and active NameNode availability during startup. Async edits are forcibly disabled due to race concerns. Operation gating is subtle: allowing reads only for Backup role while keeping mutation services muted relies on safe mode and HA context behavior. Clean shutdown reporting is best effort. Fencing is unsupported, so it is not a quorum journal replacement.

Test signals: `TestBackupNode` covers startup, tailing edits, checkpoints, read/write operation restrictions, storage matching, and authentication failure. `TestHDFSServerPorts` covers BackupNode port binding. DFSUtil/GetConf tests cover backup-node address discovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/BackupNode.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/BackupState.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/BackupState.java

Purpose: HA state implementation used by BackupNode while presenting itself as a standby-like NameNode role with custom operation checks and service lifecycle.

Important APIs/types/functions: constructor sets HA service state to `STANDBY`. `checkOperation()` delegates to the BackupNode HA context. `shouldPopulateReplQueues()` returns false. `enterState()` starts active services through context; `exitState()` stops them; `prepareToExitState()` delegates standby-service preparation.

Control flow: `BackupNode.createHAState()` returns this state. Its lifecycle callbacks call the backup-specific `BNHAContext`, which gates allowed operations and starts/stops selected NameNode services.

State and persistence behavior: no persistent state; in-memory HA state controls service behavior and operation authorization.

Dependencies and integration points: extends `HAState`, uses `HAContext`, `OperationCategory`, and `ServiceFailedException`. Tightly coupled to `BackupNode.BNHAContext` behavior.

Risks: despite using `HAServiceState.STANDBY`, `enterState()` starts active services; correctness depends on BackupNode context muting unsafe services and safe mode. Replication queues are intentionally not populated.

Test signals: BackupNode operation restriction tests exercise state behavior through reads/writes/checkpoints.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/BackupState.java -->
