# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestConsistentReadsObserver.java

## Purpose

`TestConsistentReadsObserver` verifies observer-read consistency semantics for HDFS ObserverNode clients, including `msync`, automatic msync, requeue/backoff, new-client alignment, uncoordinated calls, non-observer proxy rejection, FileContext support, and RPC queue metrics.

## Important APIs, Types, and Functions

The suite starts a QJM HA cluster with one observer through `HATestUtil.setUpObserverCluster`, with state context enabled and fast tailing disabled. It uses `ObserverReadProxyProvider`, `DistributedFileSystem.msync`, `FileContext.msync`, `HATestUtil.isSentToAnyOfNameNodes`, `NameNodeAdapter`, `RpcScheduler`, `Schedulable`, `RemoteException`, `StandbyException`, metrics assertions, and a nested `TestRpcScheduler`.

## Control Flow

Most tests perform a write on the active, then issue reads expected to block or requeue until the observer tails edits. Explicit and auto-msync tests use a second client with cache disabled and verify reads go to the observer only after state ID alignment. New-client tests reorder HA roles so a new client must contact active before observer. Uncoordinated-call tests show `datanodeReport` bypasses coordinated waiting while `getFileInfo` blocks. Non-observer proxy tests configure a plain failover provider pointed at the observer and expect `StandbyException`. Metrics tests compare queue and processing operation counters after a blocked read completes.

## State and Persistence Behavior

The tests mutate namespace directories, HA roles, observer edit-tail state, client alignment-context state, observer RPC call queue configuration, and metrics counters. Cleanup deletes the test path after each test.

## Dependencies and Integration Points

It integrates ObserverNode state IDs, client-side observer proxy selection, edit log rolling/tailing, RPC backoff, FileSystem and FileContext APIs, HA role transitions, and metrics.

## Risks and Edge Cases

Observer reads must never return stale results relative to the client's last seen state. Auto-msync period handling can make tests time-sensitive. Requeue/backoff must eventually fail over to active when observer cannot catch up. Non-observer-aware clients must be rejected by observers.

## Test Signals

Signals include reads blocking before `rollEditLogAndTail` and succeeding afterward, last proxy indices matching active or observer expectations, `TimeoutException` for effectively disabled auto-msync, fast uncoordinated `datanodeReport`, `StandbyException` for plain provider requests, successful FileContext read after msync, and equal `RpcQueueTimeNumOps` and `RpcProcessingTimeNumOps`.
