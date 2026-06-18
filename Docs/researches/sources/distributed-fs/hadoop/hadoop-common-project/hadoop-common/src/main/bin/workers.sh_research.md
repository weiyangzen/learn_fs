# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/bin/workers.sh

Purpose: helper script to run an arbitrary shell command across configured Hadoop worker hosts. It is the generic worker fan-out frontend used by administrators and higher-level scripts. The source was read as a complete 60-line script.

Important APIs/functions: defines `hadoop_usage`; sources `hadoop-config.sh`; uses `hadoop_exit_with_usage` and `hadoop_connect_to_hosts`.

Control flow: the script locates `libexec`, sources common configuration, requires at least one command argument, then passes the command to `hadoop_connect_to_hosts`, which uses `pdsh` if available or falls back to SSH with bounded parallelism.

State and persistence: no local persistent state is written. Remote commands may change state on worker hosts. Runtime state is derived from `HADOOP_WORKERS`, `HADOOP_WORKER_NAMES`, `HADOOP_CONF_DIR`, `HADOOP_SSH_OPTS`, and `HADOOP_SSH_PARALLEL`.

Dependencies and integration: integrates with the worker list file `${HADOOP_CONF_DIR}/workers` or deprecated `slaves`, optional `pdsh`, SSH, and the common config parser for `--hosts`, `--hostnames`, and `--config`.

Risks: command quoting and remote-shell interpretation are sensitive. Worker file contents and SSH options directly control target hosts. There is no high-level success aggregation beyond the underlying fan-out command. Running arbitrary commands across workers is operationally powerful and risky.

Test signals: local tests for missing arguments and worker-file resolution, integration tests with mock SSH/pdsh, hostnames versus hosts-file behavior, parallelism limits, and command/argument quoting cases.
