# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/bin/start-all.sh

Purpose: legacy convenience script for starting all available Hadoop daemons from one host. It loads common configuration, warns when starting as a non-privileged user, then delegates to HDFS and YARN start scripts if present. The source was read as a complete 65-line script.

Important APIs/functions: defines `hadoop_abort_startall`; uses `hadoop_privilege_check`, `hadoop_error`, and shared config loading from `hadoop-config.sh`; invokes `start-dfs.sh` and `start-yarn.sh`.

Control flow: after locating and sourcing `hadoop-config.sh`, it checks privileges. If the user is not privileged, it installs an interrupt trap, emits warnings, sleeps for 10 seconds to allow abort, then removes the trap. It then calls `${HADOOP_HDFS_HOME}/sbin/start-dfs.sh --config "$HADOOP_CONF_DIR"` if present and `${HADOOP_YARN_HOME}/sbin/start-yarn.sh --config "$HADOOP_CONF_DIR"` if present.

State and persistence: this wrapper writes no state directly. Delegated HDFS/YARN scripts create daemon processes, logs, and PID files.

Dependencies and integration: depends on `hadoop-config.sh`, the shared privilege check, HDFS and YARN homes, and sibling `sbin` scripts. It is a top-level orchestration shim over project-specific daemon managers.

Risks: it encourages a single-user all-daemon deployment that the script itself warns is not recommended for production. Missing HDFS or YARN scripts are silently skipped. It does not aggregate or check downstream failure statuses beyond normal shell command behavior.

Test signals: smoke tests with HDFS-only, YARN-only, both present, and neither present; interrupt behavior during the warning delay; propagation of `--config`; and integration tests verifying daemon logs/PID files are created by delegated scripts.
