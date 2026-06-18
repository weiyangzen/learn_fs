# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/bin/hadoop

Purpose: primary Unix shell launcher for Hadoop Common commands. It declares user-facing `hadoop` subcommands, maps them to Java main classes or compatibility delegates, initializes the shared shell runtime, handles worker mode, and executes Java through the generic command handler. The source was read as a complete 244-line script.

Important APIs/functions: defines `hadoop_usage` and `hadoopcmd_case`. Important subcommands include `checknative`, `classpath`, `conftest`, `credential`, `daemonlog`, `dtutil`, `envvars`, `fs`, `jar`, `jnipath`, `kerbname`, `kdiag`, `key`, `registrydns`, `version`, and `rbfbalance`. It relies on shared functions such as `hadoop_add_option`, `hadoop_add_subcommand`, `hadoop_exit_with_usage`, `hadoop_need_reexec`, `hadoop_uservar_su`, `hadoop_verify_user_perm`, `hadoop_add_client_opts`, `hadoop_subcommand_opts`, and `hadoop_generic_java_subcmd_handler`.

Control flow: the script locates `libexec`, sources `hadoop-config.sh`, validates that a subcommand exists, optionally re-execs as a configured user, checks per-subcommand permissions, dispatches to a dynamic `hadoop_subcommand_<name>` function or the `hadoopcmd_case` switch, applies client options, handles `--workers` fan-out, applies subcommand-specific options, and finally calls the generic Java/daemon launcher. Deprecated HDFS and MapReduce command names are delegated to `hdfs` or `mapred`.

State and persistence: the script mutates process-global shell variables such as `HADOOP_CLASSNAME`, `HADOOP_SUBCMD`, `HADOOP_SUBCMD_ARGS`, `HADOOP_SECURE_CLASSNAME`, classpath/native-library paths, and daemonization flags. It persists no files directly, but downstream daemon mode writes logs and PID files.

Dependencies and integration: sourced runtime comes from `hadoop-config.sh` and `hadoop-functions.sh`. Java classes named here live in Hadoop Common, HDFS, tools, or security packages. It delegates deprecated commands to `HADOOP_HDFS_HOME` and `HADOOP_MAPRED_HOME` scripts and augments tools classpath for `rbfbalance`.

Risks: backwards-compatible delegation depends on sibling project installations. Unknown subcommands containing a dot are accepted as user Java class names, so validation is intentionally shallow. Shell state is global, so subproject extensions must avoid variable collisions. The `jar` path warns but still permits YARN application launch through the legacy command.

Test signals: BATS shell tests under the shelltest profile, `hadoop envvars`, `hadoop classpath`, `hadoop jnipath`, command-specific smoke tests, deprecated command delegation tests, and daemon/worker-mode integration tests.
