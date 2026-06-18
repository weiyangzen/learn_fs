# sources/distributed-fs/coda/coda-src/util/rec_dhash.cc

## Purpose
Implements a recoverable hash table with `rec_dlist` buckets for RVM-backed intrusive objects.

## Important APIs, Types, And Functions
`rec_dhashtab` provides recoverable allocation, `Init`, `DeInit`, `SetHFn`, `SetCmpFn`, insertion variants, `remove`, `first`, `last`, `get`, `count`, `IsMember`, `bucket`, print, and `rec_dhashtab_iterator`.

## Control Flow
Initialization validates power-of-two size, allocates a recoverable array of `rec_dlist`, and initializes each bucket. Operations log the table object, hash the key, delegate to a bucket, and update `cnt`. Iteration wraps `rec_dlist_iterator` and can scan all buckets in ascending or descending order.

## State And Persistence
The table object and bucket array are RVM allocated. Structural changes are transaction logged. Hash and comparison function pointers are not inherently persistent and can be reset.

## Dependencies And Integration Points
Depends on `rec_dhash.h`, `rec_dlist`, and `rvmlib`. Used for persistent object indexes with doubly-linked bucket ordering.

## Risks
`remove()` and `get()` decrement `cnt` unconditionally like the nonrecoverable version. `DeInit()` requires empty buckets and frees the bucket array transactionally. Function pointers must be reinstalled after restart if addresses change.

## Test Signals
Transactionally insert/remove entries, verify count after failed removes, iterate across buckets, run commit/abort recovery tests, and check `SetHFn`/`SetCmpFn` after process restart.
