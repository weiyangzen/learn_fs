# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/sink/TestFileSink.java

## Purpose
Tests the plain `FileSink` by writing two annotated metrics records to a temporary file and checking the emitted textual format.

## Important APIs, Types, And Functions
Uses `FileSink`, `MetricsSystemImpl`, `ConfigBuilder`, `TestMetricsConfig`, annotated `MyMetrics1`/`MyMetrics2`, `MutableGaugeInt`, and `IOUtils.copyBytes()`.

## Control Flow
The test creates a temp output file under `${java.io.tmpdir}/${user.name}`, configures the metrics system with a large period and context filter `test1`, starts the system, registers metric sources, increments gauges, publishes immediately, stops/shuts down, reads the file, and matches it against a multiline regex.

## State And Persistence Behavior
The only persisted artifact is `outFile`, deleted in `@AfterEach`. Metrics source instances and system state are scoped to the test and explicitly shut down.

## Dependencies And Integration Points
Exercises metrics2 annotation discovery, source registration, sink file output, context filtering, UTF-8 reading, and metric/tag ordering behavior.

## Risks
The regex permits tag and metric reordering but assumes both records are emitted in registration order. Temp-directory permissions and hostname text in output can affect the file contents.

## Test Signals
The sink should write `test1.testRecord1` with `Context`, two tags, `Hostname`, and two gauges, followed by `test1.testRecord2` with its tag and hostname.
