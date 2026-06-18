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
