# sources/distributed-fs/coda/coda-src/util/ohash.cc

## Purpose
Implements `ohashtab`, a fixed-size power-of-two hash table backed by intrusive singly-linked `olist` buckets.

## Important APIs, Types, And Functions
Public operations are `insert`, `append`, `remove`, `first`, `last`, `get`, `clear`, `count`, `IsMember`, `FindObject`, `bucket`, print methods, and `ohashtab_iterator`.

## Control Flow
Construction validates a power-of-two size, allocates bucket lists, and stores the hash function. Operations hash the key with `hfn(key) & (sz - 1)` and delegate to that bucket. `FindObject()` hashes one key but compares an arbitrary tag through the bucket's object tag matcher. Iteration scans one bucket or all buckets in ascending order.

## State And Persistence
State is in-memory bucket array, count, and hash callback. Entries are caller-owned `olink` objects and can be on only one list at a time.

## Dependencies And Integration Points
Depends on `ohash.h` and `olist.h`. Used for lightweight intrusive hash maps where sorted buckets are unnecessary.

## Risks
`remove()` and `get()` decrement count unconditionally even when no object is removed. `get()` does not check table count before removing from a possibly empty bucket. No resizing, locking, or type safety exists.

## Test Signals
Insert/remove present and absent entries, verify count integrity, use `FindObject()` with separate key/tag fields, iterate single/all buckets, and reject non-power-of-two sizes.
