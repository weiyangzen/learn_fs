# subset-b-007476 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/pom.xml -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/pom.xml

## Purpose
This Maven module descriptor builds the `hadoop-hdfs` server-side jar for Apache Hadoop HDFS 3.6.0-SNAPSHOT. It inherits distribution-wide plugin and dependency management from `hadoop-project-dist`, marks the component as `hdfs`, and binds the module into Hadoop's build, test, webapp, protobuf, RAT, shell-test, and Java-8 compatibility workflows.

## Important build contracts
- Coordinates: parent `org.apache.hadoop:hadoop-project-dist:3.6.0-SNAPSHOT`, artifact `org.apache.hadoop:hadoop-hdfs`, packaging `jar`.
- Main dependencies include `hadoop-auth`, `hadoop-common`, `hadoop-hdfs-client`, Jetty, Jersey, protobuf, Netty, commons libraries, reload4j, shaded Guava, LevelDB JNI, Jackson, and Hadoop annotations.
- Test dependencies add `hadoop-common` test jar, ZooKeeper test jar, MiniKDC, Mockito inline, KMS and KMS test jar, BouncyCastle, Curator test, AssertJ, lz4, and JUnit 5.
- `maven-surefire-plugin` passes `runningWithNative` and installs `TimedOutTestsListener`.
- `maven-antrun-plugin` creates filtered webapp `web.xml` files during `compile`, rebuilds test data/log directories during `process-test-resources`, copies webapps into test classes, and stages `hdfs-default.xml` plus `configuration.xsl` for the site during `pre-site`.
- `protobuf-maven-plugin` compiles HDFS protos while adding Hadoop common and HDFS client proto paths.
- `replacer` runs for generated, main, and test sources, excluding `DFSUtil.java` from main source replacement.
- `hadoop-maven-plugins:resource-gz` gzips static webapp JS/CSS resources.
- `maven-javadoc-plugin` excludes generated protobuf packages from Javadocs.
- RAT excludes generated/binary/test fixtures, bundled web assets, config files, dev-support material, and webapp robots files.
- `maven-clean-plugin` removes site-staged `configuration.xsl` and `hdfs-default.xml`.

## Control flow
The build starts with inherited Hadoop lifecycle defaults, then this POM adds HDFS-specific phases. Compilation generates webapp descriptors and protobuf sources; resource generation gzips web static assets; test-resource processing resets local test state and copies webapps; optional profiles adjust test parallelism, shell testing, or Java 8 source roots. The `shelltest` profile is activated when tests are not skipped and executes `src/test/scripts/run-bats.sh` during the test phase.

## State and persistence behavior
The POM writes only build outputs under `${project.build.directory}` and temporarily copies site resources into `src/site/resources` before clean removes those staged files. Test state is intentionally reset under `${test.build.data}` and `${hadoop.log.dir}`. Parallel tests shard `test.build.data`, `test.build.dir`, and `hadoop.tmp.dir` by `${surefire.forkNumber}` while preserving `test.build.shared.data` for rare inter-fork coordination.

## Dependencies and integration points
This file is the integration hub between HDFS server code, HDFS client APIs, Hadoop common utilities, native/codec stacks, web UI servlets, federation tools, KMS security tests, and shell scripts. Its proto paths couple HDFS server generated classes to common and HDFS-client `.proto` definitions. Its shelltest profile directly validates scripts such as `src/main/bin/hdfs` and `hdfs-config.sh`.

## Risks
- Build behavior depends heavily on parent-managed versions and properties such as `${transient.protobuf2.scope}`, `${leveldbjni.group}`, `${test.build.data}`, and `${release-year}`.
- The antrun phases mutate generated webapp/test/site directories; stale outputs can hide missing source resources if clean is not run.
- RAT excludes are broad and must stay intentional because they can hide license drift in generated or bundled assets.
- Shell tests only run when the profile is active and `skipTests` is not set.
- The `parallel-tests` profile disables fork reuse and rewrites temp paths; tests that assume shared state outside `test.build.shared.data` can fail only in this profile.

