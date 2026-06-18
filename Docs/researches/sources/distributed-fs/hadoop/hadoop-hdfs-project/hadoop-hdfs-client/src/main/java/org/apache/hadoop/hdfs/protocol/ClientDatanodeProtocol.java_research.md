# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/ClientDatanodeProtocol.java

## Purpose
`ClientDatanodeProtocol` defines the private/evolving RPC contract from HDFS clients to DataNodes for replica visibility, local path discovery, DataNode administration, reconfiguration, block reports, volume reports, and disk balancer operations.

## Important APIs, types, and functions
The interface is annotated with `@KerberosInfo` for the DataNode principal config key and `@TokenInfo(BlockTokenSelector.class)` for block-token authentication. `versionID = 9L` is historical and no longer updated for protobuf protocol serialization. Methods include `getReplicaVisibleLength`, `refreshNamenodes`, `deleteBlockPool`, `getBlockLocalPathInfo`, `shutdownDatanode`, `evictWriters`, `getDatanodeInfo`, reconfiguration start/status/list methods, `triggerBlockReport`, `getBalancerBandwidth`, `getVolumeReport`, disk balancer submit/cancel/query, and `getDiskBalancerSetting`.

## Control flow
As an interface it contains no executable flow. Implementations on the DataNode side enforce authorization, token checks, and operation semantics. Clients call methods through RPC proxies, often via helper classes such as `DFSUtilClient`.

## State and persistence behavior
The interface owns no state. Implementations may mutate DataNode runtime state, disk balancer plans, block pool directories, configuration, and block reporting behavior. `getBlockLocalPathInfo` exposes local data/meta paths only when DataNode security/authorization requirements are met.

## Dependencies and integration points
It depends on HDFS protocol types (`ExtendedBlock`, `BlockLocalPathInfo`, `DatanodeLocalInfo`, `DatanodeVolumeInfo`), security tokens, `BlockReportOptions`, `ReconfigurationTaskStatus`, `DiskBalancerWorkStatus`, and client config keys. `BlockReaderLocalLegacy` uses `getBlockLocalPathInfo`; administration tools use the DataNode management methods.

## Risks and test signals
Tests should cover protobuf/wire compatibility for every method, Kerberos principal and block-token behavior, local path authorization, delete-block-pool force semantics, shutdown-for-upgrade behavior, reconfiguration status lifecycle, block report triggering, disk balancer plan validation/cancellation/status, and client behavior across DataNode restarts or unsupported methods. Interface changes require matching `ClientDatanodeProtocol.proto` updates.
