<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/storage/chunkbalancing/GetChunkBalanceJobStatsMsgEx.cpp -->
## sources/distributed-fs/beegfs/storage/source/net/message/storage/chunkbalancing/GetChunkBalanceJobStatsMsgEx.cpp

### Purpose
Implements a small status query for the currently configured storage chunk balancer job.

### Important APIs, Types, And Functions
processIncoming() obtains App::getChunkBalancerJob(), fills a default ChunkBalancerJobStatistics, calls getJobStats() when a job exists, and sends GetChunkBalanceJobStatsRespMsg.

### Control Flow
Control flow is read-only: no job is created for a stats query. A missing job returns the default-initialized statistics structure.

### State, Persistence, And Dependencies
No persistent state is changed. It observes in-memory ChunkBalancerJob statistics and serializes them into the response. Depends on Program/App, ChunkBalancerJob, ChunkBalancerJobStatistics, and common GetChunkBalanceJobStatsRespMsg.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Main risk is that default statistics must remain semantically valid for no-job responses; callers need to distinguish idle/no-job from a zero-progress active job if the response format permits it.

### Test Signals
Test signals include no-job responses, active-job stats, and concurrent stats reads while the job updates counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/storage/chunkbalancing/GetChunkBalanceJobStatsMsgEx.cpp -->
