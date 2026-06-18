# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/ServiceFailedException.java

Purpose: Indicates failure while modifying an HA service or application state, especially active/standby/observer transitions.

Important APIs and types: Public `ServiceFailedException extends IOException` with message and message-plus-cause constructors.

Control flow: Thrown by `HAServiceProtocol.transition*()` implementations, unwrapped by protocol helpers and translators, and propagated through failover, admin, ZKFC, and elector callbacks.

State and persistence: Exception message and optional cause only, with `serialVersionUID = 1L`.

Dependencies and integration points: Used by `HAServiceProtocol`, `FailoverController`, `ZKFailoverController`, `ZKFCProtocol`, and admin paths.

Risks: This exception often decides whether election is retried, failback is attempted, or graceful failover reports failure. Losing the cause makes operator diagnosis difficult.

Test signals: Transition failure tests, failover failure tests, ZKFC active-attempt recording tests, and protobuf exception unwrap tests should assert it is preserved.
