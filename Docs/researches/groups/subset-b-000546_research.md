# subset-b-000546 Research

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/lookup/FindLinkOwnerMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/storage/lookup/FindLinkOwnerMsg.h

### Purpose
`FindLinkOwnerMsg` asks metadata storage to find the stored link owner for a given entry ID. The file comment notes that this owner is only a hint because saved link-owner information may be stale or incorrect.

### Important APIs, Types, And Functions
The message subclasses `SimpleStringMsg`, using `NETMSGTYPE_FindLinkOwner` and the entry ID string as the payload. `getEntryID()` returns a `std::string` copy of `getValue()`.

### Control Flow
Construction either wraps an existing `std::string` for send or creates an empty deserialization instance. All wire encoding is inherited from `SimpleStringMsg`.

### State, Persistence, And Dependencies
The only message state is the transient string payload. It depends on `SimpleStringMsg` and the NetMessage type registry.

### Integration Points
Lookup/repair code can use this request before deciding which metadata node should own a hardlink or directory entry relationship.

### Risks
Because the owner is documented as a hint, callers must not treat a successful response as authoritative without fallback checks. Tests should verify string round-trip, empty/invalid entry ID handling by receivers, and compatibility with the paired response.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/lookup/FindLinkOwnerMsg.h -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/lookup/FindOwnerMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/storage/lookup/FindOwnerMsg.h

### Purpose
`FindOwnerMsg` drives recursive owner discovery for a path or entry. It carries a path, maximum search depth, current recursion depth, and the current `EntryInfo` context.

### Important APIs, Types, And Functions
The class derives from `NetMessageSerdes<FindOwnerMsg>` with type `NETMSGTYPE_FindOwner`. Serialization writes `searchDepth`, `currentDepth`, backed `EntryInfo`, and backed `Path`. Getters expose the path, depths, and parsed `EntryInfo`.

### Control Flow
Senders supply non-owned `Path*` and `EntryInfo*`; deserialization populates internal `Path parsed.path` and `EntryInfo entryInfo`. Receivers use the depth fields to continue or stop owner traversal.

### State, Persistence, And Dependencies
State is transient. Dependencies include `Path`, `EntryInfo`, the abstract message factory friend, and BeeGFS serdes backed-pointer support.

### Integration Points
Metadata lookup code uses this message to walk ownership across distributed directory partitions.

### Risks
Depth fields are unsigned on the wire while the constructor accepts an `int currentDepth`, so negative caller input would wrap. Pointer lifetimes matter on send. Tests should include zero and maximum depths, multi-component paths, deserialization of `EntryInfo`, and receiver behavior when search depth is exhausted.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/lookup/FindOwnerMsg.h -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/lookup/LookupIntentMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/storage/lookup/LookupIntentMsg.h

### Purpose
`LookupIntentMsg` combines lookup with optional revalidate, create, exclusive-create, open, and stat intents. It is a latency-reducing metadata request that lets one network message perform a compound client operation and carries extra fields when buddy-mirror replay is involved.

### Important APIs, Types, And Functions
The class derives from `MirroredMessageBase<LookupIntentMsg>` and reports `supportsMirroring() == true`. Payload intent flags are `LOOKUPINTENTMSG_FLAG_REVALIDATE`, `CREATE`, `CREATEEXCLUSIVE`, `OPEN`, and `STAT`; header feature flags include quota/event support. Key mutators are `addIntentCreate()`, `addIntentCreateExclusive()`, `addIntentOpen()`, `addIntentStat()`, `addBuddyInfo()`, and timestamp/FD setters inherited or exposed through protected fields. Serialization conditionally includes parent info, entry name, revalidate metadata/version, open access/session data, create ownership/mode/targets, optional `FileEvent`, and buddy-mirror second-phase IDs, stripe pattern, owner FD, and timestamps.

### Control Flow
Every message starts with `intentFlags`, parent entry info, and entry name. Optional blocks are serialized only if their flags are set. When `Flag_BuddyMirrorSecond` is present, create messages include the preselected new entry ID/stripe pattern/owner FD/dir timestamps, and all buddy-second messages include file timestamps.

### State, Persistence, And Dependencies
The message is transient but carries fields that later become persistent metadata: entry IDs, stripe patterns, owner/session state, and timestamps. It depends on `EntryInfo`, `FileEvent`, `StatData`, `StripePattern`, `MirroredMessageBase`, and NetMessage header flags.

### Integration Points
Client lookup/open/create/stat paths and metadata mirroring use this message. Its flag definitions must remain synchronized with the client-mode counterpart named in the comment.

### Risks
Flag-dependent layouts are brittle: sender and receiver must agree exactly or subsequent fields shift. Optional pointers such as preferred targets, entry info, and stripe pattern are non-owned. Buddy-mirror second-phase data is security and consistency sensitive because it replays chosen IDs and timestamps. Tests should cover every flag combination, event feature flag absence/presence, buddy-secondary serialization, exclusive create, and backward compatibility with clients that lack newer header feature flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/lookup/LookupIntentMsg.h -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/mirroring/GetMetaResyncStatsMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/storage/mirroring/GetMetaResyncStatsMsg.h

### Purpose
`GetMetaResyncStatsMsg` is a payload-free request for metadata buddy resync statistics.

### Important APIs, Types, And Functions
It subclasses `SimpleMsg` and uses `NETMSGTYPE_GetMetaResyncStats`.

### Control Flow
Construction is the entire behavior; `SimpleMsg` supplies header-only serialization.

### State, Persistence, And Dependencies
There is no payload state. It depends on the NetMessage type registry and the metadata service handler that produces the paired response.

### Integration Points
Management/monitoring code sends this to metadata nodes to inspect buddy resync progress.

### Risks
The only protocol risk is routing to a node that does not implement the message type. Tests should verify request/response dispatch and empty-payload compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/mirroring/GetMetaResyncStatsMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/mirroring/GetMetaResyncStatsRespMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/storage/mirroring/GetMetaResyncStatsRespMsg.h

### Purpose
`GetMetaResyncStatsRespMsg` carries `MetaBuddyResyncJobStatistics` back to a monitoring caller.

### Important APIs, Types, And Functions
The class derives from `NetMessageSerdes<GetMetaResyncStatsRespMsg>` and uses a backed pointer to serialize/deserialize `MetaBuddyResyncJobStatistics`. Getters return a pointer or copy the parsed stats to an output reference.

### Control Flow
Senders provide a non-owned stats pointer. Receivers deserialize into the internal `jobStats` object.

### State, Persistence, And Dependencies
The state is a snapshot of resync statistics, not persistent storage. It depends on `BuddyResyncJobStatistics.h`. The default constructor currently initializes `BaseType(NETMSGTYPE_FsckSetEventLoggingResp)`, which appears inconsistent with the response type used by the send constructor.

### Integration Points
Monitoring and management tools use this after `GetMetaResyncStatsMsg` to display metadata resync status.

### Risks
The default-constructor message type mismatch is a strong test signal and may affect factory/deserialization behavior if not overridden elsewhere. Tests should instantiate deserialization objects, verify message type, and round-trip representative stats including empty, running, and completed resync states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/mirroring/GetMetaResyncStatsRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/mirroring/GetStorageResyncStatsMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/storage/mirroring/GetStorageResyncStatsMsg.h

### Purpose
`GetStorageResyncStatsMsg` asks a storage node for buddy resync statistics for a specific target ID.

### Important APIs, Types, And Functions
It subclasses `SimpleUInt16Msg` with `NETMSGTYPE_GetStorageResyncStats`. `getTargetID()` returns the wrapped 16-bit target ID. The no-argument constructor is protected for factory/deserialization use.

### Control Flow
The message is a simple scalar payload. Senders construct with a target ID; receivers read it through inherited serialization.

### State, Persistence, And Dependencies
Only the target ID is held transiently. It depends on `SimpleUInt16Msg` and the storage resync handler.

### Integration Points
Management and monitoring code sends this to storage servers to inspect per-target resync progress.

### Risks
Callers must distinguish storage target IDs from buddy group IDs. Tests should cover valid target IDs, zero/unknown target handling in receivers, and pairing with the response stats message.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/mirroring/GetStorageResyncStatsMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/mirroring/GetStorageResyncStatsRespMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/storage/mirroring/GetStorageResyncStatsRespMsg.h

### Purpose
`GetStorageResyncStatsRespMsg` returns `StorageBuddyResyncJobStatistics` for a target.

### Important APIs, Types, And Functions
It derives from `NetMessageSerdes<GetStorageResyncStatsRespMsg>` with type `NETMSGTYPE_GetStorageResyncStatsResp`. Serialization uses `serdes::backedPtr(jobStatsPtr, jobStats)`. Getters return the parsed stats by pointer or copy.

### Control Flow
Senders pass a non-owned stats pointer; receivers deserialize into the internal `jobStats` object and expose it.

### State, Persistence, And Dependencies
The message is a transient stats snapshot. It depends on `BuddyResyncJobStatistics.h` and NetMessage serdes.

### Integration Points
It is consumed by monitoring tools and management paths after a storage resync stats request.

### Risks
The send-side pointer must remain valid until serialization completes. Tests should verify round-trip of all statistic fields and behavior for idle, active, failed, and completed resync states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/mirroring/GetStorageResyncStatsRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/mirroring/MirrorMetadataMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/storage/mirroring/MirrorMetadataMsg.h

### Purpose
`MirrorMetadataMsg` is the abstract common-base message for metadata mirroring tasks. It intentionally does not implement payload serialization because `MirrorerTask` lives in the metadata server component rather than common code.

### Important APIs, Types, And Functions
The class derives directly from `NetMessage` with type `NETMSGTYPE_MirrorMetadata`. It stores a non-owned `MirrorerTaskList*`, the number of list elements, and the total serialized length.

### Control Flow
Only protected constructors exist: one for send-side task-list metadata and one for deserialization. Concrete metadata-server code is expected to subclass and implement actual task serialization.

### State, Persistence, And Dependencies
The header carries transient references to mirroring tasks that represent persistent metadata changes to replay elsewhere. It depends only on `NetMessage` and forward declarations in common code.

### Integration Points
`MirrorMetadataMsgEx` or equivalent metadata-server extensions provide serialization and handlers. The common base lets the message type be known without dragging metadata-server task definitions into the common library.

### Risks
Because serialization is deferred to derived code, factory registration and handler downcasts must stay aligned. Non-owned task-list lifetime is critical. Tests should target the derived message implementation and verify task count/serialized-length consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/mirroring/MirrorMetadataMsg.h -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/mirroring/ResyncLocalFileMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/storage/mirroring/ResyncLocalFileMsg.h

### Purpose
`ResyncLocalFileMsg` transfers chunk-file content and optional attributes during storage buddy resync or chunk balancing. It can also represent metadata-only operations through the `NODATA` feature flag.

### Important APIs, Types, And Functions
The message derives from `NetMessageSerdes<ResyncLocalFileMsg>` with `NETMSGTYPE_ResyncLocalFile`. Feature flags control attributes, no-data mode, truncation, sparse checking, buddy-mirror destination, secondary writes, and chunk-balance buddy writes. Serialization writes relative path, target ID, offset, count, optional `SettableFileAttribs`, then a raw data block of `count` bytes.

### Control Flow
Senders provide a non-owned data buffer plus path/target/offset/count and optionally copy chunk attributes. Receivers inspect header feature flags to decide whether attributes/data/truncation/sparse checks apply.

### State, Persistence, And Dependencies
The message is transient but causes persistent chunk data and file attributes to be updated on disk. It depends on `PathInfo`, `StorageDefinitions`, raw-block serialization, and `SettableFileAttribs`.

### Integration Points
Storage resync workers and chunk-balancing flows use it to repair or copy chunk files between primary and secondary targets.

