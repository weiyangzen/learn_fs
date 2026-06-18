# sources/distributed-fs/lizardfs/src/master/id_pool_detainer.h

Purpose: implements an ID pool wrapper that detains released IDs for at least a configured time before reuse, reducing quick inode/id reuse hazards.

Important APIs/types/functions: `detail::SparseBitset` has a Judy-backed implementation when available and a deque fallback otherwise; `IdPoolDetainer` extends `IdPool`, stores detained IDs in timestamped buckets, exposes `acquire()`, `acquire(ts)`, `release(id,ts)`, `markAsAcquired()`, `detain()`, `releaseDetained()`, `detainedCount()`, `size()`, iteration over detained entries, and `maxSize()`.

Control flow: timestamped acquire/release calls first release a bounded number of expired detained IDs. Releasing an acquired id inserts it into the current/recent bucket unless detention is full, in which case oldest detained IDs are forced back to the base pool. Plain `acquire()` uses base pool first; if exhausted, it pulls an oldest detained ID early. `markAsAcquired()` can remove an ID from detention when metadata loading discovers it is actually in use.

State and persistence behavior: detention state is in-memory buckets of ID sets and timestamps. The metadata store persists detained IDs and timestamps through `fs_storefree()`/`fs_loadfree()` for inode pools.

Dependencies/integration: depends on `IdPool`, optional Judy arrays, STL containers, and assertions. Used by master inode allocation/free persistence.

Risks and test signals: deque fallback has O(n) test/unset and `set()` does not reject duplicates, so skip-check misuse can corrupt counts. `bucket_time_ = detain_time / bucket_count` can be zero if misconfigured. Early reuse occurs when base pool is exhausted or detention cap forces release. Tests should cover expiry boundary, bucket_count zero/large cases, duplicate detention protection, metadata load via `markAsAcquired()`, iterator correctness, Judy and fallback behavior, and forced release policy.
