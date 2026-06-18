# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/bin/hadoop-config.sh

Purpose: shared bootstrap script sourced by Hadoop shell entry points. It locates and imports the function library, layout overrides, configuration directory, environment files, shell profiles, OS/Java setup, native paths, classpath, and user rc hooks. The source was read as a complete 165-line file.

Important APIs/functions: this file mostly executes shared functions rather than defining them. It calls `hadoop_deprecate_envvar`, `hadoop_bootstrap`, `hadoop_parse_args`, `hadoop_find_confdir`, `hadoop_exec_hadoopenv`, `hadoop_import_shellprofiles`, `hadoop_exec_userfuncs`, `hadoop_exec_user_hadoopenv`, `hadoop_verify_confdir`, `hadoop_os_tricks`, `hadoop_java_setup`, `hadoop_basic_init`, optional `hadoop_subproject_init`, `hadoop_shellprofiles_init`, `hadoop_add_javalibpath`, `hadoop_add_common_to_classpath`, `hadoop_shellprofiles_classpath`, and `hadoop_exec_hadooprc`.

Control flow: it enforces Bash 3.2+, determines `HADOOP_LIBEXEC_DIR`, sources `hadoop-functions.sh`, applies deprecated environment variable aliases, optionally sources layout, bootstraps defaults, saves original user parameters, parses generic shell options and shifts consumed arguments, loads site and user configuration in a deliberate order, runs OS and Java checks, initializes project homes and shell profiles, adds native library paths and common jars, then finalizes immediately for legacy callers unless `HADOOP_NEW_CONFIG` is set.

State and persistence: it mutates the caller's shell environment, including `HADOOP_HOME`, `HADOOP_CONF_DIR`, `JAVA_HOME`, `CLASSPATH`, `JAVA_LIBRARY_PATH`, `HADOOP_USER_PARAMS`, and parsed option counters. It persists no files directly.

Dependencies and integration: sourced by `hadoop`, `workers.sh`, `start-all.sh`, `stop-all.sh`, and other project-specific wrappers. It integrates with `hadoop-env.sh`, `${HOME}/.hadoop-env`, `${HOME}/.hadooprc`, `hadoop-layout.sh`, and `shellprofile.d` plugin hooks.

Risks: because it is sourced by non-Hadoop scripts for compatibility, argument parsing and global variable side effects are part of its public contract. User-provided code is sourced from configuration and home directories, so ordering matters for security and override behavior. Missing or incomplete configuration directories warn rather than always fail.

Test signals: shell BATS tests for option parsing and environment derivation, `hadoop envvars`, classpath and native path smoke tests, user rc/profile override tests, and compatibility tests for scripts that source this file directly.
