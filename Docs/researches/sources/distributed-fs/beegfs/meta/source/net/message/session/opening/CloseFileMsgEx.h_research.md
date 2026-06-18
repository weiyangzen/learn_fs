<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/session/opening/CloseFileMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/session/opening/CloseFileMsgEx.h

Purpose: Declares the CloseFileMsgEx server-side message extension: mirrored close-file handler that removes a session file, updates inode state, and may complete deferred unlink/disposal work.

Important APIs/types/functions: Declarations/types: class CloseFileMsgEx : public MirroredMessage<CloseFileMsg, FileIDLock>; typedef ErrorCodeResponseState<CloseFileRespMsg, NETMSGTYPE_CloseFile> ResponseState;.

Control flow: The header wires this message into the mirrored-message template, names its response-state type, exposes lock(), executeLocally(), isMirrored(), and forward-to-secondary hooks where needed.

State and persistence behavior: updates or reads session-scoped open-file, lock, or version state.

Dependencies and integration points: Direct includes: <common/storage/StorageErrors.h>, <common/net/message/session/opening/CloseFileMsg.h>, <common/net/message/session/opening/CloseFileRespMsg.h>, <net/message/MirroredMessage.h>, <session/EntryLock.h>, <storage/FileInode.h>. Integration dependencies: uses EntryLockStore locks to serialize metadata mutation or query with writers; participates in buddy-mirror primary/secondary replay through MirroredMessage.

Risks and test signals: mirror replay must preserve lock order, response semantics, and idempotence between primary and secondary The early-response close path makes ordering important: session removal, write counters, inode persistence, disposal unlink, and secondary mirroring must agree even if clients disconnect.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/session/opening/CloseFileMsgEx.h -->
