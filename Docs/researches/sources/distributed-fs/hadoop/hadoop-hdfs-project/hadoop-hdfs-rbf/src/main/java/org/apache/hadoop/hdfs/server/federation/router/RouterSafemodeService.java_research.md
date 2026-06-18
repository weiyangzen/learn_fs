# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterSafemodeService.java

## Purpose
`RouterSafemodeService` is a `PeriodicService` that controls whether the Router should reject write operations as if it were a standby Namenode. It protects clients from stale State Store cache data during startup or after State Store cache refreshes stop.

## Important APIs and Types
The key methods are package-visible `isInSafeMode()`, package-visible `setManualSafeMode(boolean)`, private `enter()`, private `leave()`, `serviceInit(Configuration)`, and `periodicInvoke()`. It updates `RouterServiceState.SAFEMODE` and `RouterServiceState.RUNNING` through `router.updateRouterState`.

## Control Flow
On initialization, the service reads the safe mode check period, startup extension, and State Store expiration from `RBFConfigKeys`, records `startupTime`, and immediately enters safe mode. Each periodic tick waits until the startup interval expires, reads `StateStoreService.getCacheUpdateTime()`, considers the cache stale when it has never updated or exceeds the stale interval, enters safe mode if stale, and leaves safe mode only when cache data is fresh and safe mode was not manually set.

## State and Persistence
The service keeps volatile booleans for `safeMode` and `isSafeModeSetManually`, plus timing fields for startup, stale threshold, and safe-mode duration. It persists no data itself, but updates the Router service record/state and reports safe-mode duration into `RouterMetrics`.

## Dependencies and Integration Points
It depends on `Router`, `StateStoreService`, `RouterMetrics`, `PeriodicService`, and router safe-mode configuration keys. `RouterRpcServer.checkSafeMode` uses this service to reject unsafe client operations.

## Risks
Manual safe mode directly sets both flags; leaving manual safe mode requires callers to clear it correctly. If `StateStoreService.getCacheUpdateTime()` is stuck at zero, the Router remains in safe mode after startup. `leave()` logs an error if metrics are disabled but still transitions to running. The stale-cache check is only as accurate as the State Store cache timestamp.

## Test Signals
Tests should cover startup delay, stale cache entry, fresh cache exit, manual safe mode preventing automatic leave, Router state transitions, and metrics safe-mode duration update.
