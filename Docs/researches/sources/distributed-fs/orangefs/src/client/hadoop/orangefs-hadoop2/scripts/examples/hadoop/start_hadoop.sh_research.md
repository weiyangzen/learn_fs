<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/scripts/examples/hadoop/start_hadoop.sh -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/scripts/examples/hadoop/start_hadoop.sh

## Purpose

Starts the Hadoop 2 example daemons: ResourceManager locally and NodeManager, proxyserver, and historyserver through SSH for each configured slave.

## Important APIs, Types, and Functions

This is an operational shell entry point rather than a library API. Its interface is the script name, positional arguments where documented, and required environment variables from comments or sourced `setenv` files.

Observed command surface:

- `cd $(dirname $0)`
- `$HADOOP_PREFIX/sbin/yarn-daemon.sh --config ${HADOOP_CONF_DIR} start resourcemanager`
- `for slave in $(cat $HADOOP_CONF_DIR/slaves); do`
- `ssh $slave "$HADOOP_PREFIX/sbin/yarn-daemon.sh --config ${HADOOP_CONF_DIR} start nodemanager"`
- `ssh $slave "$HADOOP_PREFIX/sbin/yarn-daemon.sh --config ${HADOOP_CONF_DIR} start proxyserver"`
- `ssh $slave "$HADOOP_PREFIX/sbin/mr-jobhistory-daemon.sh --config ${HADOOP_CONF_DIR} start historyserver"`
- `done`
- `echo "Visit http://localhost:8088"`

## Control Flow

It reads `$HADOOP_CONF_DIR/slaves`, runs Hadoop daemon scripts with `--config`, and uses SSH for worker-side services.

## State, Persistence, and Concurrency

The script changes daemon state, local temporary state, benchmark data, logs, or OrangeFS example storage depending on its role. It performs no locking, so concurrent invocations can race with daemons, SSH cleanup, benchmark runs, or jar updates.

## Dependencies and Integration Points

Requires passwordless SSH, valid `slaves`, Hadoop daemon scripts under `HADOOP_PREFIX`, and matching configuration on all nodes.

## Risks and Test Signals

No error aggregation is performed, so one failed SSH command can leave a partial cluster. Check daemon logs, ports, and the ResourceManager UI after execution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/scripts/examples/hadoop/start_hadoop.sh -->
