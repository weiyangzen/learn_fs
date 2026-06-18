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
