# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/Schedulable.java

## Purpose
`Schedulable` is the RPC call abstraction consumed by queues and schedulers. It exposes user identity, optional caller context, and priority level.

## Important APIs, Types, and Functions
`getUserGroupInformation()` returns the caller UGI. `getCallerContext()` defaults to throwing `UnsupportedOperationException` and is overridden by `Server.Call`. `getPriorityLevel()` returns the priority assigned by scheduling logic.

## Control Flow
Schedulers and `FairCallQueue` query these methods during call admission, priority selection, and identity attribution.

## State and Persistence Behavior
The interface has no state. Implementations represent live RPC calls and do not persist through this API.

## Dependencies and Integration Points
It depends on `UserGroupInformation` and `CallerContext`, and integrates with `RpcScheduler`, `IdentityProvider`, and `FairCallQueue`.

## Risks and Test Signals
Risks include callers assuming `getCallerContext` is always supported and priority values outside queue bounds. Tests should cover default exception behavior and valid priority mapping.
