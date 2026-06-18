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
