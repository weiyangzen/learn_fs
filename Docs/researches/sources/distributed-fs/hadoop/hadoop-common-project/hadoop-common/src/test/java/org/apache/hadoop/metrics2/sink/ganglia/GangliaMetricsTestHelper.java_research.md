# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/sink/ganglia/GangliaMetricsTestHelper.java

## Purpose
Package-local test helper that exposes `AbstractGangliaSink.setDatagramSocket()` to tests outside the sink implementation.

## Important APIs, Types, And Functions
Defines `GangliaMetricsTestHelper.setDatagramSocket(AbstractGangliaSink, DatagramSocket)`.

## Control Flow
The static helper directly calls the package-private/protected sink setter. There is no branching.

## State And Persistence Behavior
It mutates the supplied sink's socket reference only. No persistent state.

## Dependencies And Integration Points
Depends on `AbstractGangliaSink` and `java.net.DatagramSocket`. It exists in the same package as Ganglia sinks to access non-public API.

## Risks
The helper can inject sockets whose lifecycle is owned elsewhere, so tests must close them. If sink visibility changes, the helper may become unnecessary or fail compilation.

## Test Signals
Useful signal is successful compilation and ability for Ganglia tests to inject a socket without reflection.
