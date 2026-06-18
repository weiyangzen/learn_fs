## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/impl/MetricsSourceAdapter.java

Purpose: Runtime adapter for a metrics source, adding filters, injected tags, and DynamicMBean exposure.

Important APIs/types/functions: Implements JMX `getAttribute`, `getAttributes`, `getMBeanInfo`, read-only mutator stubs, `getMetrics`, `startMBeans`, `stopMBeans`, and cache update helpers.

Control flow: JMX access calls `updateJmxCache`, which refreshes after TTL and releases the adapter lock while invoking source metrics to avoid lock-order deadlocks. `getMetrics` applies record/metric filters, catches source exceptions, and injects system tags into each builder.

State and persistence: Tracks JMX attribute cache, MBean info cache, TTL timestamps, MBean name, and clear/refresh flags. State is in-memory and synchronized around cache changes.

Dependencies/integration: Registered by `MetricsSystemImpl`; uses Hadoop `MBeans`, `MetricsCollectorImpl`, filters, records, tags, and time utilities.

Risks/test signals: Deadlock avoidance, TTL behavior, stale attribute names, duplicate record suffixing, source exceptions, and read-only JMX behavior need tests.
