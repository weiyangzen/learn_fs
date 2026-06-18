# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/metrics/NamenodeBeanMetrics.java

Purpose: exposes Router federation metrics through NameNode-compatible JMX interfaces so existing HDFS monitoring can treat the Router as a logical NameNode.

Important APIs and types: implements `FSNamesystemMBean`, `NameNodeMXBean`, and `NameNodeStatusMXBean`; registers FSNamesystem, FSNamesystemState, NameNodeInfo, and NameNodeStatus MBeans; uses `RBFMetrics`, `RouterClientProtocol`, `StateStoreService`, `MembershipStore`, `LoadingCache<DatanodeReportType,String>`, and Jetty JSON serialization.

Control flow: constructor registers MBeans and creates a datanode-report cache with configured timeout/expiry. Many getters delegate to `router.getMetrics()` with defensive logging and default zero/empty values on failure. `getNodes` reads cached JSON; cache loading calls Router client protocol `getDatanodeStorageReport`, waits through `syncReturn` in async mode, and serializes datanode/storage details. Namespace info getters query the membership store and collect unique cluster/block-pool IDs. Status methods return Router-derived host/port, start time, security, active state, and many unsupported NameNode fields as `"N/A"`, `null`, zero, or `-1`.

State and persistence: in-memory MBean registrations and datanode JSON cache. It does not persist metrics; it reflects Router, State Store, and downstream NameNode state at query/cache-load time.

Dependencies and integration points: bridges RBF metrics to Hadoop NameNode monitoring APIs and JMX clients. It depends on Router RPC server, RBF metrics initialization, State Store membership records, and downstream datanode reports.

Risks: `close` unregisters FSNamesystemState, NameNodeInfo, and NameNodeStatus but not the `fsBeanName`, which may leak a registration. Some NameNode fields are placeholders and can mislead generic dashboards. Datanode report collection can be expensive or timeout, so cache settings are important. Tests should verify MBean registration/close behavior, delegation to `RBFMetrics`, JSON node output, async datanode report handling, and fallback values on missing metrics.