### Risks
`NODATA` still serializes `rawBlock(dataBuf, count)`, so callers must keep count/data consistent with flag semantics or rely on count zero. `TRUNC` is documented as incompatible with `NODATA` but not enforced here. Sparse-check and buddy-mirror flags affect disk layout decisions outside the message. Tests should cover data writes, attribute-only updates, truncation, sparse data, invalid flag combinations, and large counts near payload limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/mirroring/ResyncLocalFileMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/mirroring/ResyncLocalFileRespMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/storage/mirroring/ResyncLocalFileRespMsg.h

### Purpose
`ResyncLocalFileRespMsg` returns the result of a local chunk resync operation.

### Important APIs, Types, And Functions
It subclasses `SimpleIntMsg` with `NETMSGTYPE_ResyncLocalFileResp`; `getResult()` casts the integer to `FhgfsOpsErr`.

### Control Flow
The message carries only the result code.

### State, Persistence, And Dependencies
No state persists in the message. It depends on `SimpleIntMsg` and BeeGFS storage error codes.

### Integration Points
Storage resync senders use this to advance, retry, or fail chunk resync work.

### Risks
It has no byte-count or checksum confirmation, so correctness must be guaranteed by receiver-side handling and higher-level resync verification. Tests should cover success, communication failures, and storage error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/mirroring/ResyncLocalFileRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/mirroring/ResyncRawInodesRespMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/storage/mirroring/ResyncRawInodesRespMsg.h

### Purpose
`ResyncRawInodesRespMsg` returns the status of raw inode resynchronization.

### Important APIs, Types, And Functions
It subclasses `SimpleIntMsg` using `NETMSGTYPE_ResyncRawInodesResp`; `getResult()` casts to `FhgfsOpsErr`.

### Control Flow
Serialization and deserialization are inherited single-integer behavior.

### State, Persistence, And Dependencies
The response itself is transient; the operation it acknowledges repairs persistent inode state.

### Integration Points
Metadata buddy resync code consumes this response after raw inode transfer or comparison work.

### Risks
The response does not carry per-inode failure detail. Tests should verify error-code round-trip and higher-level retry behavior on non-success results.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/mirroring/ResyncRawInodesRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/mirroring/ResyncSessionStoreMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/storage/mirroring/ResyncSessionStoreMsg.h

### Purpose
`ResyncSessionStoreMsg` transfers a serialized session store as extra stream data after a small header payload that announces the buffer size.

### Important APIs, Types, And Functions
The class derives from `NetMessageSerdes<ResyncSessionStoreMsg>` with `NETMSGTYPE_ResyncSessionStore`. Serialization writes only `sessionStoreBufSize`. `registerStreamoutHook()` installs `streamToSocketFn()` into `RequestResponseArgs` to send the actual buffer. `receiveStoreBuf()` allocates a buffer and reads exactly `sessionStoreBufSize` bytes with a timeout.

### Control Flow
The normal send path serializes the size, then the request/response framework calls the extra-data hook to stream the buffer. The receive path deserializes the size first, then explicitly receives the store bytes from the socket.

### State, Persistence, And Dependencies
The message owns deserialized storage through `parsed.sessionStoreBuf`; send-side memory is non-owned. The payload represents persistent session state to restore on a buddy or resync target. Dependencies include `MessagingTk`, `Socket`, and exact-timeout receive helpers.

### Integration Points
Metadata resync uses it when synchronizing open/session state between buddies.

### Risks
`streamToSocketFn()` does not verify that `send()` wrote the full buffer beyond relying on socket semantics/exceptions. `receiveStoreBuf()` allocates based on wire size, so receiver-side size limits must exist in handlers. Tests should cover zero-size stores, allocation failure, short reads, timeout behavior, and extra-data hook registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/mirroring/ResyncSessionStoreMsg.h -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/mirroring/SetLastBuddyCommOverrideMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/storage/mirroring/SetLastBuddyCommOverrideMsg.h

### Purpose
`SetLastBuddyCommOverrideMsg` asks a storage node to override the recorded last communication timestamp for a buddy target, optionally aborting a running resync so it restarts from the new timestamp state.

### Important APIs, Types, And Functions
It derives from `NetMessageSerdes<SetLastBuddyCommOverrideMsg>` with type `NETMSGTYPE_SetLastBuddyCommOverride`. Serialization writes `targetID`, `timestamp`, and `abortResync`. Getters expose all three fields.

### Control Flow
The message is constructed with all required fields, then receiver logic applies the timestamp override and abort decision.

### State, Persistence, And Dependencies
The message is transient, but it updates persistent resync timestamp state on the receiver. It depends on NetMessage serdes and storage resync policy outside this file.

### Integration Points
Management tools or recovery code use it to force resync windows for buddy targets.

### Risks
Incorrect timestamps can skip required resync work or cause excessive resync. Abort semantics must coordinate with running jobs. Tests should cover timestamp round-trip, abort true/false, unknown target IDs, and active-resync restart behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/mirroring/SetLastBuddyCommOverrideMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/mirroring/SetLastBuddyCommOverrideRespMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/storage/mirroring/SetLastBuddyCommOverrideRespMsg.h

### Purpose
`SetLastBuddyCommOverrideRespMsg` returns the result of a last-buddy-communication override request.

### Important APIs, Types, And Functions
It subclasses `SimpleIntMsg` with type `NETMSGTYPE_SetLastBuddyCommOverrideResp`; `getResult()` casts to `FhgfsOpsErr`.

### Control Flow
Single integer result serialization is inherited.

### State, Persistence, And Dependencies
No state persists in the response. It depends on simple-message serialization and BeeGFS error codes.

### Integration Points
The management/recovery caller uses this to confirm whether the timestamp override and optional abort were accepted.

### Risks
No detail is included about whether an abort actually interrupted a job versus no job existing. Tests should cover success, invalid target, and permission/communication-style failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/mirroring/SetLastBuddyCommOverrideRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/mirroring/SetMetadataMirroringMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/storage/mirroring/SetMetadataMirroringMsg.h

### Purpose
`SetMetadataMirroringMsg` is a payload-free request to enable metadata mirroring on the root directory.

### Important APIs, Types, And Functions
It subclasses `SimpleMsg` and uses message type `NETMSGTYPE_SetMetadataMirroring`.

### Control Flow
All behavior is inherited header-only message handling; receiver code performs the root metadata update.

### State, Persistence, And Dependencies
The message has no payload, but the handler changes persistent metadata mirroring state. It includes `EntryInfo` and `Common.h`, though the class itself only needs `SimpleMsg`.

### Integration Points
Management tooling sends this when enabling metadata mirroring for the filesystem root.

### Risks
Because the request has no body, all context and authorization must come from connection/session state. Tests should verify handler idempotence, already-enabled behavior, and response error mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/mirroring/SetMetadataMirroringMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/mirroring/SetMetadataMirroringRespMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/storage/mirroring/SetMetadataMirroringRespMsg.h

### Purpose
`SetMetadataMirroringRespMsg` returns the result of enabling metadata mirroring.

### Important APIs, Types, And Functions
It subclasses `SimpleIntMsg` with type `NETMSGTYPE_SetMetadataMirroringResp`; `getResult()` casts to `FhgfsOpsErr`.

### Control Flow
The response is a simple status payload.

### State, Persistence, And Dependencies
No response state persists. It depends on `StorageErrors` and simple-message wrappers.

### Integration Points
Management code consumes this after sending `SetMetadataMirroringMsg`.

### Risks
Only a result code is available, so detailed migration state must be logged or queried separately. Tests should cover success, already mirrored, not-owner, and internal-error cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/mirroring/SetMetadataMirroringRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/mirroring/StorageResyncStartedMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/storage/mirroring/StorageResyncStartedMsg.h

### Purpose
`StorageResyncStartedMsg` notifies another component that storage resync has started for a buddy target.

### Important APIs, Types, And Functions
It subclasses `SimpleUInt16Msg` with type `NETMSGTYPE_StorageResyncStarted`; the payload is the buddy target ID.

### Control Flow
Senders construct with a `buddyTargetID`; receivers read the inherited uint16 payload.

### State, Persistence, And Dependencies
The message is transient notification state. It depends on `SimpleUInt16Msg`.

### Integration Points
Storage resync coordination and management state machines use it to synchronize resync lifecycle transitions.

### Risks
The class does not provide a named getter, so callers use inherited `getValue()` or message-specific handling. Tests should cover target-ID round-trip and paired acknowledgement behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/mirroring/StorageResyncStartedMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/mirroring/StorageResyncStartedRespMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/storage/mirroring/StorageResyncStartedRespMsg.h

### Purpose
`StorageResyncStartedRespMsg` is an empty acknowledgement for `StorageResyncStartedMsg`.

### Important APIs, Types, And Functions
It subclasses `SimpleMsg` with type `NETMSGTYPE_StorageResyncStartedResp`.

### Control Flow
There is no payload-specific control flow.

### State, Persistence, And Dependencies
The message has no state and depends only on simple-message handling.

### Integration Points
It completes the resync-start notification handshake.

### Risks
It carries no status; failure must be represented by missing/failed response at the communication layer. Tests should verify dispatch and timeout handling by callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/mirroring/StorageResyncStartedRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/moving/MovingDirInsertMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/storage/moving/MovingDirInsertMsg.h

### Purpose
`MovingDirInsertMsg` inserts a serialized directory entry/link into a destination directory during cross-directory or cross-node rename/move handling, with support for buddy-mirror second-phase timestamps.

### Important APIs, Types, And Functions
It derives from `MirroredMessageBase<MovingDirInsertMsg>` with `NETMSGTYPE_MovingDirInsert`. Serialization writes destination `EntryInfo`, aligned new name, serialized buffer length, raw serialized buffer, and optional `dirTimestamps` when `Flag_BuddyMirrorSecond` is set. `supportsMirroring()` returns true.

### Control Flow
Senders provide destination directory info and a non-owned serialized directory-link buffer. Receivers deserialize the destination info and raw buffer, then perform insertion.

### State, Persistence, And Dependencies
The message is transient but creates persistent namespace metadata at the destination. It depends on `EntryInfo`, `StatData`, mirrored timestamps, and raw-block serdes.

### Integration Points
Rename/move workflows use it when the target directory is handled by a different metadata node or when replaying mirrored operations.

### Risks
Serialized buffer validity is trusted by downstream code; length and pointer must be correct. Buddy second-phase timestamp handling must match primary-side changes. Tests should cover normal insert, buddy-secondary insert, zero-length/invalid buffers, and overwritten/duplicate target-name behavior in handlers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/moving/MovingDirInsertMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/moving/MovingDirInsertRespMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/storage/moving/MovingDirInsertRespMsg.h

### Purpose
`MovingDirInsertRespMsg` returns the result of inserting a moved directory entry.

### Important APIs, Types, And Functions
It subclasses `SimpleIntMsg` with `NETMSGTYPE_MovingDirInsertResp`; `getResult()` casts to `FhgfsOpsErr`.

### Control Flow
Single-result-code serialization is inherited.

### State, Persistence, And Dependencies
No response state persists. It depends on simple-message serialization and storage error conventions.

### Integration Points
Move/rename orchestration consumes this to decide whether source-side cleanup can continue.

### Risks
It does not include conflict detail or overwritten metadata. Tests should cover success, exists/conflict, not-owner, and communication failure handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/moving/MovingDirInsertRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/moving/MovingFileInsertMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/storage/moving/MovingFileInsertMsg.h

### Purpose
`MovingFileInsertMsg` tells a remote metadata server to insert a moved file into a destination directory. It carries source file info, destination directory info, new name, serialized file metadata, optional streamed xattrs, and buddy-mirror timestamps.

### Important APIs, Types, And Functions
It derives from `MirroredMessageBase<MovingFileInsertMsg>` with `NETMSGTYPE_MovingFileInsert`. The feature flag `MOVINGFILEINSERTMSG_FLAG_HAS_XATTRS` enables an extra xattr stream via `registerStreamoutHook()`. Serialization writes source/destination `EntryInfo`, aligned name, raw serialized inode buffer, and optional dir/file timestamps for buddy second-phase replay.

