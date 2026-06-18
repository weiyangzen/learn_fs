# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestMultiObserverNode.java

## Purpose
`TestMultiObserverNode` validates client read routing when an HA cluster has multiple Observer NameNodes. It verifies observer failover, shutdown/restart behavior, routing fallback to active when no observer is available, and fallback when observers lag behind the client's required state ID.

## Important APIs, Types, And Functions
The static fixture builds a QJM-backed observer cluster with two observers using `HATestUtil.setUpObserverCluster(conf, 2, 0, true)`, enables state context, and creates an observer-read `DistributedFileSystem` with `ObserverReadProxyProvider`. Tests are `testObserverFailover`, `testMultiObserver`, and `testObserverFallBehind`; helper `assertSentTo(int...)` uses `HATestUtil.isSentToAnyOfNameNodes`.

## Control Flow
The tests write via the active, roll and tail edits, then perform reads expected to hit either observer. They transition observers to standby one at a time, shut them down and restart them, transition them back to observer state, and assert routing moves among observers or back to active. The fall-behind test artificially sets the client's state ID far ahead and verifies a read goes to the active instead of stale observers.

## State And Persistence
Persistent state is a small directory tree under `/TestMultiObserverNode`. Runtime state includes active, standby, and observer roles for NameNode indices 0 through 3, client last-seen state ID, observer edit-tail position, and client proxy-provider routing cache.

## Dependencies And Integration Points
Dependencies include `MiniQJMHACluster`, `MiniDFSCluster`, `ObserverReadProxyProvider`, `HATestUtil`, `DistributedFileSystem`, and HA state transitions. The tests cover multi-observer routing over a QJM-backed HA setup.

## Risks
Routing bugs can strand reads on a standby, keep using a shutdown observer, or return stale data from an observer whose state ID is behind the client. Because any observer is acceptable in some assertions, the test focuses on eligible target sets rather than strict load-balancing.

## Test Signals
Signals include `assertSentTo(2, 3)` when both observers are valid, `assertSentTo(3)` or `assertSentTo(2)` when one observer is disabled, `assertSentTo(0)` when no observer or no sufficiently current observer is available, and successful cleanup/restart of both observers.
