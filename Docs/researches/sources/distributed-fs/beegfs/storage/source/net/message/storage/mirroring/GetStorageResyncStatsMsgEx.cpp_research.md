<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/storage/mirroring/GetStorageResyncStatsMsgEx.cpp -->
## sources/distributed-fs/beegfs/storage/source/net/message/storage/mirroring/GetStorageResyncStatsMsgEx.cpp

### Purpose
Implements a storage resync statistics request for a single target.

### Important APIs, Types, And Functions
processIncoming() obtains BuddyResyncer from App, reads targetID from the message, gets the matching BuddyResyncJob, optionally fills StorageBuddyResyncJobStatistics, and sends GetStorageResyncStatsRespMsg.

### Control Flow
The flow is read-only and returns default statistics when no resync job exists for the target.

### State, Persistence, And Dependencies
No persistent state changes occur. The response reflects transient resync-job counters and state. Depends on Program/App, BuddyResyncer, BuddyResyncJob, StorageBuddyResyncJobStatistics, and the common response message.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risk is ambiguity between no job and a job with zeroed counters if consumers need that distinction.

### Test Signals
Test signals include missing job, active job, completed job still referenced, and concurrent stats reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/storage/mirroring/GetStorageResyncStatsMsgEx.cpp -->
