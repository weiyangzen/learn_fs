<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/nodes/GenericDebugMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/nodes/GenericDebugMsgEx.cpp

Purpose: Implements the GenericDebugMsgEx server-side message extension: server-side generic debug command dispatcher for metadata nodes, including live diagnostics and guarded metadata inspection/mutation commands.

Important APIs/types/functions: Implemented entry points: bool GenericDebugMsgEx::processIncoming(ResponseContext& ctx); std::string GenericDebugMsgEx::processCommand(); std::string GenericDebugMsgEx::processOpListFileAppendLocks(std::istringstream& commandStream); std::string GenericDebugMsgEx::processOpListFileEntryLocks(std::istringstream& commandStream); std::string GenericDebugMsgEx::processOpListFileRangeLocks(std::istringstream& commandStream); std::string GenericDebugMsgEx::processOpListOpenFiles(std::istringstream& commandStream); std::string GenericDebugMsgEx::processOpReferenceStatistics(std::istringstream& commandStream); std::string GenericDebugMsgEx::processOpCacheStatistics(std::istringstream& commandStream); ...

Control flow: Control flow is request/response style: processIncoming() reads fields from the decoded message, gathers data or updates App-managed stores, and sends the matching response message through ResponseContext.

State and persistence behavior: sets syncer force flags that affect later background refresh/publication cycles; persists metadata through MetaStore, inode objects, dentries, xattrs, or stripe-pattern updates; updates or reads session-scoped open-file, lock, or version state.

Dependencies and integration points: Direct includes: <common/net/message/nodes/GenericDebugRespMsg.h>, <common/net/msghelpers/MsgHelperGenericDebug.h>, <common/storage/quota/Quota.h>, <common/toolkit/MessagingTk.h>, <program/Program.h>, <session/SessionStore.h>, "GenericDebugMsgEx.h". Integration dependencies: uses the global App singleton to reach MetaStore, node stores, syncers, sessions, or statistics; integrates with MetaStore/DirInode/FileInode persistence; uses EntryLockStore locks to serialize metadata mutation or query with writers; delegates protocol-specific work to BeeGFS MsgHelper utilities.

Risks and test signals: referenced metadata objects must be released on every error path wire compatibility depends on sending the exact response message type expected by management clients Because some commands mutate dentries or inode fields, operational exposure and argument validation are the main risks; tests should exercise malformed command strings and release every referenced inode or directory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/nodes/GenericDebugMsgEx.cpp -->
