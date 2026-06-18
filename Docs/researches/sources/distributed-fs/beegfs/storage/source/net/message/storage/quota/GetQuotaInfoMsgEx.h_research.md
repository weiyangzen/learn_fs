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