## Test signals
- `mvn test -Pshelltest` exercises `src/test/scripts/run-bats.sh`, including focused BATS tests for `hdfs` subcommand dispatch and shell execution naming.
- `mvn test -Pparallel-tests` stresses fork-isolated HDFS tests.
- `TestHdfsConfigFields` compares `DFSConfigKeys` and `HdfsClientConfigKeys` against `hdfs-default.xml`.
- Build failures in protobuf, replacer, RAT, and webapp generation are strong integration signals for this module.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/pom.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/bin/distribute-exclude.sh -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/bin/distribute-exclude.sh

## Purpose
`distribute-exclude.sh` distributes a local HDFS exclude-hosts file to every configured NameNode. It supports the decommission workflow documented in the script comments: copy the file named by `dfs.hosts.exclude`, then run `refresh-namenodes.sh` so each NameNode reloads host membership.

## Important functions and commands
- Locates its `bin` directory and sources `${HADOOP_LIBEXEC_DIR:-$bin/../libexec}/hdfs-config.sh`.
- Validates `$1` as a non-empty path to an existing local file.
- Calls `$HADOOP_HOME/bin/hdfs getconf -namenodes` to discover NameNode hosts.
- Calls `$HADOOP_HOME/bin/hdfs getconf -excludeFile` to discover the remote target path from local configuration.
- Uses `scp "$excludeFilenameLocal" "$namenode:$excludeFilenameRemote"` for each NameNode and tracks any failure in `errorFlag`.

## Control flow
After setup, the script rejects a missing argument and a non-file path. It then resolves configured NameNodes and the remote exclude-file path. An empty remote path is fatal because it means `dfs.hosts.exclude` is not available in the local configuration. It iterates over all NameNodes, attempts an `scp`, records failures without aborting the loop, and exits 1 if any transfer failed.

## State and persistence behavior
The script persists the local file contents onto remote NameNode filesystems at the path configured by `dfs.hosts.exclude`. It does not modify HDFS state directly and does not reload NameNode configuration; the separate refresh script is required. It leaves no local state except command output.

## Dependencies and integration points
This script depends on `hdfs-config.sh`, Hadoop environment variables, `hdfs getconf`, SSH/SCP connectivity, consistent `dfs.hosts.exclude` configuration across NameNodes, and filesystem write permissions on the remote target directory. It integrates with `refresh-namenodes.sh` and the `DFS_HOSTS_EXCLUDE` config key in `DFSConfigKeys.java`.

## Risks
- The missing-argument branch contains a quoted string without `echo`, so the shell attempts to execute a command named `Error: please specify...`; it still exits 1, but the diagnostic is broken.
- It uses `$HADOOP_HOME/bin/hdfs` even though other scripts prefer `${HADOOP_HDFS_HOME}` after `hdfs-config.sh`; unusual HDFS layouts could fail.
- Hostnames and target paths are not escaped beyond shell quoting around the full `host:path` string; spaces in remote paths or unexpected `getconf` output are risky.
- No atomic remote copy is used, so NameNodes could observe a partially copied exclude file if an administrator refreshes concurrently.
- It assumes passwordless SSH or working credentials to all NameNodes.

## Test signals
There is no direct BATS test for this script in the focused shell tests. Useful validation is an integration test with a temporary `dfs.hosts.exclude`, multiple NameNode addresses from `hdfs getconf -namenodes`, a failing SCP target, and a follow-up `refresh-namenodes.sh`. Static shell checking should catch the missing `echo` bug.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/bin/distribute-exclude.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/bin/hdfs -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/bin/hdfs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/bin/hdfs-config.sh -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/bin/hdfs-config.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/bin/refresh-namenodes.sh -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/bin/refresh-namenodes.sh

## Purpose
`refresh-namenodes.sh` refreshes host include/exclude state on all configured NameNodes. It is a multi-NameNode wrapper around `hdfs dfsadmin -refreshNodes`, intended to be run after distributing a changed exclude file.

## Important commands
- Sources `hdfs-config.sh` from the resolved libexec directory.
- Discovers RPC addresses with `"${HADOOP_HDFS_HOME}/bin/hdfs" getconf -nnRpcAddresses`.
- For each address, runs `"${HADOOP_HDFS_HOME}/bin/hdfs" dfsadmin -fs hdfs://${namenode} -refreshNodes`.

