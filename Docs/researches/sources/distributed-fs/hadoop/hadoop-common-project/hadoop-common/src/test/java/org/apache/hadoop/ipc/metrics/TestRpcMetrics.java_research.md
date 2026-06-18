# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/metrics/TestRpcMetrics.java

## Purpose

`TestRpcMetrics` verifies that an IPC `Server` registers both aggregate and detailed RPC metrics sources and unregisters them when stopped.

## Important APIs, Types, And Functions

The test creates an anonymous `Server` over `LongWritable`, gets `server.getRpcMetrics()` and `server.getRpcDetailedMetrics()`, queries `DefaultMetricsSystem.instance()`, and calls `server.stop()`.

## Control Flow

The server constructor initializes metrics. The test asserts both metric source names are present, stops the server, then asserts both are absent from the metrics system.

## State And Persistence Behavior

The relevant state is default metrics-system registration for the server lifetime. There is no external persistence.

## Dependencies And Integration Points

It integrates Hadoop IPC server lifecycle with metrics2 source registration and complements scheduler metrics lifecycle tests.

## Risks And Test Signals

Risks include metrics registry leaks, missing detailed metrics, or stop not unregistering sources. Signals are not-null source lookup before stop and null lookup after stop.
