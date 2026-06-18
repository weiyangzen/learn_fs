# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/bin/stop-balancer.sh

## Purpose
`stop-balancer.sh` stops the local HDFS Balancer daemon. It is a compatibility wrapper around `hdfs --daemon stop balancer`.

## Important commands
- Defines usage for common buildpath/loglevel options.
- Sources `hdfs-config.sh`.
- Executes `"${HADOOP_HDFS_HOME}/bin/hdfs" --config "${HADOOP_CONF_DIR}" --daemon stop balancer`.

## Control flow
The script initializes configuration and then `exec`s the `hdfs` launcher to stop the Balancer daemon. It accepts no balancer-specific arguments in the final command.

## State and persistence behavior
Stopping state is delegated to Hadoop daemon handling: it reads PID files, signals the Balancer process, and updates logs according to common shell behavior. The wrapper itself persists nothing.

## Dependencies and integration points
It depends on the same shell/config path as `start-balancer.sh` and on the `hdfs` subcommand mapping for `balancer`. It must run on the machine where the Balancer daemon is running, as the comment states.

## Risks
- It stops only a local daemon; running it on a non-balancer host can produce false operational confidence.
- All error semantics come from the common daemon stop path.
- It cannot pass custom stop behavior beyond standard daemon stop.

## Test signals
No direct test was found. A shell stub test should verify exact forwarding to `hdfs --daemon stop balancer`; integration testing should verify PID/log handling with a running Balancer daemon.
