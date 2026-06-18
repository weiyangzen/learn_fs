# sources/distributed-fs/coda/coda-src/util/bitvect.c

## Purpose
Provides a C bit-vector abstraction with LWP read/write locks for concurrent access to fixed-length bit sets.

## Important APIs, Types, And Functions
`struct Bitv_s` stores `length`, an array of `unsigned long` words, and a `Lock`. Public functions allocate/free, read length, count set bits, get/put/clear/set bits, find-and-set a free bit, and print the words.

## Control Flow
`Bitv_new()` allocates the struct, zeroes enough words for the requested length, and initializes the lock. Accessors take read locks; `Bitv_put()` and `Bitv_getfree()` take write locks. `Bitv_getfree()` scans words for a zero bit, sets it, and returns its global bit index.

## State And Persistence
State is heap-only and protected by the embedded LWP lock. It has no RVM persistence. `Bitv_free()` releases word storage and the struct but does not null out the caller's pointer.

## Dependencies And Integration Points
Depends on `lwp/lock.h`, libutil lock macros from `util.h`, `CODA_ASSERT`, and C allocation. It is a C alternative to the C++ bitmap classes.

## Risks
`Bitv_getfree()` and `Bitv_count()` examine all bits in the rounded last word, so indexes at or beyond `length` may be returned or counted. Shifts use literal `1`, which can overflow for bit positions beyond `int` width on wide `unsigned long`. `Bitv_free()` calls `PRE_EndCritical()` on NULL input, which is an unusual side effect.

## Test Signals
Create lengths around word boundaries, set/clear/get each valid bit, call `getfree()` until exhaustion, validate no out-of-range returns, run with multiple LWP readers/writers, and check lock/unlock balance under assertions.
