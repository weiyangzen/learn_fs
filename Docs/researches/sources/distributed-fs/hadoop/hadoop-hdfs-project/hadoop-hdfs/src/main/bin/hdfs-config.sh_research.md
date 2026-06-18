# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/bin/hdfs-config.sh

## Purpose
`hdfs-config.sh` is sourced by HDFS shell entry points to load common Hadoop shell machinery and establish HDFS-specific environment defaults. It is not meant to be executed directly.

## Important functions and variables
- `hadoop_subproject_init`: HDFS-specific initialization hook consumed by Hadoop common shell setup.
- Sources `${HADOOP_CONF_DIR}/hdfs-env.sh` once, guarded by `HADOOP_HDFS_ENV_PROCESSED`.
- Maps deprecated subproject variables to common variables with `hadoop_deprecate_envvar`.
- Sets `HADOOP_HDFS_HOME` defaulting to `HADOOP_HOME`.
- Exports defaults: `HDFS_AUDIT_LOGGER`, `HDFS_NAMENODE_OPTS`, `HDFS_SECONDARYNAMENODE_OPTS`, `HDFS_DATANODE_OPTS`, `HDFS_PORTMAP_OPTS`, `HDFS_DATANODE_SECURE_EXTRA_OPTS`, and `HDFS_NFS3_SECURE_EXTRA_OPTS`.
- Locates and sources `hadoop-config.sh` from `HADOOP_COMMON_HOME`, `HADOOP_LIBEXEC_DIR`, or `HADOOP_HOME/libexec`.

## Control flow
When sourced, the file defines `hadoop_subproject_init`, ensures `HADOOP_LIBEXEC_DIR` is set based on its own path if absent, then sources Hadoop common config. The common config is expected to call back into `hadoop_subproject_init`, which processes `hdfs-env.sh`, deprecation aliases, and defaults. If no common config can be found, it prints an error and exits 1 from the caller.

## State and persistence behavior
The file mutates only the current shell environment. The most important persistent downstream effects are environment variables that control daemon JVM options, audit logging, secure starter JVM mode, log/pid directory compatibility, and HDFS home path. It does not write files directly.

## Dependencies and integration points
Every listed shell script depends on this file. It integrates administrator-provided `hdfs-env.sh` with Hadoop common shell code and backward-compatible HDFS-specific environment names. It also provides the `hadoop_subproject_init` hook used by shared shell infrastructure across Hadoop modules.

## Risks
- A missing or wrong `HADOOP_CONF_DIR` prevents `hdfs-env.sh` customization from loading, but defaults can mask the omission.
- Because this file exits on missing common config, any script sourcing it terminates immediately.
- Deprecation aliasing means old and new variable names can conflict; the common helper's precedence rules become operationally important.
- The default HDFS audit logger is `INFO,NullAppender`, so deployments relying on this default may not emit audit logs where expected.

## Test signals
The BATS tests create a minimal temporary `hdfs-config.sh` to isolate `hdfs` command behavior, so they test the sourcing contract more than this file's body. Full validation comes from running shell commands with real `hadoop-config.sh`, exercising `hdfs-env.sh` overrides, deprecated variable aliases, and secure datanode/NFS launcher defaults.
