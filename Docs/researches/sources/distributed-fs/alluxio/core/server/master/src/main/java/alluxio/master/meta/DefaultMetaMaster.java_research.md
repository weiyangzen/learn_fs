# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/meta/DefaultMetaMaster.java

## Purpose
`DefaultMetaMaster` is the core implementation of Alluxio's meta master. It manages cluster identity, master/proxy liveness, configuration reporting and dynamic updates, path-level configuration, backup roles, journal checkpointing, daily backup, update checks, and journal-space monitoring.

## Important APIs, types, and functions
It implements `MetaMaster` and extends `CoreMaster`. The nested `State` journals the cluster id under `CheckpointName.CLUSTER_INFO`. Service APIs include `getServices()`, `getStandbyServices()`, lifecycle `start(Boolean)`/`stop()`, backup methods, `checkpoint()`, configuration getters/hash/update, path configuration mutation, master id/register/heartbeat, proxy heartbeat/status, journal entry iteration/processing/reset, and liveness executors for lost masters/proxies and config report logging.

## Control flow
Construction registers worker configuration listeners with `BlockMaster`, initializes path properties and cluster state, and conditionally creates `JournalSpaceMonitor` for embedded journals on Linux. On primary start it registers the leader master's config, starts heartbeat threads for lost standby detection, config report logging, lost proxy detection, optional daily backups, optional journal-space monitor, initializes and journals a new cluster id if missing, optionally starts update checking, and uses `BackupLeaderRole`. On standby start it may run `MetaMasterSync` to heartbeat to the leader and may use `BackupWorkerRole`. Master ids are reused for known/lost addresses or randomly generated until unique. Heartbeats update mutable `MasterInfo`; timeouts move entries to lost sets.

## State and persistence behavior
Persisted state is cluster id plus path properties via journal entries. Live master/proxy sets, lost sets, config stores, backup role, newer-version flag, and monitor data are in-memory and rebuilt from runtime registration/heartbeat. `checkpoint()` delegates to `mJournalSystem.checkpoint` with the state lock manager. Dynamic configuration updates mutate runtime `Configuration` and notify `ReconfigurableRegistry`.

## Dependencies and integration points
It depends on `CoreMasterContext`, `BlockMaster`, journal system/context, backup roles, configuration stores/checker, path properties, heartbeat framework, UFS manager, Raft/UFS journal type config, OS detection, network utilities, generated meta-master service handlers, and Alluxio wire/gRPC config/status types.

## Risks
The class is `@NotThreadSafe` but heartbeat executors, RPC handlers, and maps/sets interact concurrently; mutable `IndexedSet` access needs careful synchronization. `mBackupRole` is added to services in `getServices`, so lifecycle ordering must ensure it is initialized before service discovery. Dynamic config updates only allow dynamic keys when enabled but parsing and reconfiguration failures are per-key. Master/proxy lost detection relies on local clock and heartbeat intervals.

## Test signals
Tests should cover primary and standby startup branches, cluster id journaling/replay, service registration, backup role selection, daily backup enablement, journal monitor condition, master id reuse/lost recovery, heartbeat timeout movement, proxy active/lost/delete transitions, config report/hash, path config journaling, dynamic config update success/failure, and checkpoint delegation.
