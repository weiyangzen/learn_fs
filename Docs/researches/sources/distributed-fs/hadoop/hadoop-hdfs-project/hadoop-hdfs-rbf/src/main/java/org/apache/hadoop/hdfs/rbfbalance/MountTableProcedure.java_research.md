# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/rbfbalance/MountTableProcedure.java

Purpose: `BalanceProcedure` that updates a Router mount-table entry from the source namespace/path to the destination namespace/path after data movement, then makes the mount writable again.

Important APIs and types: fields `mount`, `dstPath`, `dstNs`, and `Configuration conf`; `execute()`, `updateMountTableDestination`, `getMountEntry`, `disableWrite`, `enableWrite`, `setMountReadOnly`, Writable `write/readFields`, and testing getters.

Control flow: `execute()` calls `updateMountTable()`, which updates the mount destination and calls `enableWrite`. Admin communication uses `DFS_ROUTER_ADMIN_ADDRESS_KEY`, `NetUtils.createSocketAddr`, `RouterClient`, and `MountTableManager`. `getMountEntry` fetches entries under a source path and picks the exact `sourcePath` match. Updates mutate the existing `MountTable`, submit `UpdateMountTableEntryRequest`, require a true response status, and refresh mount-table entries.

State and persistence: procedure state is serialized through `DataOutput` with `Text.writeString` and `Configuration.write`, allowing scheduler recovery. Persistent cluster state is the Router State Store mount-table record: destinations and readonly flag.

Dependencies and integration points: part of the fedbalance job pipeline created by `RouterFedBalance`. It integrates with Router admin RPC, state-store mount-table records, and `RouterDistCpProcedure` readonly control.

Risks: the procedure overwrites destinations with a single `RemoteLocation`, so multi-destination mounts are not preserved. Mutating the fetched `MountTable` in place assumes update semantics accept the modified object. If refresh fails or stale routers exist, clients may see old routing. Tests should cover missing mount errors, readonly toggling, serialization round trip, exact path matching, and successful refresh after update.
