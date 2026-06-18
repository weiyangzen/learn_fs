# sources/distributed-fs/coda/coda-src/util/ohash.h

## Purpose
Declares the intrusive singly-linked hash table.

## Important APIs, Types, And Functions
`ohashtab` owns `olist` buckets and exposes head/tail insertion, removal, first/last/get, clear, count, membership, `FindObject()`, bucket calculation, and printing. `ohashtab_iterator` scans one bucket or all buckets.

## Control Flow
Callers provide a hash function, store `olink`-derived objects under keys, and optionally search by tag within a key's bucket.

## State And Persistence
All state is process-local. Object ownership remains with callers.

## Dependencies And Integration Points
Includes `stdint.h`, `stdio.h`, and `olist.h`. It complements `dhash` for cheaper bucket linkage.

## Risks
Keys must remain stable while objects are in the table. There is no dynamic resizing or synchronization.

## Test Signals
Compile with pointer/integer hash callbacks, validate bucket selection, tag lookup, and iterator behavior.
