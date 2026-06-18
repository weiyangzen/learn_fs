# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RouterServiceState.java

## Purpose
`RouterServiceState` is the enum used to describe the lifecycle and availability state of a Router instance.

## Important APIs and Types
The enum values are `UNINITIALIZED`, `INITIALIZING`, `SAFEMODE`, `RUNNING`, `STOPPING`, `SHUTDOWN`, and `EXPIRED`. There are no methods beyond the enum constants.

## Control Flow
Other services set or compare these states. `RouterSafemodeService` transitions between `SAFEMODE` and `RUNNING`; `RouterRpcServer.clearStaleNamespacesInRouterStateIdContext` only runs cleanup while the Router reports `RUNNING`.

## State and Persistence
The enum itself has no state. Values are likely stored in Router state records and surfaced through admin/state-store APIs.

## Dependencies and Integration Points
It is referenced by `Router`, safe mode, admin/state-manager interfaces, and state-store records describing router availability.

## Risks
Adding or renaming states impacts serialization, admin output, and state-store compatibility. Logic that treats only `RUNNING` as active must be reviewed if new active states are introduced.

## Test Signals
Tests should assert Router lifecycle transitions and admin/state-store reporting for safe mode, running, shutdown, and expired routers.
