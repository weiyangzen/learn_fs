<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/pzstd/Pzstd.cpp -->
# sources/compression/zstd/contrib/pzstd/Pzstd.cpp

## Purpose
`Pzstd.cpp` implements pzstd's parallel compression/decompression engine and CLI file-processing loop.

## Important APIs, Types, And Functions
Public functions are `pzstdMain`, `asyncCompressChunks`, `asyncDecompressFrames`, and `writeFile`. Key helpers include `handleOneInput`, file open helpers, zstd buffer adapters, `compress`, `decompress`, `calculateStep`, `readData`, and `writeData`.

## Control Flow
`pzstdMain` iterates inputs, opens files, selects output names, runs `handleOneInput`, and optionally deletes sources after successful close. Compression uses a reader thread to split input into frame-sized `BufferWorkQueue`s, a worker `ThreadPool` to compress each frame, and the writer to emit a pzstd skippable frame plus compressed data in order. Decompression reads pzstd skippable frame headers when present to parallelize frame decompression; otherwise it falls back to one serial decompression task.

## State And Persistence
`SharedState` holds logger, error holder, and zstd stream resource pools. Queues carry buffers between threads. Persistent effects are output files and optional input removal.

## Dependencies And Integration Points
It integrates `Options`, `SkippableFrame`, `Buffer`, `WorkQueue`, `ThreadPool`, `ResourcePool`, zstd streaming APIs, and stdio/file utilities.

## Risks
Concurrency correctness depends on queue finish ordering and `ErrorHolder` polling. `calculateStep` asserts window logs <=23 because skippable frame sizes are 32-bit. Writer waits for compressed frame size before output, so broken worker finish can deadlock.

## Test Signals
`PzstdTest.cpp` and `RoundTripTest.cpp` cover small/large/highly-compressible round trips, while utility tests cover queues and pools used by this flow.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/pzstd/Pzstd.cpp -->
