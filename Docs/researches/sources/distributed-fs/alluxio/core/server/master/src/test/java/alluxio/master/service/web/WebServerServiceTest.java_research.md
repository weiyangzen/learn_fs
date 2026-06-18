# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/service/web/WebServerServiceTest.java

## Purpose
`WebServerServiceTest` verifies master web service lifecycle for both primary-only and always-on standby modes. It asserts port binding, serving-state changes, and duplicate lifecycle rejection.

## Important APIs, Types, and Functions
The tests use `WebServerService.Factory.create`, `PrimaryOnlyWebServerService`, `AlwaysOnWebServerService`, `start`, `promote`, `demote`, `stop`, and `isServing`. The fixture mocks `AlluxioMasterProcess.createWebServer` to return a `MasterWebServer` bound to a reserved port.

## Control Flow, State, and Persistence
`setUp` reserves a web port and stubs the master process. With `STANDBY_MASTER_WEB_ENABLED=false`, `start` binds a rejecting server while `isServing` remains false; promote/demote toggles serving while the socket stays bound; stop releases the socket. With standby web enabled, `start` serves immediately and promote/demote keep it serving. Double-start tests assert duplicate rejecting-server or web-server startup throws.

## Dependencies and Integration Points
The test integrates master simple services with Jetty-backed `MasterWebServer`, Alluxio network service naming, configuration, sockets, and `CommonUtils.waitFor`.

## Risks
Socket polling can be affected by slow port release. The test relies on the mocked web server being close enough to real server behavior for lifecycle semantics. Literal exception message checks can fail after harmless text changes.

## Test Signals
Passing tests show that master web UI/API availability matches standby configuration, that rejected standby mode still owns the port, and that repeated start calls are guarded.
