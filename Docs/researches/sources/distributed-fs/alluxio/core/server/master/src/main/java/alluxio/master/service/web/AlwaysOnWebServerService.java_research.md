# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/service/web/AlwaysOnWebServerService.java

Purpose: web-server lifecycle variant that starts the master web server in standby and keeps it running across primary state changes.

Important APIs/types/functions: constructor forwards `MasterProcess`; overrides `start`, `promote`, `demote`, and `stop`.

Control flow: `start` calls inherited `startWebServer`; promotion and demotion are no-ops; `stop` calls inherited `stopWebServer`.

State and persistence: no local state; web server object is managed by `WebServerService`.

Dependencies/integration: selected by `WebServerService.Factory` for `AlluxioMasterProcess` when `STANDBY_MASTER_WEB_ENABLED` is true. Master process tests assert web readiness while standby under this mode.

Risks: web resources are available from standby masters, so REST handlers must enforce state-sensitive operations themselves. Repeated start is guarded by the base precondition.

Test signals: verify start creates a web server, promote/demote do not restart it, stop tears it down, and factory selection only applies to eligible master process type.
