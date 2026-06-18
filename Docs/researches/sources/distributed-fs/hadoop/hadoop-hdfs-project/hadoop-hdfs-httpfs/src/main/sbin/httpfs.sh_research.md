# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/sbin/httpfs.sh

## Purpose
`httpfs.sh` is a deprecated compatibility wrapper for managing HttpFS, forwarding legacy `httpfs.sh run|start|status|stop` commands to the modern `hdfs httpfs` subcommand.

## Important APIs, Types, and Functions
It defines `print_usage`, emits a deprecation warning, maps `run` to `hdfs httpfs`, maps `start|stop|status` to `hdfs --daemon <mode> httpfs`, locates `${HADOOP_HOME}/bin` or derives `../bin` relative to the script directory, and `exec`s `hdfs`.

## Control Flow
The script validates at least one argument, branches on the first command, computes the Hadoop bin directory, and replaces the current process with the delegated `hdfs` command.

## State and Persistence
No persistent state is created. It only emits stderr/stdout and delegates to another process.

## Dependencies and Integration Points
It depends on the Hadoop `hdfs` command and on the shellprofile subcommand implementation for actual HttpFS launch behavior.

## Risks
Additional arguments beyond the first are ignored, so legacy callers cannot pass extra options through this wrapper. Missing `HADOOP_HOME` and unusual installation layouts can cause incorrect bin resolution. The script exits with status 0 on no arguments after printing usage because it calls plain `exit`.

## Test Signals
No shell tests are in this subset. Its behavior is operational compatibility rather than Java request behavior.
