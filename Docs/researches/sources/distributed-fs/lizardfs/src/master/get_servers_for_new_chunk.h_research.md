# sources/distributed-fs/lizardfs/src/master/get_servers_for_new_chunk.h

Purpose: declares data structures and class API for selecting chunkservers for a newly created chunk.

Important APIs/types/functions: `ChunkserverChunkCounter` records server pointer, media label, weight, version, created-count history, and load factor; `ChunkCreationHistory` is a vector of those counters; `GetServersForNewChunk::addServer()` appends candidates; `prepareData()` orders candidates and syncs history; `chooseServersForLabels()` selects servers for a goal part while honoring min version and already-used servers.

Control flow: build one selector per placement attempt, add candidate servers, prepare with persistent history, then call choose for goal label parts.

State and persistence behavior: `servers_` is per-selector transient state. History is persistent only across calls in memory to smooth placement distribution.

Dependencies/integration: depends on `common/goal.h`, `MediaLabel`, and `matocsserventry`. It is integrated by the chunk creation path.

Risks and test signals: `addServer()` accepts weights as signed integers; callers must avoid zero/negative nonsensical weights. Tests should assert default construction and that `used` is mutated as part of selection.
