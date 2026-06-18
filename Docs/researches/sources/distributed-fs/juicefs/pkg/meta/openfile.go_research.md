# sources/distributed-fs/juicefs/pkg/meta/openfile.go

## Purpose

`openfile.go` implements an in-memory open-file tracker and short-lived cache for attributes and chunk slice lists. It lets metadata clients reuse attributes for recently opened files, keep page cache hints stable, and avoid repeated chunk lookups while a file remains open or recently checked.

## Important APIs, Types, And Functions

`openFile` stores an `Attr`, reference count, last-check Unix timestamp, cached first chunk, and cached nonzero chunks. It has `invalidateChunk` and `release`; released instances return to `ofPool`.

`openfiles` owns a mutex, expiry duration, entry limit, and `map[Ino]*openFile`. `newOpenFiles` initializes the map and starts the background `cleanup` goroutine.

Public methods on the tracker are `OpenCheck`, `Open`, `Close`, `Check`, `Update`, `IsOpen`, `ReadChunk`, `CacheChunk`, `InvalidateChunk`, and `find`. Sentinel chunk indexes `invalidateAllChunks` and `invalidateAttrOnly` are defined, though this file only handles all/individual chunk invalidation.

## Control Flow And State

`OpenCheck` returns a cached attr and increments refs when an inode exists and `lastCheck` is within `expire`. `Open` creates or reuses an entry, preserves `KeepCache` if mtime/mtimensec match, invalidates chunks when attributes changed, stores the new attr, forces `KeepCache = true` for the next open, increments refs, and updates `lastCheck`. `Close` decrements refs and reports whether refs are now nonpositive or the file was unknown.

`Check` reads a cached attr without incrementing refs and panics if passed nil. `Update` updates cached attrs, invalidating chunk caches on mtime changes. Chunk cache methods store chunk zero in `first` and other chunks in the `chunks` map.

The cleanup goroutine periodically scans at most 1000 entries, removes long-idle (`refs <= 0` and last check older than 12 hours) entries, and if over `limit`, evicts least-recently checked non-open entries. Sleep duration scales with scan/deletion counts.

## Dependencies And Integration Points

This file depends on `sync`, `time`, package `Ino`, `Attr`, and `Slice`. It is used by metadata engines and VFS-facing open/read/write paths to coordinate open state with attr/chunk cache invalidation.

## Risks And Edge Cases

All map and openFile field access is serialized by the outer `openfiles` mutex; the embedded `openFile.RWMutex` is unused here. `Close` can decrement refs below zero if calls are unbalanced. `cleanup` has a subtle candidate eviction flow: when a newer least-recent candidate is found, it releases/deletes the previous candidate inside the loop, so changes need careful review to avoid deleting the wrong file. `find` returns a pointer after unlocking, so external mutation would race unless callers treat it as read-only or add locking.

## Test Signals

No direct tests are listed for this file. Behavior is indirectly tested by open/read/write metadata operations and randomized filesystem state-machine tests.
