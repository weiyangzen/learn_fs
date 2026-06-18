# sources/distributed-fs/coda/coda-src/util/vmindex.h

## Purpose
Declares the `vmindex` growable index-array utility and iterator.

## Important APIs, Types, And Functions
`DEFAULTINDEXSIZE` is 32. `vmindex` stores `indices`, `size`, and `count` and exposes constructor, destructor, and `add()`. `vmindex_iterator` returns `long` values via `operator()()`.

## Control Flow
Callers add unsigned long indexes and iterate until `-1` is returned.

## State And Persistence
All state is in-memory and owned by the `vmindex` object.

## Dependencies And Integration Points
Standalone C++ header used by Coda code needing a simple index list.

## Risks
End-of-iteration sentinel can collide with large unsigned values. Public semantics do not mention copy behavior or ownership.

## Test Signals
Compile users and test growth, empty iteration, and sentinel handling.
