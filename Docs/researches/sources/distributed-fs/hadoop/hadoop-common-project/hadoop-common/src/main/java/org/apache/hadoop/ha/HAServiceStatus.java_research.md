# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/HAServiceStatus.java

Purpose: Carries an HA service's current state and readiness-to-become-active reason from `getServiceStatus()` to controllers and admin tools.

Important APIs and types: `HAServiceStatus` stores `HAServiceState state`, `readyToBecomeActive`, and `notReadyReason`. It exposes `getState()`, fluent `setReadyToBecomeActive()`, `setNotReadyToBecomeActive(String)`, `isReadyToBecomeActive()`, and `getNotReadyReason()`.

Control flow: Services construct and return it from `HAServiceProtocol.getServiceStatus()`. `FailoverController` rejects failover to a standby that is not ready unless forced. `HealthMonitor` reports statuses to ZKFC service-state callbacks.

State and persistence: Mutable in-memory DTO only. It is serialized into protobuf responses by server-side translators and reconstructed by client-side translators.

Dependencies and integration points: Depends on `HAServiceProtocol.HAServiceState`; integrates with protobuf translation and controller readiness checks.

Risks: Default readiness is false until explicitly set, so service implementations must call one of the readiness setters. Missing not-ready reasons reduce operator diagnosis.

Test signals: Failover preflight tests should cover ready and not-ready statuses, forced activation, protobuf round trips, and service-state callback behavior.
