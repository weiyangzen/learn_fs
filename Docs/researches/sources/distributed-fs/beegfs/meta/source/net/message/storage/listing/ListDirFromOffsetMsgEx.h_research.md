<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/listing/ListDirFromOffsetMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/listing/ListDirFromOffsetMsgEx.h

## Purpose
Declares the metadata-server extension for offset-based directory listing.

## Important APIs, Types, and Functions
`ListDirFromOffsetMsgEx` inherits `ListDirFromOffsetMsg`, overrides `processIncoming()`, and owns private `listDirIncremental()` for the actual `MetaStore`/`DirInode` read.

## Control Flow, State, and Persistence
The header shows this is a non-mirrored, read-only request. State is limited to response list construction and offset calculation in the implementation.

## Dependencies and Integration Points
Includes common entry info, storage errors, `MetaStore`, and the listdir request message. It is consumed by the metadata network dispatch table.

## Risks and Test Signals
The main contract is that the implementation returns all parallel lists with matching lengths and a valid next offset. Tests should validate header-level compatibility with `ListDirFromOffsetMsg` serialization and response shape.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/listing/ListDirFromOffsetMsgEx.h -->
