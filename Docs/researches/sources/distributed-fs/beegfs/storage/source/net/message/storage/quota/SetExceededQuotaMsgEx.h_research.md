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