## Control flow
The script initializes Hadoop shell state, retrieves NameNode RPC addresses, and records failure if discovery fails. If discovery succeeds, it loops over each address, prints a refresh message, executes `dfsadmin -refreshNodes` against that explicit `hdfs://host:port`, and records any failure. It exits 1 when discovery or any refresh fails; otherwise it prints completion.

## State and persistence behavior
This script causes each NameNode to reload host provider state from its configured include/exclude files. It does not write the files itself and persists no local state. The cluster state affected is administrative node admission/decommission state in NameNode memory and any resulting decommission/recommission transitions.

## Dependencies and integration points
It depends on `hdfs-config.sh`, `hdfs getconf`, `dfsadmin`, configured NameNode RPC addresses, and the same host files named by config keys such as `dfs.hosts` and `dfs.hosts.exclude`. It pairs with `distribute-exclude.sh` for full decommission file rollout.

## Risks
- If one NameNode refresh fails, the script continues refreshing others and exits 1 at the end; clusters can be temporarily inconsistent.
- It assumes `getconf -nnRpcAddresses` emits addresses usable in `hdfs://` URIs.
- It does not validate that distributed exclude files are identical across NameNodes.
- Authentication or authorization failures are only surfaced through command output and the final nonzero exit.

## Test signals
No direct shell unit test appears in the focused BATS files. Integration validation should stub or run `hdfs getconf -nnRpcAddresses` with multiple entries and verify each `dfsadmin -fs hdfs://... -refreshNodes` call, including partial failure handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/bin/refresh-namenodes.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/bin/start-balancer.sh -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/bin/start-balancer.sh

## Purpose
`start-balancer.sh` starts the HDFS Balancer as a daemon on the local machine. It is a compatibility wrapper around `hdfs --daemon start balancer`.

## Important functions and commands
- Defines `hadoop_usage` with common options plus balancer `-policy` and `-threshold`.
- Sources `hdfs-config.sh`.
- Executes `"${HADOOP_HDFS_HOME}/bin/hdfs" --config "${HADOOP_CONF_DIR}" --daemon start balancer "$@"`.

## Control flow
After resolving its directory and libexec path, the script loads HDFS configuration. It then replaces itself with the `hdfs` launcher via `exec`, preserving any user-supplied balancer options.

## State and persistence behavior
The script does not maintain state itself. Daemonization through `hdfs` persists Balancer PID/log files using common Hadoop daemon conventions and the Balancer performs cluster block movement according to configured policies.

## Dependencies and integration points
It depends on `hdfs-config.sh`, `HADOOP_CONF_DIR`, the `hdfs` launcher, and `org.apache.hadoop.hdfs.server.balancer.Balancer` as mapped by `hdfs`. Runtime behavior uses balancer config keys from `DFSConfigKeys.java`, including mover/dispatcher thread counts, bandwidth/QPS limits, keytab/principal options, and optional HTTP server settings.

## Risks
- It starts only a local balancer daemon; operators must run it where they want the daemon to live.
- Any argument validation is delegated to the Java Balancer and common shell handler.
- Misconfigured daemon PID/log directories or service user variables can make startup appear to fail before Java code is reached.

## Test signals
There is no direct BATS test for this wrapper. Useful checks are shell invocation with a stubbed `hdfs` binary to ensure exact argument forwarding, plus integration tests that validate the daemon maps to the Balancer class and honors `DFS_BALANCER_*` configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/bin/start-balancer.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/bin/start-dfs.sh -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/bin/start-dfs.sh

## Purpose
`start-dfs.sh` starts the core HDFS daemons for a cluster: NameNodes, DataNodes, optional SecondaryNameNodes, optional JournalNodes, and optional ZK Failover Controllers. It is intended to run from a master/control node.

## Important commands and variables
- Accepts optional `-upgrade` for NameNodes or `-rollback` for DataNodes, then appends remaining arguments to NameNode startup options.
- Discovers NameNodes with `hdfs getconf -namenodes`, defaulting to `hostname` if empty.
- Starts daemons with `hadoop_uservar_su hdfs <subcmd> "${HADOOP_HDFS_HOME}/bin/hdfs" --workers --config ... --daemon start <subcmd>`.
- Discovers SecondaryNameNodes via `getconf -secondarynamenodes`, JournalNodes via `getconf -journalNodes`, and automatic failover via `getconf -confKey dfs.ha.automatic-failover.enabled`.
- Accumulates exit status in `HADOOP_JUMBO_RETCOUNTER`.

