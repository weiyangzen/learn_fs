# subset-b-000559 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/storage/attribs/SetLocalAttrMsgEx.cpp -->
## sources/distributed-fs/beegfs/storage/source/net/message/storage/attribs/SetLocalAttrMsgEx.cpp

### Purpose
Implements storage-side handling for SetLocalAttr requests that update chunk timestamps and quota-relevant ownership on local or buddy-mirrored targets.

### Important APIs, Types, And Functions
Main APIs are processIncoming(), getTargetFD(), and forwardToSecondary(). It consumes SetLocalAttrMsg fields such as target ID, entry ID, PathInfo, valid attribute bitmask, SettableFileAttribs, quota flag, and buddy-mirror flags, and returns SetLocalAttrRespMsg with FhgfsOpsErr plus DynamicFileAttribs.

### Control Flow
The handler resolves a buddy group to primary or secondary target, rejects unknown targets, checks mirrored-primary consistency, forwards primary operations to the secondary, then applies utimensat and fchownat relative to the target chunk or mirror directory FD. Timestamp changes lock SyncedStoragePaths, update POSIX times, stat the chunk for dynamic attributes, and always unlock before response. Communication failures that already sent GenericResponseMsg skip the normal response path.

### State, Persistence, And Dependencies
Persistent effects are chunk file atime, mtime, uid, and gid changes on disk. Timestamp updates also create a monotonic storageVersion through SyncedStoragePaths so metadata can reconcile dynamic attributes. Runtime state includes temporary chunk locks during buddy resync and node operation counters. Depends on Program/App singletons, StorageTargets, MirrorBuddyGroupMapper, ChunkLockStore, SyncedStoragePaths, MsgHelperIO, StorageTkEx, StorageTk path construction, MessagingTk request/response forwarding, and GenericResponseMsg retry semantics.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risks include missing unlocks on new error branches, returning success-like fake dynamic attributes for ENOENT timestamp updates, forwarding this message object while mutating feature flags, and failing normal responses when unknown non-mirror targets return early after setting clientErrRes. The utimensat fallback cannot truly omit one timestamp on old platforms.

### Test Signals
Test signals include mirrored primary/secondary flows, non-good primary rejection, secondary offline marking needs-resync, ENOENT timestamp behavior, quota ownership changes with and without SETLOCALATTRMSG_FLAG_USE_QUOTA, and node op counter updates after success and handled failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/storage/attribs/SetLocalAttrMsgEx.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/storage/attribs/SetLocalAttrMsgEx.h -->
## sources/distributed-fs/beegfs/storage/source/net/message/storage/attribs/SetLocalAttrMsgEx.h

### Purpose
Declares the storage extension for SetLocalAttrMsg and the private helpers used to resolve target file descriptors and forward mirrored attribute changes.

### Important APIs, Types, And Functions
The class derives from SetLocalAttrMsg and overrides processIncoming(ResponseContext&). Private helpers getTargetFD(const StorageTarget&, ResponseContext&, bool*) and forwardToSecondary(StorageTarget&, ResponseContext&, bool*) encode the implementation contract used by the source file.

### Control Flow
The header establishes that all message handling enters through processIncoming, while target-state validation and buddy forwarding are isolated in helpers so the body can keep local POSIX attribute updates separate from communication policy.

### State, Persistence, And Dependencies
No state is declared here; state is inherited from the serialized SetLocalAttrMsg and accessed via base-class getters during processing. Depends on common StorageErrors, SetLocalAttrMsg, ResponseContext via included base declarations, and the forward-declared StorageTarget.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Interface risk is that helper return conventions are non-obvious: getTargetFD can send a response itself via outResponseSent, while forwardToSecondary can also send GenericResponseMsg and return COMMUNICATION.

### Test Signals
Compile and message-dispatch tests should verify the class remains registered as the concrete handler for NETMSGTYPE_SetLocalAttr and that helper declarations stay synchronized with the cpp file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/storage/attribs/SetLocalAttrMsgEx.h -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/storage/chunkbalancing/CpChunkPathsMsgEx.h -->
## sources/distributed-fs/beegfs/storage/source/net/message/storage/chunkbalancing/CpChunkPathsMsgEx.h

### Purpose
Declares the storage-side CpChunkPaths handler that accepts chunk balance copy candidates and owns lazy job startup.

### Important APIs, Types, And Functions
CpChunkPathsMsgEx derives from CpChunkPathsMsg, overrides processIncoming(ResponseContext&), and declares private addChunkBalanceJob(bool&).

### Control Flow
The header separates network-message dispatch from job lifecycle creation; all detailed target resolution and enqueue behavior is in the implementation.

### State, Persistence, And Dependencies
No member state is stored on the handler. Runtime state is held by the App singleton ChunkBalancerJob pointer. Depends on the common CpChunkPathsMsg base class and ChunkBalancerJob declaration.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risk is lifetime coupling: addChunkBalanceJob returns a raw pointer owned by App, so ownership must remain documented in the cpp path.

### Test Signals
Build tests should cover inclusion from message factories and ensure the override signature matches NetMessage dispatch expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/storage/chunkbalancing/CpChunkPathsMsgEx.h -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/storage/chunkbalancing/GetChunkBalanceJobStatsMsgEx.h -->
## sources/distributed-fs/beegfs/storage/source/net/message/storage/chunkbalancing/GetChunkBalanceJobStatsMsgEx.h

### Purpose
Declares the storage extension for the chunk-balancer statistics request.

### Important APIs, Types, And Functions
The class derives from GetChunkBalanceJobStatsMsg and only overrides processIncoming(ResponseContext&).

### Control Flow
All control flow is delegated to the cpp implementation; the header exposes no helper API or state.

### State, Persistence, And Dependencies
No persistent or runtime state is held in this class beyond inherited message fields. Depends on common GetChunkBalanceJobStatsMsg and StorageErrors headers.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risk is minimal, mostly dispatch drift if the base message or response type changes.

### Test Signals
A compile-time dispatch test is sufficient for the header; behavior tests live with the cpp handler.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/storage/chunkbalancing/GetChunkBalanceJobStatsMsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/storage/creating/RmChunkPathsMsgEx.cpp -->
## sources/distributed-fs/beegfs/storage/source/net/message/storage/creating/RmChunkPathsMsgEx.cpp

### Purpose
Removes a list of relative chunk paths from a target directory and opportunistically prunes empty parent chunk directories.

### Important APIs, Types, And Functions
processIncoming() reads targetID and StringList relativePaths from RmChunkPathsMsg, uses App::getChunkDirStore(), and returns RmChunkPathsRespMsg containing failed paths.

### Control Flow
The handler resolves the target, chooses mirror or chunks FD based on RMCHUNKPATHSMSG_FLAG_BUDDYMIRROR, unlinks each relative path with unlinkat, ignores ENOENT, records other failures, and invokes ChunkStore::rmdirChunkDirPath() on each successful removal parent.

### State, Persistence, And Dependencies
Persistent effects are deletion of chunk files and possible removal of empty hash/uid directories. No in-memory session or lock state is touched. Depends on StorageTargets, ChunkStore, StorageTk::getPathDirname, Path, POSIX unlinkat, and response list serialization.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risks include no buddy-group resolution in this handler, so callers must pass concrete target IDs. Parent cleanup ignores its return value, and relative path trust relies on upstream message validation.

### Test Signals
Test signals include mixed success/failure lists, ENOENT treated as success, mirrored FD selection, unknown target returning all paths as failed, and cleanup of empty parent directories.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/storage/creating/RmChunkPathsMsgEx.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/storage/creating/RmChunkPathsMsgEx.h -->
## sources/distributed-fs/beegfs/storage/source/net/message/storage/creating/RmChunkPathsMsgEx.h

### Purpose
Declares the storage-side handler for removing multiple chunk paths.

### Important APIs, Types, And Functions
RmChunkPathsMsgEx derives from RmChunkPathsMsg and overrides processIncoming(ResponseContext&).

### Control Flow
The header keeps the message surface minimal; iteration, target validation, and directory cleanup live in the cpp implementation.

### State, Persistence, And Dependencies
The class has no additional state beyond base message fields. Depends on common RmChunkPathsMsg and ResponseContext via the dispatch framework.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risk is low; behavior changes require matching cpp changes only.

### Test Signals
Compile-time tests should ensure the handler is available to storage message dispatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/storage/creating/RmChunkPathsMsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/storage/creating/UnlinkLocalFileMsgEx.cpp -->
## sources/distributed-fs/beegfs/storage/source/net/message/storage/creating/UnlinkLocalFileMsgEx.cpp

### Purpose
Handles unlinking a single local chunk file, including buddy mirror forwarding, consistency-state checks, resync chunk locking, directory cleanup, and operation accounting.

### Important APIs, Types, And Functions
Main APIs are processIncoming(), getTargetFD(), and forwardToSecondary(). It consumes UnlinkLocalFileMsg fields such as target ID, entry ID, PathInfo, buddy flags, and responds with UnlinkLocalFileRespMsg or GenericResponseMsg.

### Control Flow
The handler maps buddy group IDs to primary or secondary target IDs, validates target state, forwards primary unlink requests to the secondary by temporarily setting the SECOND flag on this message object, then derives the chunk path and calls unlinkat. It treats ENOENT as successful deletion, sends the response, prunes the containing chunk dir when appropriate, and updates StorageOpCounter_UNLINK.

### State, Persistence, And Dependencies
Persistent state is the removed chunk file and possible removed empty chunk directory. Runtime state includes temporary ChunkLockStore locks during buddy resync and StorageTarget buddyNeedsResync marking when secondary communication fails in an offline way. Depends on Program/App, MirrorBuddyGroupMapper, StorageTargets, ChunkStore, ChunkLockStore, MessagingTk, StorageTk path construction, GenericResponseMsg, and node op stats.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risks include feature-flag mutation on a reused message object, cleanup after skip_response using targetFD/chunkDirPath only when initialized, and treating ENOENT as success while higher layers may expect metadata to know whether data existed.

### Test Signals
Test signals include secondary-forward success and error cases, non-good primary rejection, ENOENT unlink, directory cleanup only for original-feature paths, unknown mirrored target retry response, and chunk lock release after all forwarded paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/storage/creating/UnlinkLocalFileMsgEx.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/storage/creating/UnlinkLocalFileMsgEx.h -->
## sources/distributed-fs/beegfs/storage/source/net/message/storage/creating/UnlinkLocalFileMsgEx.h

### Purpose
Declares the storage extension for unlinking one local chunk file and its mirrored-forwarding helpers.

### Important APIs, Types, And Functions
The class derives from UnlinkLocalFileMsg, overrides processIncoming(ResponseContext&), and declares getTargetFD() plus forwardToSecondary().

### Control Flow
The helper split mirrors SetLocalAttrMsgEx and keeps target consistency checks and secondary forwarding separate from local unlink logic.

### State, Persistence, And Dependencies
No state is held in the class outside inherited message fields and temporary stack state in processIncoming. Depends on UnlinkLocalFileMsg and a forward declaration of StorageTarget.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
The outResponseSent and COMMUNICATION conventions are subtle and must match the cpp implementation to avoid double responses.

### Test Signals
Header-level test signal is dispatch compilation; behavioral coverage belongs to the cpp handler.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/storage/creating/UnlinkLocalFileMsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/storage/listing/ListChunkDirIncrementalMsgEx.cpp -->
## sources/distributed-fs/beegfs/storage/source/net/message/storage/listing/ListChunkDirIncrementalMsgEx.cpp

