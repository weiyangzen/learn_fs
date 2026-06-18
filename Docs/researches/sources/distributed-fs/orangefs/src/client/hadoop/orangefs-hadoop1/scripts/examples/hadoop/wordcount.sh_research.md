<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/scripts/examples/hadoop/wordcount.sh -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/scripts/examples/hadoop/wordcount.sh

## Purpose
Runs the Hadoop 1 example `wordcount` with caller-supplied input/output arguments using the example configuration.

## Important APIs, Types, And Functions
Sources `setenv` and executes `${HADOOP_PREFIX}/bin/hadoop --config ${HADOOP_CONF_DIR} jar ${HADOOP_PREFIX}/hadoop-examples-1.?.?.jar wordcount $@`.

## Control Flow
Traces commands, changes directory, loads environment, and forwards arguments to the Hadoop example.

## State And Persistence
Reads and writes paths determined by caller arguments in the configured Hadoop filesystem.

## Dependencies And Integration Points
Depends on Hadoop examples jar, `setenv`, and the OrangeFS Hadoop adapter for filesystem operations.

## Risks And Test Signals
Risks include unquoted `$@`, jar glob ambiguity, no check for required input/output args, and no cleanup of output path. Test signals are a successful wordcount over an OrangeFS input file and expected output counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/scripts/examples/hadoop/wordcount.sh -->
