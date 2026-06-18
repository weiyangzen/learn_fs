# sources/distributed-fs/coda/coda-src/util/rec_ohash.h

## Purpose
Declares the recoverable singly-linked hash table.

## Important APIs, Types, And Functions
`rec_ohashtab` stores `rec_olist` buckets and exposes hash-table operations with RVM allocation and transaction annotations. `rec_ohashtab_iterator` supports bucket or whole-table scans and reset.

## Control Flow
Callers initialize with a power-of-two bucket count and hash function, mutate in transactions, and iterate over persistent `rec_olink` entries.

## State And Persistence
Hash topology and count are persistent-capable; callback pointer state is not durable.

## Dependencies And Integration Points
Includes `ohash.h`, `rec_olist.h`, and `rvmlib.h`.

## Risks
No resizing, no synchronization, and no type safety. Key hash function must be restored consistently.

## Test Signals
Compile RVM callers and verify bucket choice, iteration, and recovery of committed state.
