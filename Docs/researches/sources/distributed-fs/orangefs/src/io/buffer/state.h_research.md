# sources/distributed-fs/orangefs/src/io/buffer/state.h

## Purpose
Declares NCAC extent state-transition functions and allocation-mode constants.

## Important APIs, Types, And Functions
Defines `BLOCKING_EXTENT_ALLOC` and `NONBLOCKING_EXTENT_ALLOC`. Declares read/write access, first-access, communication-done, I/O check, recheck, request done-access, RMW mark, and clean-page propagation helpers.

## Control Flow
Job and cache-policy code use these functions when acquiring extents, checking pending I/O, finishing communication, and preparing eviction or dirty flush.

## State And Persistence
No direct state. Implementations mutate `NCAC_req_t` and `struct extent` state.

## Dependencies And Integration Points
Requires NCAC internal type declarations from including files. It is included by cache, job, internal, LRU, and Trove modules.

## Risks And Test Signals
Risks are declaration drift and missing documentation of return-value meanings. Build coverage plus state-transition unit tests are useful signals.
