# sources/distributed-fs/lizardfs/src/mount/global_chunkserver_stats.h

## Purpose
This header exposes a single mount-instance-global `ChunkserverStats` object.

## Important APIs, Types, And Functions
`extern ChunkserverStats globalChunkserverStats;` is the only API. It provides shared access to statistics defined in `global_chunkserver_stats.cc`.

## Control Flow
No control flow is present.

## State And Persistence
The header declares in-memory process state only. The concrete object is allocated as a global variable in the `.cc` file.

## Dependencies And Integration Points
It includes `common/chunkserver_stats.h` and is intended for mount-side chunkserver communication modules.

## Risks And Test Signals
Risks are the usual global mutable state concerns: synchronization must be provided by `ChunkserverStats` or callers. Compile/link coverage catches duplicate or missing definitions.
