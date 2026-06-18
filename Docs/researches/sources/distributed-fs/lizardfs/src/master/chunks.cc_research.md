# sources/distributed-fs/lizardfs/src/master/chunks.cc

Purpose: central master chunk metadata manager: tracks chunk IDs, versions, locks, file goal references, chunkserver copies/parts, availability/replication statistics, repair/rebalance work, metadata serialization, and checksum state.

Important APIs/types/functions: internal `ChunkPart` state machine; internal `Chunk` with `ChunkGoalCounters`, part list, stats, operation state, and checksum; global `ChunksMetadata`; public APIs from `chunks.h` including file reference updates, modification/truncate, version/location lookup, chunkserver copy status callbacks, repair, load/store/unload/newfs, checksum, and initialization. `ChunkWorker` performs maintenance jobs.

Control flow: chunks are allocated in buckets and indexed by hash of chunk ID with a last-hit cache. File operations update goal counters and checksums. Client writes/truncates use `chunk_multi_modify`/`chunk_multi_truncate`, which create new chunks, duplicate shared chunks, bump versions, lock chunks, and send create/duplicate/truncate/version messages to chunkservers. Chunkserver reports add/update/invalidate part records. Operation-status callbacks clear busy flags, mark failures, trigger emergency version increases, and notify clients. `ChunkWorker` periodically scans buckets and an endangered queue to delete invalid/unused/over-goal parts, replicate missing parts, rebalance across labels/disk usage/IPs, and remove empty chunk structs.

State and persistence: owns in-memory chunk table, next chunk ID, checksum fields, chunk copy stats, endangered queue, goal cache, delayed replication state, deletion/replication counters, and worker coroutine state. `chunk_store` serializes `nextchunkid` and chunk records with ID/version/lock timeout/lock ID; `chunk_load` restores them. Runtime copy locations are rebuilt from chunkserver reports.

Dependencies and integration: depends on goals, chunk copy calculators, chunkserver DB, filesystem metadata, topology, event loop, config, random, matocs/matocl protocols, media labels, checksum helpers, and metaserver promotion callbacks. Compile-time `METARESTORE` excludes live chunkserver maintenance for restore tooling.

Risks: correctness depends on consistent transitions among `VALID`, `BUSY`, `TDVALID`, `TDBUSY`, `INVALID`, and `DEL`. Maintenance is intentionally incremental and timing-sensitive; bad config for deletion/replication limits, loop CPU, same-IP avoidance, or endangered priority affects recovery speed and data placement. `chunk_apply_modification` used for changelog replay has less live validation than live operations. Metadata serialization stores only core chunk metadata, so copy state must be reconstructed safely.

Test signals: direct tests are not in this subset; behavior is indirectly exercised by chunk goal counter tests, read/write/truncate integration tests, metadata restore tests, and chunkserver protocol tests elsewhere.
