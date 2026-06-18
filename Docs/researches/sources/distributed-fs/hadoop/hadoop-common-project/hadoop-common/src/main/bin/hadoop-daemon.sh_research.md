# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/bin/hadoop-daemon.sh

Purpose: deprecated compatibility wrapper for starting, stopping, or checking HDFS daemons through the old `hadoop-daemon.sh` interface. The source was read as a complete 59-line script.

Important APIs/functions: defines `hadoop_usage`; sources `hdfs-config.sh`; uses `hadoop_exit_with_usage` and `hadoop_error`; dispatches to `hdfs --daemon`.

Control flow: the script locates `libexec`, sources HDFS configuration, requires at least one argument, treats the first argument as daemon mode, chooses `HADOOP_HDFS_HOME/bin/hdfs` or `HADOOP_HOME/bin/hdfs`, emits deprecation warnings, then `exec`s `hdfs --config "$HADOOP_CONF_DIR" --daemon "$daemonmode" "$@"`.

State and persistence: it owns no persistent state. The replacement `hdfs --daemon` command writes any daemon logs and PID files.

Dependencies and integration: depends on HDFS being installed beside Hadoop Common and on `hdfs-config.sh` providing the shared shell runtime. It preserves old command-line shapes while transferring control to the modern HDFS launcher.

Risks: invalid daemon modes are not validated locally and are left to the replacement command. If HDFS is not installed or `hdfs-config.sh` is missing, the wrapper fails early. Existing automation may rely on exact warning or argument behavior.

Test signals: compatibility smoke tests for `start`, `stop`, and `status`, missing HDFS installation tests, and checks that arguments after daemon mode are passed through to `hdfs`.
