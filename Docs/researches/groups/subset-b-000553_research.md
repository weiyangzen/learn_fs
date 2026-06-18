# Research: subset-b-000553

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/creating/UnlinkFileMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/creating/UnlinkFileMsgEx.cpp

## Purpose
Implements the metadata-server side of `UnlinkFileMsg` for BeeGFS file dentries, including buddy-mirrored forwarding, local versus remote inode ownership, hardlink-aware inode removal, chunk cleanup, timestamp repair, and file-event logging.

## Important APIs, Types, and Functions
`UnlinkFileMsgEx::lock()` preloads the target dentry, captures `fileInfo`, locks the parent directory ID, parent/name tuple, target inode ID, and, during resync for non-inlined inodes, the inode hash directory. `processIncoming()` records `MetaOpCounter_UNLINK` before delegating to `MirroredMessage`. `executeLocally()` references the parent `DirInode`, validates the dentry and mirrored entry ID, chooses same-owner local handling or remote `UnlinkLocalFileInodeMsg`, and returns `ResponseState`. `executePrimary()` performs metadata unlink, optional early response, storage chunk removal, timestamp fixes, and event logging. `executeSecondary()` mirrors only metadata effects.

## Control Flow, State, and Persistence
The handler first removes or updates metadata in `MetaStore` through `DirInode`/`MsgHelperUnlink`. If the file inode owner is remote, it removes only the local dentry and asks the owner metadata node or buddy group to unlink the inode; remote failure is logged but does not overwrite successful dentry removal for the user path. If the local primary removes the last inode reference, chunk files are deleted or deferred to disposal by `MsgHelperUnlink`. Timestamp fixup persists through inode/dir helpers when mirrored replay needs deterministic times.

## Dependencies and Integration Points
Depends on `Program::getApp()`, `MetaStore`, `DirInode`, `DirEntry`, `MetaStorageTk`, `MessagingTk`, `RequestResponseNode`, buddy group mapping, `MsgHelperUnlink`, `UnlinkLocalFileInodeMsg`, `MirroredMessage`, `FileEventLogger`, and op counters.

## Risks and Test Signals
High-risk areas are lock-time dentry lookup races, remote inode unlink failure after local dentry removal, early-response behavior that hides later chunk cleanup failures, mirrored entry-ID validation, and correct hardlink counts in events. Tests should cover local inlined and non-inlined unlink, hardlinks, open-file disposal, remote-owner inode unlink, buddy primary/secondary replay, resync-running hash locks, timestamp repair, and remote communication failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/creating/UnlinkFileMsgEx.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/creating/UnlinkFileMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/creating/UnlinkFileMsgEx.h

## Purpose
Declares the mirrored unlink message extension and its lock/response contract for file unlink operations on metadata servers.

## Important APIs, Types, and Functions
`UnlinkFileMsgEx` inherits `MirroredMessage<UnlinkFileMsg, std::tuple<HashDirLock, FileIDLock, ParentNameLock, FileIDLock>>`. The public API overrides `processIncoming()`, `lock()`, `executeLocally()`, and `isMirrored()`. `ResponseState` is an `ErrorCodeResponseState<UnlinkFileRespMsg, NETMSGTYPE_UnlinkFile>`. Private helpers split primary and secondary execution and define `forwardToSecondary()`, `processSecondaryResponse()`, and `mirrorLogContext()`.

## Control Flow, State, and Persistence
The header exposes that unlink is state-changing under the mirrored-message framework, requiring a hash lock plus parent, name, and inode locks. The split between `executePrimary()` and `executeSecondary()` documents that only the primary performs chunk cleanup and event work while both sides mutate metadata.

## Dependencies and Integration Points
Integrates common unlink request/response message types, `EntryLock` primitives, `MirroredMessage`, `DirInode`, and BeeGFS storage error response serialization.

## Risks and Test Signals
The type signature is the contract for lock ordering and replay. Compile-time tests are limited; behavioral tests should assert that secondary response errors are propagated from `UnlinkFileRespMsg` and that `isMirrored()` follows the parent directory mirror flag.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/creating/UnlinkFileMsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/creating/UnlinkLocalFileInodeMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/creating/UnlinkLocalFileInodeMsgEx.cpp

## Purpose
Implements a metadata-owner-side helper message used when another metadata node has removed a dentry but the actual file inode lives locally. It decrements hardlink state, removes the inode when appropriate, and deletes chunk files on the primary.

## Important APIs, Types, and Functions
`lock()` returns no locks for locally generated messages because callers already own the relevant locks; otherwise it should lock the inode hash during resync and the file ID. `processIncoming()` stores the response context for local-generation checks and invokes `BaseType`. `executeLocally()` copies the incoming `EntryInfo`, calls `MsgHelperUnlink::unlinkFileInode()`, fills `UnlinkLocalFileInodeResponseState`, and removes storage chunks if an inode was actually unlinked on the primary. `forwardToSecondary()` forwards the mirrored request with `NETMSGTYPE_UnlinkLocalFileInodeResp`.

## Control Flow, State, and Persistence
The metadata mutation is delegated to `MetaStore::unlinkFileInode()` through `MsgHelperUnlink`. A copied `EntryInfo` is intentionally used because unlink processing can modify parent/inlined fields; forwarding the original state to the secondary avoids primary/secondary divergence. Chunk-file deletion happens only for non-secondary execution.

## Dependencies and Integration Points
Used by `UnlinkFileMsgEx` and `RenameV2MsgEx` for remote inode cleanup. Depends on `MetaStorageTk`, `EntryLockStore`, `MirroredMessage`, `MsgHelperUnlink`, and `UnlinkLocalFileInodeRespMsg`.

## Risks and Test Signals
The `lock()` implementation contains a shadowed `HashDirLock hashLock` inside the resync branch, which appears to leave the returned hash lock empty even when resync is running. Tests should cover non-local message locking during resync, copied-entry forwarding, hardlink decrement results, chunk unlink suppression on secondary, and serialized pre-unlink hardlink count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/creating/UnlinkLocalFileInodeMsgEx.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/creating/UnlinkLocalFileInodeMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/creating/UnlinkLocalFileInodeMsgEx.h

## Purpose
Declares the mirrored local-inode unlink message and a custom response state that carries both operation status and the pre-unlink hardlink count.

## Important APIs, Types, and Functions
`UnlinkLocalFileInodeResponseState` derives from `MirroredMessageResponseState`, serializes `result` and `preUnlinkHardlinkCount`, sends `UnlinkLocalFileInodeRespMsg`, and reports `changesObservableState() == true`. `UnlinkLocalFileInodeMsgEx` inherits `MirroredMessage<UnlinkLocalFileInodeMsg, std::tuple<HashDirLock, FileIDLock>>`, overrides `processIncoming()`, `executeLocally()`, `lock()`, `isMirrored()`, and secondary forwarding hooks.

## Control Flow, State, and Persistence
The response type makes hardlink count part of the mirrored state so remote unlink callers can log accurate post-unlink event context. `isMirrored()` follows the deleted entry info rather than a parent dentry, which matches inode-owner semantics.

## Dependencies and Integration Points
Integrates common unlink-local-inode wire messages, `EntryLock`, `MetaStore`, and `MirroredMessage`. It is a response contract consumed by remote unlink and rename paths.

## Risks and Test Signals
Serialization compatibility matters because this response is mirrored and also returned cross-node. Tests should deserialize old/new buffers, assert `changesObservableState()`, verify secondary error extraction from `getResult()`, and check response hardlink count propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/creating/UnlinkLocalFileInodeMsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/listing/ListDirFromOffsetMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/listing/ListDirFromOffsetMsgEx.cpp

## Purpose
Handles incremental directory listing from a server offset, returning names, entry types, entry IDs, per-entry offsets, a new offset, and a result code.

## Important APIs, Types, and Functions
`processIncoming()` logs the request, computes an optional response payload budget when the client sets `LISTDIROFFSETMSG_COMPATFLAG_CLIENT_SUPPORTS_BUFSIZE`, calls `listDirIncremental()`, sends `ListDirFromOffsetRespMsg`, advertises `LISTDIROFFSETRESPMSG_COMPATFLAG_SERVER_SUPPORTS_BUFSIZE`, and updates `MetaOpCounter_READDIR`. `listDirIncremental()` references the target directory and invokes `DirInode::listIncrementalEx()` with count or byte-budget limiting.

