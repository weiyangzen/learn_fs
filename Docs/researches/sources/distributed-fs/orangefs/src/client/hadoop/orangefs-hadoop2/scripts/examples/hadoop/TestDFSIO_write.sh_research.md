<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/scripts/examples/hadoop/TestDFSIO_write.sh -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/scripts/examples/hadoop/TestDFSIO_write.sh

## Purpose

Runs Hadoop's `org.apache.hadoop.fs.TestDFSIO` benchmark in `write` mode against the configured OrangeFS-backed Hadoop filesystem.

## Important APIs, Types, and Functions

This is an operational shell entry point rather than a library API. Its interface is the script name, positional arguments where documented, and required environment variables from comments or sourced `setenv` files.

Observed command surface:

- `cd $(dirname $0)`
- `${HADOOP_PREFIX}/bin/hadoop \`
- `org.apache.hadoop.fs.TestDFSIO \`

## Control Flow

The script enters its directory and invokes `${HADOOP_PREFIX}/bin/hadoop --config ${HADOOP_CONF_DIR} org.apache.hadoop.fs.TestDFSIO -write` with two 64 MB files for read/write modes.

## State, Persistence, and Concurrency

The script changes daemon state, local temporary state, benchmark data, logs, or OrangeFS example storage depending on its role. It performs no locking, so concurrent invocations can race with daemons, SSH cleanup, benchmark runs, or jar updates.

## Dependencies and Integration Points

Requires `HADOOP_PREFIX`, `HADOOP_CONF_DIR`, Hadoop test classes on the classpath, and a running OrangeFS-backed Hadoop environment.

## Risks and Test Signals

Benchmark results are sensitive to `fs.ofs.file.buffer.size`, file layout, and leftover TestDFSIO data. Clean before and after runs; verify byte counts and task success in YARN logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/scripts/examples/hadoop/TestDFSIO_write.sh -->