## Control flow
The script initializes configuration, parses at most one leading startup option, and starts NameNodes on the configured hosts. It then starts DataNodes using the default workers file. If secondary NameNodes are configured, it skips them when NameNode HA appears configured, maps `0.0.0.0` to the local hostname, and starts them otherwise. If JournalNodes are configured, it starts them on their configured hosts. Finally, when automatic HA failover is enabled, it starts ZKFC on the NameNode hosts. The exit status is the sum of child command statuses.

## State and persistence behavior
The script persists daemon processes, PID files, logs, and in-cluster service state through the `hdfs --daemon start` calls. `-upgrade` and `-rollback` options alter HDFS storage startup behavior in downstream NameNode/DataNode code. The script itself stores only shell variables during execution.

## Dependencies and integration points
It depends on `hdfs-config.sh`, common shell user-switching logic, worker mode, `hdfs getconf`, service-user environment variables, configured workers/hostnames, and HDFS HA/JN/ZKFC configuration. It integrates with `DFSConfigKeys` keys for nameservices, HA, JournalNode addresses, service RPC addresses, and startup flags.

## Risks
- The usage string says `[-clusterId]`, but parsing only recognizes `-upgrade` and `-rollback`; other leading options trigger usage.
- Exit statuses are summed, so the final code can exceed normal 0/1 semantics and can lose exact failing component identity.
- HA detection for skipping SecondaryNameNode uses a comma check on `NAMENODES`; this is fragile if output format changes.
- Starting DataNodes through the workers file can start many remote daemons; a misconfigured workers file has high blast radius.
- Secure deployments require both secure and insecure service-user environment variables, as noted in comments.

## Test signals
No direct test for this wrapper appears in the focused BATS files. High-value validation stubs `hdfs getconf` and `hadoop_uservar_su` to cover no-NameNode fallback, `0.0.0.0` secondary handling, HA skip, JournalNode startup, ZKFC startup, and exit aggregation. Full integration is daemon start/stop on mini or test clusters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/bin/start-dfs.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/bin/start-secure-dns.sh -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/bin/start-secure-dns.sh

## Purpose
`start-secure-dns.sh` starts secure DataNodes in a security-enabled cluster. Despite the filename using `dns`, the script starts `datanode` daemons; it is a root-run wrapper for secure DataNode startup.

## Important commands
- Defines simple usage text.
- Sources `hdfs-config.sh`.
- Calls `hadoop_uservar_su hdfs datanode "${HADOOP_HDFS_HOME}/bin/hdfs" --workers --config "${HADOOP_CONF_DIR}" --daemon start datanode`.

## Control flow
The script initializes configuration, prints `Starting datanodes`, and delegates DataNode daemon startup to the common service-user helper over worker hosts. It does not parse additional arguments.

## State and persistence behavior
State is created by downstream daemonization: secure DataNode processes, PID files, logs, and any privileged resources opened by `SecureDataNodeStarter` through the `hdfs` subcommand mapping. The wrapper itself writes no files.

## Dependencies and integration points
It depends on `hdfs-config.sh`, `hadoop_uservar_su`, worker host configuration, secure DataNode user variables such as `HDFS_DATANODE_SECURE_USER`, and `hdfs` mapping for the `datanode` subcommand. It uses secure-extra JVM defaults from `hdfs-config.sh`.

## Risks
- The file name `secure-dns` is misleading and can cause operational confusion because it starts DataNodes, not DNS services.
- Running as root is expected; incorrect secure/insecure user variables can fail before Java startup.
- No arguments are supported, so custom datanode startup options must come from environment/config.
- Blast radius follows the workers file.

## Test signals
No direct shell test was found. Validation should stub `hadoop_uservar_su` and confirm the exact DataNode worker/daemon arguments, then run secure cluster integration tests for privileged port/resource behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/bin/start-secure-dns.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/bin/stop-balancer.sh -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/bin/stop-balancer.sh

## Purpose
`stop-balancer.sh` stops the local HDFS Balancer daemon. It is a compatibility wrapper around `hdfs --daemon stop balancer`.

