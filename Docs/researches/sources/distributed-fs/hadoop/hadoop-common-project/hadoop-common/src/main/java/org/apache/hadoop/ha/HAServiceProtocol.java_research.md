# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/HAServiceProtocol.java

Purpose: Defines the public RPC contract used by HA controllers and tools to monitor a service and request state transitions.

Important APIs and types: `HAServiceProtocol` has `versionID = 1L`, enum `HAServiceState` with `INITIALIZING`, `ACTIVE`, `STANDBY`, `OBSERVER`, and `STOPPING`, enum `RequestSource`, nested `StateChangeRequestInfo`, and idempotent methods `monitorHealth()`, `transitionToActive()`, `transitionToStandby()`, package-visible `transitionToObserver()`, and `getServiceStatus()`.

Control flow: Implementations receive calls from admin tools, health monitors, failover controllers, and protobuf translators. Request source metadata allows implementations to distinguish user, forced user, and ZKFC transitions.

State and persistence: Interface has no state, but calls mutate service HA state and may gate persistent service behavior such as write ownership. `HAServiceStatus` returned by `getServiceStatus()` includes readiness for activation.

Dependencies and integration points: Annotated for Kerberos principal lookup and idempotent retry. Implemented by HA services and exposed through protobuf RPC via `HAServiceProtocolPB` and translators.

Risks: Idempotence annotations mean callers and retry layers may repeat operations; service implementations must tolerate repeats. Observer support is not public in the same way as active/standby and must be handled carefully by implementers.

Test signals: Protocol translator tests, service implementation HA state transition tests, failover controller tests, health monitor tests, and admin command tests validate this contract.
