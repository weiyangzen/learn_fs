# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/CallQueueManager.java

## Purpose

`CallQueueManager<E extends Schedulable>` abstracts Hadoop IPC server call queue operations across different `BlockingQueue` and `RpcScheduler` implementations. It supports priority-aware queues, client backoff, failover-triggering overflow exceptions, and live queue replacement.

## Important APIs, control flow, and state

The constructor parses scheduler priority levels and capacity weights, creates a scheduler via reflection, creates a backing queue via reflection, and stores two atomic queue references: `putRef` for producers and `takeRef` for handlers. Queue operations delegate to those refs. `put()` honors client backoff by consulting `scheduler.shouldBackOff()`, while `addInternal()` converts full-queue `IllegalStateException` into `CallQueueOverflowException.DISCONNECT` or `.FAILOVER` depending on failover configuration. `getPriorityLevel()`, `addResponseTime()`, and user-level priority setters delegate to the scheduler, with special handling for `DecayRpcScheduler`.

`swapQueue()` is the key state transition. It stops the old scheduler, creates the new scheduler and queue, updates server failover config, switches `putRef` first so new calls go to the replacement queue, waits until the old queue is repeatedly empty, then switches `takeRef` and installs the new scheduler.

## Dependencies and integration points

It is used by `Server` as the IPC call admission queue. It integrates with `FairCallQueue`, `RpcScheduler`, `DecayRpcScheduler`, `Schedulable`, `UserGroupInformation`, `CommonConfigurationKeys`, `RetriableException`, `StandbyException`, and `RpcServerException`.

## Risks and test signals

The two-reference swap prevents losing calls but can spin while waiting for old queue drain; interrupted sleeps make the empty check fail and retry. Reflection constructor selection must match queue/scheduler signatures. Overflow behavior changes client outcome: keepalive/error, disconnect/fatal, or failover/fatal. Capacity weights must match priority levels and be positive. `TestCallQueueManager` covers capacity, empty consumption, FCQ compatibility, scheduler-without-FCQ, swap under contention, constructor exceptions, overflow exceptions, and failover enablement.
