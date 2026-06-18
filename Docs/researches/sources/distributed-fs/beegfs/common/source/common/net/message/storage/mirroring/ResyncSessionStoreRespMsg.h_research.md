<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/mirroring/ResyncSessionStoreRespMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/storage/mirroring/ResyncSessionStoreRespMsg.h

### Purpose
`ResyncSessionStoreRespMsg` returns the result of session-store resynchronization.

### Important APIs, Types, And Functions
It subclasses `SimpleIntMsg` with `NETMSGTYPE_ResyncSessionStoreResp`; `getResult()` casts to `FhgfsOpsErr`.

### Control Flow
The response contains only a status code.

### State, Persistence, And Dependencies
The message has no persisted state. It depends on common simple-message serialization and storage error conventions.

### Integration Points
Session-store resync senders use the result to proceed after the extra-data transfer.

### Risks
No detail is returned about which part of the store failed. Tests should cover success, communication errors, and receiver-side validation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/mirroring/ResyncSessionStoreRespMsg.h -->