## Control Flow, State, and Persistence
No persistent state is changed. The handler reads a directory inode from `MetaStore`, streams a bounded slice of names and metadata, and advances the server offset. Buffer-size mode subtracts header and fixed response fields from the smaller of client and worker buffer sizes; without the flag, the request limit remains an entry-count limit.

## Dependencies and Integration Points
Depends on `ListDirFromOffsetMsg/RespMsg`, `MetaStore`, `DirInode::listIncrementalEx`, `ListIncExOutArgs`, `Program` config, node op stats, and compatibility feature flags.

## Risks and Test Signals
Risks include off-by-one response sizing, mixed clients using count mode versus buffer mode, and stale offsets during concurrent directory mutation. Tests should cover missing directory, dot filtering, exact buffer-boundary responses, feature negotiation, large entry names, and op counter updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/listing/ListDirFromOffsetMsgEx.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/listing/ListDirFromOffsetMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/listing/ListDirFromOffsetMsgEx.h

## Purpose
Declares the metadata-server extension for offset-based directory listing.

## Important APIs, Types, and Functions
`ListDirFromOffsetMsgEx` inherits `ListDirFromOffsetMsg`, overrides `processIncoming()`, and owns private `listDirIncremental()` for the actual `MetaStore`/`DirInode` read.

## Control Flow, State, and Persistence
The header shows this is a non-mirrored, read-only request. State is limited to response list construction and offset calculation in the implementation.

## Dependencies and Integration Points
Includes common entry info, storage errors, `MetaStore`, and the listdir request message. It is consumed by the metadata network dispatch table.

## Risks and Test Signals
The main contract is that the implementation returns all parallel lists with matching lengths and a valid next offset. Tests should validate header-level compatibility with `ListDirFromOffsetMsg` serialization and response shape.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/listing/ListDirFromOffsetMsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/lookup/FindLinkOwnerMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/lookup/FindLinkOwnerMsgEx.cpp

## Purpose
Implements a legacy reverse-lookup helper that tries to find the parent/owner information for an entry ID, primarily for `fhgfs-ctl` reverse lookup mode.

## Important APIs, Types, and Functions
`processIncoming()` reads `entryID`, tries `MetaStore::referenceLoadedFile()` first, then `MetaStore::referenceDir()`, sends `FindLinkOwnerRespMsg(result, parentNodeID, parentEntryID)`, and releases any referenced object.

## Control Flow, State, and Persistence
This is a read-only lookup. It does not scan unloaded file metadata and has TODO comments noting limitations: the old caller does not send a parent ID, buddy mirroring is not handled, and the mode may no longer be used.

## Dependencies and Integration Points
Depends on `Program`, `MetaStore`, loaded file handles, directory parent info, and `FindLinkOwnerRespMsg`. It is separate from normal path lookup and does not update op counters.

## Risks and Test Signals
The function can produce incomplete results for unloaded files and buddy-mirrored metadata. Tests should treat it as best-effort legacy behavior, covering loaded file success, directory success, missing entry, and mirrored-entry limitations if retained.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/lookup/FindLinkOwnerMsgEx.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/lookup/FindLinkOwnerMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/lookup/FindLinkOwnerMsgEx.h

## Purpose
Declares the legacy link-owner lookup message extension.

## Important APIs, Types, and Functions
`FindLinkOwnerMsgEx` inherits `FindLinkOwnerMsg` and overrides only `processIncoming()`.

## Control Flow, State, and Persistence
The declaration identifies a synchronous, non-mirrored read-only response path with no helper state.

## Dependencies and Integration Points
Includes common find-link-owner request and response messages. Dispatch integration is through the standard message extension mechanism.

## Risks and Test Signals
Because the header exposes no locking or mirror awareness, tests should focus on behavior in the implementation and on compatibility with old management-tool requests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/lookup/FindLinkOwnerMsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/lookup/FindOwnerMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/lookup/FindOwnerMsgEx.cpp

## Purpose
Handles path-component owner discovery for metadata clients, returning the deepest known `EntryInfoWithDepth` and status so clients can route later operations to the correct metadata node or buddy group.

## Important APIs, Types, and Functions
`processIncoming()` special-cases depth zero as root owner lookup, otherwise calls `findOwner()`, sends `FindOwnerRespMsg`, and updates `MetaOpCounter_FINDOWNER`. `findOwner()` iterates path components from `currentDepth` to `searchDepth`, references each current directory, calls `MetaStore::getEntryData()`, updates `outInfo`, and stops once ownership leaves the local node/local buddy group.

## Control Flow, State, and Persistence
This is read-only. It follows local path components until it either reaches a missing entry, a nonlocal owner, or the requested depth. `DYNAMICATTRIBSOUTDATED` is accepted as a successful lookup for routing purposes. If a previously claimed local directory cannot be referenced, it returns success if a prior component was found, otherwise `PATHNOTEXISTS`.

## Dependencies and Integration Points
Depends on `RootDir`, `MetaStore`, `EntryInfoWithDepth`, `Path`, buddy group mapping, node op stats, and common find-owner response messages.

## Risks and Test Signals
Risks include races with deletes during traversal, stale ownership after concurrent moves, and correct mirrored owner comparison against group ID rather than node ID. Tests should cover root lookup, missing root owner, partial local traversal, remote handoff, dynamic-attrib success, and deleted-directory race behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/lookup/FindOwnerMsgEx.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/lookup/FindOwnerMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/lookup/FindOwnerMsgEx.h

## Purpose
Declares the metadata-owner path lookup extension.

## Important APIs, Types, and Functions
`FindOwnerMsgEx` inherits `FindOwnerMsg`, overrides `processIncoming()`, and uses private `findOwner(EntryInfoWithDepth*)` for normal non-root lookup.

## Control Flow, State, and Persistence
No persistent state is declared. The header documents a simple read-only message without mirrored replay or explicit locks.

## Dependencies and Integration Points
Includes storage definitions/errors, metadata toolkit/common types, and `MetaStore`. It is part of metadata routing and lookup dispatch.

## Risks and Test Signals
The important contract is the `EntryInfoWithDepth` result. Tests should assert that response depth and owner flags match traversal state across local and remote ownership boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/lookup/FindOwnerMsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/lookup/LookupIntentMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/lookup/LookupIntentMsgEx.cpp

## Purpose
Implements BeeGFS combined lookup intents: lookup, create, exclusive create, revalidate, stat, and open in one metadata message, with buddy-mirrored replay support and session insertion for opens.

## Important APIs, Types, and Functions
`lock()` chooses parent/name/file locks based on intent flags, pre-runs lookup for non-create intents under the parent lock, and handles directory/file lock ordering. `processIncoming()` validates parent/name and pre-generates a file ID for creates. `executeLocally()` sequences create, lookup, revalidate, stat, and open responses in one `LookupIntentResponseState`. Helpers include `lookup()` for dentry/inode data and remote metaVersion stat, `revalidate()`, `create()` through `MsgHelperMkFile`, `stat()` through `MsgHelperStat`, `open()` through `MsgHelperOpen` plus session store insertion, `getOpCounterType()`, and `forwardToSecondary()`.

## Control Flow, State, and Persistence
Create persists a new metadata file and optional remote storage target info, enforces quota if requested, fixes mirrored timestamps, logs file creation events, and forwards stripe pattern/new ID to the secondary. Open mutates file reference state and session stores, assigning a new owner FD on primary and replaying it on secondary. Stat may use inlined inode data from lookup or reload from disk. Revalidate compares client entry ID/owner and metaVersion.

## Dependencies and Integration Points
Depends on `MetaStore`, `DirInode`, `SessionStore`, `SessionTk`, `MsgHelperMkFile/Open/Stat/Trunc`, quota stores, storage pools, `StorageTk`, `StatMsg` for remote non-inlined revalidate, file-event logging, buddy group mapping, and `MirroredMessage`.

## Risks and Test Signals
Risks include complex lock ordering, create/lookup races, dangling dentries with null stripe patterns, remote stat failures during revalidate, secondary owner FD replay, quota checks across pool targets, and forwarding only when create/open changed observable state. Tests should cover every flag combination, exclusive create existing path, inlined versus non-inlined inode stat, remote-owner revalidate, open with trunc, mirrored primary/secondary create-open, and null stripe-pattern recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/lookup/LookupIntentMsgEx.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/lookup/LookupIntentMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/lookup/LookupIntentMsgEx.h

