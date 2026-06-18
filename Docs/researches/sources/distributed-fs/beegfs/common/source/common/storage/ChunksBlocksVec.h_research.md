# sources/distributed-fs/beegfs/common/source/common/storage/ChunksBlocksVec.h

## Purpose
Stores per-stripe-target block counts for chunk files, mainly to support sparse-file stat accounting.

## Important APIs, Types, And Functions
`setNumBlocks()`, `getNumBlocks()`, `getBlockSum()`, serialization, equality, and constructors are exported.

## Control Flow
The vector lazily resizes on first set using the caller-provided stripe target count. Out-of-range get/set logs an error and backtrace, returning or doing nothing.

## State, Persistence, And Dependencies
State is `UInt64Vector chunkBlocksVec`. It serializes directly and is embedded in `StatData` for disk metadata. Depends on serialization helpers, logging, and `<numeric>`.

## Integration Points
`StatData` uses it to track exact block usage per chunk when sparse files are detected.

## Risks
The vector size is determined by the first `setNumBlocks()` call; later stripe-pattern size changes need careful handling. Bounds errors are logged but not fatal.

## Test Signals
Test lazy initialization, per-target set/get, sum, sparse `StatData` serialization, and out-of-range logging.
