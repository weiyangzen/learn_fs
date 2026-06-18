# sources/compression/zstd/tests/fuzz/stream_decompress.c

## Purpose

`stream_decompress.c` fuzzes streaming decompression on arbitrary input with randomized input and output chunk boundaries. It validates that the streaming decoder handles partial buffers, zero-size buffers, stable-output mode, and errors without crashing.

## Important APIs And Functions

The helper `makeOutBuffer()` chooses an output buffer capacity from zero to the allocated size and sets `dst` to `NULL` when size is zero. `makeInBuffer()` chooses an input chunk size from zero to remaining bytes and sets `src` to `NULL` when size is zero. The entry point uses `ZSTD_createDStream()`, `ZSTD_DCtx_reset()`, `ZSTD_DCtx_setParameter(ZSTD_d_stableOutBuffer)`, and `ZSTD_decompressStream()`.

## Control Flow

The fuzzer reserves prefix bytes, allocates an output buffer of `MAX(10 * size, ZSTD_BLOCKSIZE_MAX)`, creates or resets the stream, and sometimes enables stable-output-buffer mode. In stable mode, one output buffer covers the entire run and filling it is treated as an error exit. Otherwise, output buffers are randomly remade whenever the previous one fills.

The main loop feeds randomized input chunks until all bytes are consumed. Each input chunk is decompressed in a `do` loop until `in.pos == in.size`. Any zstd error jumps to cleanup and returns success from the fuzz harness because arbitrary input may be invalid.

## State And Persistence

`dstream` is static and may persist under `STATEFUL_FUZZING`; otherwise it is freed per input. A global `uint32_t seed` is declared but unused. Output buffer and data producer are per input.

## Dependencies And Integration Points

This target uses zstd static decompression APIs and fuzz data producer helpers. It covers the streaming decoder boundary contract used by applications that provide partial input/output buffers.

## Risks And Edge Cases

The target exercises zero-size input/output chunks, `NULL` buffer pointers paired with size zero, stable output-buffer semantics, arbitrary invalid frames, and contexts reset with `ZSTD_reset_session_only`. It does not assert a full-frame success invariant, so semantic correctness is covered by round-trip streaming tests.

## Test Signals

The key signal is no crash or sanitizer failure through random chunking and stable buffer mode. Additional regressions are zstd errors on internally valid streaming frames, which are better detected by `stream_round_trip.c`.
