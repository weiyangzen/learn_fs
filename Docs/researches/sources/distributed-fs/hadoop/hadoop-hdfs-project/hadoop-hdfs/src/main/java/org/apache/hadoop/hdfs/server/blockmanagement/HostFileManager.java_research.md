# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/HostFileManager.java

## Purpose

`HostFileManager` is the classic include/exclude-file implementation of `HostConfigManager`. It loads configured host files, canonicalizes entries into resolved `InetSocketAddress` values, and answers whether datanodes are allowed or excluded.

## Important APIs, Types, and State

State includes `Configuration conf`, `HostSet includes`, and `HostSet excludes`. Methods include `setConf()`, `getConf()`, `refresh()`, `readFile()`, `parseEntry()`, `getIncludes()`, `getExcludes()`, `isIncluded()`, `isExcluded()`, `getUpgradeDomain()`, `getMaintenanceExpirationTimeInMS()`, and test-visible `refresh(HostSet, HostSet)`.

## Control Flow

`refresh()` reads `DFS_HOSTS` and `DFS_HOSTS_EXCLUDE`. `readFile()` uses `HostsFileReader` to load unique entries, parses each entry as a URI authority, defaults missing ports to zero, resolves it into an `InetSocketAddress`, and ignores unresolved or malformed entries with warnings. `isIncluded()` treats an empty include set as allow-all; otherwise the datanode's resolved address must match the include set. `isExcluded()` checks the exclude set.

## State and Persistence Behavior

Persistent state lives in external include/exclude files. `HostFileManager` holds synchronized in-memory `HostSet` snapshots and atomically swaps them on refresh. It does not persist upgrade domain or maintenance metadata; both return null/zero.

## Dependencies and Integration Points

`DatanodeManager` uses it by default as the host provider. It depends on `DFSConfigKeys`, `HostsFileReader`, `DatanodeID`, and `HostSet`. The parser's port-zero wildcard behavior must match `HostSet`.

## Risks and Edge Cases

DNS failures at refresh time drop entries. That is deliberate but can surprise operators if a host temporarily fails to resolve. Parsing via URI authority catches host:port syntax, but invalid lines are ignored rather than fatal. Classic host files cannot start maintenance mode or set upgrade domains; operators need the combined host provider for that.

## Test Signals

`TestHostFileManager`, `TestHostsFiles`, `TestDFSAdmin`, and `TestDatanodeRegistration` are primary signals. Tests should cover empty include allow-all behavior, wildcard port matching, unresolved entry warnings, malformed entries, exclude-driven decommission, and refresh swapping.
