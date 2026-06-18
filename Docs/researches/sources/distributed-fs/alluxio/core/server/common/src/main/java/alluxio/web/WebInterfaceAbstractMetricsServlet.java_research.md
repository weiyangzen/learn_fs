# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/web/WebInterfaceAbstractMetricsServlet.java

## Purpose
`WebInterfaceAbstractMetricsServlet` is a base servlet for UI pages that need to expose metric values as request attributes.

## Important APIs, Types, and Functions
It constructs an `ObjectMapper` with Dropwizard `MetricsModule` and provides `populateCounterValues(Map<String, Metric>, Map<String, Counter>, HttpServletRequest)`.

## Control Flow, State, and Persistence
`populateCounterValues()` iterates operation metrics, setting request attributes for gauges and counters, then sets request attributes for RPC invocation counters. It stores no persistent state beyond its mapper.

## Dependencies and Integration Points
It depends on Dropwizard metrics, Jackson, and servlet requests. Concrete web UI servlets use it to prepare metrics for JSP or template rendering.

## Risks and Test Signals
Risks include gauge value computation during request handling, ignoring non-gauge/non-counter metrics, and attribute name collisions. Signals are request attributes populated with current gauge values and counter counts.
