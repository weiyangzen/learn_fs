# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/BadFencingConfigurationException.java

Purpose: Signals invalid fencing configuration, such as an unparsable method line, missing shell argument, invalid SSH port, unavailable class, or a class not implementing `FenceMethod`.

Important APIs and types: Public `BadFencingConfigurationException extends IOException` with string and string-plus-cause constructors.

Control flow: No internal logic beyond constructor delegation. It is thrown by `NodeFencer`, `FenceMethod.checkArgs()`, and runtime fencer validation paths, then handled by failover setup or fencer iteration.

State and persistence: Serializable exception state only, with `serialVersionUID = 1L`.

Dependencies and integration points: Integrated with `HAServiceTarget.checkFencingConfigured()`, `NodeFencer.create()`, `FailoverController`, `ZKFailoverController`, and concrete fencing methods.

Risks: Since it is an `IOException`, callers may conflate configuration failures with transport failures unless they catch it specifically. Good messages are important because operators must repair HA fencing before safe failover.

Test signals: `TestNodeFencer`, `TestShellCommandFencer`, `TestSshFenceByTcpPort`, and ZKFC startup tests should cover thrown messages and failure handling.
