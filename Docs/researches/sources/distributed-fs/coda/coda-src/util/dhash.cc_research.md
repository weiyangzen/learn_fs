# sources/distributed-fs/coda/coda-src/util/dhash.cc

## Purpose
Implements `dhashtab`, a fixed-size power-of-two hash table whose buckets are sorted or unsorted intrusive `dlist` instances.

## Important APIs, Types, And Functions
The constructor takes a bucket count, hash function, and dlist comparison function. Operations are `insert`, `prepend`, `append`, `remove`, `first`, `last`, `get`, `clear`, `count`, `IsMember`, `bucket`, `print`, and `dhashtab_iterator`.

## Control Flow
Construction verifies the requested size is already a power of two, allocates a `dlist` array, and assigns each bucket's comparison callback. Operations compute `hfn(key) & (sz - 1)` and delegate to the chosen bucket. Iterators can scan one bucket or all buckets in ascending/descending bucket order.

## State And Persistence
State is the bucket array, hash callback, and total count. Entries are caller-owned intrusive `dlink` objects. No persistence is provided.

## Dependencies And Integration Points
Depends on `dhash.h` and `dlist.h`. Used when Coda needs hash lookup combined with dlist ordering within buckets.

## Risks
`remove()` and `get()` decrement `cnt` unconditionally even when the bucket does not contain the requested object or is empty for that key. Table size must be a power of two, otherwise construction aborts. There is no resizing or locking.

## Test Signals
Construct invalid and valid sizes, insert into multiple buckets, remove present and absent entries, check count integrity, iterate all/single buckets in both orders, and clear populated tables.
