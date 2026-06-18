<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/pzstd/utils/Buffer.h -->
# sources/compression/zstd/contrib/pzstd/utils/Buffer.h

## Purpose
`Buffer.h` implements a reference-counted byte-buffer slice abstraction used to move chunks through pzstd queues without copying whole allocations.

## Important APIs, Types, And Functions
`Buffer` exposes constructors from size or shared storage, `data`, `range`, `size`, `empty`, `use_count`, `advance`, `subtract`, and `splitAt`.

## Control Flow
Readers allocate a buffer, fill it, and split off populated prefixes. Compression/decompression code advances consumed input and splits produced output based on zstd buffer positions.

## State And Persistence
State is a shared underlying allocation plus begin/end range pointers or offsets. Lifetime is controlled by shared ownership; no persistence exists.

## Dependencies And Integration Points
It depends on `Range.h` and standard smart pointers. `Pzstd.cpp` and `BufferWorkQueue` use it heavily.

## Risks
Range-splitting must maintain valid boundaries and shared lifetime. Incorrect size accounting can break backpressure or frame-size calculations.

## Test Signals
`BufferTest.cpp` covers construction, shared ownership counts, advance/subtract, and split behavior.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/pzstd/utils/Buffer.h -->
