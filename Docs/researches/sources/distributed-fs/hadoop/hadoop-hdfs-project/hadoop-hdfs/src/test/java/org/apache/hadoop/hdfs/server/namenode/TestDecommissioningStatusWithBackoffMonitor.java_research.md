# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestDecommissioningStatusWithBackoffMonitor.java

Purpose: Runs the decommission status scenario with `DatanodeAdminBackoffMonitor` instead of the default monitor, proving the alternative monitor updates externally visible counters correctly.

Important APIs/types/functions: Extends `TestDecommissioningStatus`, reuses its helpers, and sets `DFS_NAMENODE_DECOMMISSION_MONITOR_CLASS` to `DatanodeAdminBackoffMonitor` implementing `DatanodeAdminMonitorInterface`.

Control flow: Overridden setup builds the base config, injects the backoff monitor class, creates the cluster, and stores inherited fixture references. The test mirrors the base decommission status flow but explicitly re-runs `BlockManagerTestUtil.recheckDecommissionState` after each decommission because the backoff monitor refreshes stats on a later pass.

State and persistence behavior: Same decommissioning status state as the base class, with monitor-specific progression. No durable restart is tested.

Dependencies and integration points: Validates pluggable decommission monitor selection through configuration and compatibility with DFSAdmin/API status surfaces.

Risks: Inheritance means base tests may also run under the alternate setup depending on test discovery. The second recheck documents a behavioral difference that future monitor changes could affect.

Test signals: Decommissioning node list size, expected leaving-service counters, DFSAdmin report count, and cleanup through exclude-host reset.
