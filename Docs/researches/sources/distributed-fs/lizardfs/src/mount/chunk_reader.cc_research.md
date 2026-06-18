# sources/distributed-fs/lizardfs/src/mount/chunk_reader.cc

## Purpose
`chunk_reader.cc` implements chunk-level read planning and execution. It chooses the best chunkserver locations for each chunk part, handles sparse/EOF reads, and tracks CRC-failed locations to avoid retrying bad copies.

## Important APIs, Types, And Functions
- `ChunkReader::prepareReadingChunk(inode,index,force_prepare)` locates a chunk and prepares part-location maps and planner scores.
- `ChunkReader::readData(buffer,offset,size,connectTimeout,waveTimeout,communicationTimeout,prefetchXorStripes)` reads available data and appends it to `buffer`.
- Static `ChunkReader::preparations` counts prepare calls for diagnostics.

## Control Flow
Preparing a new chunk clears CRC error memory, invalidates the read locator cache, fetches `ChunkLocationInfo`, returns early for sparse empty chunks, then iterates locations. For each chunk part type it selects the highest-scoring chunkserver from `globalChunkserverStats`, skipping locations previously associated with CRC exceptions. Scores and available part types are handed to `ChunkReadPlanner`.

Reading clamps the requested range to file length. Empty chunks append zeros. Non-empty chunks plan reads from block-aligned ranges, require the planner to report possible reconstruction, optionally disable XOR prefetch, and execute through `ReadPlanExecutor`. On `ChunkCrcException`, the failing server/type is recorded and the exception is rethrown. The buffer is then resized back to the actual available byte count to remove block-rounding padding.

## State And Persistence
State is per `ChunkReader`: current inode/index, cached location pointer, planner, available part list, selected location map, CRC-error list, and `chunkAlreadyRead` prefetch hint. There is no persistence; it reads chunkserver data and relies on master metadata.

## Dependencies And Integration Points
It integrates with `ReadChunkLocator`, `ChunkReadPlanner`, `ReadPlanExecutor`, `ChunkConnector`, `globalChunkserverStats`, `Timeout`, and common exception classes. Higher-level read paths call prepare/read for each file chunk.

## Risks
- `readData` assumes `prepareReadingChunk` has populated `location_`; callers must respect that lifecycle.
- `blockToReadCount` is computed from `availableSize` but not adjusted for nonzero intra-block offset; correctness depends on planner/executor handling first block offset semantics.
- CRC error memory is cleared only when changing chunks, so repeated forced prepares avoid bad locations within the same chunk.
- Prefetch is disabled at EOF or after first full read, which depends on page cache assumptions.

## Test Signals
Tests should cover sparse reads returning zeros, EOF clamping, planner failure raising `NoValidCopiesReadException`, highest-score server selection, CRC error suppression on retry, and buffer resizing for partial final blocks.
