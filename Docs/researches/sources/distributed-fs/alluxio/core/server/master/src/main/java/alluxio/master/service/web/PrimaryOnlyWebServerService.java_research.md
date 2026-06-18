# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/service/web/PrimaryOnlyWebServerService.java

Purpose: primary-only web service manager. It keeps the web port bound by a rejecting server while standby, and runs the real web UI/API server only while primary.

Important APIs/types/functions: `start`, `promote`, `demote`, `stop`, private `startRejectingServer`, `stopRejectingServer`, `waitForFree`, and `waitForBound`.

Control flow: `start` binds a `RejectingServer`. `promote` stops the rejecting server, waits for the port to free, and starts the inherited web server. `demote` stops the web server, waits for the port to free, and restarts the rejecting server. `stop` stops both, tolerating a null web server or rejecting server.

State and persistence: guarded nullable `RejectingServer` plus inherited guarded `WebServer`. No persistence.

Dependencies/integration: uses `RpcServerService.waitFor` for socket polling and `RejectingServer` for standby port behavior. Created by `WebServerService.Factory` when standby web is disabled or the process is not a full `AlluxioMasterProcess`.

Risks: no explicit precondition prevents double promotion from calling `startWebServer` when already running, but base `startWebServer` will reject an existing web server. Socket wait failures are swallowed.

Test signals: `WebServerServiceTest` should cover rejecting server bind on start, web readiness after promote, rejecting-server restoration after demote, stop cleanup, and port-bound assertions used by `AlluxioMasterProcessTest`.
