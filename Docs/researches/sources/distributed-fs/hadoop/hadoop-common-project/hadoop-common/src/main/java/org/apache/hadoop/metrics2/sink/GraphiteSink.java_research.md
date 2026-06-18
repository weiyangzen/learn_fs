<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/sink/GraphiteSink.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/sink/GraphiteSink.java

## Purpose
`GraphiteSink` publishes metrics2 records to a Graphite plaintext TCP endpoint. It converts record context, record name, tags, and metric names into Graphite path components.

## Important APIs and Types
The sink implements `MetricsSink` and `Closeable`. Configuration keys are `server_host`, `server_port`, and optional `metrics_prefix`. The nested `Graphite` class owns the socket, UTF-8 writer, reconnection, flush, close, and connection failure counting.

## Control Flow
`init` parses the host and port, normalizes a null prefix to the empty string, constructs a `Graphite` helper, and connects immediately. `putMetrics` builds one line per metric as `path value timestamp`, using seconds from the record timestamp. On write failure it logs, closes the helper, and relies on later writes to reconnect. `flush` flushes the helper and also closes on failure.

## State and Persistence
State is the configured prefix and the nested socket/writer. No metrics are buffered beyond the current `StringBuilder`. Connection failures are counted and connection attempts stop silently once the maximum is exceeded.

## Dependencies and Integration Points
It integrates metrics2 with external Graphite servers and uses Hadoop `MetricsException` for hard setup/close failures. `setGraphite` is available for tests.

## Risks and Test Signals
Misconfigured or absent `server_port` throws during init. Paths include raw tag values and `name=value` segments, so special characters can create unexpected Graphite hierarchies. Tests should cover line formatting, timestamp conversion, reconnection after close, failure limit behavior, flush exceptions, and injected `Graphite` test doubles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/sink/GraphiteSink.java -->