### Control Flow
The core message sends metadata in the normal payload. When xattrs are present, the request/response framework streams extra data through `MsgHelperXAttr::StreamXAttrState::streamXattrFn`.

### State, Persistence, And Dependencies
The message is transient but creates or replaces persistent file metadata at the destination. Dependencies include `EntryInfo`, `MessagingTk`, `MsgHelperXAttr`, and mirrored timestamps.

### Integration Points
Cross-directory rename/move logic, metadata migration, and buddy mirroring consume this message.

### Risks
The serialized inode buffer and xattr extra stream must stay consistent; a receiver that sees the feature flag must read the extra data exactly once. Non-owned pointers require send-side lifetime. Tests should cover moves with/without xattrs, buddy-secondary replay, overwrite cases, malformed buffer lengths, and stream failures after payload delivery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/moving/MovingFileInsertMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/moving/MovingFileInsertRespMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/storage/moving/MovingFileInsertRespMsg.h

### Purpose
`MovingFileInsertRespMsg` returns the result of a moved-file insertion and, if a destination entry was overwritten, returns the overwritten inode buffer and entry info.

### Important APIs, Types, And Functions
It derives from `NetMessageSerdes<MovingFileInsertRespMsg>` with `NETMSGTYPE_MovingFileInsertResp`. Serialization writes `result`, `inodeBufLen`, raw `inodeBuf`, and `overWrittenEntryInfo`.

### Control Flow
Senders provide result plus optional overwritten inode data. Receivers inspect `inodeBufLen` to determine whether an overwritten file exists.

### State, Persistence, And Dependencies
The response is transient but can carry serialized metadata needed for cleanup or rollback. It depends on `EntryInfo`, raw-block serdes, and storage error codes.

### Integration Points
Rename/move orchestration uses it after remote insertion to handle replaced files and source-side finalization.

### Risks
If `inodeBufLen` and `inodeBuf` disagree, serialization can read invalid memory. The overwritten `EntryInfo` is documented as default/unused when no overwrite occurred but is always serialized. Tests should cover no-overwrite, overwrite with inode buffer, error result with/without buffer, and deserialization of zero-length raw blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/moving/MovingFileInsertRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/moving/RenameMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/storage/moving/RenameMsg.h

### Purpose
`RenameMsg` requests a metadata rename from one directory/name to another, carrying entry type, optional file-event logging data, and buddy-mirror second-phase timestamps.

### Important APIs, Types, And Functions
The class derives from `MirroredMessageBase<RenameMsg>` with `NETMSGTYPE_Rename`. The header feature flag `RENAMEMSG_FLAG_HAS_EVENT` gates `FileEvent` serialization. The payload contains `DirEntryType`, source/destination `EntryInfo`, old/new names, optional event, and optional mirrored timestamps for source directory and renamed inode. `supportsMirroring()` returns true.

### Control Flow
Serialization always writes entry type and directory/name fields. Optional event and buddy-secondary timestamp sections are written only when their flags are present.

### State, Persistence, And Dependencies
The message is transient but triggers persistent namespace and inode timestamp changes. Dependencies include `EntryInfo`, `FileEvent`, `StatData`, and mirrored-message infrastructure.

### Integration Points
Client metadata rename operations and mirrored replay paths use this request.

### Risks
Source and destination directory info are non-owned on send. Event flag mismatches can shift the wire layout. Buddy-second timestamp replay must be exact for mirror consistency. Tests should cover same-directory rename, cross-directory rename, file and directory entry types, event/no-event cases, buddy-secondary replay, and conflict/error responses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/moving/RenameMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/moving/RenameRespMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/storage/moving/RenameRespMsg.h

### Purpose
`RenameRespMsg` returns the integer result of a metadata rename operation.

### Important APIs, Types, And Functions
It subclasses `SimpleIntMsg` with `NETMSGTYPE_RenameResp`. Unlike several neighboring response wrappers, it does not add a `getResult()` cast helper.

### Control Flow
Serialization is inherited single-integer behavior.

### State, Persistence, And Dependencies
The message has no persistent state. It depends on `SimpleIntMsg` and caller knowledge of the result-code convention.

### Integration Points
Rename callers consume this response after `RenameMsg`.

### Risks
Callers must use `getValue()` or inherited APIs and cast consistently to `FhgfsOpsErr`. Tests should cover representative success and failure result codes and ensure callers do not assume extra overwrite metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/moving/RenameRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/quota/GetDefaultQuotaMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/storage/quota/GetDefaultQuotaMsg.h

### Purpose
`GetDefaultQuotaMsg` requests default quota limits for a specific storage pool.

### Important APIs, Types, And Functions
It derives from `NetMessageSerdes<GetDefaultQuotaMsg>` with `NETMSGTYPE_GetDefaultQuota`; serialization writes `StoragePoolId storagePoolId`.

### Control Flow
The send constructor sets the pool ID. The no-arg constructor supports deserialization.

### State, Persistence, And Dependencies
The message is transient and depends on `StoragePoolId` and NetMessage serdes.

### Integration Points
Management quota tools send it to retrieve default user/group quota limits for a pool.

### Risks
There is no public getter in this base header, so handlers may rely on protected access through subclassing/friend context or direct deserialization conventions. Tests should verify pool ID round-trip, invalid pool handling, and paired response behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/quota/GetDefaultQuotaMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/quota/GetDefaultQuotaRespMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/storage/quota/GetDefaultQuotaRespMsg.h

### Purpose
`GetDefaultQuotaRespMsg` returns the default quota limits for a storage pool.

### Important APIs, Types, And Functions
It derives from `NetMessageSerdes<GetDefaultQuotaRespMsg>` with `NETMSGTYPE_GetDefaultQuotaResp`. Serialization writes a `QuotaDefaultLimits` object. `getDefaultLimits()` returns the parsed mutable reference.

### Control Flow
The response either default-constructs for deserialization or copies provided default limits for sending.

### State, Persistence, And Dependencies
The message is a transient snapshot of quota configuration. It depends on `QuotaDefaultLimits`.

### Integration Points
Quota management code uses it after `GetDefaultQuotaMsg` to display or validate defaults.

### Risks
No explicit result/error field is included; errors must be represented by communication failure or encoded defaults elsewhere. Tests should cover user/group defaults, unlimited values, and invalid storage-pool handling in the surrounding request path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/quota/GetDefaultQuotaRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/quota/GetQuotaInfoMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/storage/quota/GetQuotaInfoMsg.h

### Purpose
`GetQuotaInfoMsg` requests quota data for users or groups, scoped by query shape, target-selection mode, and storage pool.

### Important APIs, Types, And Functions
It derives from `NetMessageSerdes<GetQuotaInfoMsg>` with type `NETMSGTYPE_GetQuotaInfo`. `QuotaQueryType` covers none, single ID, ID range, ID list, and all IDs. Serialization writes query type and quota data type, then conditionally writes range/list/single-ID payload, followed by target selection, target ID, and `StoragePoolId`. Setter methods configure the query and target-selection modes.

### Control Flow
Handlers read `queryType` first to decide which ID field to consume. Target-selection values come from `GetQuotaConfig` constants and can request one target, one request per target, or all targets in one request.

### State, Persistence, And Dependencies
The message is transient. It depends on quota data enums, storage-pool IDs, management/storage target selection conventions, and NetMessage serdes.

### Integration Points
Management tools and quota collectors use this for quota scans, user/group lookups, and per-target storage quota retrieval.

### Risks
The constructor does not initialize `queryType`, `idRangeStart`, or `idRangeEnd`; callers must set a query before sending. ID-list size limits are not enforced in this header. Tests should cover every query type, target-selection setter, uninitialized/default construction safety, and payload limit behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/quota/GetQuotaInfoMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/quota/GetQuotaInfoRespMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/storage/quota/GetQuotaInfoRespMsg.h

### Purpose
`GetQuotaInfoRespMsg` returns quota data records and quota-inode support status.

### Important APIs, Types, And Functions
The class derives from `NetMessageSerdes<GetQuotaInfoRespMsg>` with `NETMSGTYPE_GetQuotaInfoResp`. It defines maximum payload-derived quota record counts. Serialization writes `quotaInodeSupport` and a backed `QuotaDataList`. Getters expose the data list and cast inode support to `QuotaInodeSupport`.

### Control Flow
Management-server responses can use `QuotaInodeSupport_UNKNOWN`; storage-server responses can set concrete support. Deserialization populates `parsed.quotaData`.

### State, Persistence, And Dependencies
The message is a transient quota snapshot. It depends on `QuotaData`, `Quota`, `NETMSG_MAX_PAYLOAD_SIZE`, and list serdes.

### Integration Points
Quota reporting, enforcement refresh, and management queries consume this response.

### Risks
Maximum record constants are advisory here; senders must enforce list sizing before serialization. The send-side list pointer is non-owned. Tests should cover empty lists, maximum-sized lists, inode-support states, and over-limit rejection in callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/quota/GetQuotaInfoRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/quota/RequestExceededQuotaMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/storage/quota/RequestExceededQuotaMsg.h

### Purpose
`RequestExceededQuotaMsg` asks for IDs that exceeded a specific quota type, either scoped by storage pool or by target ID.

### Important APIs, Types, And Functions
It derives from `NetMessageSerdes<RequestExceededQuotaMsg>` with `NETMSGTYPE_RequestExceededQuota`. Constructors set `QuotaDataType`, `QuotaLimitType`, `StoragePoolId`, and target ID variants. Serialization writes quota data type, exceeded type, storage pool ID, and target ID.

### Control Flow
The receiver interprets whether the request is pool-scoped or target-scoped based on the storage pool/target values. Getters cast integer enum fields back to quota types.

### State, Persistence, And Dependencies
The message is transient and depends on `StoragePoolStore`, `QuotaData`, and `StoragePoolId`.

### Integration Points
Quota enforcement and monitoring paths use it to query exceeded user/group IDs from management or storage components.

### Risks
Invalid combinations of storage pool and target ID are possible at the message level. Tests should cover pool-scoped and target-scoped constructors, invalid pool/target handling, and paired response list limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/quota/RequestExceededQuotaMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/quota/RequestExceededQuotaRespMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/storage/quota/RequestExceededQuotaRespMsg.h

### Purpose
`RequestExceededQuotaRespMsg` returns exceeded quota IDs using the same base payload shape as `SetExceededQuotaMsg`, plus an explicit error code.

### Important APIs, Types, And Functions
It subclasses `SetExceededQuotaMsg` but overrides payload serialization by defining `serializePayload()`, `deserializePayload()`, and a local static `serialize()` that serializes the base plus `error`. It reuses the base maximum-size constants.

### Control Flow
The base portion carries storage pool, quota data type, exceeded type, and ID list; the trailing `error` communicates whether the request succeeded. The default constructor uses message type `NETMSGTYPE_RequestExceededQuotaResp` and initializes error to `FhgfsOpsErr_INVAL`.

### State, Persistence, And Dependencies
The response is transient. It depends on `SetExceededQuotaMsg`, quota enums, and explicit serializer/deserializer override behavior.

### Integration Points
Quota query callers use it to receive exceeded IDs from stores while still getting request status.

### Risks
Subclassing a serdes message and overriding payload serialization is delicate; dispatch must use this class's serialize, not the base version. Tests should cover base-list round-trip, error-code round-trip, empty exceeded list, and payload-size limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/quota/RequestExceededQuotaRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/quota/SetDefaultQuotaMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/storage/quota/SetDefaultQuotaMsg.h

### Purpose
`SetDefaultQuotaMsg` sets default quota limits for a storage pool and quota data type.

### Important APIs, Types, And Functions
It derives from `NetMessageSerdes<SetDefaultQuotaMsg>` with `NETMSGTYPE_SetDefaultQuota`. Serialization writes `storagePoolId`, `size`, `inodes`, and integer `type`. Getters expose size, inodes, and quota data type.

### Control Flow
Senders construct with pool, type, size, and inode limits. The default constructor supports deserialization.