### Purpose
Implements incremental listing of a target chunk directory for scanners such as resync, fsck, or maintenance tools.

### Important APIs, Types, And Functions
processIncoming() reads targetID, mirror flag, relativeDir, offset, maxOutEntries, onlyFiles, and ignore-not-exists from ListChunkDirIncrementalMsg. readChunks() fills names, entryTypes, and newOffset and returns FhgfsOpsErr.

### Control Flow
The handler opens the target-relative directory or duplicates the target root FD for an empty relativeDir, wraps it with fdopendir, seekdir()s to the supplied offset, filters entries through StorageTk::readdirFiltered(), resolves d_type or fstatat fallback, applies onlyFiles filtering, records d_off as the next offset, and sends ListChunkDirIncrementalRespMsg.

### State, Persistence, And Dependencies
The operation is read-only and intentionally has no locking, as documented by the caution comment. State is the caller-provided offset cursor and the transient directory stream. Depends on StorageTargets, target chunk/mirror FDs, POSIX openat/dup/fcntl/fdopendir/readdir/seekdir, StorageTk filtering, MetadataTk type conversion, and response list serialization.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risks include offset portability across directory mutations, no locking while directories can be concurrently modified, possible O_RDONLY fcntl misuse after dup, and different behavior when ignoreNotExists suppresses logging but still maps ENOENT to PATHNOTEXISTS.

### Test Signals
Test signals include listing root and nested directories, continuation offsets, onlyFiles filtering, DT_UNKNOWN stat fallback, ENOENT with and without ignore flag, and concurrent directory changes during listing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/storage/listing/ListChunkDirIncrementalMsgEx.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/storage/listing/ListChunkDirIncrementalMsgEx.h -->
## sources/distributed-fs/beegfs/storage/source/net/message/storage/listing/ListChunkDirIncrementalMsgEx.h

### Purpose
Declares the incremental chunk-directory listing handler and its private directory-reading helper.

### Important APIs, Types, And Functions
ListChunkDirIncrementalMsgEx derives from ListChunkDirIncrementalMsg, overrides processIncoming(ResponseContext&), and declares readChunks() with target, mirror, relative directory, offset, output limit, and filtering parameters.

### Control Flow
The interface makes readChunks testable as the core listing routine while keeping network response construction in processIncoming.

### State, Persistence, And Dependencies
No persistent state is represented in this class. Cursor state is passed as offset/newOffset values. Depends on common list message definitions, StringList, IntList, and FhgfsOpsErr.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risk is that the helper takes relativeDir by non-const reference although it does not need to mutate it, which can surprise future callers.

### Test Signals
Compile and focused unit tests should validate helper signature compatibility and offset semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/storage/listing/ListChunkDirIncrementalMsgEx.h -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/storage/mirroring/GetStorageResyncStatsMsgEx.h -->
## sources/distributed-fs/beegfs/storage/source/net/message/storage/mirroring/GetStorageResyncStatsMsgEx.h

### Purpose
Declares the storage-side handler for querying resync job statistics.

### Important APIs, Types, And Functions
The class derives from GetStorageResyncStatsMsg and overrides processIncoming(ResponseContext&).

### Control Flow
The header exposes only the message-dispatch entry point; target/job lookup is in the cpp file.

### State, Persistence, And Dependencies
No handler-local state exists. Depends on common GetStorageResyncStatsMsg and StorageErrors headers.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risk is minimal and limited to dispatch signature drift.

### Test Signals
A compile-time message factory test covers this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/storage/mirroring/GetStorageResyncStatsMsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/storage/mirroring/ResyncLocalFileMsgEx.cpp -->
## sources/distributed-fs/beegfs/storage/source/net/message/storage/mirroring/ResyncLocalFileMsgEx.cpp

### Purpose
Applies resync data for a chunk file, optionally forwarding chunk-balancing mirrored writes to the secondary and setting final file attributes.

### Important APIs, Types, And Functions
Core functions are processIncoming(), doWrite(), doWriteSparse(), doTrunc(), and forwardToSecondary(). The handler reads data buffer, relative path, count, offset, target IDs, and flags such as NODATA, CHECK_SPARSE, TRUNC, SETATTRIBS, BUDDYMIRROR, and CHUNKBALANCE_BUDDYMIRROR.

### Control Flow
For chunk-balance mirrored resync it derives the buddy group from a concrete target ID, chooses primary or secondary, and forwards to the secondary unless already marked SECOND. Locally it chooses chunk or mirror FD, opens or creates the chunk through ChunkStore, truncates on offset zero data writes, writes all bytes or skips sparse zero blocks, optionally truncates to offset+count, applies chmod/chown attributes, closes the FD, and responds with ResyncLocalFileRespMsg.

### State, Persistence, And Dependencies
Persistent effects are chunk contents, sparse holes, truncation length, mode, uid, and gid. On open, write, truncate, chmod, or chown failure it marks the StorageTarget BAD. Secondary offline communication marks buddyNeedsResync rather than failing local processing. Depends on ChunkStore, SessionQuotaInfo, MsgHelperIO::pwrite, StorageTargets, MirrorBuddyGroupMapper, MessagingTk, GenericResponseMsg, StorageTarget state mutation, and common resync response messages.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risks include not checking forwardToSecondary() return before continuing local writes, fchown/fchmod errors still attempting close and response, sparse write loop assumptions about zero block size, logging invalid target IDs using !targetID instead of targetID, and target BAD transitions on transient disk errors.

### Test Signals
Test signals include full and short write loops, sparse all-zero buffer requiring ftruncate at EOF, NODATA attribute-only sync, truncation flag, secondary-forward success/failure/offline, invalid buddy mapping, quota-open failures, and target BAD marking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/storage/mirroring/ResyncLocalFileMsgEx.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/storage/mirroring/ResyncLocalFileMsgEx.h -->
## sources/distributed-fs/beegfs/storage/source/net/message/storage/mirroring/ResyncLocalFileMsgEx.h

### Purpose
Declares the storage-side resync handler and helper routines for writing, sparse writing, truncating, and mirrored forwarding.

### Important APIs, Types, And Functions
ResyncLocalFileMsgEx derives from ResyncLocalFileMsg and overrides processIncoming(ResponseContext&). Private helpers expose exact low-level operations used by processIncoming.

### Control Flow
The header models resync as a network-message entry point with isolated POSIX helpers, which makes write/truncate behavior easier to reason about in the cpp implementation.

### State, Persistence, And Dependencies
No member state is declared. All state is inherited from the message or passed as stack parameters. Depends on ResyncLocalFileMsg, StorageErrors, StorageTarget via implementation includes, and ResponseContext from the dispatch framework.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risk is that forwardToSecondary takes targetID by non-const reference named targetID in the declaration but secondaryTargetID in use, which can obscure the call contract.

### Test Signals
Tests should cover helper behavior through processIncoming or direct friend/unit access if available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/storage/mirroring/ResyncLocalFileMsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/storage/mirroring/SetLastBuddyCommOverrideMsgEx.cpp -->
## sources/distributed-fs/beegfs/storage/source/net/message/storage/mirroring/SetLastBuddyCommOverrideMsgEx.cpp

### Purpose
Handles management requests to override a target last-buddy-communication timestamp and optionally abort an active resync.

### Important APIs, Types, And Functions
processIncoming() reads targetID, timestamp, and abortResync. It uses StorageTargets::getTarget(), StorageTarget::setLastBuddyComm(), BuddyResyncer::getResyncJob(), and BuddyResyncJob::abort(). Response is SetLastBuddyCommOverrideRespMsg.

### Control Flow
The handler validates the target, writes the override timestamp as a system_clock time point, aborts the resync job when requested and present, then sends SUCCESS. Unknown targets return UNKNOWNTARGET.

### State, Persistence, And Dependencies
Persistent state is the target .lastbuddycomm preallocated file because StorageTarget::setLastBuddyComm(..., true) writes overrideSecs. Runtime resync job state may be aborted. Depends on Program/App, StorageTargets, StorageTarget, BuddyResyncer, BuddyResyncJob, chrono conversion, and common response message.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risks include trusting time_t conversion range, overriding last-comm state without verifying caller authority here, and aborting a job after the timestamp has already been persisted.

### Test Signals
Test signals include unknown target, override persistence, abort flag with and without an active job, and repeated overrides clearing/setting expected StorageTarget state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/storage/mirroring/SetLastBuddyCommOverrideMsgEx.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/storage/mirroring/SetLastBuddyCommOverrideMsgEx.h -->
## sources/distributed-fs/beegfs/storage/source/net/message/storage/mirroring/SetLastBuddyCommOverrideMsgEx.h

### Purpose
Declares the storage-side handler for last buddy communication override messages.

### Important APIs, Types, And Functions
The class derives from SetLastBuddyCommOverrideMsg and overrides processIncoming(ResponseContext&).

### Control Flow
The header exposes no helper state; target lookup and optional resync abort are in the cpp file.

### State, Persistence, And Dependencies
No member state beyond inherited message fields. Depends on common SetLastBuddyCommOverrideMsg and StorageErrors.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risk is low; behavior depends on StorageTarget persistence semantics rather than this declaration.

### Test Signals
Compile-time dispatch coverage is enough at header level.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/storage/mirroring/SetLastBuddyCommOverrideMsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/storage/mirroring/StorageResyncStartedMsgEx.cpp -->
## sources/distributed-fs/beegfs/storage/source/net/message/storage/mirroring/StorageResyncStartedMsgEx.cpp

### Purpose
Responds to notification that storage resync started by dropping all mirrored local-file sessions for the target so stale mirror handles are not reused.

### Important APIs, Types, And Functions
processIncoming() reads targetID via getValue(), calls deleteMirrorSessions(), and replies with StorageResyncStartedRespMsg. deleteMirrorSessions() walks SessionStore session IDs, references each Session, and calls SessionLocalFileStore::removeAllMirrorSessions(targetID).

### Control Flow
Control flow is a best-effort sweep over sessions. It tolerates sessions disappearing between getAllSessionIDs() and referenceSession().

### State, Persistence, And Dependencies
Runtime session state is mutated by erasing mirror sessions for the target. No session store file is directly persisted here, though later session persistence will reflect the removal. Depends on Program/App, SessionStore, Session, SessionLocalFileStore, NumNodeIDList, and common mirroring response message.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risks include removing sessions without closing underlying handles in removeAllMirrorSessions(), depending on store semantics, and racing with in-flight IO that still holds shared pointers to SessionLocalFile objects.

### Test Signals
Test signals include multiple client sessions, disappearing sessions during sweep, only mirrored sessions removed, non-mirrored sessions preserved, and subsequent mirror writes opening fresh handles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/storage/mirroring/StorageResyncStartedMsgEx.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/storage/mirroring/StorageResyncStartedMsgEx.h -->
## sources/distributed-fs/beegfs/storage/source/net/message/storage/mirroring/StorageResyncStartedMsgEx.h

### Purpose
Declares the handler for storage-resync-started notifications and its session cleanup helper.

### Important APIs, Types, And Functions
StorageResyncStartedMsgEx derives from StorageResyncStartedMsg, overrides processIncoming(ResponseContext&), and declares private deleteMirrorSessions(uint16_t).

### Control Flow
The helper split makes the side effect explicit: handling the message is primarily a session-store cleanup operation.

### State, Persistence, And Dependencies
No local state is declared. Depends on StorageResyncStartedMsg and session classes in the implementation.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risk is that cleanup policy is hidden behind a private helper with no return status, so failures cannot be surfaced in the response.

