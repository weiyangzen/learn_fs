## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/MetricsSystemMXBean.java

Purpose: JMX management interface for controlling and inspecting the metrics system.

Important APIs/types/functions: Exposes start/stop, MBean start/stop, current configuration, and immediate publish operations to JMX clients.

Control flow: `MetricsSystemImpl` implements this interface and registers a control MBean during initialization.

State and persistence: Interface only; operations mutate the concrete metrics system lifecycle.

Dependencies/integration: Registered via Hadoop `MBeans` under the metrics system prefix and control name.

Risks/test signals: JMX callers can start or stop the metrics system outside normal code paths. Tests should verify idempotent start/stop warnings and config string rendering.
