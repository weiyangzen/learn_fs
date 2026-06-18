# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/bin/start-dfs.sh

## Purpose
`start-dfs.sh` starts the core HDFS daemons for a cluster: NameNodes, DataNodes, optional SecondaryNameNodes, optional JournalNodes, and optional ZK Failover Controllers. It is intended to run from a master/control node.

## Important commands and variables
- Accepts optional `-upgrade` for NameNodes or `-rollback` for DataNodes, then appends remaining arguments to NameNode startup options.
- Discovers NameNodes with `hdfs getconf -namenodes`, defaulting to `hostname` if empty.
- Starts daemons with `hadoop_uservar_su hdfs <subcmd> "${HADOOP_HDFS_HOME}/bin/hdfs" --workers --config ... --daemon start <subcmd>`.
- Discovers SecondaryNameNodes via `getconf -secondarynamenodes`, JournalNodes via `getconf -journalNodes`, and automatic failover via `getconf -confKey dfs.ha.automatic-failover.enabled`.
- Accumulates exit status in `HADOOP_JUMBO_RETCOUNTER`.

## Control flow
The script initializes configuration, parses at most one leading startup option, and starts NameNodes on the configured hosts. It then starts DataNodes using the default workers file. If secondary NameNodes are configured, it skips them when NameNode HA appears configured, maps `0.0.0.0` to the local hostname, and starts them otherwise. If JournalNodes are configured, it starts them on their configured hosts. Finally, when automatic HA failover is enabled, it starts ZKFC on the NameNode hosts. The exit status is the sum of child command statuses.

## State and persistence behavior
The script persists daemon processes, PID files, logs, and in-cluster service state through the `hdfs --daemon start` calls. `-upgrade` and `-rollback` options alter HDFS storage startup behavior in downstream NameNode/DataNode code. The script itself stores only shell variables during execution.

## Dependencies and integration points
It depends on `hdfs-config.sh`, common shell user-switching logic, worker mode, `hdfs getconf`, service-user environment variables, configured workers/hostnames, and HDFS HA/JN/ZKFC configuration. It integrates with `DFSConfigKeys` keys for nameservices, HA, JournalNode addresses, service RPC addresses, and startup flags.

## Risks
- The usage string says `[-clusterId]`, but parsing only recognizes `-upgrade` and `-rollback`; other leading options trigger usage.
- Exit statuses are summed, so the final code can exceed normal 0/1 semantics and can lose exact failing component identity.
- HA detection for skipping SecondaryNameNode uses a comma check on `NAMENODES`; this is fragile if output format changes.
- Starting DataNodes through the workers file can start many remote daemons; a misconfigured workers file has high blast radius.
- Secure deployments require both secure and insecure service-user environment variables, as noted in comments.

## Test signals
No direct test for this wrapper appears in the focused BATS files. High-value validation stubs `hdfs getconf` and `hadoop_uservar_su` to cover no-NameNode fallback, `0.0.0.0` secondary handling, HA skip, JournalNode startup, ZKFC startup, and exit aggregation. Full integration is daemon start/stop on mini or test clusters.
