# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/meta/MetaMaster.java

## Purpose
`MetaMaster` defines the central metadata/control-plane interface for Alluxio masters. It combines backup operations with master lifecycle/service behavior and exposes cluster configuration, identity, liveness, checkpoint, dynamic configuration, and proxy status operations.

## Important APIs, types, and functions
The interface includes cluster/config APIs (`getClusterID`, `getConfigCheckReport`, `getConfiguration`, `getConfigHash`, `getJournalSpaceMonitor`), path configuration mutations, version availability flag, master/worker address accessors, master id/register/heartbeat, safe mode, checkpoint, dynamic `updateConfiguration`, proxy heartbeat, and `listProxyStatus`. It extends `BackupOps` and `Master`.

## Control flow
The interface documents expected RPC flows: standby masters obtain/register ids and heartbeat to the leader; proxies heartbeat to the primary; clients request config/report/master info; admins trigger checkpoints and backups.

## State and persistence behavior
No state is stored in the interface. `DefaultMetaMaster` persists cluster id and path configuration while keeping liveness/config stores in memory.

## Dependencies and integration points
It depends on gRPC options/commands, Alluxio wire config/status types, backup ops, master lifecycle, and address types. Client, master, proxy, REST, and configuration service handlers all depend on this contract.

## Risks
The interface is broad, mixing admin, liveness, backup, configuration, and proxy APIs. Implementations must be careful about which methods are valid only on primary, which mutate journaled state, and which are safe on standby.

## Test signals
Contract tests should cover primary/standby behavior, RPC handler mappings, checkpoint/backup error propagation, path config journaling, dynamic config updates, proxy status lifecycle, and configuration hash consistency.