## Purpose
Declares the lookup-intent mirrored message and its compound response state for multi-intent metadata operations.

## Important APIs, Types, and Functions
`LookupIntentResponseState` stores response flags, lookup/stat/revalidate/create/open results, stat data, file handle ID, entry info, stripe pattern, and path info. It serializes only fields selected by flags, sends `LookupIntentRespMsg`, and reports observable changes for successful create or open. `LookupIntentMsgEx` inherits `MirroredMessage<LookupIntentMsg, std::tuple<FileIDLock, ParentNameLock, FileIDLock>>`, declares lock/execution/forwarding hooks, helper operations, and cached lookup fields (`inodeData`, `entryID`, `lookupRes`, `inodeDataOutdated`, `diskEntryInfo`).

## Control Flow, State, and Persistence
The header encodes the operation contract: create/open are mirrored state changes; stat/revalidate/lookup are response enrichments. Cached fields are populated before or during lock acquisition and then consumed by execution to avoid redoing work on the primary.

## Dependencies and Integration Points
Integrates common lookup-intent messages, op counters, storage definitions, `MetaStore`, `StripePattern`, `StatData`, `PathInfo`, and `MirroredMessage`.

## Risks and Test Signals
Serializer flag ordering is critical for buddy replay and wire compatibility. Tests should cover response serialization for all flag combinations, `changesObservableState()` gating, `processSecondaryResponse()` create/open error extraction, and null or missing open pattern prevention.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/lookup/LookupIntentMsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/mirroring/GetMetaResyncStatsMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/mirroring/GetMetaResyncStatsMsgEx.cpp

## Purpose
Returns current metadata buddy-resync job statistics to callers.

## Important APIs, Types, and Functions
`processIncoming()` gets `BuddyResyncer`, asks for the current `BuddyResyncJob`, copies `job->getJobStats()` when present, and sends `GetMetaResyncStatsRespMsg`.

## Control Flow, State, and Persistence
This is a read-only snapshot. If no job exists, a default `MetaBuddyResyncJobStatistics` is returned. No locks or persistent updates are performed in this file.

## Dependencies and Integration Points
Depends on `BuddyResyncer`, `BuddyResyncJob`, `MetaBuddyResyncJobStatistics`, `Program`, and the common resync-stats response message.

## Risks and Test Signals
The main risks are stale or concurrently changing statistics and default-value interpretation when no job is active. Tests should cover active job, no job, and response serialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/mirroring/GetMetaResyncStatsMsgEx.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/mirroring/GetMetaResyncStatsMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/mirroring/GetMetaResyncStatsMsgEx.h

## Purpose
Declares the metadata resync statistics request handler.

## Important APIs, Types, and Functions
`GetMetaResyncStatsMsgEx` inherits `GetMetaResyncStatsMsg` and overrides `processIncoming()`.

## Control Flow, State, and Persistence
The declaration represents a non-mutating query message with no local state.

## Dependencies and Integration Points
Includes the common stats request message and is wired into metadata mirroring message dispatch.

## Risks and Test Signals
Header-level risk is low; tests should focus on implementation behavior and wire response compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/mirroring/GetMetaResyncStatsMsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/mirroring/ResyncRawInodesMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/mirroring/ResyncRawInodesMsgEx.cpp

## Purpose
Receives a streaming raw-metadata resync from a primary metadata buddy and writes mirrored inode, directory, and dentry files under the buddy-mirror metadata subtree, optionally including xattrs and whole-directory cleanup.

## Important APIs, Types, and Functions
`processIncoming()` invokes `resyncStream()` and sends a final `ResyncRawInodesRespMsg`. `resyncStream()` validates xattr support, ensures root mirroring through `SetMetadataMirroringMsgEx::setMirroring()`, creates target directories for whole-directory mode, loops over `resyncSingle()`, and removes untouched entries. `resyncSingle()` reads a length-prefixed packet, deserializes `MetaSyncFileType` and relative path, dispatches to `resyncInode()` or `resyncDentry()`, and ACKs each packet. `resyncInode()` writes or deletes raw metadata and xattrs. `resyncDentry()` handles direct dentry content or hardlinks into `#fSiDs#`. `removeUntouchedInodes()` prunes local entries not sent by the primary.

## Control Flow, State, and Persistence
The handler directly mutates on-disk metadata paths rooted at `META_BUDDYMIRROR_SUBDIR_NAME`. `IncompleteInode` writes content atomically enough for resync staging, and whole-directory mode tracks `inodesWritten` to delete stale files/directories after the stream. Packet-level ACKs let the primary stop or continue; failures are returned both as ACK and stream termination signal.

## Dependencies and Integration Points
Depends on raw socket reads, `Deserializer`, `MetaStore::beginResyncFor()` and `unlinkRawMetadata()`, `StorageTk`, `SetMetadataMirroringMsgEx`, `MsgHelperXAttr::StreamXAttrState`, `XAttrTk`, POSIX `link`, `unlink`, `opendir`, `readdir`, and BeeGFS mirror-resync packet types.

## Risks and Test Signals
Risks include malformed packet lengths, path traversal assumptions for `relPath`, xattr configuration mismatch, partial stream failure leaving staged metadata, deletion of untouched entries in whole-directory mode, and compatibility between old vector dentry content and newer xattr map content. Tests should cover bad deserialization, deletions, dentry hardlink recreation, xattr stream end/error markers, whole-directory pruning, root mirror bootstrap, and disabled xattrs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/mirroring/ResyncRawInodesMsgEx.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/mirroring/ResyncRawInodesMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/mirroring/ResyncRawInodesMsgEx.h

## Purpose
Declares the serializable raw-inode resync stream message.

## Important APIs, Types, and Functions
`ResyncRawInodesMsgEx` derives from `NetMessageSerdes<ResyncRawInodesMsgEx>`, serializes `basePath`, `hasXAttrs`, and `wholeDirectory`, overrides `processIncoming()`, and declares helpers for stream, packet, inode, dentry, xattr, and cleanup processing.

## Control Flow, State, and Persistence
The message object carries stream scope (`basePath`) and mode flags. `inodesWritten` is transient state used only for whole-directory cleanup after all packets are processed.

## Dependencies and Integration Points
Includes `NetMessage`, `Path`, and `IncompleteInode`. It is part of the metadata buddy-resync protocol rather than normal mirrored message replay.

## Risks and Test Signals
Constructor/serialization compatibility is important because the rest of the payload is streamed manually after the message header. Tests should verify serialization of mode flags and that empty/default construction works for receive-side deserialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/mirroring/ResyncRawInodesMsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/mirroring/ResyncSessionStoreMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/mirroring/ResyncSessionStoreMsgEx.cpp

## Purpose
Receives and installs a serialized mirrored session store during metadata buddy resync.

## Important APIs, Types, and Functions
`processIncoming()` calls `receiveStoreBuf()` with the short message timeout, handles out-of-memory and communication failures, clears `Program::getApp()->getMirroredSessions()`, deserializes the received buffer into the session store using `MetaStore`, and sends `ResyncSessionStoreRespMsg`.

## Control Flow, State, and Persistence
The operation replaces in-memory mirrored session state. It does not directly persist files, but deserialization references metadata inodes through `MetaStore`; failure after clearing means the secondary session store remains empty until another resync.

## Dependencies and Integration Points
Depends on `ResyncSessionStoreMsg` buffer helpers, `SessionStore::clear()` and `deserializeFromBuf()`, app config timeouts, mirrored sessions, `MetaStore`, and the resync response message.

## Risks and Test Signals
Risks include clearing good sessions before detecting bad serialized data, memory allocation failure, and metadata mismatches during session deserialization. Tests should cover receive failures, clear failure, bad buffer, successful restore, and behavior with open mirrored files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/mirroring/ResyncSessionStoreMsgEx.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/mirroring/ResyncSessionStoreMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/mirroring/ResyncSessionStoreMsgEx.h

## Purpose
Declares the session-store resync message extension.

## Important APIs, Types, and Functions
`ResyncSessionStoreMsgEx` inherits `ResyncSessionStoreMsg` and overrides `processIncoming()`.

