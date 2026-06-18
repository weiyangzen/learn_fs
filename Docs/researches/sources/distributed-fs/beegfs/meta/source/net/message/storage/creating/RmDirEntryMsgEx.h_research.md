<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/creating/RmDirEntryMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/creating/RmDirEntryMsgEx.h

Purpose: Declares the RmDirEntryMsgEx server-side message extension: non-mirrored administrative removal handler for removing a directory entry directly from a parent directory.

Important APIs/types/functions: Declarations/types: class RmDirEntryMsgEx : public RmDirEntryMsg.

Control flow: The header exposes a narrow processIncoming() override; dispatch is supplied by NetMessageFactory and the implementation builds the response synchronously.

State and persistence behavior: does not define standalone persistence; state lives in App-owned services and common message payloads.

Dependencies and integration points: Direct includes: <common/storage/StorageErrors.h>, <common/net/message/storage/creating/RmDirEntryMsg.h>, <storage/MetaStore.h>. Integration dependencies: integrates with MetaStore/DirInode/FileInode persistence.

Risks and test signals: Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/creating/RmDirEntryMsgEx.h -->
