<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/listing/ListDirFromOffsetRespMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/storage/listing/ListDirFromOffsetRespMsg.h

### Purpose
`ListDirFromOffsetRespMsg` is the server response for directory listing by server-side offset. It returns operation status, entry names, entry types, entry IDs, per-entry next offsets, and a final `newServerOffset` cursor. The compat flag `LISTDIROFFSETRESPMSG_COMPATFLAG_SERVER_SUPPORTS_BUFSIZE` advertises server support for buffer-size-driven listing while remaining safe for older clients.

### Important APIs, Types, And Functions
The class derives from `NetMessageSerdes<ListDirFromOffsetRespMsg>` with message type `NETMSGTYPE_ListDirFromOffsetResp`. Serialization orders `newServerOffset`, `serverOffsets`, `result`, `entryTypes`, `entryIDs`, and `names` through `serdes::backedPtr`. Getters expose the parsed lists by reference and cast `result` back to `FhgfsOpsErr`.

### Control Flow
Writers pass non-owned list pointers. Readers populate the `parsed` lists and redirect the backed pointers to those parsed objects. After serialization/deserialization, `serdesCheck()` validates that all parallel lists have identical lengths; the deserializer path logs a warning/backtrace and marks the message bad on mismatch.

### State, Persistence, And Dependencies
State is transient wire payload only. The message depends on BeeGFS serialization helpers, `FhgfsOpsErr`, standard list typedefs, and `LogContext` for defensive validation.

### Integration Points
Metadata directory listing handlers use this response to stream directory pages back to clients. The offsets couple directly to the server's directory iteration implementation and client pagination logic.

### Risks
The payload uses parallel arrays, so any handler that pushes one list without the others creates a malformed response. Serialization pointers are not owned by the message, so caller-owned lists must outlive send processing. Tests should cover empty listings, non-empty aligned listings, offset continuation, error results, and deserialization rejection of mismatched list sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/listing/ListDirFromOffsetRespMsg.h -->
