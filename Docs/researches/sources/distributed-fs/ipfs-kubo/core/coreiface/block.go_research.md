# sources/distributed-fs/ipfs-kubo/core/coreiface/block.go

## Purpose
Defines the CoreAPI block-layer interface for raw block import, retrieval, removal, and stat operations.

## Important APIs, Types, and Functions
Declares `BlockStat` with `Size` and `Path`, and `BlockAPI` with `Put`, `Get`, `Rm`, and `Stat`.

## Control Flow and State
This file has no implementation flow. It describes contracts over blockstore state: `Put` hashes and stores block data, optional pinning may affect pin state, `Get` resolves a path to block bytes, `Rm` removes local blocks subject to pinning/force semantics, and `Stat` returns size/path metadata.

## Dependencies and Integration Points
Depends on context, `io.Reader`, Boxo path types, and block options. Implementations live in coreapi and are tested by `coreiface/tests/block.go`.

## Risks and Test Signals
Risks are contract ambiguity around pinned block removal, path resolution, and CID option semantics. Test signals include raw/dag-pb/dag-cbor CID generation, forced removal, stat size, and pin-on-put behavior.