## Control Flow, State, and Persistence
The header exposes no lock or mirrored-message wrapper; the implementation controls replacement of the mirrored session store.

## Dependencies and Integration Points
Includes the common resync-session-store message. It is invoked by metadata buddy resync workflows.

## Risks and Test Signals
Behavioral tests should focus on implementation; the declaration’s main compatibility point is the inherited buffer-carrying message contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/mirroring/ResyncSessionStoreMsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/mirroring/SetMetadataMirroringMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/mirroring/SetMetadataMirroringMsgEx.cpp

## Purpose
Enables metadata buddy mirroring for the root directory by moving root metadata into buddy-mirror storage paths, setting the root inode mirror flag, and changing root owner to the local buddy group.

## Important APIs, Types, and Functions
`processIncoming()` verifies the local node belongs to a buddy group, is primary, and owns the root directory, then calls `setMirroring()` and sends `SetMetadataMirroringRespMsg`. `setMirroring()` serializes callers through a static mutex, no-ops when already mirrored, moves the root inode and root directory, persists `DirInode::setAndStoreIsBuddyMirrored(true)`, sets owner node ID to the buddy group, and updates `MetaRoot`. `moveRootInode()` and `moveRootDirectory()` rename paths between normal and buddy-mirror metadata trees, with revert support.

## Control Flow, State, and Persistence
This mutates on-disk metadata layout with POSIX `rename()`, updates the root `DirInode` on disk, changes in-memory root owner/mirror state, and tries to roll back file moves on intermediate failures. The mirror flag is deliberately written after moving files because it changes path calculation inside `DirInode`.

## Dependencies and Integration Points
Depends on `MirrorBuddyGroupMapper`, `RootDir`, `MetaStorageTk`, app metadata paths, `StorageTk::createPathOnDisk`, `DirInode`, `MetaRoot`, and common set-mirroring response messages. `ResyncRawInodesMsgEx` also calls `setMirroring()` during root resync bootstrap.

## Risks and Test Signals
Risks include partial rename failures, rollback failures that can corrupt root metadata, concurrent bulk-resync callers, and mismatch between local node primary status and root ownership. Tests should cover already mirrored root, non-group node, secondary node, not-owner root, successful path moves, each rollback branch, and persistent root owner/mirror flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/mirroring/SetMetadataMirroringMsgEx.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/mirroring/SetMetadataMirroringMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/mirroring/SetMetadataMirroringMsgEx.h

## Purpose
Declares the set-metadata-mirroring request handler and static root-mirroring helpers.

## Important APIs, Types, and Functions
`SetMetadataMirroringMsgEx` inherits `SetMetadataMirroringMsg`, overrides `processIncoming()`, exposes static `setMirroring()`, and declares private static `moveRootInode()` and `moveRootDirectory()`.

## Control Flow, State, and Persistence
The header makes `setMirroring()` callable outside the network request path, which is used by raw inode resync. Persistent mutation details are in the implementation.

## Dependencies and Integration Points
Includes common storage errors and the set-mirroring request message. It is a control-plane integration point for root metadata mirroring.

## Risks and Test Signals
The exposed static API should be tested both through the message and direct resync bootstrap path to ensure identical state transitions and locking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/mirroring/SetMetadataMirroringMsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/mirroring/StorageResyncStartedMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/mirroring/StorageResyncStartedMsgEx.cpp

## Purpose
Handles notification that storage/metadata resync is starting for the local metadata node, quiescing workers and invalidating mirrored metadata caches before resync changes files on disk.

## Important APIs, Types, and Functions
`processIncoming()` validates that the message target ID matches the local node, calls `pauseWorkers()`, marks the root directory as buddy mirrored, clears mirrored sessions, invalidates mirrored directory inodes in `MetaStore`, sends `StorageResyncStartedRespMsg`, and returns true. `pauseWorkers()` enqueues `BarrierWork` on all other worker personal queues and waits twice on a `Barrier` so pre-existing messages drain before resync.

## Control Flow, State, and Persistence
The handler mutates in-memory state only: root mirror flag, mirrored session store, and cached directory inodes. It relies on target state (`NeedsResync`) plus worker barrier synchronization to ensure no mirrored operations are in flight while resync overwrites mirrored metadata.

## Dependencies and Integration Points
Depends on worker lists, `MultiWorkQueue`, `Barrier`, `PThread`, `BarrierWork`, mirrored sessions, `MetaStore::invalidateMirroredDirInodes()`, and the resync-started response message.

## Risks and Test Signals
Risks include deadlock if the current worker is accidentally enqueued, incorrect barrier count, target-ID mismatch returning false without response, and clearing sessions while operations still reference files. Tests should cover multi-worker barrier behavior, single-worker behavior, wrong target ID, cache invalidation, and session clearing before raw resync begins.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/mirroring/StorageResyncStartedMsgEx.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/mirroring/StorageResyncStartedMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/mirroring/StorageResyncStartedMsgEx.h

## Purpose
Declares the resync-started notification handler.

## Important APIs, Types, and Functions
`StorageResyncStartedMsgEx` inherits `StorageResyncStartedMsg`, has a default constructor, overrides `processIncoming()`, and uses private `pauseWorkers()`.

## Control Flow, State, and Persistence
The declaration identifies an in-memory synchronization/control message, not a mirrored metadata mutation itself.

## Dependencies and Integration Points
Includes the common resync-started message and is used by resync orchestration before raw metadata transfer.

## Risks and Test Signals
Tests should focus on ensuring `pauseWorkers()` is invoked only for the intended local target and that response behavior is compatible with callers waiting for resync readiness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/mirroring/StorageResyncStartedMsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/moving/MovingDirInsertMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/moving/MovingDirInsertMsgEx.cpp

## Purpose
Handles the destination-side insertion phase of a cross-directory or cross-node directory rename.

## Important APIs, Types, and Functions
`processIncoming()` stores `ResponseContext` for lock logic and delegates to `BaseType`. `executeLocally()` references the destination parent, deserializes a `DirEntry` from the supplied metadata buffer, rejects attempts to insert a directory into itself, calls `DirInode::makeDirEntry()`, optionally fixes destination directory timestamps, releases the parent, and returns `MovingDirInsertRespMsg` through `ResponseState`. `forwardToSecondary()` mirrors the insert to the secondary.

## Control Flow, State, and Persistence
The operation persists a new directory dentry in the destination directory. It does not update the moved directory inode’s parent info; the source-side rename handler performs that through `UpdateDirParentMsg` after local removal.

## Dependencies and Integration Points
Depends on `MirroredMessage`, destination `MetaStore`, serialized `DirEntry`, `MovingDirInsertMsg/RespMsg`, timestamp repair, and `RenameV2MsgEx::remoteDirInsert()`.

## Risks and Test Signals
Risks include metadata buffer version mismatch, accepting duplicate destination names, self-move detection, and partial remote insert before source-side cleanup. Tests should cover bad deserialization, existing target, self insert, mirrored secondary replay, timestamp fixup, and destination parent missing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/moving/MovingDirInsertMsgEx.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/moving/MovingDirInsertMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/moving/MovingDirInsertMsgEx.h

## Purpose
Declares the mirrored destination-side directory insertion message for rename/move.

## Important APIs, Types, and Functions
`MovingDirInsertMsgEx` inherits `MirroredMessage<MovingDirInsertMsg, std::tuple<FileIDLock, ParentNameLock>>`. It overrides `processIncoming()`, inline `lock()`, `isMirrored()`, `executeLocally()`, forwarding, secondary response extraction, and mirror log context. `lock()` skips locks for locally generated messages and otherwise locks the destination directory and destination name.

## Control Flow, State, and Persistence
The header’s lock contract protects destination directory/name creation while allowing source-side local messages to rely on already-held locks from the initiating rename.

## Dependencies and Integration Points
Includes moving request/response messages, storage errors, `MetaStore`, and `MirroredMessage`. Used by `RenameV2MsgEx` remote directory moves.

## Risks and Test Signals
The `rctx` pointer must be set before locking; tests should include locally generated and remote-generated paths to verify lock suppression does not run on an uninitialized context.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/moving/MovingDirInsertMsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/moving/MovingFileInsertMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/moving/MovingFileInsertMsgEx.cpp

