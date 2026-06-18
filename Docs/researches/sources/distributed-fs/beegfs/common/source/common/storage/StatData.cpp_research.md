# sources/distributed-fs/beegfs/common/source/common/storage/StatData.cpp

## Purpose
Implements dynamic file attribute aggregation from storage chunk metadata and equality for `StatData`.

## Important APIs, Types, And Functions
`updateDynamicFileAttribs()` updates file size, timestamps, block accounting, sparse flag, and ctime. `operator==()` compares all persisted/stat fields including chunk block vector and metadata version.

## Control Flow
The update method first checks whether any chunk info has a nonzero storage version; if none do, static metadata remains. It scans chunk info to find the last target with the maximum chunk count, max mtime/atime, per-target block counts, and then computes file length using stripe order and chunk size. It compares estimated blocks to actual used blocks with a grace threshold to set/unset the sparse flag, updates atime, ctime when mtime or size changed, mtime, and size.

## State, Persistence, And Dependencies
Mutates `StatData` fields and `ChunksBlocksVec`. Depends on `ChunkFileInfoVec`, `StripePattern`, `TimeAbs`, serialization/logging includes, and constants from `StatData.h`.

## Integration Points
Called when metadata servers merge dynamic attributes from storage targets, especially after close/stat workflows.

## Risks
Correctness depends on `fileInfoVec` order matching stripe target order and `stripePattern->getNumStripeTargetIDs()`. Partial dynamic info uses max(MDS, chunk) timestamps, while full info trusts chunk info. Sparse detection is heuristic with grace blocks.

## Test Signals
Cover no valid dynamic attributes, partial versus full dynamic info, multi-stripe file-size calculation, sparse and non-sparse thresholds, ctime update rules, zero chunks, stale chunk info, and equality.
