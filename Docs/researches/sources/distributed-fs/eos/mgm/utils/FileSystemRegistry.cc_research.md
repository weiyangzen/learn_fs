# sources/distributed-fs/eos/mgm/utils/FileSystemRegistry.cc

## Purpose
Implements a thread-safe registry that indexes live MGM `FileSystem` objects by fsid, pointer, and queue path.

## Important APIs, types, and functions
`lookupByID()`, `lookupSpaceByID()`, `lookupByQueuePath()`, and `lookupByPtr()` provide read-side lookups. `registerFileSystem()` validates fsid, pointer, queue path, and uniqueness across all indexes. `eraseById()`, `eraseByPtr()`, `exists()`, `size()`, and `clear()` maintain and expose registry contents.

## Control flow
Registration acquires a write lock, rejects collisions and invalid inputs, then inserts all three indexes and asserts equal sizes. Erase operations locate the primary entry, assert corresponding reverse indexes exist, erase all mappings, and reassert invariants. Lookups acquire read locks and return nullable pointers or sentinel values.

## State and persistence behavior
State is process-local: `mById`, `mByFsPtr`, and `mByQueuePath`. It does not own or persist `FileSystem` objects. Durable filesystem configuration is outside this class.

## Dependencies and integration points
Uses `RWMutex`, `FileSystemLocator`, MGM `FileSystem`, `FsView`, EOS logging, and `eos_assert`. It backs `FsView::mIdView`-style lookups used by tracker, WFE, and space utilities.

## Risks and test signals
`lookupSpaceByID()` takes a read lock and then calls `lookupByID()`, which takes another read lock; this depends on read-lock reentrancy/compatibility. Header-provided iterators expose internal maps without locking, so legacy iteration can race if used concurrently. Tests should cover all collision types, fsid zero, null pointer, empty queue path, erase by both keys, queue path uniqueness, and concurrent lookup/register behavior.
