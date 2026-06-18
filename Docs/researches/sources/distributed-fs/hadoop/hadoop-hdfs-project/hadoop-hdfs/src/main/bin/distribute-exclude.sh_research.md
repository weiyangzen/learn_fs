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
