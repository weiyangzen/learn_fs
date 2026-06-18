# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/main/libexec/shellprofile.d/hadoop-kms.sh

## Purpose
`hadoop-kms.sh` registers and configures the `hadoop kms` subcommand in Hadoop's shell framework.

## Important APIs, Types, and Functions
When the shell executable is `hadoop`, it adds a `kms` daemon subcommand. `hadoop_subcommand_kms` sources `kms-env.sh` if present, declares deprecated and active environment variables, enables daemonization, sets `HADOOP_CLASSNAME` to `KMSWebServer`, and appends required Java system properties for config dir, log dir, and log4j configuration.

## Control Flow
At command execution, it loads environment overrides, registers deprecation notices for old variables, declares KMS-specific variables as used, and creates the KMS temp directory when running or starting the daemon.

## State and Persistence
It mutates shell variables and ensures a temp directory exists. It does not directly start Java; the Hadoop shell framework does that after the handler returns.

## Dependencies and Integration Points
It depends on Hadoop shell helper functions such as `hadoop_add_subcommand`, `hadoop_add_param`, `hadoop_deprecate_envvar`, and `hadoop_mkdir`. It integrates with `KMSConfiguration.validateSystemProps` by setting `-Dkms.config.dir` and `-Dlog4j.configuration`.

## Risks
Incorrect `HADOOP_CONF_DIR` or `HADOOP_LOG_DIR` produces invalid system properties and startup failure. Deprecated environment variables are still recognized by Java server code, so shell and Java override behavior must stay aligned.

## Test Signals
Shell tests should verify subcommand registration, optional `kms-env.sh` sourcing, system property construction, daemonization support flag, temp directory creation, and deprecation messaging.
