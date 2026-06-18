# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/DatanodeManager.java

## Purpose

`DatanodeManager` is the NameNode's top-level coordinator for datanode membership, registration, host inclusion/exclusion, network topology, liveness policy, heartbeat responses, located-block sorting, slow-node reporting, and admin operations. It owns `HeartbeatManager`, `DatanodeAdminManager`, the datanode descriptor map, host-to-node index, topology object, and cluster load/statistics view used by placement policies.

## Important APIs, Types, and State

Core state includes `datanodeMap` keyed by datanode UUID, `networktopology`, `host2DatanodeMap`, `hostConfigManager`, `heartbeatExpireInterval`, `blockInvalidateLimit`, stale read/write configuration, slow peer/disk trackers, software-version counts, and cached `FSClusterStats`. Constructor configuration wires topology implementation, host provider, DNS-to-switch mapping, heartbeat intervals, stale intervals, invalidation limits, read sorting policy, slow peer/disk tracking, maintenance/decommission manager, and cache directive resend interval.

Public and package-level APIs include `activate()`, `close()`, `registerDatanode()`, `refreshNodes()`, lookup methods, `sortLocatedBlocks()`, `getDatanodeListForReport()`, `handleHeartbeat()`, `handleLifeline()`, `removeDatanode()`, `removeDeadDatanode()`, `startAdminOperationIfNecessary()`, `newFSClusterStats()`, slow peer/disk report accessors, and reconfiguration setters for heartbeat and invalidate limits.

## Control Flow

Registration first normalizes the registering IP/hostname from the RPC remote address when available, rejects unresolved hostnames if configured, injects block keys, checks host inclusion, and resolves conflicts between UUID and transfer address. Existing descriptors are updated in place when possible; replacement nodes with the same storage UUID update registration info, topology, host mapping, upgrade domain, software version counts, heartbeat registration, and admin operations. New descriptors are created, assigned topology/dependencies, added to maps/topology, registered with the block-report lease manager, and counted as live.

`refreshNodes()` reloads host configuration and, under the global write lock, calls `refreshDatanodes()`. Nodes not included are marked disallowed. Included nodes with a non-expired maintenance window start maintenance; excluded nodes start decommission; otherwise maintenance and decommission are stopped. Upgrade domain is refreshed for every node.

`handleHeartbeat()` validates registration/disallowed state, updates heartbeat stats, suppresses work in safe mode, prioritizes lease recovery commands, then builds transfer, EC reconstruction, invalidation, cache, key-update, and balancer-bandwidth commands. Replication work is split approximately by queue mix and max transfer capacity, with a special hard limit path for decommissioning nodes. It also ingests slow peer and slow disk reports.

Located-block sorting first moves inactive/stale/slow nodes toward the end, then sorts active replicas by network distance or shuffles them if random ordering is enabled. Striped sorting preserves block-index and token alignment after location reordering.

## State and Persistence Behavior

`DatanodeManager` state is in-memory and reconstructed from registration, host files/providers, and block reports. Host include/exclude and combined host providers persist desired membership/admin metadata externally. `datanodeMap` intentionally tracks all storages ever registered until safe removal; physical map wipe happens when a node restarts with a different storage ID or conflict resolution requires it. Slow peer collection uses a daemon and static concurrent UUID set.

## Dependencies and Integration Points

It is a nexus for `BlockManager`, `Namesystem`, `HeartbeatManager`, `DatanodeAdminManager`, `HostConfigManager`, `Host2NodesMap`, `NetworkTopology`/`DFSNetworkTopology`, DNS mappings, block placement policy via `FSClusterStats`, protocol commands, slow peer/disk trackers, and NameNode safe mode. Client-visible reports and located block responses depend on its filtering and sorting behavior.

## Risks and Edge Cases

Key risks include registration conflict handling, topology resolution failure, stale host include/exclude state, unsafe command delivery during safe mode, and preserving striped block token/index alignment while sorting. The heartbeat response path must not drain queued work in safe mode. Dead maintenance nodes are removed with optional block-map behavior depending on admin state. The `isSlowPeerCollectorInitialized()` method returns `slowPeerCollectorDaemon == null`, which reads like an inverted test name and is worth checking before reuse.

## Test Signals

Direct tests include `TestDatanodeManager`, `TestHeartbeatHandling`, `TestDataNodeLifeline`, `TestSortLocatedBlock`, `TestSortLocatedStripedBlock`, `TestReplicationPolicyExcludeSlowNodes`, `TestSlowPeerTracker`, `TestSlowDiskTracker`, `TestHostFileManager`, `TestHostsFiles`, and decommission/maintenance suites. Regression coverage should exercise registration replacement, disallowed nodes, host refresh transitions, safe-mode heartbeat behavior, slow-node ordering, and invalidation limits derived from heartbeat interval.
