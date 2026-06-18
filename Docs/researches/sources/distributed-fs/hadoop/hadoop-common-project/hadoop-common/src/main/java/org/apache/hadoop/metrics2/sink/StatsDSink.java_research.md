<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/sink/StatsDSink.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/sink/StatsDSink.java

## Purpose
`StatsDSink` publishes Hadoop metrics2 counters and gauges to a StatsD daemon over UDP using paths shaped like `hostname.service.context.record.metric:value|type`.

## Important APIs and Types
The sink implements `MetricsSink` and `Closeable`. Configuration keys are `server.host`, `server.port`, `skip.hostname`, `host.name`, and `service.name`. The nested `StatsD` helper lazily creates a `DatagramSocket` and reuses a `DatagramPacket`.

## Control Flow
`init` reads server settings, optionally resolves a local hostname via `NetUtils.getHostname`, stores the service name, and creates the helper. `putMetrics` lets well-known tags override host, context, and process/service name, then builds a prefix. For each metric it maps counters to `c`, gauges to `g`, appends the metric value, and sends the line with `writeMetric`. The helper resolves the server during socket creation and sends UTF-8 datagrams.

## State and Persistence
There is no durable state. Runtime state is the configured names and a lazily created UDP socket/packet.

## Dependencies and Integration Points
It integrates metrics2 with StatsD/collectd style UDP collectors. It uses `MsInfo` tags for host/context/process overrides and `NetUtils.wrapException` for socket creation diagnostics.

## Risks and Test Signals
Metric types other than counter/gauge produce a null StatsD type rather than being skipped. UDP sends are lossy and no flush is implemented. Service name may be null if not configured. Tests should cover tag override precedence, hostname skipping and truncation at dot, metric type mapping, error wrapping, injected `StatsD`, and close/reset behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/sink/StatsDSink.java -->
