# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/sink/TestStatsDMetrics.java

## Purpose
Tests `StatsDSink` datagram formatting for counter and gauge metrics, including hostname omission when the hostname tag is null.

## Important APIs, Types, And Functions
Uses `StatsDSink`, nested `StatsDSink.StatsD`, `setStatsd()`, `putMetrics()`, and `close()`. Metrics are mocked `AbstractMetric` instances with `MetricType.COUNTER` or `MetricType.GAUGE`.

## Control Flow
Each test opens a local `DatagramSocket`, injects a StatsD client pointed at that socket, sends a metrics record, receives one datagram, decodes it as UTF-8, and checks it against acceptable strings because metric set iteration is unordered.

## State And Persistence Behavior
State is ephemeral UDP socket state. The sink is closed in `finally`.

## Dependencies And Integration Points
Integrates metrics2 record/tag objects with StatsD UDP line protocol, including tag-derived prefixes for hostname, process, context, and record name.

## Risks
UDP receives can time out or see only one of multiple metrics depending on send behavior; tests accept either metric line. Hostname-null behavior must avoid leading empty components.

## Test Signals
Expected datagrams include `host.process.jvm.Context.foo1:1.25|c`, `host.process.jvm.Context.foo2:2.25|g`, or without hostname `process.jvm.Context.fooN:value|type`.
