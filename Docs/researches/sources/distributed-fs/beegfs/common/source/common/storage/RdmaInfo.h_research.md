# sources/distributed-fs/beegfs/common/source/common/storage/RdmaInfo.h

## Purpose
When `BEEGFS_NVFS` is enabled, defines RDMA buffer descriptor metadata supplied by clients and an iterator-style API to consume it.

## Important APIs, Types, And Functions
`RDMA_MAX_DMA_COUNT`, `RdmaInfo` public serialized fields (`count`, `tag`, `key`, address/length/offset arrays, `status`), `more()`, `next()`, `isValid()`, and serialization.

## Control Flow
Serialization writes count/tag/key, validates count, logs and returns early if count is too large, then serializes each buffer triple. `next()` returns the current triple and advances `cur`.

## State, Persistence, And Dependencies
State is request-supplied RDMA descriptors plus private iterator cursor. Only compiled under `BEEGFS_NVFS`. Dependencies on logging/string helpers are implied by the serialization body.

## Integration Points
Used by NVFS/RDMA read/write message paths to describe remote DMA buffers.

## Risks
`isValid()` uses `count < RDMA_MAX_DMA_COUNT`, so exactly 64 buffers are invalid despite arrays sized 64; this may be intentional or off-by-one. Serialization returns after logging invalid count, leaving deserializer state considerations to callers.

## Test Signals
Compile with and without `BEEGFS_NVFS`, validate zero/one/max/excess counts, iterator exhaustion, serialized triples, and error handling for invalid count.
