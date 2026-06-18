# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/diskbalancer/command/ReportCommand.java

Purpose: implements `hdfs diskbalancer -report`, either listing the top DataNodes that would benefit from diskbalancer or printing detailed volume information for specified DataNodes.

Important APIs/types/functions: constructor registers `-report`, `-top`, and `-node`. `execute()` reads cluster info and dispatches to `handleNodeReport()` when `-node` is present or `handleTopReport()` otherwise. `handleTopReport()` reverse-sorts nodes by `DiskBalancerDataNode.compareTo()` and prints density summaries. `handleNodeReport()` resolves node names/IPs/UUIDs or `file://` host files through `Command.getNodes()`, catches invalid-node `DiskBalancerException` for user-friendly output, and calls `recordNodeReport()`. `recordNodeReport()` populates volume paths, formats usage/free ratios, capacity, failed/read-only/skip/transient flags, sorts volume lines, and appends them.

Control flow: top report is cluster-only and avoids DataNode path-name RPCs. Detailed node report does a DataNode RPC per resolved node to make volume paths human-readable. Invalid node lists are reported into output and return without throwing further.

State and persistence behavior: no durable files. It updates inherited `topNodes` and writes a text report. Cluster node density is computed during connector/model population and re-used for sorting.

Dependencies and integration points: connects `Command` node-list parsing, `DiskBalancerCluster`, `DiskBalancerVolumeSet`, `DiskBalancerVolume`, and `DiskBalancerCLI` option formatting. It is often used before planning to select candidates.

Risks: `parseTopNodes()` requires cluster initialization and throws for non-positive values. Detailed report output depends on DataNode volume-name support; without it, paths may remain UUID-like/null. Catching invalid nodes and returning can produce a successful CLI process with an error message in output depending on outer handling.

Test signals: `TestDiskBalancerCommand` has top report, default top, node report, invalid node, and host-file report tests.
