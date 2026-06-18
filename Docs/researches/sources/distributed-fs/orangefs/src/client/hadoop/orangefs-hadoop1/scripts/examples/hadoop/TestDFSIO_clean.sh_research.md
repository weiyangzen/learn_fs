<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/scripts/examples/hadoop/TestDFSIO_clean.sh -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/scripts/examples/hadoop/TestDFSIO_clean.sh

## Purpose
Runs Hadoop 1 `TestDFSIO -clean` to remove benchmark data/results from the configured Hadoop filesystem, expected to be OrangeFS-backed in these examples.

## Important APIs, Types, And Functions
Invokes `${HADOOP_PREFIX}/bin/hadoop --config ${HADOOP_CONF_DIR} jar ${HADOOP_PREFIX}/hadoop-test-1.?.?.jar TestDFSIO -clean`.

## Control Flow
The script traces commands, changes to its own directory, and executes one Hadoop command. It relies on Hadoop returning an exit status.

## State And Persistence
Deletes TestDFSIO benchmark artifacts in the Hadoop filesystem namespace.

## Dependencies And Integration Points
Depends on `HADOOP_PREFIX`, `HADOOP_CONF_DIR`, the Hadoop test jar glob, and the Hadoop filesystem configuration selecting OrangeFS where desired.

## Risks And Test Signals
Risks include unquoted variables, jar glob ambiguity, no explicit `set -e`, and comments mentioning file size even though clean does not use it. Test signals are successful cleanup after read/write runs and absence of TestDFSIO output paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/scripts/examples/hadoop/TestDFSIO_clean.sh -->
