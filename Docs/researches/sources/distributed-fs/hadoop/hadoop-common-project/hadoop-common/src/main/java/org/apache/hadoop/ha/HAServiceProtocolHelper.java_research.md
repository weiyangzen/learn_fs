# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/HAServiceProtocolHelper.java

Purpose: Wraps `HAServiceProtocol` calls and unwraps Hadoop `RemoteException` instances into the domain-specific exceptions expected by callers.

Important APIs and types: Static helpers are `monitorHealth()`, `transitionToActive()`, `transitionToStandby()`, and `transitionToObserver()`. Each accepts an `HAServiceProtocol` proxy and state-change info where relevant.

Control flow: Each helper invokes the corresponding protocol method in a try/catch and, on `RemoteException`, calls `unwrapRemoteException()` for `HealthCheckFailedException` or `ServiceFailedException`.

State and persistence: Stateless utility class. Persistent effects are only the remote protocol call effects.

Dependencies and integration points: Used by `FailoverController`, `ZKFailoverController`, and `HAAdmin` to avoid scattering remote-exception handling. Depends on Hadoop IPC `RemoteException`.

Risks: `monitorHealth()` accepts `reqInfo` but does not use it because the protocol method has no request-info parameter. If server-side exception classes change, unwrap behavior may stop preserving typed failures.

Test signals: Tests should exercise remote service failure propagation through failover/admin paths and verify callers receive `HealthCheckFailedException` or `ServiceFailedException` rather than raw `RemoteException`.
