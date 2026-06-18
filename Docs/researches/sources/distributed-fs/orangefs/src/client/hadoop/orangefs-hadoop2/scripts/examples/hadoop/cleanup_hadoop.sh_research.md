<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/scripts/examples/hadoop/cleanup_hadoop.sh -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/scripts/examples/hadoop/cleanup_hadoop.sh

## Purpose

Cleans or resets local Hadoop example runtime state. Cleanup removes `/tmp/hadoop-$USER` and `HADOOP_LOCAL_DIR` on each slave; reset stops daemons, cleans, and starts them again.

## Important APIs, Types, and Functions

This is an operational shell entry point rather than a library API. Its interface is the script name, positional arguments where documented, and required environment variables from comments or sourced `setenv` files.

Observed command surface:

- `cd $(dirname $0)`
- `. setenv`
- `for slave in $(cat $HADOOP_CONF_DIR/slaves); do`
- `ssh $slave "rm -rf /tmp/hadoop-$USER $HADOOP_LOCAL_DIR"`
- `done`

## Control Flow

The cleanup script sources `setenv` and loops over configured slaves with SSH. The reset wrapper sequences stop, sleep, cleanup, and start.

## State, Persistence, and Concurrency

The script changes daemon state, local temporary state, benchmark data, logs, or OrangeFS example storage depending on its role. It performs no locking, so concurrent invocations can race with daemons, SSH cleanup, benchmark runs, or jar updates.

## Dependencies and Integration Points

Requires `setenv`, `HADOOP_CONF_DIR/slaves`, SSH, and correct local-dir settings.

## Risks and Test Signals

It recursively removes paths from environment variables, so wrong variables can delete unintended data. Test in disposable environments and inspect expanded commands under `set -x`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/scripts/examples/hadoop/cleanup_hadoop.sh -->