## Purpose
Handles destination-side insertion of a file during a remote rename, including overwrite handling and optional xattr streaming for inlined files.

## Important APIs, Types, and Functions
`lock()` skips local generated requests, locks destination directory/name, deserializes the incoming file inode metadata to identify the new inode, checks an existing destination file, and locks new/overwritten inode IDs in lexicographic order. `executeLocally()` references the destination directory, calls `MetaStore::moveRemoteFileInsert()`, reads streamed xattrs with `MsgHelperXAttr::StreamXAttrState::readNextXAttr()`, records xattr names for secondary forwarding, serializes any overwritten inlined inode into the response, fixes timestamps, and rolls back the inserted metadata on xattr failure.

## Control Flow, State, and Persistence
The destination directory gains the moved file dentry/inode state. If a destination file is overwritten, the response may carry serialized inode metadata so the source side can delete old chunks. Xattrs are streamed after the main insert and applied to `newFileInfo`; failure unlinks the inserted metadata but cannot necessarily undo all side effects outside metadata.

## Dependencies and Integration Points
Depends on `MetaStore::moveRemoteFileInsert()`, `FileInode` serialization, `MovingFileInsertMsg/RespMsg`, `MsgHelperXAttr`, `MsgHelperUnlink`, `MirroredMessage`, and `RenameV2MsgEx::remoteFileInsertAndUnlink()`.

## Risks and Test Signals
Risks include response serialization omitting `overWrittenEntryInfo` in `serializeContents()` even though deserialization expects it, xattr streaming failures after insert, lock ordering with existing target, and memory allocation failure leaking chunks. Tests should cover overwrite inlined/non-inlined targets, xattr success/failure, secondary forwarding of xattrs, serialized response round trip, and destination parent missing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/moving/MovingFileInsertMsgEx.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/moving/MovingFileInsertMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/moving/MovingFileInsertMsgEx.h

## Purpose
Declares the mirrored destination-side file insertion message and custom response used by cross-node file rename.

## Important APIs, Types, and Functions
`MovingFileInsertResponseState` stores result, overwritten inode buffer, and overwritten entry info, sends `MovingFileInsertRespMsg`, serializes response state for mirrored replay, and reports observable change on success. `MovingFileInsertMsgEx` inherits `MirroredMessage<MovingFileInsertMsg, std::tuple<FileIDLock, FileIDLock, FileIDLock, ParentNameLock>>`, manages `xattrNames`, `newFileInfo`, and a `StreamXAttrState`, and overrides lock/execution/forwarding hooks.

## Control Flow, State, and Persistence
`prepareMirrorRequestArgs()` registers a stream-out hook when the original message has xattrs, using the xattrs just received and the new file info. This allows primary destination xattr application to be replayed to the secondary destination.

## Dependencies and Integration Points
Depends on moving wire messages, `MirroredMessage`, `MetaStore`, `MsgHelperXAttr`, and response-state serialization used by the mirror framework.

## Risks and Test Signals
Response-state serialization must include all fields needed by consumers; tests should check `overWrittenEntryInfo` survival across mirror serialization, xattr stream hook registration, and `changesObservableState()` only for successful insert.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/moving/MovingFileInsertMsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/moving/RenameV2MsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/moving/RenameV2MsgEx.cpp

## Purpose
Implements the main metadata rename operation for files and directories, supporting same-directory renames, cross-directory/cross-node moves, buddy mirroring, xattr transfer, overwritten target cleanup, event logging, and modification-event flushing.

## Important APIs, Types, and Functions
`lock()` references source and destination dirs, computes deterministic locks for source/destination dir IDs, parent/name pairs, directory child IDs, local source/target file inodes, and destination hash directories during resync. `processIncoming()` delegates to mirrored processing and updates `MetaOpCounter_RENAME`. `executeLocally()` gathers event context, invokes `movingPerform()`, fixes source timestamps, logs file events, and emits modification events. `movingPerform()` selects `renameInSameDir()`, `renameDir()`, or `renameFile()`. Remote helpers send `MovingFileInsertMsg`, `MovingDirInsertMsg`, `UpdateDirParentMsg`, `UnlinkLocalFileInodeMsg`, and `StatMsg`.

## Control Flow, State, and Persistence
Same-directory rename is performed in `MetaStore::renameInSameDir()` and then deletes overwritten chunks/inodes as needed. Directory moves serialize the source dentry, insert it remotely if not on mirror secondary, remove the source dentry, and update the moved directory inode parent. File moves serialize source inode/dentry state, optionally streams xattrs, inserts remotely, unlinks the source dentry, and completes the move in `MetaStore`. Overwritten destination files are cleaned either via chunk unlink for inlined inodes or remote inode unlink for non-inlined inodes.

## Dependencies and Integration Points
Depends on `MetaStore`, `DirInode`, `DirEntry`, `MessagingTk`, `MovingFileInsertMsgEx`, `MovingDirInsertMsgEx`, `UpdateDirParentMsg`, `UnlinkLocalFileInodeMsgEx`, `MsgHelperUnlink`, `MsgHelperXAttr`, `MsgHelperStat`, `FileEventLogger`, `ModificationEventFlusher`, buddy mappings, and target state stores.

## Risks and Test Signals
Rename has broad consistency risk: partial remote insert before source unlink, update-parent failure after directory move, overwritten inode cleanup failures hidden from clients, cross-node xattr streaming errors, lock-order regressions, remote-owner hardlink counts for event logging, and mirror-secondary shortcuts. Tests should cover same-directory replace, file move across owners, directory move, overwrite inlined/non-inlined targets, hardlinks, xattrs, buddy primary/secondary replay, failed remote insert, failed source unlink after remote insert, and modification/file event outputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/moving/RenameV2MsgEx.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/moving/RenameV2MsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/moving/RenameV2MsgEx.h

## Purpose
Declares the mirrored rename message and its composite lock set.

## Important APIs, Types, and Functions
`RenameV2Locks` owns the destination-file hash lock, source/destination name locks, source/destination directory locks, source file locks for file and directory cases, and overwritten-file lock. It is move-only and supports `swap()`. `RenameV2MsgEx` inherits `MirroredMessage<RenameMsg, RenameV2Locks>`, overrides processing, locking, execution, mirror status, forwarding, and secondary response handling. Private helpers split same-dir rename, directory rename, file rename, remote insert/unlink, directory parent update, remote inode unlink, and link-count lookup.

## Control Flow, State, and Persistence
The header makes rename a single mirrored state-changing operation with many possible sub-operations. `isMirrored()` uses the source directory mirror flag, so the initiating source side governs mirrored replay.

## Dependencies and Integration Points
Includes rename request/response messages, `MirroredMessage`, `DirEntry`, and `MetaStore`. It coordinates with moving and creating message helpers declared elsewhere.

## Risks and Test Signals
The lock struct is central to deadlock avoidance. Tests should verify move-only behavior compiles, lock acquisition ordering for same/different dirs and same/different inode IDs, and secondary response error mapping from `RenameRespMsg`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/moving/RenameV2MsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/quota/SetExceededQuotaMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/quota/SetExceededQuotaMsgEx.cpp

## Purpose
Receives quota-exceeded state from management and updates metadata-server exceeded-quota stores for all targets in a storage pool.

## Important APIs, Types, and Functions
`processIncoming()` checks `QuotaEnableEnforcement`, resolves the requested `StoragePool`, iterates pool targets, retrieves each `ExceededQuotaStore`, calls `updateExceededQuota(getExceededQuotaIDs(), getQuotaDataType(), getExceededType())`, and sends `SetExceededQuotaRespMsg`.

## Control Flow, State, and Persistence
The operation mutates in-memory quota-exceeded state per target. It returns `UNKNOWNPOOL` for missing pools, `UNKNOWNTARGET` for missing exceeded-quota stores, and `INTERNAL` when local quota enforcement is disabled while the sender expects it.

## Dependencies and Integration Points
Depends on app config, `StoragePoolStore`, `StoragePool`, `ExceededQuotaStores`, quota data types, logging, and the quota response message. Lookup/create paths consult these stores for enforcement.

## Risks and Test Signals
Risks include config skew between management and metadata daemons, partial updates across targets when one store is missing, and stale quota state after pool membership changes. Tests should cover disabled enforcement, missing pool, missing target store, user/group quota IDs, and pool with multiple targets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/quota/SetExceededQuotaMsgEx.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/quota/SetExceededQuotaMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/quota/SetExceededQuotaMsgEx.h

