# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/bin/stop-dfs.sh

## Purpose
`stop-dfs.sh` stops the core HDFS daemons started by `start-dfs.sh`: NameNodes, DataNodes, optional SecondaryNameNodes, optional JournalNodes, and optional ZK Failover Controllers.

## Important commands and variables
- Sources `hdfs-config.sh`.
- Discovers NameNodes via `hdfs getconf -namenodes`, defaulting to `hostname` if empty.
- Stops NameNodes, DataNodes, SecondaryNameNodes, JournalNodes, and ZKFC through `hadoop_uservar_su hdfs <subcmd> ... --daemon stop <subcmd>`.
- Discovers SecondaryNameNodes with `getconf -secondarynamenodes`, JournalNodes with `getconf -journalNodes`, and auto-HA with `getconf -confKey dfs.ha.automatic-failover.enabled`.

## Control flow
After initialization, it stops NameNodes on configured hosts, then DataNodes via the default workers file. It maps a SecondaryNameNode address of `0.0.0.0` to the local hostname and stops secondary NameNodes if non-empty. It stops JournalNodes if any are configured. Finally, if automatic failover is enabled, it stops ZKFC on the NameNode hosts. Unlike `start-dfs.sh`, it does not accumulate or explicitly return child exit statuses.

## State and persistence behavior
The script tears down daemon processes and affects PID/log state through common Hadoop daemon stop handling. It may change cluster availability immediately by stopping control-plane and data-plane services. It does not directly mutate HDFS metadata.

## Dependencies and integration points
It depends on `hdfs-config.sh`, `hdfs getconf`, worker mode, service-user variables, and common daemon stop logic. It integrates with the same nameservice, HA, JournalNode, and SecondaryNameNode configuration keys used by `start-dfs.sh`.

## Risks
- Failure status from intermediate stop commands is not aggregated, so the script's final exit code may reflect only the last command or shell fall-through rather than all failures.
- It does not skip SecondaryNameNode under HA the way `start-dfs.sh` does; behavior depends on `getconf -secondarynamenodes`.
- A bad workers file can stop the wrong DataNodes.
- Stopping ZKFC after NameNodes can affect HA behavior during shutdown ordering.

## Test signals
No direct test was found. Useful tests should stub `hdfs getconf` and `hadoop_uservar_su` to assert stop ordering, no-NameNode fallback, secondary `0.0.0.0` mapping, JournalNode and ZKFC branches, and failure propagation expectations. Cluster integration should verify full stop after `start-dfs.sh`.
