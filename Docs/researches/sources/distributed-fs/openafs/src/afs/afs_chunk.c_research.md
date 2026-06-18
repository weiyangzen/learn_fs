# sources/distributed-fs/openafs/src/afs/afs_chunk.c

Purpose: Owns the global default chunk-size variables for the cache manager.

Important APIs and variables: Defines `afs_FirstCSize`, `afs_OtherCSize`, and `afs_LogChunk`, initialized to `AFS_DEFAULTCSIZE` and `AFS_DEFAULTLSIZE` from `afs_chunkops.h`.

Control flow: No functions are implemented. Startup code or configuration macros such as `AFS_SETCHUNKSIZE` mutate these globals before cache operations rely on chunk geometry.

State and persistence: The variables are process/kernel-memory configuration state. They are reflected in cache behavior and callback cache-config reporting, but this file does not persist them directly.

Dependencies and integration points: Included with AFS base headers, stats, and `afs_chunkops.h` definitions. Used by dcache indexing, file fetch/store chunk math, and cache initialization.

Risks: If the chunk-size globals are changed after cache data structures are initialized, offset-to-chunk calculations can become inconsistent with existing cache entries. The comments explicitly expect setup before use.

Test signals: Verify defaults, configured chunk sizes through `AFS_SETCHUNKSIZE`, cache-config reporting, and offset/chunk conversion consistency before and after startup configuration.
