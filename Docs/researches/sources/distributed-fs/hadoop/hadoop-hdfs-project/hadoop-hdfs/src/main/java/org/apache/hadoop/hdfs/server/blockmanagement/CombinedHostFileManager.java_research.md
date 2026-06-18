# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/CombinedHostFileManager.java

## Purpose

`CombinedHostFileManager` reads the JSON combined hosts file and answers include, exclude, upgrade-domain, and maintenance-expiration queries for datanodes. It replaces separate include/exclude files with one admin-state-aware source.

## Important APIs and types

- `refresh` reloads the configured hosts file using `CombinedHostsFileReader`.
- `HostProperties` stores a multimap from resolved `InetAddress` to `DatanodeAdminProperties`.
- `isIncluded`, `isExcluded`, `getUpgradeDomain`, and `getMaintenanceExpirationTimeInMS` answer datanode policy queries.
- `getIncludes` and `getExcludes` expose iterable socket addresses.
- `parseEntry` resolves hostnames and drops unresolved entries.

## Control flow

Refresh builds a new `HostProperties` instance, reads all JSON entries with optional timeout, resolves each hostname and port, adds valid entries, and atomically swaps the manager's current properties. Inclusion treats an empty set of normal in-service entries as "include everything"; otherwise a datanode is included if its resolved IP has a matching port or wildcard port zero entry. Exclusion checks for matching decommissioned entries. Maintenance expiration is returned only for matching `IN_MAINTENANCE` entries. Upgrade domain returns the first matching entry's upgrade domain.

## State and persistence behavior

The manager stores the current Hadoop `Configuration` and current in-memory `HostProperties`. The JSON file is the durable source. Refresh builds new state before swapping, avoiding partial update exposure.

## Dependencies and integration points

It integrates with `HostConfigManager`, `DatanodeAdminProperties`, `DatanodeID`, datanode admin states, `DFS_HOSTS` configuration, `CombinedHostsFileReader`, DNS resolution, decommission/maintenance management, and upgrade-domain placement policy.

## Risks and edge cases

DNS resolution happens only at refresh time; IP changes require refresh. Multiple entries for the same IP can make upgrade-domain selection depend on iteration order. Wildcard port zero intentionally matches all datanodes on a host. Unresolved entries are logged and ignored, which can admit or reject datanodes differently than intended.

## Test signals

Tests should cover empty include semantics, normal include entries, decommission excludes, maintenance expiration, wildcard ports, unresolved host drops, refresh atomicity, timeout reader path, and upgrade-domain matching with multiple entries.
