# sources/distributed-fs/lizardfs/src/mount/global_chunkserver_stats.cc

## Purpose
This source file defines the mount-instance-global chunkserver statistics object.

## Important APIs, Types, And Functions
It defines `ChunkserverStats globalChunkserverStats;` declared in the matching header.

## Control Flow
There is no runtime control flow beyond global object construction before use.

## State And Persistence
The global object accumulates in-memory chunkserver statistics for one mount process. Persistence, if any, is outside this file.

## Dependencies And Integration Points
It depends on `global_chunkserver_stats.h` and `common/chunkserver_stats.h`. Other read/write/chunkserver code can include the header to update or query the shared stats.

## Risks And Test Signals
Risks are singleton lifetime and concurrent access semantics defined by `ChunkserverStats`. Test signals should come from users of chunkserver stats rather than this definition file.
