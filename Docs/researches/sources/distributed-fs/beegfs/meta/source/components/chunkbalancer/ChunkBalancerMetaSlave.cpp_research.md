# sources/distributed-fs/beegfs/meta/source/components/chunkbalancer/ChunkBalancerMetaSlave.cpp

## Purpose
Implements a metadata slave that consumes chunk balancing candidates, locks the file inode, validates stripe-pattern constraints, and schedules a storage-side chunk copy.

## Important APIs And Types
The main API is syncLoop(). It uses ChunkSyncCandidateFile fields, MetaStore directory references, GlobalInodeLockStore insert/release, StripePattern target lists, CopyChunkFileWork, and SynchronizedCounter.

## Control Flow
The loop skips empty queues and targetID 0, detects group IDs as mirrored chunks, references the parent directory, takes the MetaStore write lock while checking unlinkability and inserting the inode into the chunk-rebalancing lock store, releases the parent dir, validates that the source target is present and destination absent in the stripe pattern, submits CopyChunkFileWork to the comm slave queue, waits for completion, releases the inode lock on copy start failures, and increments errors or chunks synced.

## State And Persistence
State is per-slave atomic numChunksSynced/errorCount plus queue pointer. Persistent state is the temporary inode lock in GlobalInodeLockStore and remote storage copy scheduling; stripe pattern update appears to be handled elsewhere after copy completion.

## Dependencies And Integration Points
Depends on Program/App, MetaStore and GlobalInodeLockStore, ChunkSyncCandidateStore, storage target mapping/state stores, comm slave queues, CopyChunkFileWork, and chunk-balancer statistics types.

## Risks And Edge Cases
If copy scheduling succeeds, the inode lock is intentionally retained for later balancing workflow; failures release it. Missing parent dirs, unlinkability, stale stripe patterns, and queue-full responses are handled as errors. The empty-queue continue path can spin until the parent job sleeps or terminates.

## Test Signals
Test mirrored and non-mirrored candidates, invalid target 0, missing parent dir, unlinkable file, duplicate destination target, missing source target, storage queue full (AGAIN), communication failure, and lock retention/release behavior.
