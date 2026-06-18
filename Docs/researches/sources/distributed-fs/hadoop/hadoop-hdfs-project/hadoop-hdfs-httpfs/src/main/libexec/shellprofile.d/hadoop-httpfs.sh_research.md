# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/libexec/shellprofile.d/hadoop-httpfs.sh

## Purpose
`hadoop-httpfs.sh` integrates HttpFS into the modern Hadoop shell command framework as the `hdfs httpfs` daemon subcommand.

## Important APIs, Types, and Functions
When `HADOOP_SHELL_EXECNAME` is `hdfs`, it registers `httpfs` via `hadoop_add_subcommand`. Function `hdfs_subcommand_httpfs` sources optional `httpfs-env.sh`, marks daemonization support, sets `HADOOP_CLASSNAME` to `org.apache.hadoop.fs.http.server.HttpFSServerWebServer`, and appends Java system properties for HttpFS home/config/log/temp directories.

## Control Flow
On command execution, the function reads optional environment overrides (`HTTPFS_CONFIG`, `HTTPFS_HOME`, `HTTPFS_LOG`, `HTTPFS_TEMP`), falls back to Hadoop defaults, adds `-Dhttpfs.*.dir` options, and creates the temp directory for `start` or default daemon modes.

## State and Persistence
It mutates shell variables used by Hadoop launcher scripts and creates the temp directory. It does not persist configuration files.

## Dependencies and Integration Points
It depends on Hadoop shell helper functions such as `hadoop_add_subcommand`, `hadoop_add_param`, and `hadoop_mkdir`. The Java system properties it sets are consumed by `ServerWebApp` and `HttpFSServerWebServer`.

## Risks
Incorrect environment overrides can point HttpFS at the wrong config or log directory. Temp directory creation only occurs in start/default modes, so custom run modes must still have valid paths. The script assumes it is sourced in the Hadoop shell framework.

## Test Signals
No shell tests are in this subset. The Java tests simulate the same property contract by calling `HttpFSServerWebApp.setHomeDirForCurrentThread` and writing temporary `conf`, `log`, and `temp` directories.
