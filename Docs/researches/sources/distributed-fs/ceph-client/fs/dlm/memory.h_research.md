# sources/distributed-fs/ceph-client/fs/dlm/memory.h

## Purpose
`memory.h` declares DLM memory-cache lifecycle and typed allocation/free wrappers so other DLM modules avoid direct slab-cache knowledge.

## Important APIs, Types, And Functions
It exposes cache lifecycle plus alloc/free pairs for RSBs, LKBs, LVBs, midcomms handles, writequeue entries, lowcomms messages, and callbacks.

## Control Flow
Callers initialize all caches during module load, allocate objects on demand, free through the matching wrapper, and destroy caches at module exit.

## State And Persistence
No header-owned state. The implementation's caches persist for module lifetime.

## Dependencies And Integration Points
It references core DLM types and opaque communication types used by lowcomms, midcomms, callbacks, lock, recovery, and user paths.

## Risks
Every allocation must be paired with the correct free function because several frees are RCU-deferred and object-type specific. Exposing opaque types by pointer keeps compile-time coupling low but leaves lifetime correctness to callers.

## Test Signals
Compile-time API coverage plus leak detection after stress lock/recovery/comms tests validate the wrappers.
