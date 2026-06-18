# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/metrics/RouterMBean.java

Purpose: `RouterMBean` defines the private evolving JMX surface for router-specific information exported by `RBFMetrics`.

Important APIs: it declares getters for router start time, version, compile date/info, host/port, router ID/status, cluster IDs, block pool IDs, current delegation-token count, safemode text, security enablement, top token owners, federation rename job count, and scheduler job count.

Control flow and state: this is a pure interface with no state or persistence. Its behavior is supplied by `RBFMetrics`, which registers it as a `StandardMBean` under the Router domain.

Dependencies and integration points: only Hadoop classification annotations are imported. The method names are part of JMX naming, so callers and dashboards depend on these exact getter signatures.

Risks: adding/removing methods changes the JMX contract. Return values are deliberately simple strings, booleans, ints, and longs, so richer structured data has to be encoded by the implementation.

Test signals: tests should validate that `RBFMetrics` implements every method and that MBean registration exposes expected attributes.
