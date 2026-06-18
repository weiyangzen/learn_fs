# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/metrics/TimeSeriesStoreTest.java

## Purpose
`TimeSeriesStoreTest` validates the in-memory metric time-series recorder used by the master metrics layer. It checks single-series recording, multiple named series, and preservation of point order.

## Important APIs, Types, and Functions
The tests use `TimeSeriesStore.record`, `getTimeSeries`, `TimeSeries.getName`, and `TimeSeries.getDataPoints`. Assertions inspect data-point counts and values.

## Control Flow, State, and Persistence
Each test creates a fresh `TimeSeriesStore`. `recordTimeSeries` records two values under one metric name, with a short sleep to avoid same-millisecond timestamps. `recordMultipleTimeSeries` records distinct metric names and locates both resulting `TimeSeries` objects. `orderedTimeSeries` records two values and polls the queue to verify insertion order. State is in-memory only.

## Dependencies and Integration Points
The test depends on Alluxio `TimeSeries`, `TimeSeriesStore`, and `CommonUtils.sleepMs`. It integrates with the metric time-series data model consumed by monitoring and reporting paths.

## Risks
The test uses real sleeps to separate timestamps and mutates the data-point queues via `poll` in order checks. If the store changes from queue-like storage to immutable snapshots, this test would need updates.

## Test Signals
Passing tests show that metric names are grouped, multiple series coexist, values are retained, and data points are returned in record order.
