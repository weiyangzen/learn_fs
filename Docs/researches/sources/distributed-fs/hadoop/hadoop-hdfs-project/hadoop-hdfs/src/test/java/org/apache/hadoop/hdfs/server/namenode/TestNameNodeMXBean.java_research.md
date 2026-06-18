# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestNameNodeMXBean.java

## Purpose
Large integration suite for NameNode JMX/MXBean attributes exposed by `NameNodeMXBean`, `FSNamesystem`, `FSNamesystemState`, replicated block state, and EC block group state. It validates JSON payloads, DataNode admin states, top users, directory-size metrics, erasure coding policy/health metrics, total block counts, and dead-node details.

## Important APIs, Types, and Functions
- Uses platform `MBeanServer` and `ObjectName` values such as `Hadoop:service=NameNode,name=NameNodeInfo`, `FSNamesystem`, `FSNamesystemState`, `ReplicatedBlocksState`, and `ECBlockGroupsState`.
- Parses JSON with Jetty `JSON.parse` and Jackson `ObjectMapper`.
- Cluster operations use `MiniDFSCluster`, HA topologies, `HATestUtil`, `HostsFileWriter`, `CombinedHostFileManager`, `DatanodeManager`, `DatanodeDescriptor`, and DataNode admin transitions.
- EC tests use `StripedFileTestUtil`, `ErasureCodingPolicy`, `LocatedStripedBlock`, `StripedBlockUtil.parseStripedBlockGroup`, and corrupted replicas.
- Storage/metrics tests use `FileUtil.chmod`, `FileUtils.sizeOfDirectory`, `NameNodeRpc.rollEditLog`, and `saveNamespace`.

## Control Flow
- `testNameNodeMXBeanInfo` starts four DataNodes, sets upgrade domain and maintenance/decommission states, reads many NameNodeInfo attributes, verifies live/dead node JSON fields, name dir status before/after chmod-induced rollEditLog failure, cache metrics, and rolling upgrade status.
- `testLastContactTime`, `testDecommissioningNodes`, `testInServiceNodes`, and `testMaintenanceNodes` use host include/exclude/out-of-service files and refreshNodes to verify live/dead/decommission/maintenance JMX JSON and FSNamesystem counters.
- `testTopUsers`, `testTopUsersDisabled`, and `testTopUsersNoPeriods` exercise `TopUserOpCounts` under enabled, disabled, and no-window configs after repeated filesystem operations.
- `testQueueLength` reads `LockQueueLength`.
- `testNNDirectorySize` starts HA NameNodes with explicit IPC ports, rolls/tails edits, saves namespace, and compares reported per-directory sizes to actual disk usage.
- `testEnabledEcPoliciesMetric`, `testVerifyMissingBlockGroupsMetrics`, and `testTotalBlocksMetrics` validate EC policies, missing/corrupt EC block group metrics, total replicated versus EC block counts, and topology verification message.
- `testDeadNodesInNameNodeMXBean` adds an included but absent mock DataNode and verifies dead-node JSON includes blank UUID.

## State and Persistence Behavior
- Many tests depend on live cluster state, DataNode heartbeats, host include/exclude files, admin-state transitions, and MBean registration.
- Storage status and directory-size tests inspect real NameNode directories and permission-induced failure states.
- EC tests create replicated and striped files, corrupt replicas, disable heartbeats to retain corrupt-block records, and delete files while waiting for delete queues.
- HA total-block test compares active and standby metrics after namespace changes and deletion queues.

## Dependencies and Integration Points
- Broad integration across NameNode JMX, FSNamesystem metrics, block manager, DataNode manager, host config providers, HA, EC, storage directories, nntop, and native IO cache manipulation.
- Uses `@TempDir baseDir` for cluster roots and static `NativeIO.POSIX.setCacheManipulator(new NoMlockCacheManipulator())`.

## Risks and Edge Cases
- Timing-sensitive waits around heartbeats, admin-state transitions, corrupt-block discovery, HA startup ports, and standby catch-up.
- JSON payload structure is asserted directly; field rename/type changes will break tests.
- Some tests intentionally chmod storage dirs and must restore permissions in finally.
- EC topology verification assumes one rack and specific default EC policy requirements.
- Large breadth makes failures useful but sometimes expensive to diagnose.

## Test Signals
- Very high signal for NameNode observability compatibility: JMX attribute values must match internal `FSNamesystem` methods, node-state JSON must include expected fields, EC/replicated counters must add up, and storage/HTTP/top-user metrics must remain stable.
