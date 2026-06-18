# sources/distributed-fs/openafs/src/WINNT/afsapplib/hashlist.cpp

## Purpose
Implements the `EXPANDARRAY`, `HASHLIST`, `HASHLISTKEY`, and `ENUMERATION` classes declared in `hashlist.h`, plus general string hash helpers. The module is a Windows-only in-memory indexed object list: callers store raw object pointers while one or more hash keys provide fast lookup and keyed enumeration.

## Important APIs and Control Flow
`EXPANDARRAY` lazily allocates fixed-size heaps of element slots using `GlobalAlloc`; `GetAt` returns an existing element pointer and `SetAt` allocates the containing heap before optionally copying element bytes. `HASHLIST::Add` inserts a non-NULL object into a sparse array slot, links it into the global doubly linked list, adds an internal pointer-index key entry, and indexes the object through all user keys. `Remove` uses the internal key to find a slot in near constant time, unlinks global and per-key entries, and clears the object pointer without compacting the array. `Update` refreshes every user key for an existing object without changing list order.

`CreateKey` allocates a `HASHLISTKEY`, stores it in the growable key table, and indexes existing live objects. `HASHLISTKEY::Add`, `Remove`, and `Resize` maintain bucket chains backed by an `EXPANDARRAY` parallel to the owning list's object slots. `FindFirst`, `FindLast`, and `GetFirstObject` hash caller data, walk one bucket, and call the supplied compare callback. `ENUMERATION` snapshots next/previous slot links in `PrepareWalk`, holds the list critical section for its lifetime, and self-deletes when traversal reaches the end.

## State, Dependencies, and Integration
The persistent state is process memory only: object slot arrays, key arrays, bucket arrays, linked-list indices, and a `CRITICAL_SECTION`. The class does not own user objects. It depends on Win32 allocation and synchronization APIs, `TaLocale.h` allocation macros such as `New2`/`Delete`, and caller-provided callback functions. `HashString`, `HashAnsiString`, and `HashUnicodeString` are utility hashers used by clients that key on text.

## Risks and Test Signals
Enumeration leaks are severe because an unfinished `ENUMERATION` keeps the critical section locked. Several paths rely on recursive critical sections because key operations enter the owning list while callers already hold it. `KeyIndex_HashData` casts pointers through `DWORD`, which is risky for 64-bit builds despite `HASHVALUE` being `UINT_PTR`. String hashing reads unaligned `DWORD` values from character buffers. `FreeDebugInfo` frees only the bucket array and not the `HASHLISTKEYDEBUGINFO` object itself, so callers may leak unless they also delete it. Good tests would cover duplicate pointer add/remove, keyed duplicate suppression, key creation after population, update during enumeration, resize thresholds, enumeration deletion behavior, and 64-bit pointer hashing.
