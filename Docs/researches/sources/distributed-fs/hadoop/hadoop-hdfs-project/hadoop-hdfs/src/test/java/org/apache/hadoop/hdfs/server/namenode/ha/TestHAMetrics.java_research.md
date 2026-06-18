# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestHAMetrics.java

## Purpose
`TestHAMetrics` verifies HA-related NameNode metrics and state reporting: HA state names, millis since last loaded edits, pending DataNode message count, inode count after restart from fsimage, and ordinal `getNameNodeState()` values including observer and initializing states.

## Important APIs, Types, And Functions
Tests are `testHAMetrics`, `testHAInodeCount`, and `testGetNameNodeState`. They use `FSNamesystem.getHAState`, `getMillisSinceLastLoadedEdits`, `getPendingDataNodeMessageCount`, `getFilesTotal`, NameNode MXBean attribute `LastHATransitionTime`, `NameNode.getNameNodeState`, `MiniDFSCluster`, `DistributedFileSystem.saveNamespace`, and safe mode actions.

## Control Flow
The metrics test starts two NameNodes, checks initial standby metrics, transitions NN0 active and reads the JMX transition time, flips active to NN1, waits for standby lag, creates a file so the standby accumulates pending DataNode messages, then waits for catch-up and verifies the counters drop and loaded-edits age decreases. The inode test creates four files, saves namespace, flips active, restarts the former active as standby, and checks its file count from loaded image. The state API test starts three NameNodes, transitions active and observer states, then shuts one down and expects INITIALIZING.

## State And Persistence
State includes JMX NameNodeStatus metrics, in-memory FSNamesystem counters, pending DN message queues, fsimage contents, and HA service state. Persistent namespace state is created files and saved fsimage.

## Dependencies And Integration Points
The tests integrate metrics exposure, JMX, safe mode namespace saving, edit tailing, pending DataNode message draining, observer state transitions, and cluster restart/shutdown behavior.

## Risks
Metrics can be racy because they are time-based and depend on tailing cadence. `LastHATransitionTime` assumes monotonic increase across transitions. Inode count after restart protects against stale metrics when loading from fsimage rather than replaying edits.

## Test Signals
Signals include exact HA state strings, positive or zero millis-since-edits according to active/standby role, increasing JMX transition time, pending message count changing from positive to zero after catch-up, file total count of five after restart, and ordinal service-state matches for STANDBY, ACTIVE, OBSERVER, and INITIALIZING.
