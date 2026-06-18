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
