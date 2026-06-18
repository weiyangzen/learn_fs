# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/FenceMethod.java

Purpose: Defines the plugin contract for HA fencing mechanisms. Implementations forcibly prevent an old active from making progress, for example by killing a process, denying storage access, or power cycling.

Important APIs and types: Public unstable `FenceMethod` extends the optional `Configurable` pattern by documentation. It declares `checkArgs(String)` for startup validation and `tryFence(HAServiceTarget, String)` for runtime fencing.

Control flow: `NodeFencer` instantiates implementations, calls `checkArgs()` while parsing configuration, and later invokes `tryFence()` in order until one succeeds.

State and persistence: Interface itself has no state. Implementations may receive Hadoop `Configuration` through `ReflectionUtils.newInstance()` if they implement `Configurable`.

Dependencies and integration points: Implemented by `ShellCommandFencer`, `SshFenceByTcpPort`, `PowerShellFencer`, and operator-provided classes. Uses `HAServiceTarget` for address and fencer environment details.

Risks: A `true` result is trusted as sufficient split-brain protection. Implementations need clear timeout, idempotence, and failure semantics. Bad argument validation can defer misconfiguration until an emergency failover path.

Test signals: Tests should parse custom and built-in methods, validate argument failures, check ordered fallback, and verify methods receive target metadata and configuration.
