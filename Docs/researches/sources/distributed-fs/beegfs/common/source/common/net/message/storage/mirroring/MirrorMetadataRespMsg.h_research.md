<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/mirroring/MirrorMetadataRespMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/storage/mirroring/MirrorMetadataRespMsg.h

### Purpose
`MirrorMetadataRespMsg` returns the operation result for metadata mirroring task submission.

### Important APIs, Types, And Functions
It subclasses `SimpleIntMsg` with type `NETMSGTYPE_MirrorMetadataResp`. `getResult()` casts the integer payload to `FhgfsOpsErr`.

### Control Flow
The response is a single integer result written and read by `SimpleIntMsg`.

### State, Persistence, And Dependencies
No state persists beyond the response. It depends on `StorageErrors` and common message wrappers.

### Integration Points
Metadata mirroring senders use this to decide whether task replay was accepted.

### Risks
Only one result code is returned, so partial task failures must be represented by server-side semantics if task batches are used. Tests should cover success and representative storage error values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/mirroring/MirrorMetadataRespMsg.h -->
