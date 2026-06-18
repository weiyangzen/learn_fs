# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/bin/stop-all.sh

Purpose: legacy convenience script for stopping all available Hadoop daemons from one host. It loads common configuration, warns before stopping as a non-privileged user, then delegates to HDFS and YARN stop scripts if present. The source was read as a complete 65-line script.

Important APIs/functions: defines `hadoop_abort_stopall`; uses `hadoop_privilege_check`, `hadoop_error`, and shared config loading from `hadoop-config.sh`; invokes `stop-dfs.sh` and `stop-yarn.sh`.

Control flow: the script locates and sources `hadoop-config.sh`, warns and delays for 10 seconds when not privileged, then calls `${HADOOP_HDFS_HOME}/sbin/stop-dfs.sh --config "$HADOOP_CONF_DIR"` if present. It then attempts to call a YARN stop script, but the path check uses `${HADOOP_HDFS_HOME}/sbin/stop-yarn.sh` rather than `${HADOOP_YARN_HOME}` in the source read here.

State and persistence: the wrapper has no direct persistent state. Delegated stop scripts terminate daemons and remove or update PID files.

Dependencies and integration: depends on shared shell configuration, privilege checks, and project-specific stop scripts. It is part of the legacy top-level operational interface.

Risks: the apparent YARN path check against `HADOOP_HDFS_HOME` can skip YARN shutdown in layouts where YARN is separate from HDFS. Like `start-all.sh`, it is coarse-grained and does not provide strong downstream status aggregation. Missing project scripts are silently skipped.

Test signals: smoke tests in combined and split HDFS/YARN layouts, especially verifying that YARN stop runs when only `HADOOP_YARN_HOME` contains `stop-yarn.sh`; interrupt behavior during warning delay; and daemon status checks after stop.
