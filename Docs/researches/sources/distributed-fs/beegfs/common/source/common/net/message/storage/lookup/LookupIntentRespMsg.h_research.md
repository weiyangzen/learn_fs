<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/lookup/LookupIntentRespMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/storage/lookup/LookupIntentRespMsg.h

### Purpose
`LookupIntentRespMsg` returns the compound result for `LookupIntentMsg`, including lookup status and optional stat, revalidate, create, open, file-handle, stripe-pattern, path-info, and entry-info data.

### Important APIs, Types, And Functions
It derives from `NetMessageSerdes<LookupIntentRespMsg>` using `NETMSGTYPE_LookupIntentResp`. Response flags are `REVALIDATE`, `CREATE`, `OPEN`, and `STAT`. Mutators `addResponseRevalidate()`, `addResponseCreate()`, `addResponseOpen()`, `addResponseStat()`, `setLookupResult()`, and `setEntryInfo()` build the conditional payload. Serialization writes response flags and lookup result, then optional stat data in network format, revalidate result, create result, open result plus file handle/pattern/path info, and finally entry info when lookup or create succeeded.

### Control Flow
The response begins in a minimal lookup-only state with internal create defaults set to `FhgfsOpsErr_INTERNAL`. Optional response blocks are appended as the server completes requested intents. During deserialization, entry info is read if lookup or create succeeded even when the send side only writes it if a pointer was set.

### State, Persistence, And Dependencies
State is transient, but it communicates persistent metadata decisions such as created entry info and stripe pattern. Dependencies include `StripePattern`, `StorageErrors`, `PathInfo`, `StatData`, and `EntryInfo`.

### Integration Points
Client-side VFS/open/create/stat flows unpack this response after a compound metadata operation. It is tightly paired with `LookupIntentMsg` and its client-mode protocol copy.

### Risks
Open responses use non-owned file-handle, pattern, and path-info pointers. The conditional final `EntryInfo` block must match success semantics exactly or readers desynchronize. Tests should cover lookup-only, stat-only, create success/failure, open success with pattern/path info, missing entry-info pointer on success, and all combinations requested by `LookupIntentMsg`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/lookup/LookupIntentRespMsg.h -->
