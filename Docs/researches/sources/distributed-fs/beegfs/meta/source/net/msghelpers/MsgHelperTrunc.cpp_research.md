<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/msghelpers/MsgHelperTrunc.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/msghelpers/MsgHelperTrunc.cpp

## Purpose
Provides file truncation helpers that update storage chunk files, inode dynamic attributes, and persistent metadata.

## Important APIs, Types, and Functions
`truncFile()` references a file, calls `truncChunkFile()`, writes inode metadata to disk, and releases it. `truncChunkFile()` chooses sequential or parallel execution. `truncChunkFileSequential()` sends `TruncLocalFileMsg` to each target with a node-local truncation offset and optional quota user/group data. `truncChunkFileParallel()` schedules `TruncChunkFileWork` for all targets. `isTruncChunkRequired()` stats the file before open to skip unnecessary truncation. `getNodeLocalOffset()` and `getNodeLocalTruncPos()` compute per-stripe target truncation positions.

## Control Flow, State, and Persistence
Storage targets are truncated first, returned dynamic attributes are applied to the inode, and `truncFile()` persists inode metadata regardless of local result. Parallel and sequential paths both update `dynAttribs` and inode state. Quota data is propagated to storage truncation requests when requested.

## Dependencies and Integration Points
Depends on `MetaStore`, `TruncLocalFileMsg/RespMsg`, `TruncChunkFileWork`, stripe patterns, target mappers/states, path info, dynamic attributes, and quota user/group data. Used by `TruncFileMsgEx` and truncate-on-open in `MsgHelperOpen`.

## Risks and Test Signals
Risks include per-target offset math, partial truncation across targets, persisting metadata after truncation failure, quota propagation mismatch, and reliance on power-of-two chunk sizes. Tests should cover offset calculations for multiple stripe layouts, zero truncation, sequential/parallel behavior, target failures, buddy-mirror pattern routing through work objects, and `isTruncChunkRequired()` races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/msghelpers/MsgHelperTrunc.cpp -->
