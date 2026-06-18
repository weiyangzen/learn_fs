# sources/compression/zstd/lib/compress/zstd_compress_superblock.h

## Purpose
Declares the private superblock compression entry point used when zstd tries to target a compressed block size. It is the interface between the main compressor and the multi-sub-block implementation.

## Important APIs, Types, And Functions
The header declares `ZSTD_compressSuperBlock(ZSTD_CCtx* zc, void* dst, size_t dstCapacity, void const* src, size_t srcSize, unsigned lastBlock)`. The comment documents that it compresses a given block into multiple sub-blocks around `targetCBlockSize`.

## Control Flow
The header is declarative. A caller with a populated `ZSTD_CCtx`, sequence store, and block state invokes this function instead of the normal single-block emission path when target compressed block sizing is active.

## State And Persistence
State is owned by `ZSTD_CCtx`; the API passes the context directly so the implementation can access sequence store, entropy state, parameters, BMI2 status, and scratch workspace.

## Dependencies And Integration Points
It includes public `zstd.h` for `ZSTD_CCtx`. The implementation also integrates with literal and sequence encoders, but those details are intentionally hidden from this header.

## Risks And Edge Cases
Because the function receives the full context, changes to `ZSTD_CCtx_s` internals can affect the implementation without signature changes. Callers must only use it after sequence generation and entropy workspace initialization.

## Test Signals
Compile coverage plus target-block-size compression/decompression tests are the main validation signals.
