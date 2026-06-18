# sources/distributed-fs/ipfs-kubo/blocks/blockstoreutil/remove.go

## Purpose
This utility package removes blocks from a GC-capable blockstore while protecting pinned content.

## Important APIs, Types, And Functions
`RemovedBlock` reports a CID hash plus optional error. `RmBlocksOpts` carries `Prefix`, `Quiet`, and `Force`. `RmBlocks` returns an asynchronous channel of results. `FilterPinned` calls `pin.Pinner.CheckIfPinned` and emits pinned errors.

## Control Flow
`RmBlocks` creates a buffered result channel, takes the blockstore GC lock, filters pinned CIDs, checks block existence unless forced, deletes blocks, and emits successes unless quiet. Fatal pin-check failures emit a result with empty hash and stop removal.

## State And Persistence Behavior
It mutates the blockstore by deleting blocks under the GC lock. Pin state is read-only but authoritative for skip decisions.

## Dependencies And Integration Points
It integrates Boxo `GCBlockstore`, Kubo/Boxo pinner semantics, CIDs, and go-ipld-format not-found errors.

## Risks And Test Signals
Risks include asynchronous callers not draining results, stale pin state, existence checks retained for compatibility, and partial deletion after per-block errors. Signals are result objects for pinned, missing, failed, and successfully removed blocks.
