<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/msghelpers/MsgHelperTrunc.h -->
# sources/distributed-fs/beegfs/meta/source/net/msghelpers/MsgHelperTrunc.h

## Purpose
Declares static truncation helpers for metadata file operations.

## Important APIs, Types, and Functions
Public methods are `truncFile()`, `truncChunkFile()`, and `isTruncChunkRequired()`. Private methods implement sequential/parallel target truncation and local stripe offset calculations.

## Control Flow, State, and Persistence
The header distinguishes full truncation that persists inode metadata (`truncFile`) from chunk truncation that only updates in-memory inode attributes (`truncChunkFile`).

## Dependencies and Integration Points
Includes common types and `MetaStore`. Used by truncate messages and open-with-truncate handling.

## Risks and Test Signals
Offset helper correctness is central. Unit tests should directly exercise `getNodeLocalTruncPos()` through public truncation scenarios or friend/test hooks if available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/msghelpers/MsgHelperTrunc.h -->