### Test Signals
Tests should validate deletion behavior via the cpp handler.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/storage/mirroring/StorageResyncStartedMsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/storage/quota/GetQuotaInfoMsgEx.cpp -->
## sources/distributed-fs/beegfs/storage/source/net/message/storage/quota/GetQuotaInfoMsgEx.cpp

### Purpose
Handles quota information queries against one or more local storage target block devices.

### Important APIs, Types, And Functions
processIncoming() reads target selection, query type, ID range/list, quota type, and targetNumID from GetQuotaInfoMsg. It builds a QuotaBlockDeviceMap, tracks QuotaInodeSupport, uses a ZfsSession, and calls QuotaTk helpers before sending GetQuotaInfoRespMsg.

### Control Flow
For all-target requests it iterates StorageTargets and records each QuotaBlockDevice, deriving inode-quota support as none/some/all. For per-target and single-target requests it adds only the requested target if present. It then handles single ID, ID range, or ID list queries through QuotaTk and returns the accumulated QuotaDataList even when no block devices were found.

### State, Persistence, And Dependencies
No storage data is mutated. Runtime state is the transient ZfsSession, which may initialize libzfs handles for the request. The response carries quota usage and inode support classification. Depends on Program/App, StorageTargets, QuotaBlockDevice, QuotaTk, ZfsSession, quota config enums, and common response serialization.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risks include logging but not returning an explicit error for empty target/block-device selection, potentially expensive range queries, and mixed inode quota support requiring callers to interpret QuotaInodeSupport correctly.

### Test Signals
Test signals include all-target aggregation, single-target missing, ID list/range/single query types, mixed filesystem inode support, ZFS session initialization failure, and ext/XFS quotactl errors mapped by QuotaTk.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/storage/quota/GetQuotaInfoMsgEx.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/storage/quota/GetQuotaInfoMsgEx.h -->
## sources/distributed-fs/beegfs/storage/source/net/message/storage/quota/GetQuotaInfoMsgEx.h

### Purpose
Declares the storage-side quota query handler.

### Important APIs, Types, And Functions
GetQuotaInfoMsgEx derives from GetQuotaInfoMsg and overrides processIncoming(ResponseContext&).

### Control Flow
The header keeps the network dispatch surface minimal; target selection and quota backend work are in the cpp implementation.

### State, Persistence, And Dependencies
No state is stored in the class outside inherited request fields. Depends on common GetQuotaInfoMsg and Common.h.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risk is low; behavioral complexity comes from QuotaTk and block-device discovery.

### Test Signals
Dispatch compile tests plus cpp-level quota query tests cover this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/storage/quota/GetQuotaInfoMsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/storage/quota/SetExceededQuotaMsgEx.cpp -->
## sources/distributed-fs/beegfs/storage/source/net/message/storage/quota/SetExceededQuotaMsgEx.cpp

### Purpose
Receives quota-exceeded ID sets from management and updates local exceeded-quota stores for targets in the referenced storage pool.

### Important APIs, Types, And Functions
processIncoming() checks Config::getQuotaEnableEnforcement(), resolves the StoragePool by getStoragePoolId(), iterates local StorageTargets, and calls ExceededQuotaStores::get(targetID)->updateExceededQuota() for pool members. It responds with SetExceededQuotaRespMsg.

### Control Flow
If enforcement is disabled it logs a configuration mismatch and returns INTERNAL. If the pool is unknown it logs a warning and returns UNKNOWNPOOL. Otherwise it updates each matching target store and returns SUCCESS.

### State, Persistence, And Dependencies
Runtime quota-enforcement state is mutated in per-target exceeded quota stores. Persistence depends on the store implementation outside this file; no disk IO is performed directly here. Depends on Program/App, Config, StoragePoolStore, StoragePool membership, StorageTargets, ExceededQuotaStores, quota data type/exceeded type fields, and common response message.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risks include silent success when a known pool contains no local targets, configuration skew between management and storage nodes, and all-or-nothing response not identifying per-target update failures.

### Test Signals
Test signals include enforcement disabled, unknown pool, pool with multiple local targets, pool with no local targets, user/group quota types, and replacement of previous exceeded ID sets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/storage/quota/SetExceededQuotaMsgEx.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/storage/quota/SetExceededQuotaMsgEx.h -->
## sources/distributed-fs/beegfs/storage/source/net/message/storage/quota/SetExceededQuotaMsgEx.h

### Purpose
Declares the storage-side handler for quota-exceeded update messages.

### Important APIs, Types, And Functions
SetExceededQuotaMsgEx derives from SetExceededQuotaMsg and overrides processIncoming(ResponseContext&).

### Control Flow
The header exposes no additional helpers or state; enforcement and pool logic are in the cpp implementation.

### State, Persistence, And Dependencies
No class-local state exists. Depends on common SetExceededQuotaMsg and Common.h.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risk is low at declaration level; correctness depends on the cpp update loop and store implementation.

### Test Signals
Compile dispatch tests and quota-enforcement behavior tests cover this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/storage/quota/SetExceededQuotaMsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/msghelpers/MsgHelperIO.h -->
## sources/distributed-fs/beegfs/storage/source/net/msghelpers/MsgHelperIO.h

### Purpose
Provides a central inline wrapper layer for storage-server POSIX IO syscalls and a compatibility wrapper for timestamp updates.

### Important APIs, Types, And Functions
APIs include open/openat/close/read/pread/write/pwrite/lseek/fsync, syncFileRange(), readAhead(), truncateAt(), and utimensat(). It defines MAX_KERNEL_READAHEAD, MsgHelperIO_ATIME_POS, MsgHelperIO_MTIME_POS, UTIME_OMIT fallback, and feature detection for real utimensat.

### Control Flow
Most methods directly call the matching syscall. readAhead() chunks posix_fadvise(POSIX_FADV_WILLNEED) calls into MAX_KERNEL_READAHEAD pieces. truncateAt() emulates truncateat by openat + ftruncate + close. utimensat() calls the real syscall when available, otherwise maps timespec to timeval and uses futimesat.

### State, Persistence, And Dependencies
No state is stored. Persistent effects are exactly the wrapped syscall effects on filesystem objects and kernel cache hints. Depends on Config/App includes, Program singleton for broader context, POSIX/Linux syscalls, compile-time CONFIG_DISTRO_HAS_SYNC_FILE_RANGE, and BeeGFS utility macros.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risks include the futimesat fallback approximating UTIME_OMIT by copying the other timestamp rather than preserving the current value, syncFileRange becoming a no-op on unsupported builds, and truncateAt close failures collapsing into generic -1.

### Test Signals
Test signals include syscall error propagation, partial readAhead ranges, UTIME_OMIT behavior on platforms with and without utimensat, truncateAt on missing and existing files, and syncFileRange compile variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/msghelpers/MsgHelperIO.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/nodes/StorageNodeOpStats.h -->
## sources/distributed-fs/beegfs/storage/source/nodes/StorageNodeOpStats.h

### Purpose
Extends node operation statistics with per-user storage operation counters and byte accounting.

### Important APIs, Types, And Functions
UserStorageOpStats holds atomic numOps, numBytesWritten, and numBytesRead. StorageNodeOpStats derives from NodeOpStats and overloads updateNodeOp() for operation-only and byte-counted read/write updates.

### Control Flow
Each update takes a read lock, finds counters by peer IP cookie and user ID, upgrades to a write lock if either counter is absent, inserts missing StorageOpCounter objects, then increments operation or byte counters and unlocks.

### State, Persistence, And Dependencies
Runtime state is inherited maps for clientCounterMap and userCounterMap. No persistence occurs here; counters live in memory for monitoring/stat reporting. Depends on NodeOpStats, OpCounter, IPAddress, AtomicUInt64, SafeRWLock, and StorageOpCounterTypes.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risks include iterator reuse after lock upgrade based on pre-upgrade lookups, duplicated include of OpCounter.h, and accepting byte updates for operation types documented as read/write only without local assertion.

### Test Signals
Test signals include first-update insertion, concurrent updates for same and different users, byte accounting, and map consistency after lock upgrade races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/nodes/StorageNodeOpStats.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/program/Main.cpp -->
## sources/distributed-fs/beegfs/storage/source/program/Main.cpp

### Purpose
Provides the executable entry point for the BeeGFS storage daemon.

### Important APIs, Types, And Functions
main(int argc, char** argv) delegates directly to Program::main(argc, argv).

### Control Flow
There is no additional control flow; all initialization, daemon lifecycle, and exit code handling happen in Program and App.

### State, Persistence, And Dependencies
No state is stored here. Depends on Program.h and the platform C runtime calling main.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risk is minimal; this file is intentionally a thin wrapper.

### Test Signals
Test signal is that the storage binary links and process exit code matches Program::main().
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/program/Main.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/program/Program.cpp -->
## sources/distributed-fs/beegfs/storage/source/program/Program.cpp

### Purpose
Owns top-level process startup and shutdown for the storage daemon App singleton.

### Important APIs, Types, And Functions
Defines static Program::app and Program::main(). Program::main() checks build-type compatibility, runs AbstractApp runtime initialization, creates App(argc, argv), starts it in the current thread, captures getAppResult(), deletes the App, and returns the result.

### Control Flow
Control flow is linear: initialize runtime, construct App, run until App exits, read result, destroy App. Program::getApp() exposes the static pointer to the rest of the storage code while App is alive.

### State, Persistence, And Dependencies
Program::app is process-global runtime state. No persistent data is written here directly, but App startup/shutdown drives all daemon persistence. Depends on BuildTypeTk, AbstractApp, App, and Program.h.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risks include global singleton lifetime: code using Program::getApp() during shutdown after delete would dereference stale memory because app is not reset to null.

### Test Signals
Test signals include startup failure propagation, App result propagation, debug/release build-type checks, and no Program::getApp() use after Program::main() returns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/program/Program.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/program/Program.h -->
## sources/distributed-fs/beegfs/storage/source/program/Program.h

### Purpose
Declares the process-level Program singleton wrapper used to access the running storage App.

### Important APIs, Types, And Functions
Public APIs are static main(int, char**) and static getApp(). The constructor is private and the static App* app is defined in Program.cpp.

### Control Flow
The header establishes Program as the central access point used by message handlers, stores, quota helpers, and target management.

### State, Persistence, And Dependencies
The only state is the static App pointer. Depends on app/App.h.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risk is broad global coupling and lack of null-safety in getApp(); most storage code assumes App has already been constructed.

### Test Signals
Test signals include singleton availability during App lifetime and compilation of modules that include Program.h.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/program/Program.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/session/Session.cpp -->
## sources/distributed-fs/beegfs/storage/source/session/Session.cpp

### Purpose
Implements small Session operations for merging and serializing per-client open local-file state.

### Important APIs, Types, And Functions
Functions are mergeSessionLocalFiles(), serializeForTarget(), and deserializeForTarget(). They delegate most work to SessionLocalFileStore.

### Control Flow
Merging passes the other Session local-file store into this session. Serialization writes sessionID then target-filtered local files. Deserialization reads sessionID and target-filtered local files.

### State, Persistence, And Dependencies
State is the Session sessionID and localFiles store. Persistence is serializer output used by SessionStore save/load for target session state. Depends on Serialization and SessionLocalFileStore.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risks include no validation that deserialized sessionID matches the key used by SessionStore, and merge semantics that only add non-existing files while logging conflicts deeper in the store.

### Test Signals
Test signals include target-filtered serialization round trips, merging sessions with distinct and duplicate local-file keys, and deserialize failure propagation through Deserializer::good().
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/session/Session.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/session/Session.h -->
## sources/distributed-fs/beegfs/storage/source/session/Session.h

