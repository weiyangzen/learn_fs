# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/evictor/EvictionDirCandidates.java

Purpose: Helper for deprecated evictors that groups candidate blocks by directory and tracks which directory can provide the most space.

Important APIs: `add`, `candidateSize`, `candidateBlocks`, and `candidateDir`.

Control flow: Each added block appends to that directory's candidate list, updates accumulated candidate bytes, then computes candidate capacity as added bytes plus current available bytes. The max directory becomes the eviction target.

State and persistence: In-memory `Map<StorageDirEvictorView, Pair<List<Long>,Long>>`, max byte count, and selected directory. Not thread-safe and not persisted.

Dependencies and integration: Used inside `AbstractEvictor.cascadingEvict`.

Risks and test signals: Candidate selection assumes directory availability is stable while candidates are gathered. Tests should cover empty candidates, multiple dirs, tie behavior, and candidate list order preservation.
