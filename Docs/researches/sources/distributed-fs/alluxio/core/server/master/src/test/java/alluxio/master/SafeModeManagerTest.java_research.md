# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/SafeModeManagerTest.java

Purpose: unit tests for `DefaultSafeModeManager` timing and notification behavior.

Important APIs/types/functions: setup with `ManualClock`; tests `defaultSafeMode`, primary/RPC start notifications, leaving safe mode after RPC wait time, staying safe after primary start, and re-entering safe mode while already in safe mode.

Control flow: configuration rule sets `MASTER_WORKER_CONNECT_WAIT_TIME` to 100 ms. Tests drive notifications, advance manual clock, and assert `isInSafeMode`. RPC-server start establishes a timer after which safe mode exits; primary-master start keeps or resets safe mode without an exit timer.

State and persistence: only in-memory safe-mode manager state and manual clock. No persistence.

Dependencies/integration: validates the manager used by master process and notified by `RpcServerService.startGrpcServer`.

Risks: expected behavior is time-sensitive but deterministic through `ManualClock`. It does not test concurrent notifications.

Test signals: protects startup safe mode default, RPC wait timeout exit, primary start staying safe, timer reset on repeated RPC notification, and timer clearing on primary notification.
