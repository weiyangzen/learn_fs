# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/AlluxioMasterProcessTest.java

Purpose: parameterized integration-style tests for `AlluxioMasterProcess` lifecycle under combinations of standby web and standby metrics settings.

Important APIs/types/functions: parameter data for four config combinations; `before`; tests `startStopPrimary`, `startStopStandby`, `startMastersThrowsUnavailableException`, ignored `stopAfterStandbyTransition`, ignored `restoreFromBackupLocal`, `startStopStandbyStandbyServer`; helpers `startStopTest`, `waitForSocketServing`, and `isBound`.

Control flow: tests configure temp ports, metastore, metrics, and journal folders, register RPC/web/metrics services, start the master in a thread, wait for socket or service readiness, then stop and assert ports are free. Standby tests vary expectations for real gRPC/web/metric serving according to config. The unavailable-start test spies `startMasterComponents` to throw `UnavailableException` and verifies the start loop does not exit as a success failure under demotion-exit config.

State and persistence: uses `NoopJournalSystem` for most cases and temporary directories for config isolation. It observes service state through sockets and service readiness rather than direct journal state.

Dependencies/integration: exercises `RpcServerService`, `WebServerService`, `MetricsService`, primary selectors, network address utilities, and master process service orchestration.

Risks: port binding tests can be timing-sensitive despite waits. Ignored tests document important but currently disabled behavior around demotion exit and restore-from-backup-local.

Test signals: protects primary and standby service binding, rejecting-server behavior, standby-enabled server modes, metric sink modes, clean shutdown of ports, and start-loop resilience to unavailable master component startup.
