<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/scripts/examples/hadoop/cleanup_hadoop.sh -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/scripts/examples/hadoop/cleanup_hadoop.sh

## Purpose
Removes Hadoop temporary/local directories from each configured slave node for the example Hadoop cluster.

## Important APIs, Types, And Functions
Sources `setenv`, iterates over `$(cat $HADOOP_CONF_DIR/slaves)`, and runs `ssh $slave "rm -rf /tmp/hadoop-$USER $HADOOP_LOCAL_DIR"`.

## Control Flow
After tracing and directory change, it loads environment settings, then performs remote cleanup sequentially for each slave host.

## State And Persistence
Destructively removes `/tmp/hadoop-$USER` and `$HADOOP_LOCAL_DIR` on every listed slave.

## Dependencies And Integration Points
Depends on passwordless SSH, `HADOOP_CONF_DIR/slaves`, `HADOOP_LOCAL_DIR`, and a local `setenv` file. Used by reset/relaunch scripts.

## Risks And Test Signals
Risks include unquoted variables in a destructive `rm -rf`, missing/incorrect `setenv`, no handling for SSH failures, and legacy Hadoop slave file naming. Test signals are cleanup on all hosts, proper failure when a slave is unreachable, and Hadoop starting with fresh local dirs afterward.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/scripts/examples/hadoop/cleanup_hadoop.sh -->
