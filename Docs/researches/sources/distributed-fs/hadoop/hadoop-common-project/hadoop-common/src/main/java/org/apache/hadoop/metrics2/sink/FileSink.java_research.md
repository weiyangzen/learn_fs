<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/sink/FileSink.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/sink/FileSink.java

## Purpose
`FileSink` is a simple public metrics sink that writes each `MetricsRecord` as one text line to either stdout or a configured local file.

## Important APIs and Types
It implements `MetricsSink` and `Closeable`. `init(SubsetConfiguration)` reads `filename`; `putMetrics(MetricsRecord)` serializes timestamp, context, record name, tags, and metrics; `flush()` flushes the stream; `close()` closes it.

## Control Flow
Initialization chooses `System.out` when no filename is configured, otherwise it opens a UTF-8 `PrintStream` via NIO `Files.newOutputStream`. During each metrics update it prints `timestamp context.record: tag=value, metric=value` and terminates the line. Flush is explicit.

## State and Persistence
The only mutable state is the current `PrintStream`. When a filename is configured, metrics persist in that file and are overwritten or created according to `Files.newOutputStream` defaults. Without a filename, output goes to process stdout.

## Dependencies and Integration Points
The sink is loaded through metrics2 sink configuration and consumes `MetricsRecord`, `MetricsTag`, and `AbstractMetric` objects. It is a reference implementation for sink formatting.

## Risks and Test Signals
`close()` will close `System.out` when stdout mode is used, which callers must consider. There is no escaping of tag or metric values. Tests should cover stdout/file initialization, UTF-8 output, tag and metric ordering, flush behavior, and error wrapping in `MetricsException`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/sink/FileSink.java -->
