# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestObserverNode.java

## Purpose
`TestObserverNode` is the main Observer NameNode integration suite. It validates observer read routing, observer state transition restrictions, edit-tail requeue behavior, startup configuration, failover with observers, observer shutdown/restart, bootstrapping, safe mode and missing-block retry fallback, fsck, active-retry exceptions for writes, access-time redirects, sticky-active probing, state-ID consistency after mkdir races, deleted-dir listing, and empty file/dir reads.

## Important APIs, Types, And Functions
The static fixture enables NameNode state context, sets observer probe retry period to zero, and uses `HATestUtil.setUpObserverCluster(conf, 1, 1, true)` to create one active, one standby, and one observer over QJM. Tests include `testObserverRequeue`, `testNoActiveToObserver`, `testGetGroups`, `testNoObserverToActive`, `testSimpleRead`, `testConfigStartup`, `testFailover`, `testDoubleFailover`, `testObserverShutdown`, `testObserverFailOverAndShutdown`, `testBootstrap`, `testObserverNodeSafeModeWithBlockLocations`, `testObserverNodeBlockMissingRetry`, `testFsckWithObserver`, `testObserverRetryActiveException`, `testAccessTimeUpdateRedirectToActive`, `testStickyActive`, `testFsckDelete`, `testMkdirsRaceWithObserverRead`, `testGetListingForDeletedDir`, and `testSimpleReadEmptyDirOrFile`. Helpers include `assertSentTo`, `setObserverRead`, `ClientState`, and `MkDirRunner`.

## Control Flow
Most tests write or mutate through the active, roll and tail edits, then perform reads expected to go to the observer. They change HA states, shut down/restart the observer, disable observer startup, or disable observer reads to verify routing. Retry tests spy the observer `BlockManager` to return empty-located fake blocks so `open`, listing, and located-file APIs fall back to active. Requeue testing stops the observer edit tailer, schedules a read that blocks until edits are tailed, verifies RPC requeue metrics, then restores the tailer. The mkdir race delays active edit-log sync, runs multiple clients with separate DFS instances, and verifies last-seen state IDs are high enough to avoid stale observer reads.

## State And Persistence
Persistent state is a collection of test directories/files under `/TestObserverNode`, fsimage/edit-log state in QJM, and sometimes corrupt replica state. Transient state includes observer edit-tail progress, client last-seen state ID, proxy provider target choice, RPC requeue metrics, active/standby/observer HA states, safe mode status, block location responses, and observer probe timers.

## Dependencies And Integration Points
Dependencies include `MiniQJMHACluster`, `MiniDFSCluster`, `ObserverReadProxyProvider`, `HATestUtil`, `NameNodeAdapterMockitoUtil`, `NameNodeRpcServer`, `RpcMetrics`, `BlockManager`, `TestFsck`, `BootstrapStandby`, `GetGroups`, `HadoopExecutors`, Mockito, and `LambdaTestUtils`. The suite ties Observer NameNode behavior to client routing, state IDs, edit tailing, block location semantics, fsck, admin tools, and HA transitions.

## Risks
Observer reads are correctness-sensitive: a client must not read stale data from an observer behind its last seen state, writes must be retried on active, reads that need block locations or atime updates may need active fallback, and observer restarts must not leave clients stuck on dead targets. The tests use timing, scheduled tasks, and Mockito spies, so race windows and metrics timing are important.

## Test Signals
Signals include `assertSentTo` matching active or observer indices, expected `ServiceFailedException` for invalid transitions, RPC requeue count increment and eventual file status, successful `GetGroups` and fsck runs, healthy/corrupt fsck output as appropriate, `ObserverRetryOnActiveException` for direct observer write, active fallback for atime or missing-block cases, no stale read after mkdir race, expected `FileNotFoundException` for deleted dirs, and observer handling of empty directories/files.