## Purpose
Declares the exceeded-quota update message extension.

## Important APIs, Types, and Functions
`SetExceededQuotaMsgEx` inherits `SetExceededQuotaMsg` and overrides `processIncoming()`.

## Control Flow, State, and Persistence
The header exposes a non-mirrored control message whose implementation updates quota caches.

## Dependencies and Integration Points
Includes the common quota request message and BeeGFS common types. It is sent by management-side quota propagation.

## Risks and Test Signals
Header risk is low; tests should validate implementation response codes and that message fields map correctly into quota-store updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/quota/SetExceededQuotaMsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/msghelpers/MsgHelperClose.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/msghelpers/MsgHelperClose.cpp

## Purpose
Provides shared close-file helpers for metadata messages, coordinating session-store removal, storage target close RPCs, dynamic attribute updates, inode reference close, disposal decisions, and mirrored disposal behavior.

## Important APIs, Types, and Functions
`closeFile()` wraps `closeSessionFile()`, `closeChunkFile()`, timestamp capture, and `MetaStore::closeFile()`, returning whether a disposal file should be unlinked. `closeSessionFile()` removes a session file by owner FD, or recovers by opening metadata when the meta-server lost session state. `closeChunkFile()` chooses sequential or parallel storage close. `closeChunkFileSequential()` sends `CloseChunkFileMsg` per target and applies returned dynamic attributes. `closeChunkFileParallel()` schedules `CloseChunkFileWork` on the communication slave queue. `unlinkDisposableFile()` deletes a file from normal or mirrored disposal directories unless mirrored disposal GC is configured.

## Control Flow, State, and Persistence
Session state is removed from normal or mirrored `SessionStore`. Storage close RPCs return size/block/time dynamic attributes that are applied to the inode before the inode is closed in `MetaStore`. If hardlinks and references reach zero, callers can unlink the disposal file. Disposal unlink mutates metadata through `MsgHelperUnlink`.

## Dependencies and Integration Points
Depends on session stores, `SessionTk`, `CloseChunkFileMsg/RespMsg`, storage target mapping/state stores, `CloseChunkFileWork`, `MetaStore`, `MsgHelperUnlink`, stripe patterns, path info, and mirrored disposal configuration.

## Risks and Test Signals
Risks include session recovery opening with read/write when original flags are unknown, storage close errors after session removal, ignored `INUSE` target errors, partial dynamic attributes, and delayed mirrored disposal cleanup. Tests should cover missing session recovery, sequential and parallel close, buddy-mirror pattern close, max-used-node `-1`, dynamic attribute propagation, timestamp capture, and disposal unlink gating.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/msghelpers/MsgHelperClose.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/msghelpers/MsgHelperClose.h -->
# sources/distributed-fs/beegfs/meta/source/net/msghelpers/MsgHelperClose.h

## Purpose
Declares static close helpers used by metadata close and cleanup messages.

## Important APIs, Types, and Functions
Public methods are `closeFile()`, `closeSessionFile()`, `closeChunkFile()`, and `unlinkDisposableFile()`. Private methods are `closeChunkFileSequential()` and `closeChunkFileParallel()`. The class is non-instantiable through a private constructor.

## Control Flow, State, and Persistence
The signatures expose caller-owned outputs for disposal unlink, hardlink count, last-writer state, dynamic attributes, and mirrored timestamps. Persistent effects are delegated to implementation helpers and `MetaStore`.

## Dependencies and Integration Points
Includes common types and `MetaStore`. Integrates with session/opening messages and storage target close work.

## Risks and Test Signals
Callers must pass valid output pointers for required values. Tests should verify all optional outputs are filled only when expected and default/null dynamic attribute pointers are safe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/msghelpers/MsgHelperClose.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/msghelpers/MsgHelperLocking.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/msghelpers/MsgHelperLocking.cpp

## Purpose
Provides shared lock-message helpers, especially recovery of lost file sessions and append-style flock updates.

## Important APIs, Types, and Functions
`trySesssionRecovery()` logs recovery, opens the file with read/write access, builds a `SessionFile`, attempts `SessionFileStore::addAndReferenceRecoverySession()`, and compensates by closing metadata if the owner FD is already reused. `flockAppend()` references the client session and owner FD, ignores unlocks for missing sessions, handles lock-cancel on existing files without full recovery, recovers sessions for lock requests, calls `FileInode::flockAppend()`, and notifies waiters through `LockingNotifier`.

## Control Flow, State, and Persistence
The helper mutates session stores and file lock state. Recovery reopens metadata because client lock requests can imply a session that vanished after metadata-server restart. Failed recovery closes the reopened inode to avoid leaked references.

## Dependencies and Integration Points
Depends on `SessionStore`, `SessionFileStore`, `SessionFile`, `MetaStore`, `EntryLockDetails`, `LockingNotifier`, client IDs, and mirrored session selection based on `EntryInfo`.

## Risks and Test Signals
Risks include the misspelled API name `trySesssionRecovery`, recovering with broader read/write access than originally used, races where owner FD is reused, and lock cancel behavior without session state. Tests should cover missing session unlock, cancel, recover success/failure, WOULD_BLOCK locks, waiter notifications, and mirrored sessions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/msghelpers/MsgHelperLocking.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/msghelpers/MsgHelperLocking.h -->
# sources/distributed-fs/beegfs/meta/source/net/msghelpers/MsgHelperLocking.h

## Purpose
Declares static helpers for metadata file locking messages.

## Important APIs, Types, and Functions
`MsgHelperLocking` exposes `trySesssionRecovery()` and `flockAppend()` and hides construction. The header depends on `EntryInfo`, `StorageErrors`, and `SessionFileStore`.

## Control Flow, State, and Persistence
The signatures show that recovery returns a referenced `SessionFile*` to the caller on success and that flock append mutates lock state through `EntryLockDetails`.

## Dependencies and Integration Points
Used by flock message handlers and session recovery paths. Integrates with file session stores and lock detail types.

## Risks and Test Signals
Tests should verify caller ownership/reference expectations for `outSessionFile` and that `flockAppend()` maps lock-grant state to `SUCCESS` or `WOULDBLOCK`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/msghelpers/MsgHelperLocking.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/msghelpers/MsgHelperMkFile.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/msghelpers/MsgHelperMkFile.cpp

## Purpose
Centralizes metadata file creation, stripe pattern allocation/validation, and modification-event emission for file-create handlers.

## Important APIs, Types, and Functions
`MsgHelperMkFile::mkFile()` accepts a parent directory, `MkFileDetails`, preferred targets, stripe sizing, optional prebuilt stripe pattern for secondary replay, optional remote storage target info, output entry/inode data, and storage pool ID. It creates a stripe pattern when absent, rejects empty target sets, calls `MetaStore::mkNewMetaFile()`, and emits `ModificationEvent_FILECREATED` when enabled.

## Control Flow, State, and Persistence
The function persists new metadata through `MetaStore::mkNewMetaFile()`. Stripe pattern ownership transfers to a `unique_ptr` when creation proceeds; invalid patterns are deleted before returning. Modification events are side effects after metadata creation attempt, keyed by output entry ID when available.

## Dependencies and Integration Points
Depends on `DirInode::createFileStripePattern()`, `MetaStore`, `MkFileDetails`, `StripePattern`, `RemoteStorageTarget`, `StoragePoolId`, and `ModificationEventFlusher`. Used by `MkFileMsgEx` and `LookupIntentMsgEx`.

## Risks and Test Signals
Risks include null/empty stripe patterns, secondary replay requiring exact primary pattern, and event emission when creation failed but `outEntryInfo` contains stale data. Tests should cover default pattern creation, provided pattern ownership, empty target failure, RST propagation, storage-pool selection, and event logging only on successful creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/msghelpers/MsgHelperMkFile.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/msghelpers/MsgHelperMkFile.h -->
# sources/distributed-fs/beegfs/meta/source/net/msghelpers/MsgHelperMkFile.h

## Purpose
Declares the static metadata file creation helper.

