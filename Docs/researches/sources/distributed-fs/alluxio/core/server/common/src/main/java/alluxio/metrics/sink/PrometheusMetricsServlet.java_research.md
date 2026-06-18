# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/metrics/sink/PrometheusMetricsServlet.java

## Purpose
`PrometheusMetricsServlet` exposes Dropwizard metrics in Prometheus format through the default Prometheus collector registry.

## Important APIs, Types, and Functions
It defines path `/metrics/prometheus`, constructors taking `MetricRegistry` or `Properties` plus registry, `getHandler()`, and no-op `start()`, `stop()`, and `report()`. It registers `DropwizardExports` in `CollectorRegistry.defaultRegistry`.

## Control Flow, State, and Persistence
Construction stores the default registry and registers a new Dropwizard exporter for the supplied registry. `getHandler()` creates a Jetty context and mounts Prometheus' `MetricsServlet` at `/`. There is no file persistence.

## Dependencies and Integration Points
It depends on Dropwizard metrics, Prometheus Java client, Jetty, and `Sink`. `WebServer` installs it next to the JSON metrics endpoint.

## Risks and Test Signals
Risks include duplicate exporter registration in the global default registry if multiple servlet instances are created, no unregister on stop, and path-level exposure of all registered metrics. Signals are scrapeable Prometheus text output and absence of duplicate collector exceptions during repeated web-server construction.
