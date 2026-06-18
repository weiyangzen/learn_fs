# sources/distributed-fs/coda/coda-src/util/rec_ohash.cc

## Purpose
Implements a recoverable hash table with singly-linked `rec_olist` buckets.

## Important APIs, Types, And Functions
`rec_ohashtab` provides recoverable allocation, `Init`, `DeInit`, `SetHFn`, `insert`, `append`, `remove`, `first`, `last`, `get`, `count`, `IsMember`, `bucket`, print, and `rec_ohashtab_iterator` with `Reset()`.

## Control Flow
Initialization logs the table, validates power-of-two size, allocates recoverable bucket storage, and initializes each `rec_olist`. Mutators log the table, hash keys to buckets, delegate list changes, and update count. Iteration walks one bucket or all buckets in increasing order.

## State And Persistence
Bucket array, list topology, and count can be RVM persistent. Hash function pointer is process-local and can be reset.

## Dependencies And Integration Points
Depends on `rec_ohash.h`, `rec_olist`, and `rvmlib`. Used where persistent hash lookup does not need doubly-linked bucket ordering.

## Risks
`remove()` and `get()` decrement `cnt` even if no object is returned. `DeInit()` frees buckets but does not explicitly clear all fields. Function pointer restoration is required after restart.

## Test Signals
Transactionally add/remove/get entries, verify count integrity, reset iterator, recover after commit/abort, and compare behavior against `ohash`.