## Important APIs, Types, and Functions
`MsgHelperMkFile::mkFile()` is the sole public method and takes parent directory, create details, target/pattern parameters, optional `RemoteStorageTarget`, output entry/inode data, and optional storage pool ID. Construction is disabled by a private constructor.

## Control Flow, State, and Persistence
The header establishes ownership-sensitive parameters: callers may pass a raw `StripePattern*` that the implementation assumes ownership of on success path.

## Dependencies and Integration Points
Includes storage errors, `MetaStore`, and `MkFileDetails`; forward-declares the create details struct. Used by file-create message handlers.

## Risks and Test Signals
Tests and call sites should verify raw pointer ownership expectations and that optional output pointers can be null only where `MetaStore::mkNewMetaFile()` supports it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/msghelpers/MsgHelperMkFile.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/msghelpers/MsgHelperOpen.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/msghelpers/MsgHelperOpen.cpp

## Purpose
Provides the metadata open helper, including compatibility checks for stripe chunk size and optional truncate-on-open of storage chunks.

## Important APIs, Types, and Functions
`openFile()` checks whether `OPENFILE_ACCESS_TRUNC` requires chunk truncation, opens metadata via `openMetaFile()`, validates stripe chunk size against minimum and power-of-two constraints, optionally calls `MsgHelperTrunc::truncChunkFile()` for truncation on the primary, and compensates with `openMetaFileCompensate()` on later errors. `openMetaFile()` wraps `MetaStore::openFile()`. `openMetaFileCompensate()` closes the inode reference through `MetaStore::closeFile()`.

## Control Flow, State, and Persistence
Opening mutates inode reference/open state in `MetaStore`. Truncate-on-open mutates storage chunk files and dynamic attributes but does not run on secondary. Invalid legacy chunk sizes are rejected after opening and compensated to avoid corrupting files.

## Dependencies and Integration Points
Depends on `MsgHelperTrunc`, `MetaStore`, `StripePattern`, `MathTk`, `OPENFILE_ACCESS_TRUNC`, quota flag propagation, and metadata open access checks. Used by lookup/open and locking recovery.

## Risks and Test Signals
Risks include compensation failures, primary/secondary truncation divergence if called incorrectly, legacy chunk-size refusal, and deciding truncation need from pre-open stat. Tests should cover normal open, invalid chunk size, truncate needed/not needed, truncate failure compensation, bypass access check handling, and secondary open without chunk truncation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/msghelpers/MsgHelperOpen.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/msghelpers/MsgHelperOpen.h -->
# sources/distributed-fs/beegfs/meta/source/net/msghelpers/MsgHelperOpen.h

## Purpose
Declares static open helpers for metadata file open operations.

## Important APIs, Types, and Functions
`MsgHelperOpen::openFile()` is public and returns a `MetaFileHandle` on success. Private helpers `openMetaFile()` and `openMetaFileCompensate()` wrap `MetaStore` open/close behavior. The class is non-instantiable.

## Control Flow, State, and Persistence
The public signature exposes quota, access-check bypass, message user ID, output inode handle, and secondary flag, making callers responsible for later session insertion and close.

## Dependencies and Integration Points
Includes `EntryInfo`, `MetaStore`, and `MetadataEx`. Used by lookup-intent, explicit open messages, and session recovery.

## Risks and Test Signals
Tests should verify output handle is set only on success and that callers close or transfer ownership after successful open.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/msghelpers/MsgHelperOpen.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/msghelpers/MsgHelperStat.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/msghelpers/MsgHelperStat.cpp

## Purpose
Provides stat and dynamic-attribute refresh helpers for metadata files, retrieving up-to-date size/block/time data from storage targets when metadata marks dynamic attributes stale.

## Important APIs, Types, and Functions
`stat()` wraps `MetaStore::stat()`, handles `DYNAMICATTRIBSOUTDATED` by calling `refreshDynAttribs()` and retrying, and logs benign missing metadata races. `refreshDynAttribs()` references the file inode, chooses sequential or parallel target refresh based on target count, optionally persists refreshed metadata, and releases the inode. `refreshDynAttribsSequential()` sends `GetChunkFileAttribsMsg` per target, including buddy-mirror flags and mirror routing. `refreshDynAttribsParallel()` schedules `GetChunkFileAttribsWork` across the communication slave queue.

## Control Flow, State, and Persistence
Refresh mutates in-memory inode dynamic attributes and optionally persists them to disk. Stat itself may become a mutating operation when attributes are stale. Errors from individual targets are logged and propagated after updating whatever dynamic attributes were returned.

## Dependencies and Integration Points
Depends on `MetaStore`, `FileInode`, stripe patterns, storage target mappers/states, storage buddy group mapper, `GetChunkFileAttribsMsg/RespMsg`, `GetChunkFileAttribsWork`, and `SynchronizedCounter`. Used by stat, lookup intent, rename event link counts, and revalidation.

## Risks and Test Signals
Risks include indefinite stale-attribute loops avoided by accepting the second stale result, partial target failures leaving mixed dynamic attributes, buddy-mirror primary-only reads, and persistence failure after successful refresh. Tests should cover stale refresh retry, sequential/parallel paths, buddy-mirror target routing, missing metadata race logging, make-persistent failure, and dynamic attribute vector sizing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/msghelpers/MsgHelperStat.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/msghelpers/MsgHelperStat.h -->
# sources/distributed-fs/beegfs/meta/source/net/msghelpers/MsgHelperStat.h

## Purpose
Declares static stat and dynamic-attribute refresh helpers.

## Important APIs, Types, and Functions
`MsgHelperStat::stat()` returns `StatData` and optional parent node/entry IDs. `refreshDynAttribs()` refreshes and optionally persists dynamic attributes. Private `refreshDynAttribsSequential()` and `refreshDynAttribsParallel()` implement target communication strategies.

## Control Flow, State, and Persistence
The header exposes that stat may depend on storage target communication through refresh. `makePersistent` controls whether refreshed attributes are written to disk.

## Dependencies and Integration Points
Includes common types, `MetaStore`, and `MetadataEx`. Used by metadata stat and combined intent operations.

## Risks and Test Signals
Tests should check optional parent output pointer combinations and that refresh helpers are selected based on stripe pattern target count and mirror type.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/msghelpers/MsgHelperStat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/msghelpers/MsgHelperTrunc.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/msghelpers/MsgHelperTrunc.cpp

## Purpose
Provides file truncation helpers that update storage chunk files, inode dynamic attributes, and persistent metadata.

## Important APIs, Types, and Functions
`truncFile()` references a file, calls `truncChunkFile()`, writes inode metadata to disk, and releases it. `truncChunkFile()` chooses sequential or parallel execution. `truncChunkFileSequential()` sends `TruncLocalFileMsg` to each target with a node-local truncation offset and optional quota user/group data. `truncChunkFileParallel()` schedules `TruncChunkFileWork` for all targets. `isTruncChunkRequired()` stats the file before open to skip unnecessary truncation. `getNodeLocalOffset()` and `getNodeLocalTruncPos()` compute per-stripe target truncation positions.

## Control Flow, State, and Persistence
Storage targets are truncated first, returned dynamic attributes are applied to the inode, and `truncFile()` persists inode metadata regardless of local result. Parallel and sequential paths both update `dynAttribs` and inode state. Quota data is propagated to storage truncation requests when requested.

## Dependencies and Integration Points
Depends on `MetaStore`, `TruncLocalFileMsg/RespMsg`, `TruncChunkFileWork`, stripe patterns, target mappers/states, path info, dynamic attributes, and quota user/group data. Used by `TruncFileMsgEx` and truncate-on-open in `MsgHelperOpen`.

## Risks and Test Signals
Risks include per-target offset math, partial truncation across targets, persisting metadata after truncation failure, quota propagation mismatch, and reliance on power-of-two chunk sizes. Tests should cover offset calculations for multiple stripe layouts, zero truncation, sequential/parallel behavior, target failures, buddy-mirror pattern routing through work objects, and `isTruncChunkRequired()` races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/msghelpers/MsgHelperTrunc.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/msghelpers/MsgHelperTrunc.h -->
# sources/distributed-fs/beegfs/meta/source/net/msghelpers/MsgHelperTrunc.h

## Purpose
Declares static truncation helpers for metadata file operations.

## Important APIs, Types, and Functions
Public methods are `truncFile()`, `truncChunkFile()`, and `isTruncChunkRequired()`. Private methods implement sequential/parallel target truncation and local stripe offset calculations.

