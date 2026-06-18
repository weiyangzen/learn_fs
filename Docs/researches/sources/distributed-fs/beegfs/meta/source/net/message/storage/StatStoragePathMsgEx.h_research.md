<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/StatStoragePathMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/StatStoragePathMsgEx.h

Purpose: Declares the StatStoragePathMsgEx server-side message extension: storage-path stat handler for local metadata storage capacity and inode availability.

Important APIs/types/functions: Declarations/types: class StatStoragePathMsgEx : public StatStoragePathMsg.

Control flow: The header exposes a narrow processIncoming() override; dispatch is supplied by NetMessageFactory and the implementation builds the response synchronously.

State and persistence behavior: does not define standalone persistence; state lives in App-owned services and common message payloads.

Dependencies and integration points: Direct includes: <common/storage/StorageErrors.h>, <common/net/message/storage/StatStoragePathMsg.h>.

Risks and test signals: Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/StatStoragePathMsgEx.h -->
