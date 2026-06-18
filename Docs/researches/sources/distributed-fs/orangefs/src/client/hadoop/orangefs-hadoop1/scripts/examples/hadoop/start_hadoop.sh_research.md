<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/scripts/examples/hadoop/start_hadoop.sh -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/scripts/examples/hadoop/start_hadoop.sh

## Purpose
Starts the Hadoop 1 MapReduce daemons for the example environment.

## Important APIs, Types, And Functions
Runs `$HADOOP_PREFIX/bin/start-mapred.sh` and prints the jobtracker URL `http://localhost:50030`.

## Control Flow
Traces commands, changes to the script directory, and invokes the Hadoop start script.

## State And Persistence
Starts Hadoop daemon processes and causes Hadoop runtime/log directories to be created by Hadoop itself.

## Dependencies And Integration Points
Depends on `HADOOP_PREFIX`, `HADOOP_CONF_DIR` being meaningful to the Hadoop scripts, and Hadoop 1 mapred tooling.

## Risks And Test Signals
Risks include comments saying environment variables are required but not sourcing `setenv`, unquoted variables, and assuming the UI is local. Test signals are running daemons, reachable jobtracker UI, and successful example job submission.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/scripts/examples/hadoop/start_hadoop.sh -->
