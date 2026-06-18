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
