<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/scripts/examples/hadoop/wordcount.sh -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/scripts/examples/hadoop/wordcount.sh

## Purpose

Runs the Hadoop MapReduce examples jar command for `wordcount` against the configured OrangeFS-backed filesystem.

## Important APIs, Types, and Functions

This is an operational shell entry point rather than a library API. Its interface is the script name, positional arguments where documented, and required environment variables from comments or sourced `setenv` files.

Observed command surface:

- `cd $(dirname $0)`
- `. setenv`
- `${HADOOP_PREFIX}/bin/hadoop \`
- `jar ${HADOOP_PREFIX}/share/hadoop/mapreduce/hadoop-mapreduce-examples-?.?.?.jar \`

## Control Flow

The script changes to its directory, optionally sources `setenv`, then runs `hadoop --config` with the examples jar and fixed/default input-output paths.

## State, Persistence, and Concurrency

The script changes daemon state, local temporary state, benchmark data, logs, or OrangeFS example storage depending on its role. It performs no locking, so concurrent invocations can race with daemons, SSH cleanup, benchmark runs, or jar updates.

## Dependencies and Integration Points

Requires Hadoop example jars matching the wildcard, `HADOOP_PREFIX`, `HADOOP_CONF_DIR`, and a working YARN/MapReduce cluster using `ofs://` storage.

## Risks and Test Signals

Wildcard jar matching and hard-coded data directories can fail or collide with previous runs. Test by listing generated paths, checking job history, and validating output with `teravalidate` or `hadoop fs -cat` for wordcount.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/scripts/examples/hadoop/wordcount.sh -->