### State, Persistence, And Dependencies
The message is transient but updates persistent quota configuration on the receiver. It depends on `QuotaData` and `StoragePoolId`.

### Integration Points
Quota administration tools use it to change default user or group quota limits.

### Risks
There is no getter for `storagePoolId` in this header even though it is serialized. Unlimited/sentinel values must be interpreted consistently by handlers. Tests should cover user/group types, zero/unlimited values, invalid pool IDs, and response result handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/quota/SetDefaultQuotaMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/quota/SetDefaultQuotaRespMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/storage/quota/SetDefaultQuotaRespMsg.h

### Purpose
`SetDefaultQuotaRespMsg` returns the integer result of setting default quota limits.

### Important APIs, Types, And Functions
It subclasses `SimpleIntMsg` with `NETMSGTYPE_SetDefaultQuotaResp`.

### Control Flow
Single integer result serialization is inherited.

### State, Persistence, And Dependencies
The response has no persistent state and depends on simple-message behavior.

### Integration Points
Quota administration callers consume this after `SetDefaultQuotaMsg`.

### Risks
The class does not add a typed `getResult()` helper, so callers must use inherited `getValue()` consistently. Tests should cover success and common validation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/quota/SetDefaultQuotaRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/quota/SetExceededQuotaMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/storage/quota/SetExceededQuotaMsg.h

### Purpose
`SetExceededQuotaMsg` updates the set of quota IDs known to have exceeded a limit for a storage pool, data type, and limit type.

### Important APIs, Types, And Functions
It derives from `NetMessageSerdes<SetExceededQuotaMsg>` with type `NETMSGTYPE_SetExceededQuota`, and it also has constructors that allow subclasses to set a different message type. Serialization writes `storagePoolId`, `quotaDataType`, `exceededType`, and `UIntList exceededQuotaIDs`. Constants derive maximum ID counts from `NETMSG_MAX_PAYLOAD_SIZE`.

### Control Flow
Senders fill the exceeded ID list through `getExceededQuotaIDs()`. Receivers deserialize the same list and update quota state.

### State, Persistence, And Dependencies
The message is transient but updates persistent or cached quota-exceeded stores. It depends on `StoragePoolStore`, `QuotaData`, and list serdes.

### Integration Points
Management/storage quota synchronization uses this message, and `RequestExceededQuotaRespMsg` reuses it as a base payload.

### Risks
The ID list is mutable by pointer, so callers can exceed maximum advisory counts unless checked elsewhere. Subclass message-type constructors rely on the same layout. Tests should cover empty and max-sized lists, storage pool IDs, user/group and size/inode combinations, and subclass serialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/quota/SetExceededQuotaMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/quota/SetExceededQuotaRespMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/storage/quota/SetExceededQuotaRespMsg.h

### Purpose
`SetExceededQuotaRespMsg` returns the result of updating exceeded-quota state.

### Important APIs, Types, And Functions
It subclasses `SimpleIntMsg` with `NETMSGTYPE_SetExceededQuotaResp`.

### Control Flow
Only the integer result is serialized.

### State, Persistence, And Dependencies
The message has no persistent state. It depends on `SimpleIntMsg`.

### Integration Points
Quota synchronization callers use this after `SetExceededQuotaMsg`.

### Risks
No typed getter is provided. Tests should verify result-code handling, especially partial or validation failures in the receiver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/quota/SetExceededQuotaRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/quota/SetQuotaMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/storage/quota/SetQuotaMsg.h

### Purpose
`SetQuotaMsg` sends explicit quota limits for a storage pool as a list of `QuotaData` records.

### Important APIs, Types, And Functions
It derives from `NetMessageSerdes<SetQuotaMsg>` with `NETMSGTYPE_SetQuota`. Serialization writes `storagePoolId` and `QuotaDataList quotaData`. Constants estimate maximum quota records per payload. `insertQuotaLimit()` appends records, and getters expose the pool ID and data list.

### Control Flow
Senders construct with a storage pool ID and append quota records before sending. The protected default constructor supports deserialization through factories/subclasses.

### State, Persistence, And Dependencies
The message is transient but causes persistent quota limit updates. It depends on `QuotaData` and NetMessage payload sizing.

### Integration Points
Quota administration paths use it to update per-user or per-group quota limits.

### Risks
The header does not enforce maximum record count. The protected default constructor may require factory access. Tests should cover empty lists, max-sized lists, mixed user/group records if allowed by handlers, invalid pool IDs, and persistence confirmation via subsequent `GetQuotaInfoMsg`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/quota/SetQuotaMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/quota/SetQuotaRespMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/storage/quota/SetQuotaRespMsg.h

### Purpose
`SetQuotaRespMsg` returns the result of setting explicit quota limits.

### Important APIs, Types, And Functions
It subclasses `SimpleIntMsg` with type `NETMSGTYPE_SetQuotaResp`.

### Control Flow
The response uses inherited single-integer serialization.

### State, Persistence, And Dependencies
There is no persistent state in the response. It depends on simple message serialization.

### Integration Points
Quota administration tools consume it after `SetQuotaMsg`.

### Risks
No typed result getter is defined. Tests should cover result-code round-trip and caller casting to `FhgfsOpsErr`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/quota/SetQuotaRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/msghelpers/MsgHelperGenericDebug.cpp -->
## sources/distributed-fs/beegfs/common/source/common/net/msghelpers/MsgHelperGenericDebug.cpp

### Purpose
`MsgHelperGenericDebug.cpp` implements service debug operations for reading logs/config/load average, dropping caches, changing log levels, listing outbound connections, showing exceeded quota IDs, and listing target/storage-pool state.

### Important APIs, Types, And Functions
Public static handlers include `processOpVarLogMessages()`, `processOpVarLogKernLog()`, `processOpFhgfsLog()`, `processOpLoadAvg()`, `processOpDropCaches()`, `processOpGetLogLevel()`, `processOpSetLogLevel()`, `processOpCfgFile()`, `processOpNetOut()`, `processOpQuotaExceeded()`, `processOpListTargetStates()`, and `processOpListStoragePools()`. Helpers `loadTextFile()`, `writeTextFile()`, `printNodeStoreConns()`, and `printNodeConns()` do the concrete file and node formatting work.

### Control Flow
Most handlers parse arguments from an `istringstream`, perform a local operation, and return human-readable text. `loadTextFile()` stats the file, seeks to the last 100 KiB for large files, then reads bounded lines. `processOpSetLogLevel()` can update one log topic or all topics. Network output walks management/meta/storage node stores and prints connection counts plus first peer names. Quota output validates `uid/gid` and `size/inode` arguments before asking `ExceededQuotaStore`.

### State, Persistence, And Dependencies
This file can read sensitive local files and can write `/proc/sys/vm/drop_caches`. It mutates global logger levels and can trigger kernel cache dropping. Dependencies include `AbstractApp`, `PThread`, `System`, node stores, quota stores, `TargetStateStore`, `StoragePoolStore`, and `ZipIterator`.

### Integration Points
Generic debug messages call these handlers based on string operation names from `MsgHelperGenericDebug.h`. Admin/debug tooling receives the returned text.

### Risks
Debug operations are operationally powerful: reading logs/configs may expose sensitive data, setting log levels changes runtime behavior, and dropping caches requires privilege and affects performance. File reads are bounded but line truncation/read errors produce text responses rather than structured errors. Tests should cover argument parsing, bounded large-file reads, missing files, log-topic validation, quota argument validation, and connection formatting with zero/TCP/RDMA connections.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/msghelpers/MsgHelperGenericDebug.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/msghelpers/MsgHelperGenericDebug.h -->
## sources/distributed-fs/beegfs/common/source/common/net/msghelpers/MsgHelperGenericDebug.h

### Purpose
`MsgHelperGenericDebug.h` declares operation-string constants and static helpers for generic debug commands exposed over BeeGFS messages.

### Important APIs, Types, And Functions
It defines operation names such as `varlogmessages`, `beegfslog`, `dropcaches`, `getloglevel`, `setloglevel`, `net`, `quotaexceeded`, target-state listing, storage-pool listing, and rejection-rate control. The `MsgHelperGenericDebug` class declares public processors plus `loadTextFile()` and `writeTextFile()`.

### Control Flow
Callers dispatch on the operation string and call the corresponding static function with an argument stream and relevant stores. Private helpers format node stores and node connection state.

### State, Persistence, And Dependencies
The header has no state but exposes functions that can mutate runtime logger state or system cache state in the implementation. It depends on `NodeStoreServers`, `ExceededQuotaStore`, and common storage/target types.

### Integration Points
Generic debug message handlers include this header to map command strings to implementation functions.

### Risks
The command surface is stringly typed and security-sensitive. Tests should cover every operation constant's dispatch path and ensure unavailable stores produce clear responses rather than crashes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/msghelpers/MsgHelperGenericDebug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/sock/Channel.h -->
## sources/distributed-fs/beegfs/common/source/common/net/sock/Channel.h

### Purpose
`Channel` is the common pollable communication endpoint base, storing connection classification, activity, authentication, and peer node identity metadata.

### Important APIs, Types, And Functions
It derives from `Pollable`. State fields are `isDirect`, `hasActivity`, `isAuthenticated`, `NodeType nodeType`, and `NumNodeID nodeID`. Inline getters/setters expose direct-work status, idle/activity tracking, authentication, node type, and node ID.

### Control Flow
The protected constructor initializes channels as direct, active, unauthenticated, and with invalid node type. Worker/connection handling code toggles activity and authentication as messages are received.

### State, Persistence, And Dependencies
State is in-memory per connection and not persisted. It depends on `Pollable`, `NodeType`, and `NumNodeID`.

### Integration Points
`Socket` derives from `Channel`, so TCP/RDMA sockets inherit these flags. Worker pools and authentication handlers use them to manage routing and idle disconnects.

### Risks
The booleans are not internally synchronized; callers must respect owning-thread or external-lock assumptions. Tests should cover initial state, authentication transitions, activity reset/set behavior, and propagation through socket subclasses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/sock/Channel.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/sock/IPAddress.cpp -->
## sources/distributed-fs/beegfs/common/source/common/net/sock/IPAddress.cpp

### Purpose
`IPAddress.cpp` implements IPv4/IPv6 address normalization, resolution, string conversion, CIDR network matching, and socket-address conversion.

### Important APIs, Types, And Functions
`IPAddress::resolve()` uses `getaddrinfo()` and prefers IPv4 over IPv6. `setAddr()` accepts `sockaddr`, IPv4, IPv6, and uint128 values. Query methods detect zero, IPv4-mapped, IPv6, loopback, and link-local addresses. Conversion methods produce uint128, IPv4 `in_addr`, string form, and `SocketAddress`. Helpers `extractPort()` and `sockAddrLen()` inspect raw sockaddr values. `IPNetwork::fromCidr()` parses CIDR strings and `containsAddress()` tests prefix membership. `SocketAddress` converts between BeeGFS address objects and `sockaddr_in`/`sockaddr_in6`.

### Control Flow
IPv4 addresses are stored as IPv4-mapped IPv6 (`::ffff:a.b.c.d`) in a 16-byte array. Network containment first rejects IPv4/IPv6 family mismatch, then compares bytes and bits up to the prefix. CIDR parsing validates prefix length separately for IPv4 and IPv6.

### State, Persistence, And Dependencies
All state is value-object memory. Dependencies include `getaddrinfo`, `inet_pton`, `inet_ntop`, socket address structs, and BeeGFS `uint128_t`.

### Integration Points
Sockets, NIC discovery, routing, client-op reporting, and serialization all use this address abstraction.

### Risks
`IPAddress::resolve()` prefers IPv4 even on IPv6-capable hosts, which affects connection selection. `isLinkLocal()` compares bytes against constants and should be tested carefully for network-byte layout. `containsAddress()` indexes `addr[bytePos]` after a full match; identical addresses return before a differing byte is found only through loop completion logic, so boundary tests matter. Tests should cover IPv4/IPv6 round-trips, CIDR parsing errors, default networks, mapped IPv4 behavior, loopback/link-local detection, and socket-address conversions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/sock/IPAddress.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/sock/IPAddress.h -->
## sources/distributed-fs/beegfs/common/source/common/net/sock/IPAddress.h

