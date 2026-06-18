<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/lookup/FindLinkOwnerRespMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/storage/lookup/FindLinkOwnerRespMsg.h

### Purpose
`FindLinkOwnerRespMsg` returns the result of a link-owner lookup: an integer status, the stored owner node ID, and the parent directory ID associated with the link.

### Important APIs, Types, And Functions
It derives from `NetMessageSerdes<FindLinkOwnerRespMsg>` and uses `NETMSGTYPE_FindLinkOwnerResp`. Serialization writes `result`, a raw parent-directory string, and `NumNodeID linkOwnerNodeID`. Getters expose `getResult()`, `getLinkOwnerNodeID()`, and `getParentDirID()`.

### Control Flow
The send constructor stores a pointer into the caller's `parentDirID` string and records its length. The deserializer fills the raw string pointer through the serdes layer, after which `getParentDirID()` copies it.

### State, Persistence, And Dependencies
State is wire-only and not persisted. Dependencies include `NetMessage`, `NumNodeID`, and raw-string serialization.

### Integration Points
This response is consumed by metadata lookup/repair paths that need to decide where a link should be handled next.

### Risks
The parent directory string pointer is non-owned, so send-side lifetime matters. The result field is a plain `int` rather than `FhgfsOpsErr`, so caller conventions must stay consistent. Tests should cover success, error, zero node ID, and parentDirID strings with expected serialization length.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/lookup/FindLinkOwnerRespMsg.h -->
