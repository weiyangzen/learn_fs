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