### Purpose
Declares a client session object that owns all open local chunk-file sessions for one client node ID.

### Important APIs, Types, And Functions
Session has constructors for normal and deserialization paths, mergeSessionLocalFiles(), serializeForTarget(), deserializeForTarget(), getSessionID(), and getLocalFiles().

### Control Flow
The class acts as a small aggregate around SessionLocalFileStore; all per-file lifecycle operations are delegated to the store.

### State, Persistence, And Dependencies
State consists of NumNodeID sessionID and SessionLocalFileStore localFiles. It is serialized by target for session persistence. Depends on NumNodeID, Common.h, and SessionLocalFileStore.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risks include the default constructor leaving sessionID unset until deserialization and exposing a mutable localFiles pointer directly.

### Test Signals
Test signals include construction with a known client ID, default construction followed by deserialize, and local file store access through getLocalFiles().
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/session/Session.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/session/SessionLocalFile.cpp -->
## sources/distributed-fs/beegfs/storage/source/session/SessionLocalFile.cpp

### Purpose
Implements opening, closing, serialization support, and mirror-node assignment for an open chunk file within a client session.

### Important APIs, Types, And Functions
Important APIs are SessionLocalFile::Handle::close(), serializeNodeID() deserializer overload, openFile(), and setMirrorNodeExclusive(). openFile() uses target FD, PathInfo, write/read mode, SessionQuotaInfo, ChunkStore, MsgHelperIO, and ExceededQuotaStore.

### Control Flow
openFile() fast-paths already-open handles, then locks the session, constructs the chunk path, opens or creates the chunk. Write opens go through ChunkStore::openChunkFile with quota enforcement and a V2 chmod retry on NOTOWNER. Read opens call MsgHelperIO::openat and ignore ENOENT. The handle FD and offset are initialized before returning. setMirrorNodeExclusive() stores the first mirror node only.

### State, Persistence, And Dependencies
Runtime state includes FDHandle, offset, counters, mirror node, mirror session flag, and serverCrashed flag. Persistent effects are chunk file creation and ownership/permission fixes via ChunkStore. Depends on Program/App, ChunkStore, StorageTk path helpers, quota stores, MsgHelperIO, NodeStoreServers for mirror node deserialization, serialization framework, and FDHandle.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risks include assigning FDHandle(-1) after read-open ENOENT, logging File created even for read opens, quotaInfo assumed non-null for write opens, and deserialization failing when mirrorNode ID no longer exists.

### Test Signals
Test signals include read missing file, write create with quota, NOTOWNER chmod retry, concurrent open races, mirror node deserialization success/failure, close failure logging, and setMirrorNodeExclusive race behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/session/SessionLocalFile.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/session/SessionLocalFile.h -->
## sources/distributed-fs/beegfs/storage/source/session/SessionLocalFile.h

### Purpose
Declares the per-open-chunk session object used to cache file descriptors, offsets, mirroring metadata, IO counters, and crash-dirty state.

### Important APIs, Types, And Functions
SessionLocalFile contains nested Handle with close(), serialization template, openFile(), setMirrorNodeExclusive(), releaseLastReference(), close(), getters/setters for FD, flags, offset, mirror state, counters, and serverCrashed.

### Control Flow
The class separates store ownership from underlying filesystem handle lifetime: stores hold shared_ptr<SessionLocalFile>, outsiders may hold references, and releaseLastReference returns a closeable Handle only when the removed file has no remaining references and the handle was not claimed by another caller.

### State, Persistence, And Dependencies
Runtime state includes shared Handle, targetID, fileID, openFlags, offset, mirrorNode, isMirrorSession, atomic read/write/read-ahead counters, sessionMutex, and serverCrashed. Serialized state includes IDs, flags, offset, mirror info, crash flag, and counters. Depends on NodeHandle, PathInfo, QuotaData, Mutex, FDHandle, atomic, and BeeGFS serialization helpers.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risks include complex lifetime protocol around shared_ptr/weak_ptr and claimed atomic, exposing FDHandle by const reference that may become invalid after close, and lock granularity mixing atomics with mutex-protected offset/FD fields.

### Test Signals
Test signals include serialization round trip, handle close after last reference removal, multiple concurrent removals claiming only once, direct IO flag detection, counter atomics, and mirror-session key separation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/session/SessionLocalFile.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/session/SessionLocalFileStore.cpp -->
## sources/distributed-fs/beegfs/storage/source/session/SessionLocalFileStore.cpp

### Purpose
Implements a mutex-protected map of local-file session objects keyed by file handle, target, and mirror-session status.

### Important APIs, Types, And Functions
APIs include addAndReferenceSession(), referenceSession(), removeSession(), removeAllSessions(), removeAllMirrorSessions(), deleteAllSessions(), getSize(), mergeSessionLocalFiles(), serializeForTarget(), and deserializeForTarget().

### Control Flow
Add inserts a unique_ptr and returns a shared_ptr to inserted or existing session. Remove erases from the map, then calls releaseLastReference() outside the mutex to decide whether a handle can be closed by the caller. Serialization writes a fixed-up element count for sessions matching targetID. Deserialization reads keys and SessionLocalFile objects and rejects mismatched target IDs.

### State, Persistence, And Dependencies
Runtime state is the sessions map guarded by mutex. Persistence is target-filtered serialization used by SessionStore. Depends on SessionLocalFile, Program/App for logging context, serialization framework, boost::make_unique, std::map ordering, and Mutex.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risks include removeAllMirrorSessions erasing shared_ptrs without returning handles for close, mergeSessionLocalFiles moving from another store without locking that other store, and serializeForTarget writing total session count placeholder correctly only if Serializer mark fixup remains valid.

### Test Signals
Test signals include duplicate add returning existing session, remove with active external reference, target-filtered serialize/deserialize, mismatch target deserialization failure, duplicate merge warning, and mirror cleanup behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/session/SessionLocalFileStore.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/session/SessionLocalFileStore.h -->
## sources/distributed-fs/beegfs/storage/source/session/SessionLocalFileStore.h

### Purpose
Declares the local-file session store and its compound key for file handle, concrete target ID, and mirror/non-mirror namespace.

### Important APIs, Types, And Functions
Public APIs add/reference/remove sessions, bulk remove, mirror-target cleanup, size, merge, serialize, and deserialize. Key has a serialization template and operator< based on tuple ordering.

### Control Flow
The key design lets original and mirrored sessions for the same file handle and target coexist when rotated mirrors can attach both buddies to one server.

### State, Persistence, And Dependencies
State is std::map<Key, shared_ptr<SessionLocalFile>> plus a mutable Mutex. Depends on ObjectReferencer include legacy, Mutex, Common.h, and SessionLocalFile.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risks include raw pointer parameter to mergeSessionLocalFiles() and direct map ownership semantics that require cpp code to manage handle closing correctly.

### Test Signals
Test signals include key ordering, mirror namespace separation, and compile-time serialization of Key.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/session/SessionLocalFileStore.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/session/SessionStore.cpp -->
## sources/distributed-fs/beegfs/storage/source/session/SessionStore.cpp

### Purpose
Implements the top-level client Session map, synchronization with management node session lists, and binary session persistence per target.

### Important APIs, Types, And Functions
APIs include referenceSession(), referenceOrAddSession(), syncSessions(), getAllSessionIDs(), getSize(), serializeForTarget(), deserializeForTarget(), loadFromFile(), and saveToFile().

### Control Flow
The store is mutex protected. syncSessions() compares ordered local sessions with ordered master NodeHandle list and removes local sessions not present in the master list, returning removed sessions for cleanup. Serialization writes session count and each key/session payload. Deserialization merges local files into existing sessions. loadFromFile() opens, stats, reads, deserializes, and validates; saveToFile() serializes into a sized buffer and writes a truncating file.

### State, Persistence, And Dependencies
Runtime state is a map from NumNodeID to shared_ptr<Session>. Persistent state is a target-specific session file containing serialized session IDs and local file stores. Depends on Session, Mutex, serialization framework, NodeHandle, filesystem open/read/write/stat/close, boost scoped_array/make_unique, and StringTk/System logging.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risks include holding the store mutex during file IO, not looping on partial reads/writes, using statBuf.st_size directly for allocation, not fsyncing saved session files, and deserialization count accepting duplicate keys by merging.

### Test Signals
Test signals include session creation/reference, sync removal against sorted master lists, load corrupt/truncated files, save/load round trip, partial write simulation, and merge of duplicate sessions after restart.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/session/SessionStore.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/session/SessionStore.h -->
## sources/distributed-fs/beegfs/storage/source/session/SessionStore.h

### Purpose
Declares the storage daemon session registry keyed by client NumNodeID.

### Important APIs, Types, And Functions
Public APIs allow referencing, adding, synchronizing, listing IDs, sizing, target-filtered serialization/deserialization, and load/save from file.

### Control Flow
The class models sessions as shared objects so in-flight operations can retain references while the map is synchronized or cleaned.

### State, Persistence, And Dependencies
State is std::map<NumNodeID, shared_ptr<Session>> guarded by mutable Mutex. Depends on Node.h, ObjectReferencer include, Mutex, Common.h, and Session.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risks include exposing removed sessions to caller cleanup while other references may remain and relying on callers to pass an ordered master list to syncSessions().

### Test Signals
Test signals include map lookup/add behavior, syncSessions ordering assumptions, and persistence method declarations matching cpp behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/session/SessionStore.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/session/ZfsSession.cpp -->
## sources/distributed-fs/beegfs/storage/source/session/ZfsSession.cpp

### Purpose
Implements dynamic libzfs session management for quota queries against ZFS-backed storage targets.

### Important APIs, Types, And Functions
APIs are constructor, destructor, initZfsSession(void*), and getZfsDeviceHandle(uint16_t, string). It loads function pointers zfs_open, zfs_prop_get_userquota_int, libzfs_error_description, and libzfs_error_action.

### Control Flow
The constructor creates an invalid session. initZfsSession() stores the dlopen handle, calls QuotaTk::initLibZfs(), resolves required symbols through dlsym(), marks App libzfs error state on failures, and returns validity. getZfsDeviceHandle() reuses a cached per-target handle or opens a new ZFS filesystem/pool handle.

### State, Persistence, And Dependencies
Runtime state is the libzfs handle, dlopen handle, function pointers, validity flag, and fsHandles map. The destructor calls QuotaTk::uninitLibZfs(); individual zfs handles are cached but not explicitly closed in this file. Depends on QuotaTk, Program/App error reporting, dlfcn, libzfs ABI names, and ZFSSESSION_ZFS_TYPE matching libzfs ZFS_TYPE_FILESYSTEM.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risks include ABI drift in libzfs symbols/signatures, not clearing dlerror before each dlsym, cached zfs_open handles lacking explicit close, and a single invalid symbol leaving partial state in the object.

### Test Signals
Test signals include missing dlopen handle, missing symbols, invalid libzfs init, handle reuse per target, ZFS error logging, and destructor cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/session/ZfsSession.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/session/ZfsSession.h -->
## sources/distributed-fs/beegfs/storage/source/session/ZfsSession.h

### Purpose
Declares the ZFS quota query session wrapper and cached ZFS pool handle map.

### Important APIs, Types, And Functions
Public APIs include constructor/destructor, initZfsSession(), getZfsDeviceHandle(), function pointers used by QuotaTk, getlibZfsHandle(), and isSessionValid().

### Control Flow
The class is a thin ABI bridge around libzfs loaded at runtime rather than linked directly.

