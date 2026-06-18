<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/scripts/examples/hadoop/stop_hadoop.sh -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/scripts/examples/hadoop/stop_hadoop.sh

## Purpose
Stops Hadoop 1 MapReduce daemons for the example environment.

## Important APIs, Types, And Functions
Runs `$HADOOP_PREFIX/bin/stop-mapred.sh` after changing to the script directory.

## Control Flow
Single traced command invocation; no explicit environment sourcing.

## State And Persistence
Stops Hadoop daemon processes. It does not remove runtime directories.

## Dependencies And Integration Points
Depends on `HADOOP_PREFIX`, Hadoop 1 scripts, and the configured cluster environment.

## Risks And Test Signals
Risks include missing `HADOOP_PREFIX`, unquoted path, no verification daemons stopped, and no `set -e`. Test signals are jobtracker/tasktracker processes gone and reset scripts able to clean local state after stop.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/scripts/examples/hadoop/stop_hadoop.sh -->
