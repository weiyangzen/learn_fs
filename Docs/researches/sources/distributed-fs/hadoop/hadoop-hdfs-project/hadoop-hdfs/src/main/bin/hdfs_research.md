# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/bin/hdfs

## Purpose
`hdfs` is the main HDFS command launcher. It maps public subcommands to Java class names, initializes Hadoop shell support, handles daemon and worker mode, supports dynamic subcommand overrides, and delegates final execution to the common Hadoop Java command handler.

## Important functions and APIs
- `hadoop_usage`: registers global options and all supported HDFS subcommands, then calls `hadoop_generate_usage`.
- `hdfscmd_case`: maps a subcommand to `HADOOP_CLASSNAME`, `HADOOP_SECURE_CLASSNAME`, and daemon support flags.
- Dynamic extension hook: if `hdfs_subcommand_${HADOOP_SUBCMD}` exists after sourcing config, it is invoked before built-in mapping.
- Common shell APIs from `hdfs-config.sh`/`hadoop-config.sh`: `hadoop_add_option`, `hadoop_add_subcommand`, `hadoop_need_reexec`, `hadoop_uservar_su`, `hadoop_verify_user_perm`, `hadoop_add_client_opts`, `hadoop_common_worker_mode_execute`, `hadoop_subcommand_opts`, and `hadoop_generic_java_subcmd_handler`.

## Subcommand mapping
The script supports daemon commands such as `namenode`, `datanode`, `journalnode`, `secondarynamenode`, `zkfc`, `balancer`, `mover`, `dfsrouter`, `diskbalancer`, `nfs3`, `portmap`, and `sps`; admin/client tools such as `dfs`, `dfsadmin`, `fsck`, `getconf`, `haadmin`, `cacheadmin`, `crypto`, `ec`, `debug`, `storagepolicies`, `fetchdt`, `jmxget`, snapshot commands, offline image/edit viewers, and `version`; and direct class execution if the supplied subcommand validates as a class name.

## Control flow
The script sets `HADOOP_SHELL_EXECNAME=hdfs`, locates `hdfs-config.sh` from `HADOOP_HOME` or the script directory, and sources it. It canonicalizes `MYNAME`, requires at least one argument, then extracts the subcommand. If common shell logic says this subcommand needs re-exec under a service user, it calls `hadoop_uservar_su` and exits. It verifies user permissions, stores remaining arguments, invokes a dynamic override function if present, otherwise maps the built-in subcommand, appends client options, optionally executes worker mode across hosts, applies subcommand-specific options, and finally calls the generic Java handler.

## State and persistence behavior
The script itself is stateless, but it sets global shell variables used by downstream common handlers to choose JVM classes, daemon PID/log behavior, secure starters, classpaths, and user switching. Daemon subcommands persist PID files and logs through common Hadoop daemon handling. The `envvars` subcommand prints computed environment state and exits without Java execution.

## Dependencies and integration points
It depends on `hdfs-config.sh` and Hadoop common shell functions. Java class mappings integrate with server packages under `org.apache.hadoop.hdfs.*`, client/admin tools, federation router/admin classes, NFS classes, and `org.apache.hadoop.util.VersionInfo`. The script is the target invoked by `start-dfs.sh`, `stop-dfs.sh`, balancer scripts, secure datanode scripts, and helper scripts that call `hdfs getconf`.

## Risks
- Subcommand behavior is global-variable driven; wrong ordering in dynamic overrides or common function changes can silently alter launches.
- The fallback direct-class path can run arbitrary valid class names from the Hadoop classpath.
- Re-exec and permission behavior depends on environment variables such as `HDFS_NAMENODE_USER`, `HDFS_DATANODE_USER`, secure-user variables, and common shell policy.
- `envvars` can expose environment paths and, in `QATESTMODE`, script internals.
- Worker mode depends on the configured workers file or `--hostnames` option and can fan out failures across hosts.

## Test signals
`src/test/scripts/hdfs_subcommands.bats` verifies dynamic subcommand addition, dynamic replacement of `cacheadmin`, `HADOOP_SHELL_EXECNAME` propagation, and multi-argument handling. `hadoop_shell_execname.bats` verifies that `MYNAME` resolves to the `hdfs` script and `HADOOP_SHELL_EXECNAME` is `hdfs`. Broader integration is covered when lifecycle scripts execute `hdfs --daemon` and Java tests exercise command classes.
