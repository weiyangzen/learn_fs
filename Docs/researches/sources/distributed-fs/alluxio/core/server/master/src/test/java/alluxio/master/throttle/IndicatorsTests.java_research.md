# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/throttle/IndicatorsTests.java

## Purpose
`IndicatorsTests` validates `ServerIndicator`, the object used by throttling logic to snapshot and compare server resource indicators such as memory, CPU load, JVM pause time, RPC queue size, and Netty direct memory.

## Important APIs, Types, and Functions
The tests use `ServerIndicator.createFromMetrics`, copy/multiply constructors, `addition`, `reduction`, and getter methods for direct memory, Netty direct memory, heap max/used, CPU load, JVM pause values, RPC queue size, and snapshot time. The fixture starts a `JvmPauseMonitor` and registers JVM pause gauges.

## Control Flow, State, and Persistence
`before` enables JVM monitor configuration, starts a static `JvmPauseMonitor`, and registers three gauges in `MetricsSystem`. `basicIndicatorCreationTest` allocates direct buffers, captures indicators before and after a sleep, and compares direct memory and time fields. `basicIndicatorComparisonTest` constructs fixed indicators, verifies multiplication, reduction deltas, and addition/reduction aggregation arithmetic. State is runtime metric state and JVM memory allocation.

## Dependencies and Integration Points
The test integrates throttling indicators with `MetricsSystem`, `MetricKey`, direct buffer accounting, and JVM pause monitor metrics.

## Risks
Direct memory accounting can be JVM- and GC-sensitive. The first test uses real sleeps and assumes allocated direct buffers remain accounted for. The fixture starts a static monitor and stops it afterward, so failures before teardown can affect later tests.

## Test Signals
Passing tests show that server indicator snapshots can be built from metrics, time progresses, direct memory values are stable across snapshots, and arithmetic operations produce expected aggregate and delta indicators.
