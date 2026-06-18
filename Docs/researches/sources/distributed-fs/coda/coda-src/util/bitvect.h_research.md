# sources/distributed-fs/coda/coda-src/util/bitvect.h

## Purpose
Declares the opaque C `Bitv` bit-vector API.

## Important APIs, Types, And Functions
`typedef struct Bitv_s *Bitv` hides implementation state. Functions are `Bitv_new`, `Bitv_free`, `Bitv_length`, `Bitv_count`, `Bitv_put`, `Bitv_clear`, `Bitv_set`, `Bitv_getfree`, and `Bitv_print`.

## Control Flow
Callers allocate a fixed-length vector, use bit operations by index, optionally find a free bit, print diagnostics, and free through `Bitv_free(&b)`.

## State And Persistence
The API promises heap-resident in-memory bit state only. Synchronization is implementation-owned.

## Dependencies And Integration Points
This header is standalone except for `FILE` being expected from includers or C library context. Implementation integrates with LWP locks and libutil.

## Risks
No declaration for `Bitv_get()` appears even though the implementation exports it, so callers without a prototype may be broken under modern C. Bounds semantics for `getfree()` are not described.

## Test Signals
Compile strict-prototype builds, exercise all declared functions, and verify callers that need `Bitv_get()` either include a declaration or fail cleanly.
