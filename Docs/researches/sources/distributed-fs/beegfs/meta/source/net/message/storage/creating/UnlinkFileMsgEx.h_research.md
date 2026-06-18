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
