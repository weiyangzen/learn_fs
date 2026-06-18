# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/MountTableRefresherThread.java

## Purpose
`MountTableRefresherThread` is the per-router worker used by `MountTableRefresherService` to invoke `refreshMountTableEntries` against either the local admin server or a remote router admin proxy.

## Important APIs, Types, And Functions
- The constructor accepts a `MountTableManager` and admin address, sets a descriptive daemon thread name, and stores the manager.
- `work()` runs under login-user credentials, refreshes Kerberos TGTs when security is enabled, calls `manager.refreshMountTableEntries`, records the response result, and always counts down the latch.
- `isSuccess()`, `setCountDownLatch`, `getAdminAddress`, and `toString()` expose worker state to the service.

## Control Flow
The inherited `SubjectInheritingThread` invokes `work`. The worker wraps the admin call in `SecurityUtil.doAsLoginUser`; successful responses drive the `success` flag, `IOException` is logged, and `finally` releases the parent latch. The service later reads `isSuccess` to log aggregate results and evict failed clients.

## State And Persistence
The thread stores only process-local execution state: target admin address, manager proxy, latch, and a boolean success flag. It does not persist anything itself; persistence happens through the target router's cache reload and state-store-backed mount table.

## Dependencies And Integration Points
It depends on `MountTableManager`, `RefreshMountTableEntriesRequest/Response`, Hadoop security utilities, and `SubjectInheritingThread`. It is instantiated by `MountTableRefresherService` for local and remote targets.

## Risks And Edge Cases
`countDownLatch` must be set before `start`; otherwise `finally` can throw `NullPointerException` after an admin failure. There is no explicit timeout inside the worker; the parent service controls waiting but not thread cancellation. A false response and an exception both appear as unsuccessful, so diagnostics rely on logs.

## Test Signals
Coverage is mainly through `TestRouterMountTableCacheRefresh` and secure refresh tests, which validate the service-level behavior that creates and observes these threads. Unit tests can use a fake `MountTableManager` to assert latch countdown and success flag handling.
