# sources/distributed-fs/orangefs/src/io/buffer/aiovec.h

## Purpose
Defines a small fixed-size vector for batching NCAC extent operations into a single Trove list I/O request.

## Important APIs, Types, And Functions
Defines `AIOVEC_SIZE` as 6 and `struct aiovec`, holding parallel arrays for extents, stream offsets/sizes, memory offsets/sizes, and count `nr`. Inline helpers are `aiovec_init`, `aiovec_reinit`, `aiovec_count`, `aiovec_space`, and `aiovec_add`.

## Control Flow
NCAC code initializes or reinitializes the vector, appends extent/file/memory tuples until space is exhausted, then passes the arrays to Trove helper functions.

## State And Persistence
State is embedded in requests or inode-like structures and is process-local. `aiovec_init` sets `nr` then zeros the whole struct; `aiovec_reinit` only resets count and leaves old array contents for overwrite.

## Dependencies And Integration Points
Depends on `internal.h` for `struct extent`, `PVFS_offset`, and `PVFS_size`. Used by NCAC Trove batching and inode/request structures.

## Risks And Test Signals
Risks include no bounds check in `aiovec_add`, a hard batch size of six extents, and stale contents after `aiovec_reinit` if callers read beyond `nr`. Tests should verify capacity handling and list-I/O construction under exactly-full and overflow-attempt scenarios.
