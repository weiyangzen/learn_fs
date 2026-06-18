# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/bin/hadoop-daemons.sh

Purpose: deprecated compatibility wrapper for running HDFS daemon operations across worker hosts through the old `hadoop-daemons.sh` interface. The source was read as a complete 77-line script.

Important APIs/functions: defines `hadoop_usage`; sources `hdfs-config.sh`; uses `hadoop_exit_with_usage` and `hadoop_error`; rewrites `HADOOP_USER_PARAMS`; invokes `hdfs --workers --daemon`.

Control flow: the script locates `libexec`, sources HDFS configuration, requires arguments, extracts the daemon mode, chooses the HDFS launcher, warns about deprecation, removes `start`, `stop`, or `status` tokens from the saved original user parameter array, then runs `hdfs --workers --daemon "$daemonmode" "${HADOOP_USER_PARAMS[@]}"`.

State and persistence: it mutates the transient `HADOOP_USER_PARAMS` array to avoid duplicating the daemon mode. Persistent logs, PID files, and remote process state are owned by the replacement HDFS worker/daemon command.

Dependencies and integration: depends on HDFS shell configuration and the shared worker fan-out behavior behind `hdfs --workers`. It preserves old multi-host operational scripts while delegating to the modern HDFS CLI.

Risks: token removal scans all saved user parameters, so an argument value equal to `start`, `stop`, or `status` could be dropped. Unlike the single-host wrapper, it does not `exec`, so exit/status propagation depends on the final command invocation. Missing HDFS installation fails at execution time.

Test signals: compatibility tests for multi-host start/stop/status, preservation of `--hosts` and daemon options, worker list handling, and regression tests for argument values that match daemon mode names.
