# sources/distributed-fs/moosefs/mfschunkserver/busychunks.c

## Purpose
`busychunks.c` maintains a small in-memory hash table of chunks that are currently busy, associating each busy chunk with an opaque packet pointer. It is a lightweight guard/helper for code that needs to prevent duplicate or conflicting handling for the same chunk id.

## Important Types and Functions
`busy_chunk` stores the opaque `packet`, normalized `chunkid`, and intrusive linked-list pointers (`next`, `prev`). `bchashmap` is a static array of 1024 bucket heads. `busychunk_hashfn` maps a normalized chunk id to a bucket by modulo.

`busychunk_start(packet, chunkid)` masks the chunk id with `0x00FFFFFFFFFFFFFF`, allocates a `busy_chunk`, inserts it at the head of the relevant bucket, and returns the entry pointer as an opaque handle. `busychunk_end(vbc)` unlinks the entry, frees it, and returns the original packet pointer. `busychunk_isbusy(chunkid)` scans one bucket for a normalized chunk id and returns `1` or `0`. `busychunk_init` clears all bucket heads.

## Control Flow
The expected lifecycle is start, optional repeated busy checks, then end with the handle returned by start. The module does not reject duplicate starts for the same normalized chunk id; callers must call `busychunk_isbusy` first if duplicates should be suppressed.

## State and Persistence
All state is process-local and volatile. There is no locking, persistence, or reference counting. The stored packet pointer is opaque and not freed by this module.

## Dependencies and Integration
Only libc allocation and fixed-width types are used. The chunk-id mask is an important integration detail for MooseFS chunk-id encoding: high bits are ignored for busy tracking, matching code that treats the lower 56 bits as the chunk identity.

## Risks
The module is not thread-safe. If called from worker threads without external serialization, bucket links can corrupt. Allocation failures are not checked. Duplicate starts for the same chunk id are allowed, so `busychunk_end` on one handle may leave the chunk still busy if another entry exists. Passing an invalid or already-ended handle to `busychunk_end` will corrupt memory.

## Test Signals
Focused tests should cover initialization, start/isbusy/end, hash collisions, high-byte masking equivalence, duplicate starts, and returning the original packet pointer on end. Concurrency tests only make sense if callers intend to use it outside the single-threaded event-loop context.
