<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/listing/ListDirFromOffsetMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/listing/ListDirFromOffsetMsgEx.cpp

## Purpose
Handles incremental directory listing from a server offset, returning names, entry types, entry IDs, per-entry offsets, a new offset, and a result code.

## Important APIs, Types, and Functions
`processIncoming()` logs the request, computes an optional response payload budget when the client sets `LISTDIROFFSETMSG_COMPATFLAG_CLIENT_SUPPORTS_BUFSIZE`, calls `listDirIncremental()`, sends `ListDirFromOffsetRespMsg`, advertises `LISTDIROFFSETRESPMSG_COMPATFLAG_SERVER_SUPPORTS_BUFSIZE`, and updates `MetaOpCounter_READDIR`. `listDirIncremental()` references the target directory and invokes `DirInode::listIncrementalEx()` with count or byte-budget limiting.

## Control Flow, State, and Persistence
No persistent state is changed. The handler reads a directory inode from `MetaStore`, streams a bounded slice of names and metadata, and advances the server offset. Buffer-size mode subtracts header and fixed response fields from the smaller of client and worker buffer sizes; without the flag, the request limit remains an entry-count limit.

## Dependencies and Integration Points
Depends on `ListDirFromOffsetMsg/RespMsg`, `MetaStore`, `DirInode::listIncrementalEx`, `ListIncExOutArgs`, `Program` config, node op stats, and compatibility feature flags.

## Risks and Test Signals
Risks include off-by-one response sizing, mixed clients using count mode versus buffer mode, and stale offsets during concurrent directory mutation. Tests should cover missing directory, dot filtering, exact buffer-boundary responses, feature negotiation, large entry names, and op counter updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/listing/ListDirFromOffsetMsgEx.cpp -->
