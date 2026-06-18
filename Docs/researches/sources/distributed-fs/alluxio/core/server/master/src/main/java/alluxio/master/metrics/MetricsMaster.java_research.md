# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/metrics/MetricsMaster.java

## Purpose
`MetricsMaster` is the interface for the Alluxio master that aggregates cluster-level metrics from workers and clients and exposes those metrics to RPC clients.

## Important APIs and Types
- Extends `Master`.
- `clearMetrics()` clears current master metrics.
- `clientHeartbeat(String, List<Metric>)` accepts client-side metric reports.
- `workerHeartbeat(String, List<Metric>)` accepts worker metric reports.
- `getMasterServiceHandler()` returns the metrics client service handler.
- `getMetrics()` returns metric name to protobuf `MetricValue`.

## Control Flow
Implementations receive heartbeat metrics from service handlers, store or aggregate them, and serve queries through `getMetrics`.

## State and Persistence
The interface does not prescribe persistence. `DefaultMetricsMaster` keeps metrics in memory and is `NoopJournaled`.

## Dependencies and Integration Points
Used by `MetricsMasterClientServiceHandler`, master service registration, worker/client metric heartbeat paths, and monitoring endpoints. Depends on Alluxio `Metric` and gRPC `MetricValue`.

## Risks and Edge Cases
Implementations must define concurrency and eventual consistency semantics for heartbeat ingestion and metric reads.

## Test Signals
Contract tests should verify clear, client heartbeat, worker heartbeat, service handler availability, and metric map output for concrete implementations.