### State, Persistence, And Dependencies
State includes dlOpenHandleLibZfs, libZfsHandle, fsHandles, zfs_open pointer, quota/error function pointers, and isValid. Depends on std::map types, target IDs, and libzfs-compatible opaque void* handles.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risks include public mutable function pointer members and raw void* handles with no type safety.

### Test Signals
Test signals include initialization state transitions and caller checks of isSessionValid before ZFS requests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/session/ZfsSession.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/storage/ChunkDir.h -->
## sources/distributed-fs/beegfs/storage/source/storage/ChunkDir.h

### Purpose
Declares the in-memory lock object representing one chunk directory path element.

### Important APIs, Types, And Functions
ChunkDir stores an ID string and an RWLock, with readLock(), writeLock(), unlock(), and getID(). ChunkStore is a friend and creates/manages instances.

### Control Flow
The object gives ChunkStore a per-directory-element lock to coordinate mkdir/rmdir races across V3 chunk directory paths.

### State, Persistence, And Dependencies
Runtime state is the RWLock and stable ID. No direct persistence exists; it represents filesystem directories on disk indirectly. Depends on string and BeeGFS RWLock.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risks include manual lock/unlock usage without RAII in callers and ID uniqueness relying on ChunkStore::getUniqueDirID().

### Test Signals
Test signals include concurrent mkdir/rmdir paths using the same directory ID and lock/unlock pairing under errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/storage/ChunkDir.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/storage/ChunkLockStore.h -->
## sources/distributed-fs/beegfs/storage/source/storage/ChunkLockStore.h

### Purpose
Provides abstract per-target chunk ID locking used mainly to serialize mirrored chunk modifications during buddy resync.

### Important APIs, Types, And Functions
ChunkLockStoreContents contains lockedChunks, lockedChunksMutex, and chunkUnlockedCondition. ChunkLockStore exposes lockChunk(), unlockChunk(), and debug-only size/copy helpers, with private getOrInsertTargetLockStore() and findTargetLockStore().

### Control Flow
lockChunk() inserts the chunk ID into a target-specific set, waiting on a condition variable while another holder owns it. unlockChunk() removes the ID and broadcasts to waiters. Target lock-store maps are inserted under an RWLock.

### State, Persistence, And Dependencies
Runtime state is the target-to-lock-store map and per-target locked chunk sets. No persistence occurs. Depends on Mutex, Condition, RWLock/UniqueRWLock, StringSet, logging/backtrace utilities, and target IDs.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risks include no ownership token, so any caller can unlock any chunk ID; missing target store on unlock only logs; and condition waits rely on Mutex/Condition semantics rather than std::condition_variable predicates.

### Test Signals
Test signals include multiple waiters on same chunk, independent targets using same chunk ID, unlock of unknown target/chunk, and stress tests for target-store insertion races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/storage/ChunkLockStore.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/storage/ChunkStore.cpp -->
## sources/distributed-fs/beegfs/storage/source/storage/ChunkStore.cpp

### Purpose
Implements chunk directory cache/reference management, chunk directory creation/removal, quota-aware chunk opening, and legacy V2 permission repair.

### Important APIs, Types, And Functions
Important functions are constructor, referenceDir(), releaseDir(), cache sweep helpers, rmdirChunkDirPath(), mkdirV2ChunkDirPath(), mkdirChunkDirPath(), openAndChown(), openChunkFile(), and chmodV2ChunkDirPath().

### Control Flow
Directory references are stored in a map of AtomicObjectReferencer objects and a separate refCache that holds extra references for cache retention. Opening a chunk first checks quota-exceeded stores, tries openAndChown(), creates missing directories with V2 or V3 locking if PATHNOTEXISTS, retries open, unlocks/releases the last directory element, and logs failures. V3 mkdir holds parent/current locks to prevent racing bottom-up rmdir from removing a just-created parent.

### State, Persistence, And Dependencies
Persistent effects include creating chunk directories, creating/opening chunk files, chowning quota-owned files, removing empty chunk directories, and chmodding legacy V2 paths. Runtime state includes the directory reference map, refCache, random sweep state, and locks. Depends on Program/App config, ChunkDir, StorageTk path conventions, ExceededQuotaStore, StorageTkEx include, Random, Path, POSIX mkdirat/unlinkat/openat/fchown/fchmodat, and quota/session data.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risks include StorageTk::pathExists() in quota check not using targetFD and therefore checking process-relative paths, unlink(path.c_str()) in openAndChown also not targetFD-relative, manual cache reference accounting, ignored chmodV2 retry result in callers, and complex lock release paths on mkdir/open failures.

### Test Signals
Test signals include V2 and V3 path creation, racing mkdir/rmdir, quota exceeded on new versus existing chunk, NOTOWNER repair, cache sweep limits, openAndChown failure cleanup, and rmdir stopping on ENOTEMPTY/ENOENT.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/storage/ChunkStore.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/storage/ChunkStore.h -->
## sources/distributed-fs/beegfs/storage/source/storage/ChunkStore.h

### Purpose
Declares the directory-level chunk store used by storage IO paths to manage chunk directory locks, references, cache, creation, removal, and file opening.

### Important APIs, Types, And Functions
Public APIs include referenceDir(), releaseDir(), getCacheSize(), cacheSweepAsync(), rmdirChunkDirPath(), openChunkFile(), and chmodV2ChunkDirPath(). Private helpers manage directory insertion, release, cache add/remove/sweep, mkdir variants, openAndChown(), and getUniqueDirID().

### Control Flow
The class separates directory object lifetime from filesystem paths: ChunkDir instances lock path elements, while POSIX calls operate relative to target FDs.

### State, Persistence, And Dependencies
State consists of dirs, refCacheSyncLimit, refCacheAsyncLimit, randGen, refCache, and rwlock. Persistent state is only changed by the cpp methods that create/remove dirs and files. Depends on AtomicObjectReferencer, MetadataTk, Random, Path, StorageDefinitions, StorageErrors, SessionQuotaInfo, ExceededQuotaStorePtr, and ChunkDir.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risks include raw pointer referencers, manual release requirements after referenceDir(), and cache limits computed at construction from global App config.

### Test Signals
Test signals include reference/release balance, getUniqueDirID depth uniqueness, cache size and sweep behavior, and openChunkFile declarations matching caller expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/storage/ChunkStore.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/storage/QuotaBlockDevice.cpp -->
## sources/distributed-fs/beegfs/storage/source/storage/QuotaBlockDevice.cpp

### Purpose
Discovers and classifies the filesystem/block device backing storage targets for quota queries.

### Important APIs, Types, And Functions
APIs are getBlockDeviceOfTarget(), getBlockDevicesOfTargets(), quotaInodeSupportFromBlockDevice(), and getFsType(). getFsType() maps statfs magic values to EXTX, XFS, ZFS, or UNKNOWN.

### Control Flow
getBlockDeviceOfTarget() uses StorageTk::findMountForPath(), constructs a normalized QuotaBlockDevice from mount path, device, fs type, and storage target path, then checks libzfs compatibility for ZFS targets when needed. Multi-target discovery iterates target path maps.

### State, Persistence, And Dependencies
Persistent state is not changed. Runtime state is the returned QuotaBlockDevice values and possible App libzfs error/support flags set through QuotaTk during ZFS probing. Depends on StorageTk mount lookup, Program/App, QuotaTk, statfs filesystem magic constants, Path normalization, and Linux filesystem headers.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risks include throwing runtime_error from getFsType() on statfs failure, hard-coded ZFS magic, and returning a default UNKNOWN block device when no mount is found without an explicit error.

### Test Signals
Test signals include ext4/XFS/ZFS/unknown statfs mappings, no mount found, normalized storage paths, ZFSOLD fallback via QuotaTk, and multi-target map population.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/storage/QuotaBlockDevice.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/storage/QuotaBlockDevice.h -->
## sources/distributed-fs/beegfs/storage/source/storage/QuotaBlockDevice.h

### Purpose
Declares QuotaBlockDevice, the value object that records the mount, device path, filesystem type, and normalized storage target path used for quota backends.

### Important APIs, Types, And Functions
Public APIs include default and value constructors, static discovery helpers, quotaInodeSupportFromBlockDevice(), getFsType(), getters/setters, and supportsInodeQuota(). It also defines QuotaBlockDeviceMap typedefs.

### Control Flow
The class abstracts filesystem-specific quota capability decisions away from quota message handlers and QuotaTk.

### State, Persistence, And Dependencies
State is storageTargetPath, mountPath, blockDevicePath, and fsType. It is copied into maps for quota query requests. Depends on Common.h, Path, StorageDefinitions, and quota enums.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risks include mutable setters allowing fsType/path changes after discovery and UNKNOWN default values that callers must handle.

### Test Signals
Test signals include constructor normalization, supportsInodeQuota for EXTX/XFS/ZFS/ZFSOLD/UNKNOWN, and map usage by target ID.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/storage/QuotaBlockDevice.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/storage/StorageTargets.cpp -->
## sources/distributed-fs/beegfs/storage/source/storage/StorageTargets.cpp

### Purpose
Implements storage target initialization, persistent buddy-resync state communication, target-state decisions, resync startup checks, target info reporting, and target-state map construction.

### Important APIs, Types, And Functions
Important APIs include StorageTarget constructor, prepareTargetDir(), isTargetDir(), setBuddyNeedsResync(), setBuddyNeedsResyncComm(), handleTargetStateChange(), StorageTargets::decideResync(), checkBuddyNeedsResync(), generateTargetInfoList(), getStatInfo(), and fillTargetStateMap().

### Control Flow
StorageTarget opens chunk and buddy mirror directories, initializes quota block device info, and schedules retry if .buddyneedsresync is unacked. setBuddyNeedsResync() writes an unacked state file and sends SetTargetConsistencyStatesMsg to management, retrying through TimerQueue on communication failure. decideResync() compares local clean shutdown, local state, mgmt state, buddy mapping, and offline timeout to choose local consistency states. checkBuddyNeedsResync() reports persisted buddy resync needs and starts BuddyResyncer jobs for online NEEDS_RESYNC secondaries.

### State, Persistence, And Dependencies
Persistent state includes storage-format files, chunks/mirror directory creation, .buddyneedsresync, and .lastbuddycomm. Runtime state includes target FDs, consistency state, cleanShutdown, offline timeout, buddyResyncInProgress, timer retry handle, and StorageTargets map. Depends on StorageTk, PreallocatedFile, TimerQueue, MessagingTk, management NodeStoreServers, MirrorBuddyGroupMapper, TargetStateStore, BuddyResyncer, InternodeSyncer, QuotaBlockDevice, and storage target info messages.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risks include global App access during target state callbacks, retry lambda capturing this during destruction mitigated only by cancel, only primaries communicating buddy resync state, and getStatInfo override files affecting capacity reports. decideResync is sensitive to management-state race timing and cleanShutdown one-shot handling.

### Test Signals
Test signals include target directory preparation, missing chunks/mirror directory constructor failures, buddyneedsresync unacked retry, mgmt communication success/failure, clean versus dirty startup decisions, BAD state stickiness, offline timeout publication, and resync job start conditions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/storage/StorageTargets.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/storage/StorageTargets.h -->
## sources/distributed-fs/beegfs/storage/source/storage/StorageTargets.h

### Purpose
Declares StorageTarget, the per-target runtime/persistent state object, and StorageTargets, the immutable map wrapper for local targets.

