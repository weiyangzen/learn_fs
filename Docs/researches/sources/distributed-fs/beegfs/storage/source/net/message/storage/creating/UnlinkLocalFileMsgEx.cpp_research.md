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
