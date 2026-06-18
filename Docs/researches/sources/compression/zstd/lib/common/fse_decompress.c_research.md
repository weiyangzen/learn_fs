# sources/compression/zstd/lib/common/fse_decompress.c

## Purpose
`fse_decompress.c` implements FSE decoding table construction and workspace-backed decompression for byte symbols. It is a template-style source that depends on `FSE_FUNCTION_TYPE`, `FSE_FUNCTION_EXTENSION`, and `FSE_DECODE_TYPE` macros so the same logic can be reused for specific symbol types.

## Important APIs, Types, and Functions
The key builder is `FSE_buildDTable_internal()`, exported through `FSE_buildDTable_wksp()`. It lays out low-probability symbols, spreads the remaining symbols across the decode table, and computes each entry's `nbBits` and `newState`. `FSE_decompress_usingDTable_generic()` drives two interleaved `FSE_DState_t` states over a `BIT_DStream_t` and selects normal or fast symbol reads. `FSE_decompress_wksp_body()` reads normalized counts with `FSE_readNCount_bmi2()`, validates `maxLog`, partitions the caller workspace into `FSE_DecompressWksp`, DTable, and scratch space, builds the DTable, reads `fastMode`, and dispatches to the generic decoder. `FSE_decompress_wksp_bmi2()` performs runtime BMI2 dispatch when `DYNAMIC_BMI2` is enabled.

## Control Flow, State, and Persistence
Build flow starts by checking workspace, symbol, and table-log bounds. It initializes the DTable header, reserves high table slots for `-1` low-probability symbols, sets `fastMode` to false when any symbol frequency can decode with zero bits, spreads symbols either through an optimized branchless two-stage path or a slower path that skips the low-probability zone, then derives state transitions from `symbolNext`. Decode flow initializes the bitstream and two states, rejects immediate overflow, emits four symbols per loop while the bitstream is unfinished and there is room, then finishes with a guarded tail loop. State is entirely in caller buffers and stack variables; no global persistence exists.

## Dependencies and Integration Points
The implementation includes `debug.h`, `bitstream.h`, `compiler.h`, `fse.h`, `error_private.h`, `zstd_deps.h`, and `bits.h`. It uses `MEM_write64()` for the spread optimization, `ZSTD_memcpy()` for the DTable header, `ZSTD_highbit32()` for transition bit counts, and `ERROR()`/`CHECK_F()` for zstd-style failures. Huffman table parsing and zstd entropy decompression call through the workspace API, often with CPU BMI2 selection supplied by higher layers.

## Risks and Test Signals
The highest-risk areas are malformed normalized counts that fail to visit every decode table cell, too-small workspaces, table logs above caller policy, and tail-loop output bounds. The optimized spread path intentionally over-writes up to 8 bytes inside scratch space, so its workspace sizing macro must stay in sync. Test signals include corruption errors for bad NCounts, `dstSize_tooSmall` when the destination tail is tight, successful decoding of low-probability symbols, fast-mode and non-fast-mode coverage, BMI2/non-BMI2 parity, and sanitizer coverage for fuzzed compressed streams.