### Important APIs, Types, And Functions
StorageTarget APIs expose path, ID, chunk/mirror FDs, quota block device, consistency state, buddy resync in-progress/needed state, clean shutdown, offline timeout, last buddy communication, setState(), prepareTargetDir(), and isTargetDir(). StorageTargets exposes decideResync(), checkBuddyNeedsResync(), generateTargetInfoList(), fillTargetStateMap(), getTarget(), and getTargets().

### Control Flow
The header defines persistent buddy-resync flags and LastBuddyComm serialization, plus the state-transition hooks used by cpp implementation.

### State, Persistence, And Dependencies
State includes Path, target ID, FDHandles, PreallocatedFile values, QuotaBlockDevice, TimerQueue references, management and buddy mapper references, atomics, RWLock-protected consistency/clean/offline state, and optional retry timer handle. Depends on TargetStateStore types, StorageTargetInfo, PreallocatedFile, TimerQueue, Config, QuotaBlockDevice, boost::optional, chrono, and atomics.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risks include const StorageTargetMap preventing target insertion/removal after construction, raw target pointer returns, and timer callbacks coupled to object lifetime.

### Test Signals
Test signals include getters/setters under concurrent access, PreallocatedFile serialization compatibility, offline timeout expiry, and target map lookup semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/storage/StorageTargets.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/storage/SyncedStoragePaths.h -->
## sources/distributed-fs/beegfs/storage/source/storage/SyncedStoragePaths.h

### Purpose
Provides per-target path serialization and monotonic storage version generation for operations that need synchronized dynamic attributes.

### Important APIs, Types, And Functions
APIs are constructor, lockPath(path, targetID), unlockPath(path, targetID), initStorageVersion(), and incStorageVersion().

### Control Flow
lockPath() builds a target-qualified path string, waits until it can insert it into a set, increments storageVersion, and returns the new version. unlockPath() erases the target-qualified path and broadcasts to waiters.

### State, Persistence, And Dependencies
Runtime state is a mutex, condition variable, storageVersion initialized from current seconds shifted left 32, and a set of locked path keys. No disk persistence occurs; versions are returned in responses for metadata reconciliation. Depends on LogContext, System time, Condition, Mutex, StringTk hex conversion, and Common.h.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risks include inconsistent StringTk::uint64ToHexStr in lockPath versus uintToHexStr in unlockPath, which could break unlock for some target IDs if formatting differs, and no RAII guard for lock/unlock pairing.

### Test Signals
Test signals include concurrent lock wait/unlock wake, monotonically increasing versions, unlock of unknown path logging, and target-qualified independence for same path on different targets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/storage/SyncedStoragePaths.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/toolkit/QuotaTk.cpp -->
## sources/distributed-fs/beegfs/storage/source/toolkit/QuotaTk.cpp

### Purpose
Implements quota usage retrieval across ext-family, XFS, and ZFS storage target block devices.

### Important APIs, Types, And Functions
Important functions are appendQuotaForID(), requestQuotaForRange(), requestQuotaForList(), checkQuota(), initLibZfs(), uninitLibZfs(), checkRequiredLibZfsFunctions(), and requestQuotaFromZFS().

### Control Flow
Range/list helpers repeatedly call appendQuotaForID(). checkQuota() iterates QuotaBlockDeviceMap and dispatches to XFS Q_XGETQUOTA, ZFS property reads, or generic Q_GETQUOTA, merges block and inode counters into QuotaData, and tolerates missing-user ESRCH/XFS ENOENT. ZFS support dynamically loads libzfs functions and probes inode quota support, falling back to ZFSOLD when needed.

### State, Persistence, And Dependencies
No BeeGFS persistent state is written. Runtime state includes ZfsSession handles, App libzfs error-reported flag, and returned QuotaData counters. Kernel quota subsystem state is read through quotactl. Depends on QuotaData, QuotaBlockDevice, ZfsSession, Program/App, UnitTk, System logging, boost lexical_cast, dlfcn, quotactl, xfs headers, and ZFS user/group property names.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risks include large ID ranges causing many syscalls, ZFS property names built from IDs without validation, mixed-target partial failures returning false while preserving some data, dynamic libzfs ABI drift, and fstype UNKNOWN falling into generic quotactl path.

### Test Signals
Test signals include ext/XFS/ZFS quota reads, missing users, invalid quota type, partial target failure, ZFSOLD inode behavior, missing libzfs symbols, and counter merging across multiple block devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/toolkit/QuotaTk.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/toolkit/QuotaTk.h -->
## sources/distributed-fs/beegfs/storage/source/toolkit/QuotaTk.h

### Purpose
Declares static quota toolkit functions for querying usage and managing dynamic ZFS support.

### Important APIs, Types, And Functions
The QuotaTk class exposes ID, range, and list quota request helpers; checkQuota(); init/uninit libzfs; checkRequiredLibZfsFunctions(); and requestQuotaFromZFS(). Constructor is private.

### Control Flow
The header centralizes backend quota APIs so message handlers do not directly call quotactl or libzfs.

### State, Persistence, And Dependencies
No state is held by the class; state is passed through QuotaBlockDeviceMap, QuotaData, and ZfsSession parameters. Depends on Common.h, QuotaData, ZfsSession, and QuotaBlockDevice.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risks include raw pointer parameters and no explicit ownership annotations; callers must pass valid output lists and sessions.

### Test Signals
Test signals include compile coverage for all backend function declarations and null/invalid pointer behavior through cpp tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/toolkit/QuotaTk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/toolkit/StorageTkEx.h -->
## sources/distributed-fs/beegfs/storage/source/toolkit/StorageTkEx.h

### Purpose
Provides storage-server-specific helper routines for reading dynamic POSIX file attributes from open FDs or target-relative paths.

### Important APIs, Types, And Functions
APIs are two overloads of getDynamicFileAttribs(): one for an open file descriptor and one for dirFD plus path. It also defines storage format constants, max EntryInfo serialization size, and default chunk dir/file modes.

### Control Flow
Each overload calls fstat or fstatat and fills file size, allocated blocks, modification time, and last access time on success.

### State, Persistence, And Dependencies
No state is stored. Persistent state is not changed; these helpers observe filesystem metadata. Depends on Config, Common, FsckChunk, Path, Storagedata, StorageErrors, Mutex/SafeRWLock includes, StorageTk, and POSIX stat APIs.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risks include returning false without preserving errno for callers, using st_blocks units directly as allocated block count, and broad includes in a header-only utility.

### Test Signals
Test signals include fstat/fstatat success, missing path failure, symlink behavior via fstatat flags, and correct timestamp/block values for sparse files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/toolkit/StorageTkEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/tests/TestConfig.cpp -->
## sources/distributed-fs/beegfs/storage/tests/TestConfig.cpp

### Purpose
Implements GoogleTest coverage for storage daemon configuration file handling.

### Important APIs, Types, And Functions
Test fixture methods SetUp() and TearDown() initialize dummy config paths and remove generated empty config files. Tests are missingConfigFile and defaultConfigFile.

### Control Flow
missingConfigFile constructs argv with a guaranteed non-existent cfgFile path and asserts Config construction throws InvalidConfigException. defaultConfigFile resolves the test binary path through /proc/self/exe, builds the relative default config path, constructs Config, and treats ConnAuthFileException as an acceptable return path.

### State, Persistence, And Dependencies
State is temporary path strings and possible /tmp empty config cleanup. No repository persistence is changed. Depends on TestConfig.h, Config, StorageTk::pathExists, StringTk, readlink, dirname, GoogleTest, and ConnAuthFileException.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risks include fixed /tmp filenames, Linux-specific /proc/self/exe, mutable std::string buffers used as argv entries, and defaultConfigFile not asserting success beyond absence of unexpected exceptions.

### Test Signals
Test signals are the tests themselves; additional coverage should include empty config file cleanup and invalid auth-file paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/tests/TestConfig.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/tests/TestConfig.h -->
## sources/distributed-fs/beegfs/storage/tests/TestConfig.h

### Purpose
Declares the GoogleTest fixture and constants for storage configuration tests.

### Important APIs, Types, And Functions
Defines DUMMY_NOEXIST_CONFIG_FILE, DUMMY_EMPTY_CONFIG_FILE, DEFAULT_CONFIG_FILE_RELATIVE, APP_NAME, and class TestConfig with SetUp/TearDown plus dummyConfigFile and emptyConfigFile members.

### Control Flow
The fixture provides reusable path state for tests that construct Config with synthetic argv arrays.

### State, Persistence, And Dependencies
State is per-test strings; cleanup is performed in TearDown in the cpp file. Depends on Config, LogContext, gtest, ConnAuthFileException, and libgen.h.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risks include a semicolon embedded in APP_NAME macro expansion and fixed /tmp names shared across parallel test runs.

### Test Signals
Test signal is successful fixture setup/teardown around the TestConfig.cpp cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/tests/TestConfig.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/.clippy.toml -->
## sources/distributed-fs/ceph-client/.clippy.toml

### Purpose
Configures Rust Clippy policy for the kernel tree embedded in the ceph-client source.

### Important APIs, Types, And Functions
Important settings are msrv = 1.85.0, check-private-items = true, disallowed kernel::dbg macro, and disallowed CStr pointer conversion methods with kernel-prelude replacements.

### Control Flow
Clippy reads this TOML during lint runs and applies repository-wide restrictions to Rust code.

### State, Persistence, And Dependencies
No runtime state or persistence beyond the configuration file itself. Depends on Clippy configuration schema and kernel Rust prelude APIs.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risks include MSRV drift with toolchains and allow-invalid reliance for custom macro paths.

### Test Signals
Test signals include running cargo/clippy or kernel Rust lint targets and confirming forbidden methods/macros fail.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/.clippy.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/.rustfmt.toml -->
## sources/distributed-fs/ceph-client/.rustfmt.toml

### Purpose
Configures Rust formatting defaults for the kernel Rust code.

### Important APIs, Types, And Functions
Sets edition = 2021 and newline_style = Unix, with several unstable formatting options commented for occasional manual use.

### Control Flow
rustfmt reads this file when formatting Rust sources and ignores commented unstable options unless enabled in a nightly-capable workflow.

### State, Persistence, And Dependencies
No runtime state exists; it persists repository formatting policy. Depends on rustfmt support for edition and newline_style options.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risks are minimal; commented unstable options may become stale or misleading over time.

### Test Signals
Test signal is rustfmt producing stable Unix-newline output for Rust files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/.rustfmt.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/Kconfig -->
## sources/distributed-fs/ceph-client/Documentation/Kconfig

### Purpose
Adds documentation-related build-time warning options under COMPILE_TEST.

### Important APIs, Types, And Functions
Defines menu Documentation with CONFIG_WARN_MISSING_DOCUMENTS and CONFIG_WARN_ABI_ERRORS boolean options and help text.

### Control Flow
When COMPILE_TEST is enabled, Kconfig exposes these options so Documentation/Makefile can run missing-reference and ABI validation commands during builds.

### State, Persistence, And Dependencies
State is kernel .config selections; no runtime behavior. Depends on Kconfig syntax, COMPILE_TEST, Documentation/Makefile conditionals, and tools/docs scripts.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risks include warnings increasing build noise and ABI validation depending on Python tooling availability.

### Test Signals
Test signals include menu visibility under COMPILE_TEST and Makefile checks firing when options are y.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/Makefile -->
## sources/distributed-fs/ceph-client/Documentation/Makefile

### Purpose
Coordinates Linux kernel Sphinx documentation builds, documentation checks, cleanup, and help output.

