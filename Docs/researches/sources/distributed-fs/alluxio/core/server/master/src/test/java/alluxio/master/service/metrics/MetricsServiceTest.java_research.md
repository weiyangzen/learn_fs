# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/service/metrics/MetricsServiceTest.java

## Purpose
`MetricsServiceTest` verifies which metrics simple-service implementation is selected for a master and how it manages `MetricsSystem` lifecycle in primary and standby roles.

## Important APIs, Types, and Functions
The tests use `MetricsService.Factory.create`, `AlwaysOnMetricsService`, `PrimaryOnlyMetricsService`, `start`, `promote`, `demote`, `stop`, and `MetricsSystem.isStarted`. Configuration is driven by `STANDBY_MASTER_METRICS_SINK_ENABLED`.

## Control Flow, State, and Persistence
When standby metrics sinks are enabled, the factory returns `AlwaysOnMetricsService`; `start` starts `MetricsSystem`, and repeated promote/demote cycles keep it running until `stop`. When standby metrics sinks are disabled, `PrimaryOnlyMetricsService` keeps metrics stopped on `start`, starts them on promote, stops them on demote, and leaves them stopped after `stop`. State is the global metrics-system started flag.

## Dependencies and Integration Points
The test integrates simple-service role transitions with the global metrics subsystem and Alluxio master standby configuration.

## Risks
Because the test reads global `MetricsSystem.isStarted`, previous tests that fail to stop metrics can contaminate results. The test does not clear metric contents, only started/stopped state.

## Test Signals
Passing tests show that standby metrics are either always emitted or primary-only according to configuration and that service stop leaves the metrics system stopped.
