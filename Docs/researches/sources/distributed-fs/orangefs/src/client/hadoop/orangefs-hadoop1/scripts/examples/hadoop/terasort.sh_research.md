<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/scripts/examples/hadoop/terasort.sh -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/scripts/examples/hadoop/terasort.sh

## Purpose
Runs Hadoop example `terasort` from `teragen_data` to `terasort_data`.

## Important APIs, Types, And Functions
Executes the Hadoop examples jar with `terasort teragen_data terasort_data`. Comments mention optional `-D mapred.reduce.tasks`.

## Control Flow
One traced Hadoop command after changing to the script directory.

## State And Persistence
Reads `teragen_data` and creates sorted output at `terasort_data`.

## Dependencies And Integration Points
Depends on prior `teragen.sh`, Hadoop examples jar, `HADOOP_PREFIX`, `HADOOP_CONF_DIR`, and OrangeFS adapter read/write behavior.

## Risks And Test Signals
Risks include fixed paths, stale output, unquoted variables, no tuning defaults, and no cleanup. Test signals are successful sort completion and `teravalidate.sh` passing against `terasort_data`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/scripts/examples/hadoop/terasort.sh -->
