<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/scripts/examples/hadoop/TestDFSIO_read.sh -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/scripts/examples/hadoop/TestDFSIO_read.sh

## Purpose
Runs Hadoop 1 `TestDFSIO -read` with two 64 MB files against the configured filesystem to benchmark read throughput.

## Important APIs, Types, And Functions
Invokes the Hadoop command with `TestDFSIO -read -nrFiles 2 -fileSize 64`. Comments document optional `-Dfs.ofs.file.buffer.size` override for the OrangeFS adapter.

## Control Flow
Traces commands, changes to its directory, and launches one Hadoop job.

## State And Persistence
Reads benchmark files and writes Hadoop/TestDFSIO result output in the configured filesystem/job output locations.

## Dependencies And Integration Points
Depends on `HADOOP_PREFIX`, `HADOOP_CONF_DIR`, the Hadoop test jar, existing TestDFSIO write data, and `OrangeFileSystem` honoring `fs.ofs.file.buffer.size`.

## Risks And Test Signals
Risks include fixed small workload, unquoted variables, ambiguous jar glob, and no cleanup/error enforcement. Test signals are successful job completion, expected read throughput counters, and buffer-size override changing adapter logs/behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/scripts/examples/hadoop/TestDFSIO_read.sh -->
