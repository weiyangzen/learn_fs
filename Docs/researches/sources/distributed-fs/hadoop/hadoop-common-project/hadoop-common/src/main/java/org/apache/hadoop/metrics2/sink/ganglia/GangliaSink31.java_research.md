<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/sink/ganglia/GangliaSink31.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/sink/ganglia/GangliaSink31.java

## Purpose
`GangliaSink31` adapts `GangliaSink30` emission logic to the Ganglia 3.1 protocol by overriding packet encoding.

## Important APIs and Types
The only overridden API is `emitMetric(String groupName, String name, String type, String value, GangliaConf gConf, GangliaSlope gSlope)`. All configuration, sparse/dense selection, tag prefix logic, and metric traversal come from `GangliaSink30` and `AbstractGangliaSink`.

## Control Flow
The method validates name, value, and type, logs at debug level, emits a metadata packet with metric id 128 and a `GROUP` extra field, sends it, then emits a value packet with metric id 133 and sends it. The buffer is reset by `emitToGangliaHosts` after each send.

## State and Persistence
No additional state is introduced. It uses inherited socket and XDR buffer state. Ganglia receives metadata and value datagrams for every emitted metric.

## Dependencies and Integration Points
It targets Ganglia 3.1 gmond. Protocol field order is documented as derived from `gm_protocol.x` and `gmetric` tracing.

## Risks and Test Signals
Metadata is resent every metric update rather than cached, increasing traffic. Buffer overflow risks are inherited. Tests should assert the two-packet sequence, metric ids, hostname/name/type/units/slope/tmax/dmax fields, GROUP extra field, null guard behavior, and inherited sparse/dense behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/sink/ganglia/GangliaSink31.java -->
