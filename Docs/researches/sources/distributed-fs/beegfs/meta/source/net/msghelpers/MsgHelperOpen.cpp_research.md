<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/msghelpers/MsgHelperOpen.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/msghelpers/MsgHelperOpen.cpp

## Purpose
Provides the metadata open helper, including compatibility checks for stripe chunk size and optional truncate-on-open of storage chunks.

## Important APIs, Types, and Functions
`openFile()` checks whether `OPENFILE_ACCESS_TRUNC` requires chunk truncation, opens metadata via `openMetaFile()`, validates stripe chunk size against minimum and power-of-two constraints, optionally calls `MsgHelperTrunc::truncChunkFile()` for truncation on the primary, and compensates with `openMetaFileCompensate()` on later errors. `openMetaFile()` wraps `MetaStore::openFile()`. `openMetaFileCompensate()` closes the inode reference through `MetaStore::closeFile()`.

## Control Flow, State, and Persistence
Opening mutates inode reference/open state in `MetaStore`. Truncate-on-open mutates storage chunk files and dynamic attributes but does not run on secondary. Invalid legacy chunk sizes are rejected after opening and compensated to avoid corrupting files.

## Dependencies and Integration Points
Depends on `MsgHelperTrunc`, `MetaStore`, `StripePattern`, `MathTk`, `OPENFILE_ACCESS_TRUNC`, quota flag propagation, and metadata open access checks. Used by lookup/open and locking recovery.

## Risks and Test Signals
Risks include compensation failures, primary/secondary truncation divergence if called incorrectly, legacy chunk-size refusal, and deciding truncation need from pre-open stat. Tests should cover normal open, invalid chunk size, truncate needed/not needed, truncate failure compensation, bypass access check handling, and secondary open without chunk truncation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/msghelpers/MsgHelperOpen.cpp -->
