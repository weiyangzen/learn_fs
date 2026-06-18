<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/sink/ganglia/AbstractGangliaSink.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/sink/ganglia/AbstractGangliaSink.java

## Purpose
`AbstractGangliaSink` is the shared base for Ganglia metrics2 sinks. It manages hostname discovery, server parsing, multicast/unicast socket setup, Ganglia per-metric configuration, sparse mode configuration, and XDR buffer primitives.

## Important APIs and Types
The class implements `MetricsSink`. Important types are `GangliaSlope`, `GangliaConfType`, `GangliaMetricVisitor`, and `GangliaConf`. Protected helpers include `getGangliaConfForMetric`, `getHostName`, `xdr_string`, `xdr_int`, `emitToGangliaHosts`, `resetBuffer`, and `isSupportSparseMetrics`.

## Control Flow
`init` chooses a host name from `slave.host.name` or `DNS.getDefaultHost`, parses `servers` with default port 8649, applies multicast settings, loads arrays for `units`, `tmax`, `dmax`, and `slope`, creates a datagram or multicast socket, and records sparse support. `emitToGangliaHosts` sends the current XDR buffer to every configured server and then resets the buffer offset.

## State and Persistence
State is process-local: datagram socket, server list, hostname, XDR buffer and offset, config map, and sparse flag. Nothing is persisted by this class.

## Dependencies and Integration Points
Subclasses `GangliaSink30` and `GangliaSink31` use this base to encode protocol-specific packets. It depends on metrics2, Hadoop `DNS`, `Servers`, Java UDP sockets, and commons configuration.

## Risks and Test Signals
The fixed 1500 byte buffer has no bounds checks, so very long names or tags can overflow. Invalid `key=value` config can still fall through to array indexing. Tests should cover DNS fallback, multicast TTL setup, server parsing, per-metric config parsing, XDR padding, unresolved hosts, and buffer reset after exceptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/sink/ganglia/AbstractGangliaSink.java -->