## Important commands
- Defines usage for common buildpath/loglevel options.
- Sources `hdfs-config.sh`.
- Executes `"${HADOOP_HDFS_HOME}/bin/hdfs" --config "${HADOOP_CONF_DIR}" --daemon stop balancer`.

## Control flow
The script initializes configuration and then `exec`s the `hdfs` launcher to stop the Balancer daemon. It accepts no balancer-specific arguments in the final command.

## State and persistence behavior
Stopping state is delegated to Hadoop daemon handling: it reads PID files, signals the Balancer process, and updates logs according to common shell behavior. The wrapper itself persists nothing.

## Dependencies and integration points
It depends on the same shell/config path as `start-balancer.sh` and on the `hdfs` subcommand mapping for `balancer`. It must run on the machine where the Balancer daemon is running, as the comment states.

## Risks
- It stops only a local daemon; running it on a non-balancer host can produce false operational confidence.
- All error semantics come from the common daemon stop path.
- It cannot pass custom stop behavior beyond standard daemon stop.

## Test signals
No direct test was found. A shell stub test should verify exact forwarding to `hdfs --daemon stop balancer`; integration testing should verify PID/log handling with a running Balancer daemon.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/bin/stop-balancer.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/bin/stop-dfs.sh -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/bin/stop-dfs.sh

## Purpose
`stop-dfs.sh` stops the core HDFS daemons started by `start-dfs.sh`: NameNodes, DataNodes, optional SecondaryNameNodes, optional JournalNodes, and optional ZK Failover Controllers.

## Important commands and variables
- Sources `hdfs-config.sh`.
- Discovers NameNodes via `hdfs getconf -namenodes`, defaulting to `hostname` if empty.
- Stops NameNodes, DataNodes, SecondaryNameNodes, JournalNodes, and ZKFC through `hadoop_uservar_su hdfs <subcmd> ... --daemon stop <subcmd>`.
- Discovers SecondaryNameNodes with `getconf -secondarynamenodes`, JournalNodes with `getconf -journalNodes`, and auto-HA with `getconf -confKey dfs.ha.automatic-failover.enabled`.

## Control flow
After initialization, it stops NameNodes on configured hosts, then DataNodes via the default workers file. It maps a SecondaryNameNode address of `0.0.0.0` to the local hostname and stops secondary NameNodes if non-empty. It stops JournalNodes if any are configured. Finally, if automatic failover is enabled, it stops ZKFC on the NameNode hosts. Unlike `start-dfs.sh`, it does not accumulate or explicitly return child exit statuses.

## State and persistence behavior
The script tears down daemon processes and affects PID/log state through common Hadoop daemon stop handling. It may change cluster availability immediately by stopping control-plane and data-plane services. It does not directly mutate HDFS metadata.

## Dependencies and integration points
It depends on `hdfs-config.sh`, `hdfs getconf`, worker mode, service-user variables, and common daemon stop logic. It integrates with the same nameservice, HA, JournalNode, and SecondaryNameNode configuration keys used by `start-dfs.sh`.

## Risks
- Failure status from intermediate stop commands is not aggregated, so the script's final exit code may reflect only the last command or shell fall-through rather than all failures.
- It does not skip SecondaryNameNode under HA the way `start-dfs.sh` does; behavior depends on `getconf -secondarynamenodes`.
- A bad workers file can stop the wrong DataNodes.
- Stopping ZKFC after NameNodes can affect HA behavior during shutdown ordering.

## Test signals
No direct test was found. Useful tests should stub `hdfs getconf` and `hadoop_uservar_su` to assert stop ordering, no-NameNode fallback, secondary `0.0.0.0` mapping, JournalNode and ZKFC branches, and failure propagation expectations. Cluster integration should verify full stop after `start-dfs.sh`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/bin/stop-dfs.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/bin/stop-secure-dns.sh -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/bin/stop-secure-dns.sh

## Purpose
`stop-secure-dns.sh` stops secure DataNodes in a security-enabled cluster. Like the start script, the filename is misleading: it controls DataNodes, not DNS.

