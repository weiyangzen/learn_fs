# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/shellprofile.d/hadoop-s3guard.sh

Purpose: shell profile fragment registering the `hadoop s3guard` subcommand when the Hadoop shell command dispatcher is running.

Important APIs/types/functions: defines `hadoop_subcommand_s3guard` once. When invoked, the function sets `HADOOP_CLASSNAME=org.apache.hadoop.fs.s3a.s3guard.S3GuardTool` and adds the `hadoop-aws` tool jar to the classpath through `hadoop_add_to_classpath_tools`.

Control flow: guarded by `declare -f hadoop_subcommand_s3guard` to avoid redefining the function. If `HADOOP_SHELL_EXECNAME` is `hadoop`, it calls `hadoop_add_subcommand "s3guard" client "S3 Commands"` before defining the implementation.

State and persistence: mutates shell process variables and command registry only; no filesystem state.

Dependencies and integration: depends on Hadoop shell helper functions provided by the surrounding shell framework. Integrates S3Guard tooling into the `hadoop` CLI.

Risks: assumes shell dispatcher helpers are already sourced. The command points at S3Guard, a feature area with changing support status, so downstream packaging must ensure the class still exists.

Test signals: no local tests; behavior is normally validated by shell command discovery or packaging tests.
