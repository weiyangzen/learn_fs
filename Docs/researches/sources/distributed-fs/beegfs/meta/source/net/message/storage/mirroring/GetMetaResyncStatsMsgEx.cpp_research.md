<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/mirroring/GetMetaResyncStatsMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/mirroring/GetMetaResyncStatsMsgEx.cpp

## Purpose
Returns current metadata buddy-resync job statistics to callers.

## Important APIs, Types, and Functions
`processIncoming()` gets `BuddyResyncer`, asks for the current `BuddyResyncJob`, copies `job->getJobStats()` when present, and sends `GetMetaResyncStatsRespMsg`.

## Control Flow, State, and Persistence
This is a read-only snapshot. If no job exists, a default `MetaBuddyResyncJobStatistics` is returned. No locks or persistent updates are performed in this file.

## Dependencies and Integration Points
Depends on `BuddyResyncer`, `BuddyResyncJob`, `MetaBuddyResyncJobStatistics`, `Program`, and the common resync-stats response message.

## Risks and Test Signals
The main risks are stale or concurrently changing statistics and default-value interpretation when no job is active. Tests should cover active job, no job, and response serialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/mirroring/GetMetaResyncStatsMsgEx.cpp -->
