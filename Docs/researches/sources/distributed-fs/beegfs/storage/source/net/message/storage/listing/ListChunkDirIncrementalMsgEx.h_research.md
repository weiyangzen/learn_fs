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
