# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/FailoverFailedException.java

Purpose: Represents a failed HA failover operation, including unsafe target state, failed health checks, failed fencing, failed activation, or failed failback.

Important APIs and types: Public `FailoverFailedException extends Exception` with message and message-plus-cause constructors.

Control flow: Thrown by `FailoverController.preFailoverChecks()` and `failover()`, then surfaced to admin tools or tests as an operational failure rather than an RPC-specific exception.

State and persistence: Exception message and optional cause only, with `serialVersionUID = 1L`.

Dependencies and integration points: Used by `FailoverController` and related tests. It deliberately does not extend `IOException`, which separates orchestration failures from lower-level RPC failures.

Risks: Callers must preserve causes to avoid hiding whether failure came from health, fencing, or activation. Messages are operator-facing and affect diagnosis.

Test signals: Manual failover tests should assert this exception for self-failover, non-standby target, unhealthy target, failed fencer, failed active transition, and failed failback.