## Important commands
- Defines simple usage text.
- Sources `hdfs-config.sh`.
- Calls `hadoop_uservar_su hdfs datanode "${HADOOP_HDFS_HOME}/bin/hdfs" --workers --config "${HADOOP_CONF_DIR}" --daemon stop datanode`.

## Control flow
The script initializes HDFS shell configuration and delegates a worker-mode DataNode daemon stop to the common service-user helper. It accepts no additional arguments.

## State and persistence behavior
The downstream daemon handler stops DataNode processes and updates PID/log state. The wrapper itself writes nothing.

## Dependencies and integration points
It depends on common shell user switching, worker host configuration, secure DataNode environment variables, and `hdfs` datanode subcommand daemon support. It pairs with `start-secure-dns.sh`.

## Risks
- Misleading name can cause operator mistakes.
- It stops all DataNodes in the workers scope; incorrect workers configuration has large blast radius.
- It does not aggregate or print detailed per-host results itself.

## Test signals
No direct test was found. Stub tests should verify the exact `hadoop_uservar_su` invocation; secure-cluster integration should confirm it stops secure DataNodes started by the companion script.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/bin/stop-secure-dns.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/conf/hdfs-site.xml -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/conf/hdfs-site.xml

## Purpose
This is the default site-specific HDFS configuration override file shipped with the module. It is intentionally empty apart from the XML header, stylesheet reference, license, and `<configuration>` root, serving as the place for deployment-specific properties.

## Important structure
- XML declaration and `configuration.xsl` stylesheet reference.
- Comment instructing users to put site-specific property overrides in this file.
- Empty `<configuration>` element.

## Control flow
There is no executable control flow. Hadoop configuration loading merges this file after defaults when it is present on the configuration path, allowing properties here to override defaults from `hdfs-default.xml` and code constants.

## State and persistence behavior
The source file stores no active settings. In deployments, edits to this file persist administrative configuration such as NameNode addresses, DataNode directories, host include/exclude paths, security principals, HA settings, and balancing parameters.

## Dependencies and integration points
The file is consumed by Hadoop `Configuration` loading and by shell/admin commands through `HADOOP_CONF_DIR`. Scripts in this subset depend on properties typically supplied here: `dfs.hosts.exclude`, NameNode addresses, JournalNode addresses, SecondaryNameNode addresses, and `dfs.ha.automatic-failover.enabled`. `DFSConfigKeys.java` defines the constants/defaults that correspond to many possible entries.

## Risks
- An empty shipped file is correct for a template but unusable for most real clusters until site-specific properties are supplied.
- XML syntax errors or wrong property names fail at runtime/config load time.
- Configuration drift across NameNodes is dangerous for scripts such as `distribute-exclude.sh`, which assumes `dfs.hosts.exclude` is consistent across NameNodes.

## Test signals
`TestRefreshUserMappings` references the `hdfs-site.xml` resource path. Configuration-field tests compare constants and defaults mainly against `hdfs-default.xml`, not this empty site override. Operational validation is loading Hadoop configuration with a populated `HADOOP_CONF_DIR` and checking `hdfs getconf` output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/conf/hdfs-site.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/DFSConfigKeys.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/DFSConfigKeys.java

## Purpose
`DFSConfigKeys` is the server-side HDFS configuration constant catalog. It extends `CommonConfigurationKeys`, re-exports many client keys from `HdfsClientConfigKeys`, and defines NameNode, DataNode, JournalNode, Balancer, Mover, StoragePolicySatisfier, WebHDFS, security, HA, cache, erasure coding, disk balancer, topology, and compatibility defaults used throughout HDFS.

## Important APIs and types
- Class: `@InterfaceAudience.Private public class DFSConfigKeys extends CommonConfigurationKeys`.
- Re-exported key groups: block size, replication, checksum, many DFS client retry/read/write/short-circuit/mmap/failover keys, NameNode RPC/HTTP keys, and nameservice keys from `HdfsClientConfigKeys`.
- Default class constants: `RamDiskReplicaLruTracker`, `ReservedSpaceCalculator.ReservedSpaceCalculatorAbsolute`, `BlockPlacementPolicyDefault`, `BlockPlacementPolicyRackFaultTolerant`, `DFSNetworkTopology`, and `GlobalFSNamesystemLock`.
- Enum/default references: `HdfsConstants.StoragePolicySatisfierMode.NONE`, `HdfsConstants.StoragePolicy.HOT`, `HttpConfig.Policy.HTTP_ONLY`.
- Time defaults use a mix of raw milliseconds/seconds and `TimeUnit` conversions.

