# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/throttle/DefaultThrottleMaster.java

Purpose: optional master component that periodically monitors master load indicators and logs/throttles status through `SystemMonitor`.

Important APIs/types/functions: extends `AbstractMaster` and implements `NoopJournaled`; `setMaster`, `getDependencies`, `getName`, `start`, `getServices`, and nested `ThrottleExecutor`.

Control flow: construction registers the master in `MasterRegistry`. `setMaster` must be called before startup and creates a `ThrottleExecutor`. `start(isLeader)` starts the base master, verifies dependencies, and only for leaders submits a `HeartbeatThread` using `MASTER_THROTTLE_HEARTBEAT_INTERVAL`. The executor delegates heartbeat work to `SystemMonitor.run`.

State and persistence: holds `MasterProcess`, `ThrottleExecutor`, and the future for the heartbeat service. It is `NoopJournaled`, so no journal state is persisted and no gRPC services are exposed.

Dependencies/integration: declares dependencies on `BlockMaster`, `FileSystemMaster`, and `MetricsMaster`. Uses master context executor services, heartbeat framework, configuration, and `SystemMonitor`.

Risks: `setMaster` is a required out-of-band initialization step. Standby masters do not run monitoring. The future is stored but not otherwise managed in this file; stop behavior relies on `AbstractMaster`.

Test signals: verify factory enablement, dependency set, leader-only heartbeat start, null-precondition failures when `setMaster` is omitted, and executor heartbeat delegation.