### Purpose
`IPAddress.h` declares value types for normalized IP addresses, CIDR networks, network filters, and host/port socket addresses.

### Important APIs, Types, And Functions
`IPAddress` stores a 16-byte address, constructors accept IPv4, IPv6, sockaddr, sockaddr_storage, and uint128. It exposes family checks, loopback/link-local checks, conversions, comparisons, hashing, and string output. `IPNetwork` stores an address plus normalized prefix, with IPv4 prefixes shifted by 96 bits because IPv4 is mapped into IPv6 space. `SocketAddress` stores `IPAddress addr` and host-order `port`, with sockaddr conversion helpers.

### Control Flow
Most operations are value-object inline wrappers around implementation functions in the `.cpp`. Hash specialization allows `IPAddress` to key unordered maps.

### State, Persistence, And Dependencies
State is copied by value and not persisted. The header depends on system socket headers and BeeGFS `UInt128`.

### Integration Points
`NetworkInterfaceCard`, `RoutingTable`, `Socket`, `StandardSocket`, and `ClientOps` use these types for route matching, binding, peer naming, and client-ID conversion.

### Risks
IPv4 prefixes are internally offset by 96, so callers must use public constructors rather than directly reasoning about `getPrefix()` as a raw IPv4 prefix. `SocketAddress()` default construction is deleted, which requires immediate initialization. Tests should cover hash/equality, ordering, IPv4 prefix normalization, invalid prefixes, and string formatting with bracketed IPv6 ports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/sock/IPAddress.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/sock/NetworkInterfaceCard.cpp -->
## sources/distributed-fs/beegfs/common/source/common/net/sock/NetworkInterfaceCard.cpp

### Purpose
`NetworkInterfaceCard.cpp` discovers usable local network interfaces, applies allow/deny preference rules, detects RDMA capability, sorts NICs, and formats NIC data.

### Important APIs, Types, And Functions
`findNicPosition()` matches preference rows against interface name, IP, protocol family, and type (`tcp`/`rdma`), with `!` rows acting as blacklists. `findAll()` discovers standard interfaces and optionally appends RDMA-capable variants. `findAllInterfaces()` wraps `getifaddrs()`, skips loopback/down/non-IP/link-local entries, honors IPv6 disablement, and applies allowed-interface filters. `filterInterfacesForRDMA()` and `checkAndAddRdmaCapability()` bind test RDMA sockets to candidate IPs. `NicAddrComp` sorts by preferences, then RDMA, IPv4, and IP order. Formatting and capability helpers expose type strings and RDMA support.

### Control Flow
Interface discovery first builds TCP candidates, then RDMA probing clones candidates as RDMA NICs when `RDMASocket` can bind. Preference matching can include wildcards and escaped literal `*`/`!` names; blacklist rows return `-1` immediately.

### State, Persistence, And Dependencies
There is no persistent state. Dependencies include `getifaddrs`, `ifaddrs`, `RDMASocket`, `LogContext`, `System`, `StringTk`, and BeeGFS NIC serialization types.

### Integration Points
Local node startup, connection-pool setup, route selection, and node serialization use discovered `NicAddressList` values.

### Risks
`findNicPosition()` assumes split rows have at least one token; empty preference rows could be unsafe depending on `StringTk::explode()` behavior. RDMA detection catches `SocketException` and silently skips interfaces, so diagnostics can be limited. Sorting prefers RDMA and IPv4 after explicit preferences, affecting connection choices. Tests should cover allow/deny rows, escaped names, IPv6 disabled mode, link-local exclusion, RDMA probing success/failure, and sorting stability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/sock/NetworkInterfaceCard.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/sock/NetworkInterfaceCard.h -->
## sources/distributed-fs/beegfs/common/source/common/net/sock/NetworkInterfaceCard.h

### Purpose
`NetworkInterfaceCard.h` defines NIC address data structures, serialization, list types, preference helpers, and the interface-discovery API.

### Important APIs, Types, And Functions
`NicAddrType` distinguishes standard TCP and RDMA NICs. `NicAddress` stores `IPAddress`, NIC type, interface name, and protocol version, with custom serializer/deserializer that preserves IPv4/IPv6 payloads and fixed-size names. `NicAddressList` is a list wrapper. `serdesNicAddressList()` provides backed-pointer serialization. `NetworkInterfaceCard` declares discovery, formatting, RDMA capability, and sorting helpers.

### Control Flow
NIC list deserialization reads serialized length/count, deserializes each `NicAddress`, and redirects the pointer to backing storage. `NicAddress::serialize()` writes protocol first, then either IPv4 or 16-byte IPv6 address, fixed name, type, and padding.

### State, Persistence, And Dependencies
State is value/list data exchanged over the wire in node descriptions. Dependencies include `IPAddress`, BeeGFS serialization, and system `IFNAMSIZ`.

### Integration Points
Node serialization, connection pools, route matching, and management node stores rely on `NicAddressList`.

### Risks
The deserializer reads `nicListLength` but does not validate it against count in this helper. Protocol values other than `4` are treated as IPv6. Tests should cover IPv4/IPv6 NIC serialization, fixed-name truncation/null termination, RDMA type preservation, and list length/count mismatch handling by the broader serialization layer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/sock/NetworkInterfaceCard.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/sock/PooledSocket.h -->
## sources/distributed-fs/beegfs/common/source/common/net/sock/PooledSocket.h

### Purpose
`PooledSocket` extends `Socket` with connection-pool bookkeeping: availability, close-on-release, and optional expiration timing.

### Important APIs, Types, And Functions
It derives from `Socket`. Methods include `isAvailable()`, `setAvailable()`, `setExpireTimeStart()`, `getHasExpirationTimer()`, `isCloseOnRelease()`, `setCloseOnRelease()`, and `getHasExpired(expireSecs)`.

### Control Flow
Connection pools mark sockets unavailable on acquire and available on release. Expiration is inactive when `expireTimeStart` is zero; otherwise elapsed time is compared with `expireSecs`.

### State, Persistence, And Dependencies
State is in-memory per pooled connection. It depends on `Socket` and `Time`.

### Integration Points
`NodeConnPool`, `LocalNodeConnPool`, `StandardSocket`, and `RDMASocket` use this as the common pooled socket base.

### Risks
No internal locking is present, so pool code must synchronize access. Expiration uses seconds converted to milliseconds and can overflow if huge values are passed. Tests should cover availability transitions, close-on-release behavior, expiration disabled/enabled, and pool synchronization around these flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/sock/PooledSocket.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/sock/RDMASocket.cpp -->
## sources/distributed-fs/beegfs/common/source/common/net/sock/RDMASocket.cpp

### Purpose
`RDMASocket.cpp` dynamically loads the BeeGFS RDMA socket implementation from `libbeegfs_ib.so` and exposes availability, device detection, fork initialization, and socket creation through callback pointers.

### Important APIs, Types, And Functions
An internal `IBLibLoader` calls `dlopen("libbeegfs_ib.so", RTLD_NOW)` at startup and looks up `beegfs_socket_impl` with `dlsym()`. Public methods `isRDMAAvailable()`, `rdmaDevicesExist()`, `rdmaForkInitOnce()`, and `create()` delegate to loaded callbacks.

### Control Flow
If the shared library cannot load or lacks the callback symbol, RDMA remains unavailable. `create()` throws `std::logic_error` when called without a loaded implementation.

### State, Persistence, And Dependencies
The static loader owns the dynamic-library handle until process exit. Dependencies include `dlfcn.h` and the ABI contract of `RDMASocket::ImplCallbacks`.

### Integration Points
NIC discovery probes RDMA availability through this file, and connection pools create RDMA sockets through the callback interface.

### Risks
ABI mismatch in `beegfs_socket_impl` can crash at callback use. Startup-time loading means environment/library path issues decide RDMA support globally. Tests should cover missing library, missing symbol, callback success, create-without-support exception, and device-detection false/true cases using a test shim.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/sock/RDMASocket.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/sock/RDMASocket.h -->
## sources/distributed-fs/beegfs/common/source/common/net/sock/RDMASocket.h

### Purpose
`RDMASocket.h` defines the abstract RDMA socket interface and the dynamic implementation callback table.

### Important APIs, Types, And Functions
`RDMASocket` derives from `PooledSocket`. `ImplCallbacks` contains function pointers for device existence, fork initialization, and socket creation. Static methods report availability and create instances. Pure virtual RDMA-specific APIs include connection checks, nonblocking receive checks, delayed event checks, buffer/timeouts/type-of-service configuration, and connection rejection-rate configuration.

### Control Flow
Concrete implementations are supplied by the dynamically loaded RDMA library. Callers should check availability before `create()` unless they are prepared for exceptions.

### State, Persistence, And Dependencies
The header holds no state; concrete RDMA implementations hold connection state. It depends on `PooledSocket`.

### Integration Points
Connection pools use this interface polymorphically with `StandardSocket`. Debug code can adjust rejection rates through the virtual API.

### Risks
The interface is an ABI boundary with `libbeegfs_ib.so`; changes require coordinated library updates. Tests should validate every callback path and polymorphic behavior expected by `NodeConnPool`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/sock/RDMASocket.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/sock/RoutingTable.cpp -->
## sources/distributed-fs/beegfs/common/source/common/net/sock/RoutingTable.cpp

### Purpose
`RoutingTable.cpp` queries the OS routing table through libnl3, builds immutable destination-network-to-source-address mappings, and matches peer addresses to the best local NIC source address.

### Important APIs, Types, And Functions
`Destnet` stores an `IPNetwork` and source IP set. `RoutingTableQuery` abstracts route collection, with `Nl3RouteQuery` implementing libnl3 route/address cache access. `populateInterfaces()` maps interface indices to local IPs. `populateDestnetMap()` walks unicast routes, using preferred source addresses when present or nexthop interface addresses otherwise. `RoutingTable::match()` checks non-default routes first, then a default route unless blocked by `noDefaultRouteNets`. `loadIpSourceMap()` builds peer-to-source maps. `RoutingTableFactory::init()`, `load()`, and `create()` manage shared route snapshots.

### Control Flow
Factory `load()` creates a query, initializes libnl caches, builds a fresh `DestnetMap`, and swaps it in only when changed. Created `RoutingTable` instances hold shared immutable snapshots for thread-safe reads. Matching iterates routes, remembers a default route, and uses local NIC preference order to select a source address.

### State, Persistence, And Dependencies
Route data is cached in shared pointers and guarded by `destnetsMutex` during factory updates. No data is persisted. Dependencies include libnl3 route/address APIs, `IPAddress`, `IPNetwork`, `NetworkInterfaceCard`, logging, and BeeGFS exception macros.

### Integration Points
Connection pools and node route setup use routing tables to choose local source IPs for peer NICs.

### Risks
Route iteration order in an unordered map can affect which overlapping non-default route is considered first; longest-prefix selection is not explicit here. Some `if ((rc = call(...) != 0))` expressions assign boolean results instead of raw error codes, reducing diagnostics. Default-route filtering depends on `noDefaultRouteNets`. Tests should cover overlapping routes, preferred-source routes, nexthop-derived sources, IPv4/IPv6 separation, no-default-route filters, route reload change detection, and empty-route logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/sock/RoutingTable.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/sock/RoutingTable.h -->
## sources/distributed-fs/beegfs/common/source/common/net/sock/RoutingTable.h

### Purpose
`RoutingTable.h` declares immutable routing-table snapshots and the factory that loads them from the operating system.

### Important APIs, Types, And Functions
It defines `RoutingTableException`, `DestnetMap`, and `IpSourceMap`. `RoutingTable::match()` finds a source address for a destination and candidate local NIC list. `loadIpSourceMap()` computes a map for many peer NICs. `RoutingTableFactory` provides `init()`, `load()`, and `create()`.