### Important APIs, Types, And Functions
Key variables include SPHINXBUILD, SPHINXOPTS, SPHINXDIRS, DOCS_THEME, DOCS_CSS, BUILDDIR, PDFLATEX, LATEXOPTS, PYTHONPYCACHEPREFIX, BUILD_WRAPPER, and FONTS_CONF_DENY_VF. Targets include htmldocs, mandocs, latexdocs, pdfdocs, linkcheckdocs, htmldocs-redirects, refcheckdocs, cleandocs, dochelp, and device-tree binding integration.

### Control Flow
The Makefile conditionally runs missing-document and ABI checks, detects sphinx-build, either emits skip guidance or invokes sphinx-pre-install and sphinx-build-wrapper, and prints dynamic help based on Documentation subdirectories.

### State, Persistence, And Dependencies
Persistent outputs go under $(obj)/output and Python cache prefix. cleandocs removes the build directory. Depends on kernel build variables srctree/obj/Q/PYTHON3, tools/docs scripts, Sphinx, xelatex, dt binding subdir clean integration, and shell utilities.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risks include shell-based command detection, PATH-dependent Sphinx behavior, linkcheck target network access, and generated output cleanup scope.

### Test Signals
Test signals include make htmldocs with and without Sphinx installed, SPHINXDIRS subset builds, cleandocs, dochelp, WARN_MISSING_DOCUMENTS, and WARN_ABI_ERRORS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/admin-guide/aoe/autoload.sh -->
## sources/distributed-fs/ceph-client/Documentation/admin-guide/aoe/autoload.sh

### Purpose
Installs modprobe aliases so the ATA over Ethernet kernel module can autoload for major 152 block and char devices.

### Important APIs, Types, And Functions
The script sets f=/etc/modprobe.d/aoe.conf, checks it is readable and writable, greps for major-152, and appends alias lines when absent.

### Control Flow
Control flow is simple shell validation and append. It exits 1 when the config file cannot be accessed.

### State, Persistence, And Dependencies
Persistent effect is editing /etc/modprobe.d/aoe.conf. Depends on /bin/sh, grep, shell redirection, and root/write permission to /etc/modprobe.d.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risks include unquoted $f, requiring the file to already exist, duplicate detection matching any major-152 text, and no atomic update.

### Test Signals
Test signals include existing alias no-op, missing file failure, unwritable file failure, and successful append under a temp root or container.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/admin-guide/aoe/autoload.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/admin-guide/aoe/status.sh -->
## sources/distributed-fs/ceph-client/Documentation/admin-guide/aoe/status.sh

### Purpose
Prints a compact status table for AoE block devices from sysfs.

### Important APIs, Types, And Functions
Uses sysfs_dir environment override defaulting to /sys, validates $sysd/block, loops over $sysd/block/etherd* excluding partitions, reads netif and state files, prints formatted device/netif/state rows, and sorts output.

### Control Flow
It exits if sysfs is unavailable and otherwise tolerates no devices via a sentinel end word.

### State, Persistence, And Dependencies
No persistent state is changed; it reads sysfs device attributes. Depends on /bin/sh, basename, ls, grep, sed, cat, printf, sort, and AoE sysfs layout.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risks include backtick word splitting, unquoted paths in the for list, and limited fields compared with aoe-stat.

### Test Signals
Test signals include no sysfs, empty device list, custom sysfs_dir fixture, devices with ! in names, and partition filtering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/admin-guide/aoe/status.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/admin-guide/aoe/udev-install.sh -->
## sources/distributed-fs/ceph-client/Documentation/admin-guide/aoe/udev-install.sh

### Purpose
Installs AoE-specific udev rules from udev.txt into the system udev rules directory.

### Important APIs, Types, And Functions
The script finds udev.conf from $conf, /etc/udev/udev.conf, or find /etc; extracts udev_rules, defaults to /etc/udev/rules.d, validates the directory, and copies dirname($0)/udev.txt to 60-aoe.rules using sh -xc.

### Control Flow
Persistent effect is writing a udev rules file under the selected rules directory.

### State, Persistence, And Dependencies
State is shell variables for config and rules path; no runtime daemon state. Depends on /bin/sh, basename, find, sed, dirname, cp, and root/write permission.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risks include command injection/word splitting through sh -xc and unquoted variables, multiple udev.conf paths from find, and no atomic copy.

### Test Signals
Test signals include env-provided conf, missing conf, missing rules dir, and copy from a fixture script directory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/admin-guide/aoe/udev-install.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/admin-guide/cifs/winucase_convert.pl -->
## sources/distributed-fs/ceph-client/Documentation/admin-guide/cifs/winucase_convert.pl

### Purpose
Converts a Windows uppercase mapping table into two-level C wchar_t lookup arrays for CIFS documentation/support generation.

### Important APIs, Types, And Functions
The Perl script parses lines matching 0xHHLL to 0xUUUU mappings, stores them in @top[first][second], prints static t2_xx[256] arrays for populated top-level bytes, and prints a toplevel[256] pointer array.

### Control Flow
Input is read from stdin. Output is generated C initializer text on stdout.

### State, Persistence, And Dependencies
No persistent state beyond generated output redirected by callers. Runtime state is the @top sparse two-dimensional array. Depends on Perl, expected tab-separated input format, and C wchar_t type in the generated consumer.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risks include ignoring unmapped/malformed lines silently, GPLv3-or-later script license in a GPL-2.0 kernel context needing historical review, and memory/output size for large tables.

### Test Signals
Test signals include sample mapping lines, gaps producing NULL top-level entries, populated 256-entry tables, and malformed input ignored.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/admin-guide/cifs/winucase_convert.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/arch/arm/samsung/clksrc-change-registers.awk -->
## sources/distributed-fs/ceph-client/Documentation/arch/arm/samsung/clksrc-change-registers.awk

### Purpose
Transforms older Samsung ARM clock source structure initializers by deriving reg_src/reg_div metadata from register mask definitions.

### Important APIs, Types, And Functions
Functions include extract_value(), remove_brackets(), splitdefine(), find_length(), and find_shift(). BEGIN reads a header file passed as ARGV[1] to collect *_MASK definitions except USB_SIG_MASK. The main rule rewrites clksrc_clk initializers.

### Control Flow
The script parses nested initializer blocks, records .shift, .mask, .reg_divider, .reg_source, and .divider_shift fields, derives generated mask names, then emits .reg_div and .reg_src substructures before closing the initializer.

