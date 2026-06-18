# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/HealthCheckFailedException.java

Purpose: Indicates that an HA service responded to a health-check RPC but reported itself unhealthy.

Important APIs and types: Public `HealthCheckFailedException extends IOException` with message and message-plus-cause constructors.

Control flow: Thrown by `HAServiceProtocol.monitorHealth()` implementations, unwrapped by `HAServiceProtocolHelper`, and interpreted by `HealthMonitor` as `SERVICE_UNHEALTHY` rather than transport-level nonresponse.

State and persistence: Exception message and optional cause only, with `serialVersionUID = 1L`.

Dependencies and integration points: Used across protocol translators, health monitor, admin check-health command, and failover preflight checks.

Risks: Distinguishing this from generic `IOException` matters: health failure keeps the monitor connected but exits election, while IO failure treats the service as not responding and reconnects.

Test signals: `TestHealthMonitor`, `TestFailoverController`, and `HAAdmin -checkHealth` tests should assert unhealthy versus not-responding behavior.
