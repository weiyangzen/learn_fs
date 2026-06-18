<!-- Source: sources/distributed-fs/ceph-client/fs/netfs/iterator.c -->
# sources/distributed-fs/ceph-client/fs/netfs/iterator.c

## Purpose
Provides iterator helpers used by netfs IO dispatch and retry paths. It can extract user iterators into bvec-backed iterators and compute how much of a given iterator can be submitted under size and segment constraints.

## Important APIs, Types, And Functions
Exports `netfs_extract_user_iter()` and `netfs_limit_iter()`. Internal limiters handle bvec, kvec, xarray, and folio_queue iterators: `netfs_limit_bvec()`, `netfs_limit_kvec()`, `netfs_limit_xarray()`, and `netfs_limit_folioq()`.

## Control Flow
`netfs_extract_user_iter()` verifies the source is ubuf/iovec, allocates one buffer large enough for bvecs and page pointers, repeatedly calls `iov_iter_extract_pages()`, builds bvec entries with offsets and lengths, advances the original iterator, then initializes a bvec iterator. `netfs_limit_iter()` dispatches by iterator type; each limiter skips `start_offset`, walks segments, and returns a span capped by `max_size` and `max_segs`.

## State And Persistence
No persistent state. The extraction result owns allocated bvec storage whose cleanup mode is determined by generic iov_iter extraction APIs. Limiters are read-only over iterator descriptors and underlying arrays/xarrays/folio queues.

## Dependencies And Integration Points
Used by read/write retry code when negotiated max IO length or segment count requires splitting a retry span. Depends on Linux `iov_iter`, xarray, folio queue, bvec, kvec, and page extraction APIs.

## Risks
Risks include iterator type mismatch, off-by-one segment limiting, overrun of allocated bvec/page-pointer storage, and RCU visibility while scanning xarrays. The xarray limiter assumes no hugetlb folios and warns if encountering value entries.

## Test Signals
Unit-style tests should cover ubuf/iovec extraction with offsets, bvec/kvec/xarray/folioq limit calculations, zero count, start offset at boundaries, max segment caps, and retry splitting with negotiated `sreq_max_segs`.
