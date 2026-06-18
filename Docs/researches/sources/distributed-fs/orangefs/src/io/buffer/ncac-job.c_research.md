# sources/distributed-fs/orangefs/src/io/buffer/ncac-job.c

## Purpose
Implements NCAC job workers for cached extent operations, primarily the read path, plus placeholders for write/query/demote/sync jobs.

## Important APIs, Types, And Functions
Exports `NCAC_do_a_read_job`, `NCAC_do_a_write_job`, `NCAC_do_a_query_job`, `NCAC_do_a_demote_job`, and `NCAC_do_a_sync_job`. Private helpers find extents, allocate extents, initialize Trove reads, mark pending reads, test read completion, increment read references, and add extents to cache.

## Control Flow
`NCAC_do_a_read_job` locks the inode, iterates communication buffers, locates or allocates extents by index, starts a Trove read for misses, admits new extents into LRU cache, increments one read reference per distinct extent, checks pending read completion, and sets per-buffer readiness flags. After unlocking, it sets request status to submitted, partial, or buffer-complete based on ready count. The write/query/demote/sync workers currently return success or log "not implemented yet" without meaningful state transitions.

## State And Persistence
Read jobs mutate inode page trees, LRU lists, extent flags, read counters, pending Trove ids, and request buffer/status fields. Extents come from the global free list or eviction. No disk persistence occurs beyond Trove reads into cache memory.

## Dependencies And Integration Points
Uses internal NCAC state, flag macros, cache management, `ncac-trove` read helpers, and LRU policy. It is dispatched by `internal.c`.

## Risks And Test Signals
Risks include only read path being implemented, `free_extent` being a no-op on read-init failure, hardcoded debug output, blocking allocation relying on clean eviction, possible counter inconsistencies, and full-extent reads for partial requests. Tests should cover cache miss/read completion, cache hit promotion, eviction under no free extents, partial request readiness, read failures, and explicit write/query/sync unsupported behavior.
