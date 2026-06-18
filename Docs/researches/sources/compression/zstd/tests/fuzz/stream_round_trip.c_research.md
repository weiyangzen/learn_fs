# sources/compression/zstd/tests/fuzz/stream_round_trip.c

## Purpose

`stream_round_trip.c` fuzzes zstd streaming compression and decompression as a complete round trip. It randomizes input chunk sizes, output chunk sizes, flush/end/continue actions, context resets between frames, compression parameters, and in-place decompression margin behavior.

## Important APIs And Functions

Helpers `makeOutBuffer()` and `makeInBuffer()` create nonzero-sized streaming buffers. `compress()` drives `ZSTD_compressStream2()` with randomly selected `ZSTD_e_continue`, `ZSTD_e_flush`, and `ZSTD_e_end` operations. `decompress()` uses `ZSTD_decompressStream()` to consume the generated stream and may configure `ZSTD_d_maxBlockSize` from the compressor's max block size.

The entry point allocates static buffers sized as `ZSTD_compressBound(size) * 15`, creates `ZSTD_CCtx` and `ZSTD_DCtx`, then validates normal and in-place-style decompression.

## Control Flow

Compression starts by resetting the compression session, setting random parameters, and reading the selected max block size. The compressor loops over randomized source chunks. For each input chunk, it randomly chooses actions: flush, end, continue, and a special zero-input/zero-output continue call. When an end operation completes a frame, it resets the session and occasionally selects new random parameters while preserving the same max block size.

After all source bytes are consumed, it repeatedly calls `ZSTD_e_end` with empty input until the final frame is closed. Decompression feeds the complete compressed stream to `ZSTD_decompressStream()` in one input buffer and asserts each return is zero while progress remains, then returns the output position. The entry point checks decompressed size and byte equality, then verifies `ZSTD_decompressionMargin()` by copying the compressed stream to the tail of a combined buffer and decompressing into the front.

## State And Persistence

`cctx`, `dctx`, `cBuf`, `rBuf`, and `bufSize` are static. Buffers grow to meet the largest seen input and persist for stateful fuzzing and across calls until process exit. Contexts are freed per input unless `STATEFUL_FUZZING` is defined; static buffers are not freed in the non-stateful cleanup path.

## Dependencies And Integration Points

The target uses zstd static-linking APIs, random parameter helpers, fuzz allocation/assertion utilities, and optional third-party sequence producer setup. It covers applications that interleave flush/end actions and create multiple frames in one stream.

## Risks And Edge Cases

Important edges include very small output chunks, repeated flushes, ending and resetting frames mid-input, zero-buffer continue calls, multiple frames in a single compressed stream, preserved decoder max-block constraints, large safety multiplier for compressed buffer capacity, and overlap-sensitive decompression margins.

The `decompress()` helper asserts `ret == 0` for every streaming call while input remains. This matches the expectation that a complete compressed stream is available in the input buffer, but it is stricter than generic streaming caller behavior and is tuned for this generated data.

## Test Signals

Failures include streaming API crashes, unexpected compression/decompression zstd errors, incomplete decompression, byte corruption, incorrect decompression margins, and reset/parameter bugs between frames. Corpus inputs that trigger multiple frames, many flushes, and max-block-size changes are especially useful.
