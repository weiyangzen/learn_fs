<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/lookup/FindOwnerRespMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/storage/lookup/FindOwnerRespMsg.h

### Purpose
`FindOwnerRespMsg` returns the result of owner discovery and the discovered `EntryInfoWithDepth`, allowing callers to know both the owner and how far the lookup progressed.

### Important APIs, Types, And Functions
It derives from `NetMessageSerdes<FindOwnerRespMsg>` with `NETMSGTYPE_FindOwnerResp`. The wire layout is `result` plus a backed `EntryInfoWithDepth`. `getResult()` returns the integer status and `getEntryInfo()` returns the parsed entry info.

### Control Flow
The serialization constructor keeps a non-owned pointer to the response entry info; deserialization fills the internal `entryInfo` object.

### State, Persistence, And Dependencies
The message has only transient result and entry-info fields. It depends on `EntryInfoWithDepth`, `EntryInfo`, and BeeGFS NetMessage serdes.

### Integration Points
It completes the request/response pair for metadata owner discovery and informs clients or metadata nodes where to continue operations.

### Risks
The result is an integer convention rather than a strongly typed enum. Send-side entry-info lifetime must cover serialization. Tests should verify success and error results, depth preservation, and default deserialization behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/lookup/FindOwnerRespMsg.h -->
