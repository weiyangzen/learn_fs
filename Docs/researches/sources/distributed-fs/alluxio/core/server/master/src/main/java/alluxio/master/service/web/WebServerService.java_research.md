# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/service/web/WebServerService.java

Purpose: abstract base for master web server lifecycle services, with factory selection for standby-enabled or primary-only behavior.

Important APIs/types/functions: guarded `WebServer mWebServer`, `isServing`, `startWebServer`, `stopWebServer`, and nested `Factory.create`.

Control flow: concrete services call `startWebServer` when their lifecycle mode should expose the web server. The helper checks no server exists, asks `MasterProcess.createWebServer`, and starts it. `stopWebServer` catches and logs stop failures, then clears the field. Factory chooses `AlwaysOnWebServerService` only for `AlluxioMasterProcess` with standby web enabled; otherwise it chooses `PrimaryOnlyWebServerService`.

State and persistence: service state is only the guarded `WebServer` reference. No journal persistence.

Dependencies/integration: implements `SimpleService`; integrates with master process service registration, web bind address configuration, and `MasterWebServer` creation.

Risks: `isServing` assumes `getServer()` is non-null after web server creation. Stop failures are logged but do not prevent clearing the reference, which could hide leaked Jetty resources.

Test signals: factory branch coverage, start/stop helper state, stop exception handling, and `isServing` behavior across lifecycle transitions.
