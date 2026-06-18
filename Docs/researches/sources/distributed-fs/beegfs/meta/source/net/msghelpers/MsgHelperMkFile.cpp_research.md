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
