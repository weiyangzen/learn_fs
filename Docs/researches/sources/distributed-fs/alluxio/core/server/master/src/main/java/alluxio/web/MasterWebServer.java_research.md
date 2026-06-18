# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/web/MasterWebServer.java

Purpose: Jetty/Jersey web server for the Alluxio master REST API and optional static web UI.

Important APIs/types/functions: constructor sets up REST resources, servlet context attributes, static resources, and SPA 404 fallback; `stop` closes the filesystem client before stopping the base server. Public context keys expose the master process and filesystem client.

Control flow: construction validates `AlluxioMasterProcess`, creates a Jersey `ResourceConfig` scanning master packages and protobuf object mapper provider, creates a `FileSystem` client, and installs a custom `ServletContainer` whose `init` stores master and filesystem objects in servlet context. If `WEB_UI_ENABLED`, it sets base resources from `WEB_RESOURCES/master/build`, registers `DefaultServlet`, sets `index.html`, and maps 404s to `/`.

State and persistence: owns one `FileSystem` client to service web/REST handlers. No persistent state.

Dependencies/integration: extends `WebServer`; integrates Jersey REST packages, Jetty servlets/resources, `AlluxioMasterProcess`, `FileSystem.Factory`, and configuration for static assets.

Risks: malformed resource paths only log an error and leave REST available without UI resources. The filesystem client is created at construction and must be closed on stop. REST handlers depend on exact servlet context key names.

Test signals: web service tests should verify REST servlet registration, context attributes after init, static UI enabled/disabled behavior, 404 fallback, and filesystem client closure on stop.
