# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/bin/start-balancer.sh

## Purpose
`start-balancer.sh` starts the HDFS Balancer as a daemon on the local machine. It is a compatibility wrapper around `hdfs --daemon start balancer`.

## Important functions and commands
- Defines `hadoop_usage` with common options plus balancer `-policy` and `-threshold`.
- Sources `hdfs-config.sh`.
- Executes `"${HADOOP_HDFS_HOME}/bin/hdfs" --config "${HADOOP_CONF_DIR}" --daemon start balancer "$@"`.

## Control flow
After resolving its directory and libexec path, the script loads HDFS configuration. It then replaces itself with the `hdfs` launcher via `exec`, preserving any user-supplied balancer options.

## State and persistence behavior
The script does not maintain state itself. Daemonization through `hdfs` persists Balancer PID/log files using common Hadoop daemon conventions and the Balancer performs cluster block movement according to configured policies.

## Dependencies and integration points
It depends on `hdfs-config.sh`, `HADOOP_CONF_DIR`, the `hdfs` launcher, and `org.apache.hadoop.hdfs.server.balancer.Balancer` as mapped by `hdfs`. Runtime behavior uses balancer config keys from `DFSConfigKeys.java`, including mover/dispatcher thread counts, bandwidth/QPS limits, keytab/principal options, and optional HTTP server settings.

## Risks
- It starts only a local balancer daemon; operators must run it where they want the daemon to live.
- Any argument validation is delegated to the Java Balancer and common shell handler.
- Misconfigured daemon PID/log directories or service user variables can make startup appear to fail before Java code is reached.

## Test signals
There is no direct BATS test for this wrapper. Useful checks are shell invocation with a stubbed `hdfs` binary to ensure exact argument forwarding, plus integration tests that validate the daemon maps to the Balancer class and honors `DFS_BALANCER_*` configuration.
