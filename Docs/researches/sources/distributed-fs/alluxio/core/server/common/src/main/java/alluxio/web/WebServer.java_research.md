# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/web/WebServer.java

## Purpose
`WebServer` bootstraps a Jetty web server for Alluxio services, including REST/webapp handlers, thread dump, JMX, CORS, JSON metrics, and Prometheus metrics.

## Important APIs, Types, and Functions
Important methods are the constructor, `getServerConnector()`, `addHandler()`, `setHandler()`, `disableMethod()`, `getServer()`, `getBindHost()`, `getLocalPort()`, `stop()`, and `start()`. It uses Jetty `Server`, `ServerConnector`, `QueuedThreadPool`, `ServletContextHandler`, `ConstraintSecurityHandler`, `HandlerList`, `MetricsServlet`, `PrometheusMetricsServlet`, `StacksServlet`, `JmxServlet`, and `CORSFilter`.

## Control Flow, State, and Persistence
The constructor validates service name/address, sizes a Jetty thread pool from `WEB_THREADS`, creates and opens a server connector early so ephemeral ports are resolved, configures a security servlet context with no sessions, disables TRACE and OPTIONS through constraint mappings, mounts thread dump and JMX servlets, installs CORS for all dispatcher types, and sets a handler list containing JSON metrics, Prometheus metrics, the service servlet context, and a default handler. `start()` starts Jetty and wraps failures; `stop()` stops connectors then the server.

## Dependencies and Integration Points
It depends on Alluxio configuration, metrics registry, REST prefix constants, Jetty, and service subclasses that add concrete handlers/servlets. It is a base class for master and worker web servers.

## Risks and Test Signals
Risks include opening the connector in the constructor, constraint mapping path scope, duplicate Prometheus collector registration through member initialization, CORS exposure, and incomplete shutdown if connector stop fails. Signals are bind host/port resolution, disabled TRACE/OPTIONS behavior, servlet availability at metrics/JMX/thread-dump paths, handler ordering when `addHandler()` is used, and stop releasing the port.
