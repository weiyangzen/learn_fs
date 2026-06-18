# sources/distributed-fs/openafs/src/dir/buffer.c

This file implements a fixed-size 2 KiB page buffer cache for AFS directory objects. Buffers are keyed by an opaque `dir_file_t` stored in an embedded fid byte array plus page number, hashed into 32 chains, protected by a global `afs_bufferLock` and per-buffer locks, and evicted by least-recently-used access time.

Important APIs are `DInit`, `DReadWithErrno`, `DRead`, `DNew`, `DRelease`, `DVOffset`, `DZap`, `DFlushVolume`, `DFlushEntry`, `DFlush`, and `DStat`; internal helpers are `bufferDir`, `FixupBucket`, and `newslot`. External integration callbacks are `FidZero`, `FidEq`, `ReallyRead`, `ReallyWrite`, `FidZap`, `FidVolEq`, and `FidCpy`.

Control flow on read first searches the hash chain, moves found buffers to the front, and increments lockers. Misses call `newslot`, which chooses an unlocked LRU buffer, writes it if dirty, zaps/copies the fid, zeros stale data, assigns the new page, and hashes it. Persistence occurs when dirty buffers are written by eviction or flush APIs. Risks include fatal `Die` on all buffers locked or write failure, access time wrap, fid layout assumptions in `pHash`, and correctness under concurrent lock transitions. Test signals are dtest operations, flush error propagation, and stress tests with small buffer counts.
