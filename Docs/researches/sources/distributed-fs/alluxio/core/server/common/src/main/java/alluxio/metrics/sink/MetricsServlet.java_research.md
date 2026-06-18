# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/metrics/sink/MetricsServlet.java

## Purpose
`MetricsServlet` is a metrics sink that exposes a Dropwizard `MetricRegistry` as pretty-printed JSON over HTTP.

## Important APIs, Types, and Functions
It defines `SERVLET_PATH` as `/metrics/json`, a shared Jackson `OBJECT_MAPPER` with Dropwizard `MetricsModule`, a constructor taking `MetricRegistry`, `createServlet()`, `getHandler()`, and no-op `start()`, `stop()`, and `report()`.

## Control Flow, State, and Persistence
`getHandler()` creates a Jetty `ServletContextHandler` at `/metrics/json` and mounts an anonymous servlet at `/`. The servlet handles GET by setting JSON content type, status OK, no-cache headers, serializing the registry, and writing the result. It stores no persistent state.

## Dependencies and Integration Points
It depends on Dropwizard metrics, Jackson, Jetty servlet handlers, and the Alluxio `Sink` interface. `WebServer` installs its handler alongside Prometheus and application servlet handlers.

## Risks and Test Signals
Risks include expensive registry serialization, no access control in this class, and pretty-printed output size. Signals are HTTP 200 JSON responses, no-cache headers, and serialization of gauges, counters, timers, and histograms.
