<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/scripts/examples/hadoop/TestDFSIO_write.sh -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/scripts/examples/hadoop/TestDFSIO_write.sh

## Purpose
Runs Hadoop 1 `TestDFSIO -write` with two 64 MB files to benchmark OrangeFS-backed write throughput.

## Important APIs, Types, And Functions
Invokes `TestDFSIO -write -nrFiles 2 -fileSize 64`. Comments document adapter properties `fs.ofs.file.layout=PVFS_SYS_LAYOUT_RANDOM` and `fs.ofs.file.buffer.size`.

## Control Flow
Traces commands, changes to the script directory, and runs a single Hadoop job.

## State And Persistence
Creates TestDFSIO benchmark files and result output in the configured Hadoop filesystem.

## Dependencies And Integration Points
Depends on Hadoop 1 test jar, `HADOOP_PREFIX`, `HADOOP_CONF_DIR`, and the OrangeFS Hadoop adapter mapping create calls to layout/buffer settings.

## Risks And Test Signals
Risks include unquoted env vars, jar glob ambiguity, fixed benchmark scale, no `set -e`, and stale data if clean is not run. Test signals are successful file creation in OrangeFS, adapter layout setting observed in logs, and clean/read scripts working afterward.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/scripts/examples/hadoop/TestDFSIO_write.sh -->
