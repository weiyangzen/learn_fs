<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/session/opening/OpenFileMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/session/opening/OpenFileMsgEx.h

Purpose: Declares the OpenFileMsgEx server-side message extension: mirrored open-file handler that references metadata, checks access, and registers the open file in the session store.

Important APIs/types/functions: Declarations/types: class OpenFileResponseState : public MirroredMessageResponseState; class OpenFileMsgEx : public MirroredMessage<OpenFileMsg, FileIDLock>; typedef OpenFileResponseState ResponseState;.

Control flow: The header wires this message into the mirrored-message template, names its response-state type, exposes lock(), executeLocally(), isMirrored(), and forward-to-secondary hooks where needed.

State and persistence behavior: updates or reads session-scoped open-file, lock, or version state.

Dependencies and integration points: Direct includes: <common/storage/StorageErrors.h>, <common/net/message/session/opening/OpenFileMsg.h>, <common/net/message/session/opening/OpenFileRespMsg.h>, <storage/DirInode.h>, <storage/FileInode.h>, <net/message/MirroredMessage.h>, <session/EntryLock.h>. Integration dependencies: uses EntryLockStore locks to serialize metadata mutation or query with writers; participates in buddy-mirror primary/secondary replay through MirroredMessage.

Risks and test signals: mirror replay must preserve lock order, response semantics, and idempotence between primary and secondary Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/session/opening/OpenFileMsgEx.h -->