### Control Flow
Public `RoutingTable` methods are const to support thread-safe immutable snapshots. The factory is mutable and synchronized around the current `DestnetMap`.

### State, Persistence, And Dependencies
`RoutingTable` holds shared pointers to const route data and optional default-route exclusion networks. The factory caches mutable route data in memory. Dependencies include `NetworkInterfaceCard`, `IPAddress`, mutexes, and standard maps.

### Integration Points
Networking setup code uses the factory to refresh OS routes and distribute snapshots to connection-selection code.

### Risks
Callers must call `RoutingTableFactory::init()` and `load()` before `create()`, and a default-constructed `RoutingTable` throws if used uninitialized. Tests should cover initialization ordering, thread-safe create/load behavior, and matching with empty/local NIC lists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/sock/RoutingTable.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/sock/Socket.cpp -->
## sources/distributed-fs/beegfs/common/source/common/net/sock/Socket.cpp

### Purpose
`Socket.cpp` implements common socket base behavior: hostname connection resolution, wildcard binding, dummy stats setup, and global IPv6 capability detection/caching.

### Important APIs, Types, And Functions
`Socket::connect(hostname, port, ai_socktype)` resolves hostnames with `getaddrinfo()`, selects IPv4 or IPv6 based on cached IPv6 availability, formats `peername`, and delegates to `connect(SocketAddress)`. `bind(port)` binds to zero-address plus port. `checkAndCacheIPv6Availability()` probes IPv6 socket creation, loopback connect behavior, and dual-stack support; `isIPv6Available()` returns the cached value.

### Control Flow
Callers must initialize IPv6 availability before constructing code paths that call `isIPv6Available()`. Hostname connect sets canonical peer names and brackets IPv6 literal peer names. IPv6 probing honors explicit config disablement and logs fallback reasons.

### State, Persistence, And Dependencies
`dummyStats` is static fallback stats storage. `ipv6Available` is a static atomic optional cache. Dependencies include `getaddrinfo`, socket syscalls, `IPAddress`, logging, and BeeGFS config access.

### Integration Points
`StandardSocket` and RDMA/socket subclasses inherit this behavior. Startup code should call `checkAndCacheIPv6Availability()` before socket creation.

### Risks
`Socket::connect()` frees `addressList` before constructing `SocketAddress` from `addrSelected->ai_addr`, leaving `addrSelected` pointing into freed memory; this is a notable lifetime risk unless allocator behavior masks it. `isIPv6Available()` throws if the cache was not initialized. Tests should cover IPv6 disabled/unavailable/dual-stack cases, hostname IPv4/IPv6 resolution, peername formatting, and the address-list lifetime path under sanitizers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/sock/Socket.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/sock/Socket.h -->
## sources/distributed-fs/beegfs/common/source/common/net/sock/Socket.h

### Purpose
`Socket.h` defines the abstract socket interface used by BeeGFS networking, covering connection setup, binding/listening/accepting, shutdown, send/receive, optional NVFS RDMA read/write, exact/min-max receive helpers, stats, and addressing metadata.

### Important APIs, Types, And Functions
Pure virtual methods define `connect()`, `bindToAddr()`, `listen()`, `accept()`, `shutdown()`, `shutdownAndRecvDisconnect()`, `send()`, `sendto()`, `recv()`, and `recvT()`. Inline helpers `recvExact()`, `recvExactT()`, `recvMinMax()`, and `recvMinMaxT()` repeatedly call receive methods until length conditions are met. Static methods manage IPv6 availability.

### Control Flow
Subclasses implement raw transport behavior while the base tracks stats pointer, socket type, peer/bind IPs, bind port, and peer name. Exact/min-max receive loops depend on subclass receive calls throwing on disconnect rather than returning negative values.

### State, Persistence, And Dependencies
State is per socket and in-memory only. It depends on `Channel`, `NetworkInterfaceCard`, `IPAddress`, `HighResolutionStats`, `Time`, and socket exception subclasses.

### Integration Points
`StandardSocket`, `RDMASocket`, `PooledSocket`, and connection pools use this as their common interface.

### Risks
Exact receive helpers can loop forever if a subclass returns zero without throwing for stream sockets. Stats pointer is mutable and not owned. Tests should cover helper loops, timeout behavior, stats incrementing in subclasses, and IPv6 initialization requirements.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/sock/Socket.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/sock/SocketConnectException.h -->
## sources/distributed-fs/beegfs/common/source/common/net/sock/SocketConnectException.h

### Purpose
`SocketConnectException.h` declares the named exception type for connection-establishment failures.

### Important APIs, Types, And Functions
It uses `DECLARE_NAMEDSUBEXCEPTION(SocketConnectException, "SocketConnectException", SocketException)`.

### Control Flow
Socket implementations throw this subclass for hostname resolution, connect timeout, and failed local socket-pair creation paths.

### State, Persistence, And Dependencies
There is no state beyond exception message data supplied by the macro base. It depends on `SocketException`.

### Integration Points
Connection pools catch this type to distinguish connect failures from established-connection disconnects.

### Risks
Tests should verify catch ordering, name string, and that connect failure paths throw this subclass rather than generic `SocketException`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/sock/SocketConnectException.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/sock/SocketDisconnectException.h -->
## sources/distributed-fs/beegfs/common/source/common/net/sock/SocketDisconnectException.h

### Purpose
`SocketDisconnectException.h` declares the named exception type for established-socket disconnects and send/receive hard failures.

### Important APIs, Types, And Functions
It uses `DECLARE_NAMEDSUBEXCEPTION(SocketDisconnectException, "SocketDisconnectException", SocketException)`.

### Control Flow
`StandardSocket::recv()`, `send()`, `sendto()`, and related methods throw this when peers disconnect or syscalls fail after connection setup.

### State, Persistence, And Dependencies
Only exception text is stored. It depends on `SocketException`.

### Integration Points
Connection pools and request/response code catch disconnects to invalidate sockets and retry as appropriate.

### Risks
Tests should distinguish soft disconnect, hard disconnect, and connect-time exceptions so retry logic invalidates the correct pool entry.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/sock/SocketDisconnectException.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/sock/SocketException.h -->
## sources/distributed-fs/beegfs/common/source/common/net/sock/SocketException.h

### Purpose
`SocketException.h` declares the base named exception for BeeGFS socket-layer errors.

### Important APIs, Types, And Functions
It uses `DECLARE_NAMEDEXCEPTION(SocketException, "SocketException")`.

### Control Flow
Socket implementations throw this for generic socket, epoll, bind, listen, shutdown, and option errors.

### State, Persistence, And Dependencies
Exception message state is handled by the macro-defined type. It depends on `NamedException`.

### Integration Points
All socket exception subclasses derive from this base, allowing broad socket error handling.

### Risks
Tests should ensure broad catches do not hide cases where callers need the more specific timeout/connect/disconnect subclasses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/sock/SocketException.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/sock/SocketInterruptedPollException.h -->
## sources/distributed-fs/beegfs/common/source/common/net/sock/SocketInterruptedPollException.h

### Purpose
`SocketInterruptedPollException.h` declares the exception used when blocking poll-style waits are interrupted.

### Important APIs, Types, And Functions
It uses `DECLARE_NAMEDSUBEXCEPTION(SocketInterruptedPollException, "SocketInterruptedPollException", SocketException)`.

### Control Flow
Polling helpers can throw this on `EINTR` when they choose not to retry internally.

### State, Persistence, And Dependencies
Only exception message state is carried. It depends on `SocketException`.

### Integration Points
Callers can catch this separately when interruption should be treated differently from timeout or disconnect.

### Risks
Some epoll loops retry `EINTR` internally, so behavior differs by API. Tests should cover `waitForIncomingData()` interruption and caller retry policy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/sock/SocketInterruptedPollException.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/sock/SocketTimeoutException.h -->
## sources/distributed-fs/beegfs/common/source/common/net/sock/SocketTimeoutException.h

### Purpose
`SocketTimeoutException.h` declares the socket timeout exception type.

### Important APIs, Types, And Functions
It uses `DECLARE_NAMEDSUBEXCEPTION(SocketTimeoutException, "SocketTimeoutException", SocketException)`.

### Control Flow
Timed receive methods throw this when epoll waits expire without input.

### State, Persistence, And Dependencies
Only exception message state is carried. It depends on `SocketException`.

### Integration Points
Request/response and connection-pool code catch timeouts to fail, retry, or mark peers as slow without conflating them with disconnects.

### Risks
Tests should confirm timeout exceptions are used by `recvT()`/`recvfromT()` and not by immediate nonblocking or connect timeout paths where `SocketConnectException` is expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/sock/SocketTimeoutException.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/sock/StandardSocket.cpp -->
## sources/distributed-fs/beegfs/common/source/common/net/sock/StandardSocket.cpp

### Purpose
`StandardSocket.cpp` implements TCP/UDP/UNIX-domain socket behavior for the BeeGFS socket abstraction, including IPv4/IPv6 creation, connect with timeout, bind/listen/accept, shutdown, send/receive, epoll-based timed receive, socket options, and grouped UDP epoll handling.

### Important APIs, Types, And Functions
Constructors create AF_INET6 dual-stack sockets when available, otherwise AF_INET sockets, and optionally add the socket to an epoll set. `createSocketPair()` builds local UNIX socket pairs. `connect()` performs nonblocking connect with poll timeout. `bindToAddr()`, `listen()`, and `accept()` wrap server-side setup. `send()` requires full-length writes. `sendto()` retries `EPERM` UDP sends with cooling sleeps and suppresses repeated `ENETUNREACH`. `recv()`, `recvT()`, `recvfrom()`, and `recvfromT()` handle blocking and epoll receive. Option setters configure keepalive, reuseaddr, receive buffer, TCP_NODELAY, and TCP_CORK. `StandardSocketGroup` lets one epoll parent wait on subordinate sockets.

### Control Flow
Timed receives wait on epoll, recover from `EINTR`, and dispatch to the socket pointer stored in epoll event data. Listening sockets close their epoll FD because timed receive is not used on them. Shutdown sends `SHUT_WR` then drains until disconnect for graceful close.

### State, Persistence, And Dependencies
State is the OS file descriptor, epoll FD, socket family, peer/bind metadata, random backoff generator, and subordinate sockets. Dependencies include Linux sockets, epoll, poll, TCP options, logging, `System`, `PThread` config, and `IPAddress`.

### Integration Points
`NodeConnPool`, UDP datagram paths, local worker sockets, and the generic `Socket` interface rely on this implementation for standard networking.

### Risks
`send()` treats partial stream writes as fatal rather than looping, so callers must pass sizes appropriate for blocking sockets. `sendto()` uses a static `netUnreachLogged` flag without synchronization. `connect()` restores original flags only on success paths, so failure paths rely on destruction or later cleanup. `addToEpoll()` closes `sock` and `epollFD` on failure even when adding a subordinate, which can affect the owning group. Tests should cover IPv4 fallback, dual-stack bind, connect timeout/refusal, partial send simulation, UDP EPERM retry and ENETUNREACH suppression, epoll timeout/EINTR/HUP/ERR paths, socket option errors, socket-pair cleanup, and subordinate group lifetime.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/sock/StandardSocket.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/sock/StandardSocket.h -->
## sources/distributed-fs/beegfs/common/source/common/net/sock/StandardSocket.h

### Purpose
`StandardSocket.h` declares the concrete non-RDMA socket implementation and a grouped socket variant for epoll over multiple subordinate sockets.

### Important APIs, Types, And Functions
`StandardSocket` derives from `PooledSocket` and implements all `Socket` operations, UDP `recvfrom` variants, socket-option setters, `getFD()`, and `getFamily()`. Inline `waitForIncomingData()` wraps `poll()` for POLLIN/error checks. `StandardSocketGroup` creates subordinate sockets and uses the parent epoll FD to receive from any of them.

### Control Flow
Constructors decide whether an epoll FD exists. Methods that require epoll reject non-epoll instances. Subordinate sockets are created without their own epoll and added to the group's epoll set.