## Configuration domains
- Core file layout: block size, replication, bytes/checksum, checksum type, stream buffer size, storage directory permissions, name/edits dirs, data dirs, and min/max filesystem limits.
- NameNode operations: safe mode, checkpointing, heartbeat/redundancy intervals, block reports, lease recovery, retry cache, edit log rolling/async logging, fsimage transfer/load, resource checks, access control, snapshots, xattrs, quotas, and lock metrics.
- DataNode operations: volume scanning, cache reports, bandwidth throttles, disk checks, reserved capacity, lazy persist/RAM disk, slow peer/disk reporting, socket buffers, transfer behavior, EC reconstruction, same-disk tiering, and block scanner behavior.
- HA/federation: nameservices, HA NameNode prefix/id, auto failover, ZKFC port/SSL, tail edits/log roll, stale reads, JournalNode addresses/timeouts/cache, QJM timeouts, and Router-adjacent command support through the shell.
- Admin/data movement: Balancer, Mover, SPS, DiskBalancer, NameNode getBlocks QPS, keytab/principal settings, HTTP server settings, and storage policy defaults.
- Security/web: HTTPS keystore/truststore resources, Kerberos principals/keytabs, WebHDFS auth, data transfer encryption/SASL compatibility, block tokens, XFrame protection, encryption zone and re-encryption controls.
- Compatibility: many deprecated constants alias newer nested `HdfsClientConfigKeys` locations to preserve older HDFS server code and external references.

## Control flow
The class has no methods or runtime branching. Its behavior is compile-time/static constant publication. Runtime HDFS components import these constants and use Hadoop `Configuration` getters to resolve actual values, falling back to the defaults declared here or in `HdfsClientConfigKeys`.

## State and persistence behavior
This file does not persist state, but it defines the keys by which HDFS persists and loads administrative configuration from XML files such as `hdfs-default.xml` and `hdfs-site.xml`. Several defaults have direct persistence impact, such as NameNode edits/name directories, JournalNode edit directories, DataNode data directory permissions, retry cache expiry, fsimage transfer settings, and block report intervals.

## Dependencies and integration points
The class depends on Hadoop common configuration keys, HDFS client config keys, HDFS protocol constants, block placement classes, NameNode lock manager implementations, DataNode fsdataset helpers, WebHDFS URL connection defaults, and HTTP policy enums. It is used broadly by HDFS server code, tools, tests, and configuration documentation. Shell scripts in this subset indirectly rely on constants for `dfs.hosts.exclude`, nameservice/NameNode discovery, HA automatic failover, JournalNodes, and Balancer settings via `hdfs getconf` and daemon startup.

## Risks
- Constants are a cross-module API despite `Private`; renames or default changes can break config files, tests, docs, and downstream code.
- Unit semantics are inconsistent by historical convention: some keys are seconds, some milliseconds, some duration strings, and some raw counts. Misuse can create severe timing or resource bugs.
- Deprecated aliases can obscure the canonical source of a key and complicate field/documentation comparison.
- Hidden/internal/test-only keys are intentionally skipped by `TestHdfsConfigFields`; adding a new key without documentation or skip logic can fail tests.
- Some defaults are operationally powerful, for example permissions enabled, ACLs/xattrs enabled, caching enabled, block token disabled, HTTP-only policy, and default local `/tmp` storage paths.
- Broad static catalog makes merge conflicts likely when multiple HDFS features add keys near the same domain.

## Test signals
`src/test/java/org/apache/hadoop/tools/TestHdfsConfigFields.java` compares `DFSConfigKeys`, `HdfsClientConfigKeys`, and nested client key classes against `hdfs-default.xml`, with explicit skip lists for hidden, deprecated, example, native, dynamic, and module-specific properties. Many HDFS tests import these constants directly for behavior setup, including security, HA, block placement, cache, erasure coding, balancer, and CLI tests. Compilation itself is a strong signal because default class constants must remain assignable to the expected implementation types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/DFSConfigKeys.java -->
