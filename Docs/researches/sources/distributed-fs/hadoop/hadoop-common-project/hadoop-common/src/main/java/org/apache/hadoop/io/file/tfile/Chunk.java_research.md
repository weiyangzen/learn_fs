# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/file/tfile/Chunk.java

Purpose: chunk-encoding utilities for representing sub-streams as length-prefixed chunk chains.

Important APIs/types/functions: `ChunkDecoder`, `ChunkEncoder`, and `SingleChunkEncoder`.

Control flow: encoded chains use VInt lengths where non-terminal chunks are negative and the terminal chunk is non-negative. `ChunkDecoder` reads chunk lengths lazily, tracks remaining bytes, and drains to the last chunk on close. `ChunkEncoder` buffers data and writes negative chunks until close writes the final positive-length chunk. `SingleChunkEncoder` writes the advertised size first, then enforces exactly that many bytes before close succeeds.

State and persistence: stream-local counters and buffers; chunk format is persisted to the underlying stream.

Dependencies and integration: uses `Utils.readVInt/writeVInt`; supports TFile sub-stream/data-block encoding patterns.

Risks: corrupted streams where data ends before declared chunk size raise `IOException`. `ChunkEncoder.close()` nulls internal buffer/out, making repeated use invalid. Tests should cover empty stream final chunk, multi-chunk data, reset reuse of decoder, advertised size under/over-write, close draining, skip semantics, and corrupt length/data cases.