### State, Persistence, And Dependencies
State includes raw FD, datagram flag, epoll FD, address family, and random generator. Dependencies include `PooledSocket`, `RandomReentrant`, `IPAddress`, and system poll/socket types.

### Integration Points
Connection pools instantiate `StandardSocket` for TCP/UDP communication. UDP listener code can use `StandardSocketGroup` to listen across multiple local addresses.

### Risks
Inline `waitForIncomingData()` throws on `EINTR` instead of retrying, unlike epoll receive methods. `StandardSocketGroup` relies on closing epoll before subordinate destruction to avoid stale event pointers. Tests should cover poll error flags, non-epoll receive misuse, group subordinate dispatch, and destructor cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/sock/StandardSocket.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/AbstractNodeStore.h -->
## sources/distributed-fs/beegfs/common/source/common/nodes/AbstractNodeStore.h

### Purpose
`AbstractNodeStore` defines the common interface for stores of BeeGFS nodes such as metadata, storage, management, and clients.

### Important APIs, Types, And Functions
It declares `NodeStoreResult` values `Unchanged`, `Added`, `Updated`, and `Error`. Virtual methods include `addOrUpdateNode()`, `addOrUpdateNodeEx()`, `referenceFirstNode()`, `referenceAllNodes()`, and `getSize()`. The protected `NodeMap` maps `NumNodeID` to `shared_ptr<Node>`.

### Control Flow
Concrete stores implement insertion/update semantics and reference retrieval. The protected constructor fixes the `NodeType` applied to contained nodes.

### State, Persistence, And Dependencies
The abstract base stores only `storeType`; concrete stores manage node maps. It depends on `Node`, `NumNodeID`, and shared pointer ownership.

### Integration Points
Messaging, management, heartbeat, and debug code interact with node stores through this abstraction.

### Risks
Reference-returning methods must define thread-safety and lifetime in concrete stores. Tests should cover concrete store add/update result transitions, first/all references, and type enforcement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/AbstractNodeStore.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/CapacityPoolType.h -->
## sources/distributed-fs/beegfs/common/source/common/nodes/CapacityPoolType.h

### Purpose
`CapacityPoolType.h` defines capacity pool categories used to classify targets or nodes by free capacity.

### Important APIs, Types, And Functions
`CapacityPoolType` enum values are `CapacityPool_NORMAL`, `CapacityPool_LOW`, `CapacityPool_EMERGENCY`, and sentinel `CapacityPool_END_DONTUSE`. The comment notes values are sequential and zero-based for array indexing.

### Control Flow
There is no control flow; consumers compare or index by enum values.

### State, Persistence, And Dependencies
No state or dependencies beyond the enum. Pool assignments may be persisted by other components.

### Integration Points
Dynamic pool limit logic, target capacity pools, and mirroring group mappers use these categories.

### Risks
Adding/reordering enum values can break array-indexed data structures and wire/storage compatibility. Tests should cover category calculations in `DynamicPoolLimits` and any serialization assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/CapacityPoolType.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/ClientOps.cpp -->
## sources/distributed-fs/beegfs/common/source/common/nodes/ClientOps.cpp

### Purpose
`ClientOps.cpp` stores per-client or per-user operation counters, computes deltas between snapshots, and requests client operation statistics from remote nodes using old and v2 protocol messages.

### Important APIs, Types, And Functions
`ClientOps::addOpsList()` validates counter-list sizes, sums per-ID and total counters, and stores absolute values. `sumOpsListValues()` uses `std::transform` and `sum`. `getDiffOpsMap()` compares current counters against `oldIdOpsMap`. `getDiffSumOpsList()` subtracts `oldSumOpsList` from `sumOpsList`. `clear()` swaps current maps/lists into old snapshots. `ClientOpsRequestor::request()` loops over `GetClientStatsMsg` or `GetClientStatsV2Msg` responses until `moreData` is false, validates layout version, and converts old IPv4 client IDs into the new uint128 IP representation.

### Control Flow
The requestor starts with current ID `~0`, sends paged stats requests, parses vector metadata (`moreData`, layout version, number of ops), then groups each ID plus `numOps` counters into the result map. Per-user requests preserve numeric IDs; per-client old protocol requests convert IPv4 network-order IDs through `IPAddress`.

### State, Persistence, And Dependencies
`ClientOps` keeps current and previous snapshots in memory under `idOpsMapMutex`. It depends on `MessagingTk`, `GetClientStats*` messages, `NodeOpStats`, `IPAddress`, and `uint128`.

### Integration Points
Monitoring and management code use this to report client/user operation rates rather than raw cumulative counters.

### Risks
`getDiffSumOpsList()` assumes `oldSumOpsList` is at least as long as `sumOpsList`; calling it before a valid old snapshot can be unsafe. Vector parsing uses `.at()` for header fields but relies on correct vector shape for grouped data. Tests should cover first snapshot behavior, size mismatches, paging, layout mismatch, v1 IPv4 conversion, v2 uint128 IDs, per-user mode, and counter wrap/underflow semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/ClientOps.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/ClientOps.h -->
## sources/distributed-fs/beegfs/common/source/common/nodes/ClientOps.h

### Purpose
`ClientOps.h` declares storage and request helpers for per-client/per-user operation statistics.

### Important APIs, Types, And Functions
`ClientOps` defines `OpsList` and `IdOpsMap`, exposes `addOpsList()`, diff getters, absolute getters, and `clear()`. Protected helpers define sum/diff arithmetic and hold current/old maps plus a mutex. `ClientOpsRequestor` defines `IdOpsUnorderedMap` and static `request(Node&, bool perUser, bool useClientStatsV2)`.

### Control Flow
Consumers add absolute lists during collection, read absolute or diff views, then call `clear()` to advance the baseline.

### State, Persistence, And Dependencies
State is in-memory snapshots only. Dependencies include `IPAddress`, `Node`, and `Mutex`.

### Integration Points
Management statistics code combines `ClientOpsRequestor` network collection with `ClientOps` diff calculations.

### Risks
The arithmetic helpers use unsigned function signatures while lists store `int64_t`, so type conversion should be tested for large values. Tests should cover snapshot lifecycle and concurrent add/clear access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/ClientOps.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/DynamicPoolLimits.cpp -->
## sources/distributed-fs/beegfs/common/source/common/nodes/DynamicPoolLimits.cpp

### Purpose
`DynamicPoolLimits.cpp` is present only to include `DynamicPoolLimits.h`; the class implementation is entirely inline in the header.

### Important APIs, Types, And Functions
No functions are defined in this translation unit.

### Control Flow
There is no runtime control flow here.

### State, Persistence, And Dependencies
No additional state beyond the inline header class.

### Integration Points
The file likely exists to satisfy build-system expectations for a corresponding source file.

### Risks
Behavioral tests belong to `DynamicPoolLimits.h`; build tests should ensure this empty translation unit remains harmless.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/DynamicPoolLimits.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/DynamicPoolLimits.h -->
## sources/distributed-fs/beegfs/common/source/common/nodes/DynamicPoolLimits.h

### Purpose
`DynamicPoolLimits` classifies free capacity into normal/low/emergency pools and determines whether dynamic demotion thresholds are active based on spread across targets.

### Important APIs, Types, And Functions
Constructor parameters set static low/emergency limits, spread thresholds, and dynamic demotion limits. Getters expose all thresholds. `getPoolTypeFromFreeCapacity()` classifies free capacity. `demotionActiveNormalPool()` and `demotionActiveLowPool()` compare min/max spread to thresholds. `demoteNormalToLow()` and `demoteLowToEmergency()` test dynamic limits.

### Control Flow
Capacity first maps to a base pool by comparing free space to low and emergency thresholds. Dynamic demotion only applies when spread exceeds the configured threshold for the current pool.

### State, Persistence, And Dependencies
All thresholds are immutable per instance. It depends on `MinMaxStore` and `CapacityPoolType`.

### Integration Points
Capacity-pool managers use it when assigning targets to pools and balancing across uneven free space.

### Risks
Boundary comparisons are strict `>` for base pools and `>` for spread activation; exact-threshold values demote differently than just-above values. Tests should cover all threshold boundaries, negative/free-space sentinel values if possible, and spread activation/demotion combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/DynamicPoolLimits.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/LocalNode.h -->
## sources/distributed-fs/beegfs/common/source/common/nodes/LocalNode.h

### Purpose
`LocalNode` represents the current service as a `Node` while using a special local connection pool for in-process/internal communication.

### Important APIs, Types, And Functions
It derives from `Node`. The constructor calls the protected `Node` constructor and installs a `LocalNodeConnPool`. `getPortTCP()` overrides the node TCP port to return `0`, reflecting internal local communication rather than a network stream port.

### Control Flow
Construction sets up local-node identity and attaches an internal connection pool built from the local NIC list.

### State, Persistence, And Dependencies
State is inherited node identity plus a local connection pool. It depends on `LocalNodeConnPool`, `NodeConnPool`, and `Node`.

### Integration Points
Services use `LocalNode` when inserting themselves into node stores and routing self-directed messages internally.

### Risks
Returning TCP port `0` is intentional but can surprise code that treats all nodes as network peers. Tests should cover self-message routing and node serialization paths that include a local node.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/LocalNode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/LocalNodeConnPool.cpp -->
## sources/distributed-fs/beegfs/common/source/common/nodes/LocalNodeConnPool.cpp

### Purpose
`LocalNodeConnPool.cpp` implements an internal connection pool for messages sent from a service to itself, using `LocalConnWorker` instances instead of TCP.

### Important APIs, Types, And Functions
The constructor copies NICs, initializes connection counters, and reads max internal connections from config. `acquireStreamSocketEx()` returns an available worker endpoint, waits when allowed and maxed out, or starts a new `LocalConnWorker`. `releaseStreamSocket()` marks a worker available. `invalidateStreamSocket()` removes a worker, gracefully shuts down the endpoint, joins the worker, and deletes it. `updateInterfaces()` updates the copied NIC list and ignores the stream port.

### Control Flow
Acquire is synchronized by `mutex`: wait for availability, reuse a worker, or increment established count before creating a new worker. Invalidation removes the worker under lock, then performs shutdown/join outside the lock. The destructor copies the worker list and invalidates every endpoint.

### State, Persistence, And Dependencies
State is in-memory worker list, connection counters, max connection limit, condition variable, and NIC list. Dependencies include `LocalConnWorker`, `PThread` app config, `NodeConnPool`, logging, and socket exceptions.

### Integration Points
`LocalNode` installs this pool so normal messaging code can talk to the local service through the same `Socket` abstraction.

### Risks
Several searches dereference `*iter` before checking `iter != end`, which is unsafe if the socket is absent. Worker creation increments `establishedConns` before allocation/start and must decrement on failure. Tests should cover acquire/release reuse, max-connection waiting, no-wait acquire, invalidation of missing sockets, worker start failure, destructor cleanup, and interface-change detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/LocalNodeConnPool.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/LocalNodeConnPool.h -->
## sources/distributed-fs/beegfs/common/source/common/nodes/LocalNodeConnPool.h

### Purpose
`LocalNodeConnPool.h` declares the local/internal connection pool used by `LocalNode`.

### Important APIs, Types, And Functions
It derives from `NodeConnPool`, defines `UnixConnWorkerList`, and overrides `acquireStreamSocketEx()`, `releaseStreamSocket()`, `invalidateStreamSocket()`, and `updateInterfaces()`. It stores a list of `UnixConnWorker*` and a creation counter.

### Control Flow
The pool follows the same acquire/release contract as network node pools while creating local worker endpoints.

### State, Persistence, And Dependencies
State is in-memory local worker ownership. It depends on `NodeConnPool`, `LocalConnWorker`, and node/socket types.

### Integration Points
`LocalNode` uses it to avoid network paths for self-directed messaging.

