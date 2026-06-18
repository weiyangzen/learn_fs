# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/bin/start-secure-dns.sh

## Purpose
`start-secure-dns.sh` starts secure DataNodes in a security-enabled cluster. Despite the filename using `dns`, the script starts `datanode` daemons; it is a root-run wrapper for secure DataNode startup.

## Important commands
- Defines simple usage text.
- Sources `hdfs-config.sh`.
- Calls `hadoop_uservar_su hdfs datanode "${HADOOP_HDFS_HOME}/bin/hdfs" --workers --config "${HADOOP_CONF_DIR}" --daemon start datanode`.

## Control flow
The script initializes configuration, prints `Starting datanodes`, and delegates DataNode daemon startup to the common service-user helper over worker hosts. It does not parse additional arguments.

## State and persistence behavior
State is created by downstream daemonization: secure DataNode processes, PID files, logs, and any privileged resources opened by `SecureDataNodeStarter` through the `hdfs` subcommand mapping. The wrapper itself writes no files.

## Dependencies and integration points
It depends on `hdfs-config.sh`, `hadoop_uservar_su`, worker host configuration, secure DataNode user variables such as `HDFS_DATANODE_SECURE_USER`, and `hdfs` mapping for the `datanode` subcommand. It uses secure-extra JVM defaults from `hdfs-config.sh`.

## Risks
- The file name `secure-dns` is misleading and can cause operational confusion because it starts DataNodes, not DNS services.
- Running as root is expected; incorrect secure/insecure user variables can fail before Java startup.
- No arguments are supported, so custom datanode startup options must come from environment/config.
- Blast radius follows the workers file.

## Test signals
No direct shell test was found. Validation should stub `hadoop_uservar_su` and confirm the exact DataNode worker/daemon arguments, then run secure cluster integration tests for privileged port/resource behavior.
