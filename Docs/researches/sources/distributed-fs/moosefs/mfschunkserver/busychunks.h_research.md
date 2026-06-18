# sources/distributed-fs/moosefs/mfschunkserver/busychunks.h

## Purpose
`busychunks.h` declares the small busy-chunk tracking API used by chunkserver code to mark chunk ids as in-use and recover an associated packet pointer when the busy period ends.

## Important APIs
`busychunk_start(void *packet, uint64_t chunkid)` starts tracking a chunk and returns an opaque handle. `busychunk_end(void *vbc)` ends tracking for that handle and returns the `packet` pointer supplied at start. `busychunk_isbusy(uint64_t chunkid)` checks whether a normalized chunk id is present. `busychunk_init(void)` clears the internal hash table.

## Control Flow and State
The header exposes a strict handle lifecycle: callers should store the return value from `busychunk_start` and pass that exact value to `busychunk_end`. The implementation stores only in-memory state and treats `packet` as opaque caller-owned data.

## Dependencies
The only dependency is `<inttypes.h>` for `uint64_t` and `uint8_t`. There are no MooseFS protocol dependencies in the public header.

## Risks
The API does not expose errors for allocation failure, duplicate chunk starts, or invalid handles. It also does not communicate thread-safety constraints; callers need to know from the implementation or usage context that external serialization is required.

## Test Signals
Tests should verify that start returns a non-null handle, `isbusy` observes the normalized chunk id, end returns the same packet pointer, and `isbusy` clears after end. Include tests around chunk ids that differ only in the high byte because the implementation masks those bits.
