<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/creating/MkFileWithPatternMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/creating/MkFileWithPatternMsgEx.cpp

Purpose: Implements the MkFileWithPatternMsgEx server-side message extension: mirrored file creation handler that honors an explicit caller-provided stripe pattern.

Important APIs/types/functions: Implemented entry points: std::tuple<FileIDLock, ParentNameLock, FileIDLock> MkFileWithPatternMsgEx::lock( EntryLockStore& store); bool MkFileWithPatternMsgEx::processIncoming(ResponseContext& ctx); std::unique_ptr<MirroredMessageResponseState> MkFileWithPatternMsgEx::executeLocally( ResponseContext& ctx, bool isSecondary); FhgfsOpsErr MkFileWithPatternMsgEx::mkFile(const EntryInfo* parentInfo, MkFileDetails& mkDetails, EntryInfo* outEntryInfo, FileInodeStoreData& inodeDiskData); FhgfsOpsErr MkFileWithPatternMsgEx::mkMetaFile(DirInode& dir, MkFileDetails& mkDetails, EntryInfo* outEntryInfo, FileInodeStoreData& inodeDiskData); void MkFileWithPatternMsgEx::forwardToSecondary(ResponseContext& ctx).

Control flow: Control flow enters processIncoming(), delegates to BaseType/MirroredMessage, obtains the declared locks, executes the local primary or secondary branch, serializes a ResponseState, and forwards the same operation to the secondary when the entry is mirrored.

State and persistence behavior: persists metadata through MetaStore, inode objects, dentries, xattrs, or stripe-pattern updates.

Dependencies and integration points: Direct includes: <common/net/message/storage/creating/MkFileMsg.h>, <common/net/message/storage/creating/MkFileRespMsg.h>, <program/Program.h>, <common/net/message/storage/creating/UnlinkLocalFileMsg.h>, <common/net/message/storage/creating/UnlinkLocalFileRespMsg.h>, <common/storage/striping/StripePattern.h>, <common/toolkit/MathTk.h>, <common/toolkit/MessagingTk.h>, <components/FileEventLogger.h>, <net/msghelpers/MsgHelperMkFile.h>, ... Integration dependencies: uses the global App singleton to reach MetaStore, node stores, syncers, sessions, or statistics; integrates with MetaStore/DirInode/FileInode persistence; uses EntryLockStore locks to serialize metadata mutation or query with writers; participates in buddy-mirror primary/secondary replay through MirroredMessage; delegates protocol-specific work to BeeGFS MsgHelper utilities; emits file/modification events when enabled.

Risks and test signals: mirror replay must preserve lock order, response semantics, and idempotence between primary and secondary referenced metadata objects must be released on every error path Explicit patterns need validation for target existence, buddy-group primary mapping, minimum targets, and power-of-two chunk size.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/creating/MkFileWithPatternMsgEx.cpp -->
