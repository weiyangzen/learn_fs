<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/storage/chunkbalancing/CpChunkPathsMsgEx.cpp -->
## sources/distributed-fs/beegfs/storage/source/net/message/storage/chunkbalancing/CpChunkPathsMsgEx.cpp

### Purpose
Handles requests to enqueue chunk-copy work for the storage chunk balancer, translating optional buddy mirror group IDs into concrete source and destination targets.

### Important APIs, Types, And Functions
processIncoming() reads targetID, destinationID, relativePath, EntryInfo, and FileEvent from CpChunkPathsMsg. addChunkBalanceJob(bool&) lazily creates and starts a ChunkBalancerJob stored on App. The response is CpChunkPathsRespMsg.

### Control Flow
For mirrored requests it resolves both source and destination buddy group IDs to primary targets. It validates the source target, then serializes job creation and job restart under App::ChunkBalanceJobMutex. Existing stopped jobs are joined, reset, restarted, and set STARTING before a ChunkSyncCandidateFile is constructed and submitted with addChunkSyncCandidate().

### State, Persistence, And Dependencies
Persistent data movement is deferred to ChunkBalancerJob; this handler mutates App runtime state by creating or restarting the singleton chunk balancer job and appending a candidate to its queue. Integrates with StorageTargets, MirrorBuddyGroupMapper, ChunkBalancerJob, ChunkBalancerFileSyncSlave types, EntryInfo, FileEvent, and GenericResponseMsg retry behavior for unknown mirrored source targets.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risks include a leaked job object if App ownership rules change, races if status says not running but timedjoin fails, and accepting destination IDs without validating the destination target exists locally at message time. The source target variable is only used for validation.

### Test Signals
Test signals include first-job creation, restart of completed jobs, AGIAN return when a job cannot be joined, invalid mirrored group IDs, non-mirror unknown source targets, and queue insertion preserving relative path and FileEvent data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/storage/chunkbalancing/CpChunkPathsMsgEx.cpp -->
