# sources/distributed-fs/openafs/src/ubik/disk.c

## Purpose
Implements ubik's local transactional disk layer: a fixed-size page cache, write-ahead log record generation, read/write/truncate operations, transaction begin/commit/abort/end, dirty-buffer flushing, and database version labeling on commit.

## Important APIs, Types, And Functions
Public functions include `udisk_Debug`, `udisk_Init`, `udisk_Invalidate`, `udisk_read`, `udisk_truncate`, `udisk_write`, `udisk_begin`, `udisk_commit`, `udisk_abort`, and `udisk_end`. Internal helpers include `udisk_LogOpcode`, `udisk_LogEnd`, `udisk_LogTruncate`, `udisk_LogWriteData`, `DRead`, `DNew`, `DRelease`, `DFlush`, `DSync`, `DAbort`, `DTrunc`, truncation-list helpers, `FixupBucket`, `newslot`, `DedupBuffer`, and `unthread`.

## Control Flow
`udisk_Init` allocates page metadata and data buffers and initializes an LRU ring/hash table. Reads find a clean visible page for read transactions, prefer dirty pages for write transactions, or allocate/read a page from physical storage. Writes first append log data, then update cached pages and mark them dirty. Truncates are logged but deferred in a transaction truncation list. A write transaction begins by logging `LOGNEW` and setting `DBWRITING`. Commit may relabel a newly elected sync site's database, increments the version counter, logs `LOGEND`, flushes dirty buffers to files, syncs files, applies truncations, writes the database label, and truncates the log. Abort logs `LOGABORT`, truncates the log, and discards dirty buffers.

## State And Persistence
Persistent state is the ubik database files and log file through `ubik_dbase` physical callbacks. In-memory state includes global page buffers, hash/LRU structures, dirty/locker flags, transaction lists, active truncations, `DBWRITING`, reader count, version fields, and write transaction counters. Commit ordering is designed so crash recovery can replay a committed log or ignore an uncommitted one.

## Dependencies And Integration Points
This file depends on ubik database callbacks for physical read/write/sync/truncate/setlabel/buffered append, beacon sync-site checks, recovery flags and quorum version propagation, lock release from `lock.c`, condition/LWP wakeups, and network propagation via `ContactQuorum_DISK_SetVersion`.

## Risks And Test Signals
Risks include global cache state shared across databases, no explicit allocation failure checks for buffer arrays, LRU exhaustion when all buffers are locked or dirty, subtle read visibility rules around dirty duplicate pages, panic-on-I/O-error after commit point, and strict log format coupling with `recovery.c`. Tests should cover read/write transactions, abort discarding uncommitted changes, commit log replay after crash, truncate ordering, version counter updates, dirty duplicate invalidation, low-buffer pressure, read transactions not seeing uncommitted writes, and wakeup behavior for blocked writers.