## Control Flow, State, and Persistence
The header distinguishes full truncation that persists inode metadata (`truncFile`) from chunk truncation that only updates in-memory inode attributes (`truncChunkFile`).

## Dependencies and Integration Points
Includes common types and `MetaStore`. Used by truncate messages and open-with-truncate handling.

## Risks and Test Signals
Offset helper correctness is central. Unit tests should directly exercise `getNodeLocalTruncPos()` through public truncation scenarios or friend/test hooks if available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/msghelpers/MsgHelperTrunc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/msghelpers/MsgHelperUnlink.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/msghelpers/MsgHelperUnlink.cpp

## Purpose
Provides shared unlink helpers for metadata dentries, file inodes, storage chunks, and disposal fallback.

## Important APIs, Types, and Functions
`unlinkFile()` wraps `unlinkMetaFile()` and `unlinkChunkFiles()`. `unlinkMetaFile()` calls `MetaStore::unlinkFile()` and emits `ModificationEvent_FILEREMOVED`. `unlinkFileInode()` decrements hardlink count and returns an inode when link count reaches zero. `unlinkChunkFiles()` calls `unlinkChunkFilesInternal()` and inserts the inode into the disposable store if chunk deletion fails. `unlinkChunkFileSequential()` sends `UnlinkLocalFileMsg` to each target and ignores unknown node/target errors. `unlinkChunkFileParallel()` schedules `UnlinkChunkFileWork` for each target.

## Control Flow, State, and Persistence
Metadata unlink happens first; chunk unlink is required only when an unlinked inode object is returned. Storage deletion failures do not recreate metadata; instead the inode is persisted into disposal for later retry. Modification events are emitted based on metadata unlink entry ID.

## Dependencies and Integration Points
Depends on `MetaStore`, `DirInode`, `FileInode`, `ModificationEventFlusher`, `UnlinkLocalFileMsg/RespMsg`, target mappers/states, `UnlinkChunkFileWork`, `MultiWorkQueue`, and disposal-store insertion. Used by unlink, rename overwrite cleanup, close disposal, and moving rollback.

## Risks and Test Signals
Risks include emitting removal events after failed unlink if `entryInfo` is stale, suppressing unknown target errors, disposal insertion failure after chunk delete failure, and partial parallel unlink. Tests should cover open-file disposal, hardlink decrement, inlined/non-inlined inode cleanup, sequential/parallel storage deletion, unknown target suppression, disposal fallback, and modification-event conditions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/msghelpers/MsgHelperUnlink.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/msghelpers/MsgHelperUnlink.h -->
# sources/distributed-fs/beegfs/meta/source/net/msghelpers/MsgHelperUnlink.h

## Purpose
Declares static unlink helpers for metadata and storage cleanup.

## Important APIs, Types, and Functions
Public methods are `unlinkFile()`, `unlinkMetaFile()`, `unlinkFileInode()`, `unlinkChunkFiles()`, and inline-public `unlinkChunkFilesInternal()`. Private methods implement sequential/parallel chunk deletion and an unused/undeclared-in-implementation `insertDisposableFile(FileInode&)` declaration.

## Control Flow, State, and Persistence
The signatures expose ownership transfer: `unlinkChunkFiles(FileInode*)` consumes and deletes or stores the raw inode pointer. `unlinkMetaFile()` may return a `unique_ptr<FileInode>` requiring caller cleanup.

## Dependencies and Integration Points
Includes `Path`, common types, and `MetaStore`. Used widely by creating, moving, close, and helper paths.

## Risks and Test Signals
Callers must respect ownership semantics to avoid leaks or double deletes. Tests should verify `unique_ptr` output behavior and that `unlinkChunkFilesInternal()` remains safe when called directly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/msghelpers/MsgHelperUnlink.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/msghelpers/MsgHelperXAttr.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/msghelpers/MsgHelperXAttr.cpp

## Purpose
Provides shared extended-attribute operations for files, directories, and streamed xattr transfer during mirroring/resync/rename.

## Important APIs, Types, and Functions
`listxattr()`, `getxattr()`, `removexattr()`, and `setxattr()` choose between non-inlined regular-file inode operations and directory/dentry operations through `DirInode`. `MAX_VALUE_SIZE` caps values returned through normal net messages. `StreamXAttrState::streamXattrFn()` is a hook adapter. `streamXattr()` sends name length, name, value length, and value for each xattr, ending with zero or `-1` on error. `readNextXAttr()` reads the same stream with short timeouts and returns `AGAIN` for an xattr record, `SUCCESS` for end, or an error.

## Control Flow, State, and Persistence
Basic operations mutate or read xattrs in metadata inode/dentry storage. Stream operations are socket-level protocols used after a normal message request; they do not send a full net message per attribute. For directory entries and inlined file dentries, operations reference the containing directory; for non-inlined regular files, they reference the file inode.

## Dependencies and Integration Points
Depends on `MetaStore`, `DirInode`, `FileInode`, `XAttrTk`, POSIX xattr limits, sockets, app config timeouts, and user-xattr prefixing. Used by xattr messages, rename xattr copy, and raw inode resync.

## Risks and Test Signals
Risks include value-size limits differing between normal messages and stream mode, communication timeout mid-stream, range errors for oversized names/values, empty value handling with `&value[0]`, and correct reference/release paths for each entry type. Tests should cover all entry types, max value enforcement, stream success/end/error markers, oversized name/value, disabled xattr config callers, and zero-length values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/msghelpers/MsgHelperXAttr.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/msghelpers/MsgHelperXAttr.h -->
# sources/distributed-fs/beegfs/meta/source/net/msghelpers/MsgHelperXAttr.h

## Purpose
Declares static xattr helpers and the socket streaming state object.

## Important APIs, Types, and Functions
`MsgHelperXAttr` exposes `listxattr()`, `getxattr()`, `removexattr()`, `setxattr()`, constants `CURRENT_DIR_FILENAME` and `MAX_VALUE_SIZE`, and nested `StreamXAttrState`. `StreamXAttrState` can be constructed from an `EntryInfo` plus names or from a filesystem path plus names, exposes `streamXattrFn()` for hook registration, and `readNextXAttr()` for receivers.

## Control Flow, State, and Persistence
The nested state stores either an entry pointer or a raw path and a list of names. Its private `streamXattr()` sends the records when invoked by a registered stream-out hook.

## Dependencies and Integration Points
Forward-declares `EntryInfo` and `Socket`; includes storage errors. Used by xattr messages, moving, and mirroring code paths.

## Risks and Test Signals
The `EntryInfo*` in stream state must outlive streaming. Tests should cover both constructors, hook invocation, and receiver interpretation of `SUCCESS` as stream end versus `AGAIN` as record received.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/msghelpers/MsgHelperXAttr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/nodes/MetaNodeOpStats.h -->
# sources/distributed-fs/beegfs/meta/source/nodes/MetaNodeOpStats.h

## Purpose
Defines metadata operation accounting by client IP and user ID for metadata-server filesystem operations.

## Important APIs, Types, and Functions
`MetaNodeOpStats` derives from `NodeOpStats` and exposes `updateNodeOp(const IPAddress&, MetaOpCounterTypes, unsigned)`. It takes a read lock, looks up counters by 128-bit client IP and user ID, upgrades to a write lock when either key is absent, inserts `MetaOpCounter` instances as needed, then increments both counters.

## Control Flow, State, and Persistence
State lives in inherited `clientCounterMap` and `userCounterMap`; no disk persistence happens here. The function intentionally allows a race between read unlock and write lock because duplicate insertion is a no-op via map insert semantics. Counters are updated while the lock is held.

## Dependencies and Integration Points
Depends on `NodeOpStats`, `MetaOpCounter`, `SafeRWLock`, `Node`, `IPAddress`, and `MetaOpCounterTypes`. Called by message handlers such as unlink, listdir, find-owner, lookup-intent, and rename.

## Risks and Test Signals
The read-to-write upgrade path uses iterators found before unlocking; after reacquiring the write lock, stale end/non-end checks can be risky if the maps changed. Tests should stress concurrent first-use updates for the same and different IP/user pairs, IPv6 address conversion, and correct increments for both client and user counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/nodes/MetaNodeOpStats.h -->
