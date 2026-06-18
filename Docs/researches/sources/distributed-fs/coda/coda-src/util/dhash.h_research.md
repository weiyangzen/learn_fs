# sources/distributed-fs/coda/coda-src/util/dhash.h

## Purpose
Declares the intrusive doubly-linked hash table.

## Important APIs, Types, And Functions
`dhashtab` owns an array of `dlist` buckets and exposes insertion variants, removal, min/max-style bucket get, membership, bucket computation, printing, and counting. `DhIterOrder` and `dhashtab_iterator` support table or bucket scans.

## Control Flow
Callers provide a hash function and optional bucket comparator, insert `dlink`-derived objects under a key, and iterate by key or whole table.

## State And Persistence
Only bucket topology and counts are stored. Objects remain caller-owned and in-memory only.

## Dependencies And Integration Points
Depends on `dlist.h`; it is a C++ utility primitive for Coda's object registries.

## Risks
The API requires stable keys and intrusive link ownership discipline. It has no type safety, resizing, or synchronization.

## Test Signals
Compile users with custom hash/comparison callbacks and validate count, bucket, membership, and iterator behavior.