### Risks
The class owns raw worker pointers, so destructor/invalidation correctness is important. Tests should verify ownership cleanup and polymorphic behavior through `NodeConnPool*`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/LocalNodeConnPool.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/MirrorBuddyGroup.h -->
## sources/distributed-fs/beegfs/common/source/common/nodes/MirrorBuddyGroup.h

### Purpose
`MirrorBuddyGroup.h` defines the simple value object representing a mirror buddy group as primary and secondary target IDs.

### Important APIs, Types, And Functions
`MirrorBuddyGroup` stores `firstTargetID` and `secondTargetID`, provides constructors, equality comparison, and a serializer that writes both IDs. It defines `MirrorBuddyGroupList`, `MirrorBuddyGroupMap`, and iterator typedefs.

### Control Flow
There is no behavioral control flow; consumers interpret first as primary and second as secondary.

### State, Persistence, And Dependencies
State is two 16-bit IDs. The type is serialized in management mappings and used in memory by mappers.

### Integration Points
`MirrorBuddyGroupMapper`, `MirrorBuddyGroupCreator`, management messages, and storage/metadata mirroring logic use this type.

### Risks
The field names `firstTargetID`/`secondTargetID` are semantically primary/secondary by convention; misuse can invert roles. Tests should cover serialization and equality, and higher-level tests should verify primary/secondary role handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/MirrorBuddyGroup.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/MirrorBuddyGroupCreator.cpp -->
## sources/distributed-fs/beegfs/common/source/common/nodes/MirrorBuddyGroupCreator.cpp

### Purpose
`MirrorBuddyGroupCreator.cpp` implements manual and automatic mirror buddy group creation. It validates target combinations, talks to management to create groups, selects target pairs for automatic mode, warns about uneven target sizes, and handles storage-pool constraints.

### Important APIs, Types, And Functions
`addGroup()` validates metadata root ownership, calls `addGroupComm()`, logs user-facing success/errors, and returns `FhgfsOpsErr`. `addGroupComm()` sends `SetMirrorBuddyGroupMsg` to management and reads `SetMirrorBuddyGroupRespMsg`. `createMirrorBuddyGroups()` applies generated groups unless dry-run. `removeTargetsFromExistingMirrorBuddyGroups()` removes already grouped targets from the local mapper. `findNextTarget()` chooses a target from the node with most remaining targets, optionally excluding a node and filtering by storage pool. ID helpers generate normal or unique group IDs. `checkSizeOfTargets()` queries `StorageTargetInfo::statStoragePath()`. `selectPrimaryTarget()` balances primary-target counts. `generateMirrorBuddyGroups()` pairs targets automatically while respecting storage pools and metadata root rules.

### Control Flow
Automatic generation repeatedly selects a primary candidate, determines its storage pool, tries to select a secondary on a different node in the same pool, falls back to same-node pairing with warnings, ensures metadata root owner is primary, allocates a group ID, and updates output lists until fewer than two targets remain.

### State, Persistence, And Dependencies
The creator mutates local target mapper copies during selection; actual persistent group creation occurs through management messages. Dependencies include node stores, target mappers, storage pool store, root info, `MessagingTk`, `NodesTk`, `StorageTargetInfo`, and `ZipIterator`.

### Integration Points
Management CLI/tools use this class for mirror buddy group setup in storage and metadata contexts.

### Risks
Automatic selection is heuristic and ignores size mismatches beyond warnings. `findNextTarget()` unmaps `retVal` even when zero. Storage-pool lookups assume the primary target belongs to a pool. Communication failures during multi-group creation can leave partial changes. Tests should cover manual create errors, root-owner secondary rejection, dry-run/force modes, odd target counts, same-node fallback, storage-pool filtering, unique-ID conflicts with target IDs, and partial failure behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/MirrorBuddyGroupCreator.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/MirrorBuddyGroupCreator.h -->
## sources/distributed-fs/beegfs/common/source/common/nodes/MirrorBuddyGroupCreator.h

### Purpose
`MirrorBuddyGroupCreator.h` declares the helper used to create mirror buddy groups manually or automatically.

### Important APIs, Types, And Functions
The class stores node type, management nodes, target mappers, node stores, local/system target mappers, existing buddy lists, config flags (`cfgForce`, `cfgDryrun`, `cfgUnique`), storage pool store, and metadata root info. Public methods include `addGroup()`, `createMirrorBuddyGroups()`, `removeTargetsFromExistingMirrorBuddyGroups()`, `generateMirrorBuddyGroups()`, and static `generateID()`. Private/protected helpers handle communication, target selection, unique IDs, size checks, and primary selection.

### Control Flow
Consumers configure the creator with current system mappings and flags, generate candidate groups, then optionally create them through management.

### State, Persistence, And Dependencies
The class holds references/pointers to external stores and copies of target mappers. Persistence happens through management messages, not directly in the creator. Dependencies include node stores, target mappers, buddy-group mapper, root info, and storage pool store.

### Integration Points
Command-line management and administrative workflows use this abstraction to set up mirroring.

### Risks
Most dependencies are raw pointers/references and must outlive the creator. Config flags materially alter behavior. Tests should cover constructor setup, flag combinations, null/invalid store assumptions, and generated output lists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/MirrorBuddyGroupCreator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/MirrorBuddyGroupMapper.cpp -->
## sources/distributed-fs/beegfs/common/source/common/nodes/MirrorBuddyGroupMapper.cpp

### Purpose
`MirrorBuddyGroupMapper.cpp` manages in-memory mirror buddy group mappings, validates additions, updates related capacity/storage pools, tracks the local group, and answers target-to-buddy queries.

### Important APIs, Types, And Functions
Constructors initialize optional target mapper references and attached stores. `mapMirrorBuddyGroup()` validates target existence, self-pairing, group ID conflicts, update permission, and target reuse before inserting/updating a `MirrorBuddyGroup`. `unmapMirrorBuddyGroup()` removes a group and updates attached pool stores. `syncGroupsFromLists()` replaces mappings from list payloads. Query methods return mappings as lists, find buddy group IDs, buddy target IDs, and buddy states. `generateID()` finds the next free group ID with gap handling.

### Control Flow
Mapping validation runs mostly before taking the write lock, including target existence and current group membership checks. Under the write lock, group ID zero triggers generated ID allocation, the map is updated, attached pools are updated, and `localGroupID` is set if the local node is a member. Sync builds a new map without holding the write lock, then swaps it in.

### State, Persistence, And Dependencies
State is the `mirrorBuddyGroups` map and `localGroupID`, protected by `RWLock`. Attached `NodeCapacityPools`, `StoragePoolStore`, and `NodeStore` are updated as side effects but persistence is handled by surrounding management code. Dependencies include `TargetMapper`, `NodeStore`, capacity pools, storage pools, and `MirrorBuddyGroup`.

### Integration Points
Management target-state stores, storage/metadata services, and mirroring logic use this mapper to resolve primary/secondary roles and buddy targets.

### Risks
Some validation before acquiring the write lock can race with concurrent map updates. `getBuddyGroupIDUnlocked()` unconditionally writes through `outTargetIsPrimary`, so callers must pass a non-null pointer. `unmapMirrorBuddyGroup()` indexes `mirrorBuddyGroups[buddyGroupID]`, which can insert a default group before erase if the ID is absent. Tests should cover create/update conflicts, generated IDs at boundaries, local group tracking, pool attachment side effects, absent-group unmap, sync replacement, and concurrent readers/writers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/MirrorBuddyGroupMapper.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/MirrorBuddyGroupMapper.h -->
## sources/distributed-fs/beegfs/common/source/common/nodes/MirrorBuddyGroupMapper.h

### Purpose
`MirrorBuddyGroupMapper.h` declares the mirror buddy group mapping service and buddy-state enum.

### Important APIs, Types, And Functions
`MirrorBuddyState` has unmapped, primary, and secondary states. The mapper exposes mapping/unmapping, sync-from-lists, list extraction, target-to-group and target-to-buddy queries, buddy-state queries, and attachment points for meta capacity pools, storage pools, and usable node stores. Inline getters return group details, map copies, size, and local group data under read locks.

### Control Flow
Public methods acquire read/write locks around map access. Friend target-state stores can perform atomic state/group transitions with protected internals.

### State, Persistence, And Dependencies
Protected state includes `TargetMapper*`, optional pool/node stores, `RWLock`, `MirrorBuddyGroupMap`, and `localGroupID`. Dependencies include capacity pools, target mapper, safe RW locks, node stores, and buddy group value types.

### Integration Points
Mirroring, management, and target state code use this mapper for role resolution and mapping synchronization from management.

### Risks
Inline unlocked helpers require callers to hold locks. `localGroupID` is a single group ID, so multi-membership assumptions would not fit. Tests should cover all query APIs and lock-safe copy/list extraction behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/MirrorBuddyGroupMapper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/Node.cpp -->
## sources/distributed-fs/beegfs/common/source/common/nodes/Node.cpp

### Purpose
`Node.cpp` implements construction, heartbeat tracking, interface updates, and display-name formatting for BeeGFS nodes.

### Important APIs, Types, And Functions
The main constructor initializes node type, alias, numeric ID, UDP port, and allocates a `NodeConnPool`. The protected constructor supports subclasses such as `LocalNode` that install their own pool. `updateLastHeartbeatT()` and `getLastHeartbeatT()` guard `Time lastHeartbeatT` with `mutex`. `updateInterfaces()` updates UDP port and delegates stream/NIC changes to the connection pool. `getTypedNodeID()` and `getNodeIDWithTypeStr()` build log-friendly identity strings under `aliasMutex`.

### Control Flow
Interface updates preserve the old UDP port when passed zero and return the connection pool's update result. The destructor deletes the connection pool.

### State, Persistence, And Dependencies
Node identity, ports, heartbeat, alias, and connection pool are in-memory state. Dependencies include `NodeConnPool`, `Socket`, `Time`, mutexes, shared mutexes, and `boost::format`.

### Integration Points
Node stores, messaging, heartbeat processing, debug output, and management logs use `Node`.

### Risks
`numID` changes are not guarded by `aliasMutex` or `mutex`, while formatted ID methods read it under only the alias lock. Raw `NodeConnPool*` ownership requires derived classes to set it correctly. Tests should cover construction/destruction, subclass pool installation, heartbeat updates, port-zero preservation, alias concurrent reads/writes, and identity string formatting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/Node.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/Node.h -->
## sources/distributed-fs/beegfs/common/source/common/nodes/Node.h

### Purpose
`Node.h` declares the common representation of a BeeGFS service node, including identity, connection pool access, heartbeat time, port/NIC data, and serialization helpers for vectors of node handles.

### Important APIs, Types, And Functions
`Node` stores alias, numeric ID, node type, `NodeConnPool*`, UDP port, heartbeat time, and alias mutex. Public APIs expose heartbeat, interface updates, typed ID strings, alias/ID/port/NIC/pool getters and setters. `VectorDes` deserializes node vectors in old and v6 formats; global `operator%` serializes/deserializes `std::vector<NodeHandle>`. `inV6Format()` selects the v6 deserialization layout.

### Control Flow
Vector serialization writes count then alias, NIC list, numeric ID, UDP/TCP ports, and node type for each node. v6 deserialization reads count plus padding, then feature flags, aligned string ID, NIC list, version, IDs, ports, and node type, creating `Node` objects.

### State, Persistence, And Dependencies
Node state is in-memory; serialized vectors are exchanged over management and heartbeat messages. Dependencies include `NumNodeID`, `Condition`, `BitStore`, serialization helpers, `Time`, `NodeConnPool`, `NodeType`, and `NetworkInterfaceCard`.

### Integration Points
Node stores and management messages serialize node lists through these operators. Connection code uses `getConnPool()` to communicate with nodes.

### Risks
Serialization constructs full `NodeConnPool` instances for deserialized nodes, so NIC and port correctness matters. `VectorDes::runV6()` reads fields it does not store, such as feature flags/version. Alias locking does not cover numeric ID changes. Tests should cover old/v6 node vector round-trips, malformed counts, NIC list parsing, alias updates, and port getters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/nodes/Node.h -->
