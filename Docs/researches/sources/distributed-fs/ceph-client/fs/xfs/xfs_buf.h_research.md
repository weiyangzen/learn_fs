<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_buf.h -->
## sources/distributed-fs/ceph-client/fs/xfs/xfs_buf.h

Purpose: Defines XFS metadata buffer and buffer target types, flags, verifier contracts, and public buffer cache/I/O APIs.

Important APIs and types: `struct xfs_buftarg` abstracts a block/memory target with device, DAX, sector geometry, atomic write units, LRU, readahead counter, rate limiting, and rhashtable. `struct xfs_buf_map` identifies disk ranges. `struct xfs_buf_ops` provides verifier callbacks and magic values. `struct xfs_buf` stores cache key, length, lockref, semaphore, flags, LRU/list links, target/mount/perag, data address, I/O completion, log item linkage, maps, pin count, errors, retry state, iodone callback, and verifier ops. Public APIs cover get/read/readahead, uncached buffers, hold/release, lock/unlock, writes/errors/corruption, delwri queues, LRU ref control, checksums, buftarg lifecycle/configuration, and magic verification.

Control flow and integration: Inline wrappers create single-map operations for common get/read/readahead/incore calls. Flags distinguish operation intent (`XBF_READ`, `XBF_WRITE`, `XBF_ASYNC`), buffer state (`XBF_DONE`, `XBF_STALE`, `XBF_WRITE_FAIL`), internal ownership (`_XBF_KMEM`, `_XBF_DELWRI_Q`), and lookup modifiers (`XBF_INCORE`, `XBF_TRYLOCK`, `XBF_LIVESCAN`).

State and persistence: The definitions describe all in-core state needed to mediate persistent metadata I/O. Verifier and checksum helpers protect on-disk metadata integrity.

Dependencies: Pulls Linux list, mm, fs, DAX, uio, list_lru, and lockref primitives plus XFS core scalar types.

Risks: Flags used only as arguments must not leak into persistent buffer state. `xfs_buf_islocked` reads semaphore internals, so kernel semaphore semantics matter. Callers must pair lock/release helpers correctly and honor async submission ownership rules documented in implementation.

Test signals: Static/build coverage for flag tracing, struct layout expectations, verifier magic checks, wrapper behavior, and call-site audits for lock/ref pairing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_buf.h -->