### State, Persistence, And Dependencies
No persistent state unless stdout is redirected. Runtime state is awk associative array dmask and per-block parsed fields. Depends on awk, legacy Samsung clock header macro shape, and source initializers matching clksrc_clk.*=.*{ patterns.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risks include fragile textual parsing, exit on unknown masks/shifts, disabled debug branches, and no support for formatting variants outside expected legacy code.

### Test Signals
Test signals include known Samsung header/source fixtures, missing mask definitions, nested initializer depth handling, and generated reg_div/reg_src output comparison.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/arch/arm/samsung/clksrc-change-registers.awk -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/arch/arm64/kasan-offsets.sh -->
## sources/distributed-fs/ceph-client/Documentation/arch/arm64/kasan-offsets.sh

### Purpose
Prints arm64 KASAN shadow offsets for selected virtual address sizes and shadow scale shifts.

### Important APIs, Types, And Functions
Defines print_kasan_offset(scale argument via $2 and VABITS via $1) and prints tables for KASAN_SHADOW_SCALE_SHIFT 3 and 4 across VABITS 48, 47, 42, 39, and 36.

### Control Flow
Control flow is deterministic shell arithmetic and printf output.

### State, Persistence, And Dependencies
No persistent state; output is documentation/reference text. Depends on POSIX shell arithmetic supporting 64-bit-like expressions in the running shell and printf formatting.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risks include arithmetic portability across shells and hard-coded VABITS set getting stale as arm64 VA modes evolve.

### Test Signals
Test signals include expected offset table values and execution under dash/bash used by kernel scripts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/arch/arm64/kasan-offsets.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/arch/s390/config3270.sh -->
## sources/distributed-fs/ceph-client/Documentation/arch/s390/config3270.sh

### Purpose
Autogenerates a /tmp/mkdev3270 shell script to create s390 3270 tty/tub device nodes and update /etc/inittab.

### Important APIs, Types, And Functions
Key variables define proc driver path, root/dev directories, output script paths, inittab paths, and mingetty line template. The script probes /proc/tty/driver/tty3270, modprobes tub3270 if needed, queries config, and writes shell commands.

### Control Flow
It initializes output scripts, optionally removes/recreates /dev/3270, filters existing inittab tty lines, reads driver device rows, writes mknod/chmod commands and mingetty entries, appends inittab replacement commands, and exits.

### State, Persistence, And Dependencies
Persistent effects happen only when the generated /tmp/mkdev3270 is later run; this script itself writes /tmp/mkdev3270 and temporary /tmp/mkdev3270.a. Depends on /bin/sh, modprobe, /proc tty3270 interface, mknod, chmod, grep, mv, /etc/inittab style init systems, and s390 device major/minor semantics.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risks include legacy init assumptions, unquoted variables, destructive generated commands, /tmp path predictability, and root requirements.

### Test Signals
Test signals include running against a mocked proc file, generated script diffing, missing driver exit, and no /dev/dasd conditional branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/arch/s390/config3270.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/conf.py -->
## sources/distributed-fs/ceph-client/Documentation/conf.py

### Purpose
Configures the Linux kernel Sphinx documentation build, including extension loading, dynamic include/exclude patterns, theme options, LaTeX/PDF settings, and Sphinx event hooks.

### Important APIs, Types, And Functions
Important objects include kern_doc_dir, needs_sphinx, has_include_patterns, config_init(), have_command(), extensions, c_id_attributes, source_suffix, version/release detection, get_cline_version(), HTML/LaTeX/man/texinfo/epub/pdf settings, add_subproject_index(), and setup().

### Control Flow
At import time it computes Sphinx version support, extension list, math renderer, theme settings from environment, version from Makefile or command line, and static output settings. config_init() adjusts include/exclude patterns relative to app.srcdir and populates latex_documents. setup() connects config-inited and source-read hooks.

### State, Persistence, And Dependencies
Build state is Sphinx config variables and event-time mutations. Persistent outputs are created by Sphinx outside this file. Depends on Sphinx, kernel Documentation/sphinx extensions, tools/scripts paths, environment variables DOCS_THEME/DOCS_CSS/SPHINX_IMGMATH, LaTeX/dvipng availability, and Read the Docs theme packages when selected.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risks include broad except while parsing ../Makefile, a likely typo encoding="utf=8", mutable global latex_documents, tags global use from Sphinx, and optional theme imports silently falling back to alabaster.

### Test Signals
Test signals include full Documentation build, SPHINXDIRS subproject build, old and new Sphinx include_patterns behavior, DOCS_THEME fallback, imgmath selection, and generated latex_documents.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/conf.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/Makefile -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/Makefile

### Purpose
Defines device-tree binding schema validation, example extraction, linting, schema generation, compatibility checking, and cleanup targets.

### Important APIs, Types, And Functions
Key tools are dt-doc-validate, dt-extract-example, dt-mk-schema, yamllint, and dt-check-compatible. Targets include check_dtschema_version, %.example.dts, processed-schema.json, .yamllint.checked, .dt-binding.checked, dt_compatible_check, dt_binding_check_one, and dt_binding_check.

### Control Flow
The Makefile verifies dtschema minimum version 2023.9, finds YAML schemas excluding processed-schema, extracts examples for schemas with examples, lints YAML in parallel, validates schemas, builds processed-schema.json through a temp file, and handles clean artifact deletion.

### State, Persistence, And Dependencies
Persistent build outputs live under $(obj), including processed-schema.json, .checked stamp files, and generated example dts/dtb files. Depends on kernel build variables, dtschema Python package, yamllint, find/sed/grep/xargs/sort, DTC_FLAGS, and scripts/dtc helpers.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risks include shell find/xargs behavior with unusual paths, grep-based DT_SCHEMA_FILES filtering, yamllint absence causing skipped lint, and clean-files executing find during makefile evaluation.

### Test Signals
Test signals include dt_binding_check, single-schema DT_SCHEMA_FILES, missing tool errors, minimum version enforcement, and clean removing example artifacts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/access-controllers/access-controllers.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/access-controllers/access-controllers.yaml

### Purpose
Defines the common device-tree binding schema for generic domain access controller providers and consumers.

### Important APIs, Types, And Functions
Properties include #access-controller-cells, access-controller-names string-array, and access-controllers phandle-array. select: true makes the schema always participate, with additionalProperties allowed.

### Control Flow
The schema documents how consumer nodes reference one or more access controllers by phandle and optional arguments defined by provider-specific bindings.

### State, Persistence, And Dependencies
No runtime state; it validates DTS source and provides generated documentation. Depends on devicetree core meta-schema and /schemas/types.yaml definitions.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risks include broad select:true and additionalProperties:true making validation permissive; provider-specific cell semantics must be enforced elsewhere.

### Test Signals
Test signals include dt_binding_check and examples with multiple controllers and matching names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/access-controllers/access-controllers.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arc/snps,archs-pct.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arc/snps,archs-pct.yaml

### Purpose
Defines the binding for ARC HS pipeline performance counters.

### Important APIs, Types, And Functions
Requires compatible const snps,archs-pct, one reg entry, and one clocks entry; additionalProperties is false.

### Control Flow
The schema validates a single performance counter hardware block capable of counting CPU/cache events and overflow interrupts as described.

### State, Persistence, And Dependencies
No runtime state; it constrains DTS nodes and generates docs. Depends on devicetree core schema and generic reg/clocks schemas.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risks include no interrupt property despite description mentioning overflow interrupts, which may be intentional or incomplete.

### Test Signals
Test signals include dt_binding_check with valid compatible/reg/clocks and rejection of extra properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arc/snps,archs-pct.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/actions.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/actions.yaml

### Purpose
Defines root-node compatible strings for Actions Semi S500, S700, and S900 platforms.

### Important APIs, Types, And Functions
The schema constrains $nodename to / and compatible to oneOf board-specific item chains ending in SoC compatibles such as actions,s500, actions,s700, or actions,s900.

### Control Flow
It validates board DTS root compatible ordering and leaves additionalProperties true for normal root-node content.

### State, Persistence, And Dependencies
No runtime state; used by dt-schema and docs generation. Depends on core devicetree meta-schema.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risks include board list staleness and permissive additional properties.

### Test Signals
Test signals include valid board compatible arrays and rejection of wrong ordering or missing SoC fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/actions.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/airoha,en7581-chip-scu.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/airoha,en7581-chip-scu.yaml

### Purpose
Defines the binding for the Airoha EN7581 chip SCU syscon block.

### Important APIs, Types, And Functions
Requires compatible items airoha,en7581-chip-scu followed by syscon and one reg entry. additionalProperties is false and an example shows syscon@1fa20000.

### Control Flow
The schema validates the shared SCU register block used by clock, pinctrl, ECC, and other controllers.

### State, Persistence, And Dependencies
No runtime state; it constrains DTS and documents the hardware node. Depends on core devicetree schemas and syscon compatible conventions.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risks include restricting all additional properties, which may require updates if child nodes or syscon-related properties become necessary.

### Test Signals
Test signals include dt_binding_check example validation and rejection of missing syscon fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/airoha,en7581-chip-scu.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/airoha.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/airoha.yaml

### Purpose
Defines root-node compatible strings for Airoha EN7523 and EN7581 evaluation boards.

### Important APIs, Types, And Functions
Constrains $nodename to / and compatible to board plus SoC fallback pairs: airoha,en7523-evb/airoha,en7523 and airoha,en7581-evb/airoha,en7581.

### Control Flow
The schema validates platform root compatible ordering while allowing additional root properties.

### State, Persistence, And Dependencies
No runtime state; used for device-tree validation and generated docs. Depends on devicetree core meta-schema.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risks include board coverage staleness and broad additionalProperties true.

### Test Signals
Test signals include valid board arrays and invalid ordering checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/airoha.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/altera.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/altera.yaml

### Purpose
Defines root-node compatible strings for Altera/Intel SoCFPGA ARM platforms across Arria, Cyclone, Stratix, Agilex, and related modules.

### Important APIs, Types, And Functions
The schema constrains $nodename to / and compatible to many oneOf item chains with board compatibles followed by module/family/SoC fallbacks.

### Control Flow
It validates ordering and accepted board IDs for SoCFPGA root nodes and permits normal root-node extra properties.

### State, Persistence, And Dependencies
No runtime state; schema affects DTS validation and documentation. Depends on core devicetree schema.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risks include large enum maintenance burden, subtle compatible ordering for module/carrier combinations, and permissive additionalProperties.

### Test Signals
Test signals include dt_binding_check with representative boards from each family and rejection of missing family fallback strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/altera.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/altera/socfpga-clk-manager.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/altera/socfpga-clk-manager.yaml

### Purpose
Defines the binding for the Altera SoCFPGA clock manager and nested clock tree nodes.

### Important APIs, Types, And Functions
Top-level properties require compatible altr,clk-mgr and one reg. Optional clocks object defines #address-cells/#size-cells and patternProperties for oscillators and clock/pll/gate/divider child nodes. $defs/clock-props defines reg, #clock-cells, clk-gate, div-reg, and fixed-divider.

### Control Flow
The schema validates nested clock provider structure for Cyclone5, Arria5, and Arria10 families, including compatible values and required clock cells for child clock nodes.

### State, Persistence, And Dependencies
No runtime state; it constrains DTS and documents clock manager layout. Depends on core devicetree schemas and /schemas/types.yaml uint32-array definitions.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risks include complex patternProperties admitting broad names, nested unevaluatedProperties interactions, and fixed compatible list needing updates for new clock variants.

### Test Signals
Test signals include example validation, nested child clock checks, extra-property rejection, and invalid compatible rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/altera/socfpga-clk-manager.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/amazon,al.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/amazon,al.yaml

### Purpose
Defines root-node compatible strings for Amazon Annapurna Labs Alpine platforms.

### Important APIs, Types, And Functions
The compatible property supports Alpine V1 with const al,alpine, Alpine V2 board al,alpine-v2-evp plus al,alpine-v2, and Alpine V3 board amazon,al-alpine-v3-evp plus amazon,al-alpine-v3.

### Control Flow
The schema validates platform root compatible arrays and allows additional root properties.

### State, Persistence, And Dependencies
No runtime state; used by dt-schema and docs generation. Depends on devicetree core meta-schema.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risks include no $nodename constraint unlike many peer root schemas and stale board lists.

### Test Signals
Test signals include valid V1/V2/V3 compatible arrays and wrong-order rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/amazon,al.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/amd,pensando.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/amd,pensando.yaml

### Purpose
Defines root-node compatible strings for AMD Pensando Elba SoC platforms.

### Important APIs, Types, And Functions
Constrains $nodename to / and compatible to amd,pensando-elba-ortano followed by amd,pensando-elba.

### Control Flow
The schema validates root compatible ordering for Pensando Elba boards while allowing additional root properties.

### State, Persistence, And Dependencies
No runtime state. Depends on devicetree core meta-schema.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risks are mainly board-list staleness and permissive additionalProperties true.

### Test Signals
Test signals include valid ortano compatible pair and rejection of missing SoC fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/amd,pensando.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/amd,seattle.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/amd,seattle.yaml

### Purpose
Defines root-node compatible strings for AMD Seattle SoC platforms.

### Important APIs, Types, And Functions
Constrains $nodename to / and compatible to amd,seattle-overdrive followed by amd,seattle.

### Control Flow
The schema validates Seattle Overdrive root compatible ordering and allows additional root properties.

### State, Persistence, And Dependencies
No runtime state. Depends on devicetree core meta-schema.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risks are minimal beyond stale platform coverage.

### Test Signals
Test signals include dt_binding_check for valid compatible pair and invalid order rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/amd,seattle.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/amlogic.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/amlogic.yaml

### Purpose
Defines root-node compatible strings for a broad set of Amlogic Meson and newer Amlogic SoC boards.

### Important APIs, Types, And Functions
Constrains $nodename to / and compatible to many oneOf item arrays covering Meson6/8/8m2/8b, GXBB/GXL/GXLX/GXM, AXG, G12A/G12B, SM1, A1/A4/A5/C3/S4/S6/S7/S7D/T7, and board-specific compatibles.

### Control Flow
The schema validates platform root compatible ordering, including board, module, SoC, and family fallback strings where applicable.

### State, Persistence, And Dependencies
No runtime state; it drives DTS validation and generated platform docs. Depends on devicetree core meta-schema.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risks include high maintenance cost, duplicate boards across SoC variants requiring careful ordering, and additionalProperties true leaving non-compatible root validation to other schemas.

### Test Signals
Test signals include representative valid boards per SoC family, module/carrier arrays, and rejection of missing family or SoC fallback entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/amlogic.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/amlogic/amlogic,meson-gx-ao-secure.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/amlogic/amlogic,meson-gx-ao-secure.yaml

### Purpose
Defines the binding for Amlogic Meson AO secure firmware register syscon interfaces.

### Important APIs, Types, And Functions
select matches nodes containing amlogic,meson-gx-ao-secure. compatible supports the base meson-gx-ao-secure plus syscon, or newer SoC-specific ao-secure compatibles followed by meson-gx-ao-secure and syscon. reg is required, and amlogic,has-chip-id is an optional boolean.

### Control Flow
The schema validates the secure firmware shared register bank and optional chip ID availability.

### State, Persistence, And Dependencies
No runtime state; it constrains DTS nodes used by firmware/syscon drivers. Depends on core devicetree meta-schema and syscon compatible conventions.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risks include explicit select to avoid matching every syscon, and false additionalProperties blocking future properties unless schema is updated.

### Test Signals
Test signals include base and SoC-specific compatible arrays, chip-id boolean, and rejection of nodes missing reg.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/amlogic/amlogic,meson-gx-ao-secure.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/amlogic/amlogic,meson-mx-secbus2.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/amlogic/amlogic,meson-mx-secbus2.yaml

### Purpose
Defines the binding for Amlogic Meson8/Meson8b/Meson8m2 SECBUS2 syscon register interface.

### Important APIs, Types, And Functions
Requires compatible items enum amlogic,meson8-secbus2 or amlogic,meson8b-secbus2 followed by syscon, plus one reg entry. additionalProperties is false and an example shows secbus2@4000.

### Control Flow
The schema documents a register bank used by pin-controller and AO ARC core control bits, accessed directly or through secure monitor calls depending on secure mode.

### State, Persistence, And Dependencies
No runtime state; it validates DTS and produces binding docs. Depends on core devicetree schema and syscon conventions.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risks include Meson8m2 mentioned in title/description but not as a separate compatible enum, which may be intentional if it reuses meson8b.

### Test Signals
Test signals include dt_binding_check example, valid compatible alternatives, and rejection of extra properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/amlogic/amlogic,meson-mx-secbus2.yaml -->
