# sources/distributed-fs/lizardfs/src/master/filesystem_operations.h

## Purpose
`filesystem_operations.h` declares lower-level operation support shared by the public filesystem API, lock management code, and statistics/reporting modules.

## Important APIs and types
It defines defaults `DEFAULT_GOAL` and `DEFAULT_TRASHTIME`, the `FsStats` enum for operation counters, and `gFsStatsArray`. Declared functions include `fs_retrieve_stats`, goal definition accessors, metadata saved broadcasting, `fs_changelog`, `fs_add_files_to_chunks`, `fs_getversion`, a legacy repair signature, flock/POSIX lock operations and probes, session lock clearing, lock listing, inode unlock, and pending lock removal.

## Control flow and state behavior
The header separates helper operations from the broad client API in `filesystem.h`. Lock functions operate on `gMetadata->flock_locks` or `posix_locks`, can emit changelog entries, and return owners whose pending locks became active. Statistics retrieval copies then clears the counter array.

## Dependencies and integration points
It depends on goals, FsContext, lock types, setgoal task declarations, and protocol lock info. It is included by checksum updater, node code, periodic code, and operations implementation.

## Risks and test signals
Because some declarations are master-only behavior but not all are guarded by `METARESTORE`, compile matrices matter. Tests should build normal and metarestore targets, verify stats reset semantics, and exercise lock APIs through both active and pending queues.
