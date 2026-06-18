<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/scripts/examples/hadoop/teragen.sh -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/scripts/examples/hadoop/teragen.sh

## Purpose
Runs Hadoop example `teragen` to create 10,000,000 TeraSort records in `teragen_data`.

## Important APIs, Types, And Functions
Invokes `${HADOOP_PREFIX}/bin/hadoop --config ${HADOOP_CONF_DIR} jar ${HADOOP_PREFIX}/hadoop-examples-1.?.?.jar teragen 10000000 teragen_data`. Comments describe optional map task tuning.

## Control Flow
Traced script with one Hadoop job command.

## State And Persistence
Creates `teragen_data` in the configured Hadoop filesystem, which may map to OrangeFS through the adapter.

## Dependencies And Integration Points
Depends on Hadoop examples jar, `HADOOP_PREFIX`, `HADOOP_CONF_DIR`, and functional OrangeFS filesystem configuration.

## Risks And Test Signals
Risks include fixed output path, jar glob ambiguity, unquoted vars, and stale output causing job failure. Test signals are successful data generation, expected file count/size, and subsequent `terasort.sh` consuming the output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/scripts/examples/hadoop/teragen.sh -->
