# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/bin/stop-secure-dns.sh

## Purpose
`stop-secure-dns.sh` stops secure DataNodes in a security-enabled cluster. Like the start script, the filename is misleading: it controls DataNodes, not DNS.

## Important commands
- Defines simple usage text.
- Sources `hdfs-config.sh`.
- Calls `hadoop_uservar_su hdfs datanode "${HADOOP_HDFS_HOME}/bin/hdfs" --workers --config "${HADOOP_CONF_DIR}" --daemon stop datanode`.

## Control flow
The script initializes HDFS shell configuration and delegates a worker-mode DataNode daemon stop to the common service-user helper. It accepts no additional arguments.

## State and persistence behavior
The downstream daemon handler stops DataNode processes and updates PID/log state. The wrapper itself writes nothing.

## Dependencies and integration points
It depends on common shell user switching, worker host configuration, secure DataNode environment variables, and `hdfs` datanode subcommand daemon support. It pairs with `start-secure-dns.sh`.

## Risks
- Misleading name can cause operator mistakes.
- It stops all DataNodes in the workers scope; incorrect workers configuration has large blast radius.
- It does not aggregate or print detailed per-host results itself.

## Test signals
No direct test was found. Stub tests should verify the exact `hadoop_uservar_su` invocation; secure-cluster integration should confirm it stops secure DataNodes started by the companion script.
