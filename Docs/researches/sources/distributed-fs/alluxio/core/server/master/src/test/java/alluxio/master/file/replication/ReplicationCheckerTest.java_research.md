# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/replication/ReplicationCheckerTest.java

## Purpose
`ReplicationCheckerTest` validates the master heartbeat logic that detects under-replicated, over-replicated, lost, and misplaced file blocks and submits replication or migration jobs.

## Important APIs, Types, and Functions
The test exercises `ReplicationChecker.heartbeat`, a mock `ReplicationHandler` implementing `setReplica`, `migrate`, `getJobStatus`, and `findJobs`, and helpers that create file inodes, register block workers, commit blocks, and heartbeat block locations.

## Control Flow, State, and Persistence
Setup starts a UFS journal system, block master, inode tree, and safe-mode aware context. File helpers create completed one-block files with replication min/max and optional pin location. Heartbeats compare actual block locations against replication policy, call the mock handler, and track in-flight job ids to avoid duplicate scheduling.

## Dependencies and Integration Points
The suite integrates `InodeTree`, `BlockMaster`, worker registration/heartbeats, journal system startup, file-create contexts, replication job APIs, and Alluxio configuration such as `JOB_MASTER_JOB_CAPACITY`.

## Risks
The checker must avoid scheduling for lost blocks, avoid duplicates while jobs are running, reschedule failed jobs, and use migration for wrong storage medium rather than replica-count changes. The test mutates one `CreateFileContext` across cases, so isolation depends on per-test setup.

## Test Signals
Signals include empty-tree no-op, within-range no-op, under-replication by 1 or 10, pinned-medium migration, over-replication, mixed under/over files, lost-block suppression, multiple files, partial scheduling under capacity, running-job suppression, failed-job retry, and completed-job cleanup.
