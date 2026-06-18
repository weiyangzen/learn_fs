# sources/distributed-fs/ceph-client/lib/zstd/common/fse_decompress.c

## Purpose
`fse_decompress.c` implements FSE decoding table construction and workspace-backed FSE block decompression. It is the runtime counterpart to `fse.h`'s DTable API and is used when decoding FSE-coded Zstd sequence streams and FSE-compressed Huffman weight tables.

## Important Functions
`FSE_buildDTable_wksp()` delegates to `FSE_buildDTable_internal()`, which validates `tableLog`, `maxSymbolValue`, and workspace size, lays out low-probability symbols, spreads symbols through the decode table, and computes each entry's `nbBits` and `newState`. `FSE_decompress_usingDTable_generic()` decodes with two interleaved states and chooses `FSE_decodeSymbolFast()` when the table header allows it. `FSE_decompress_wksp_bmi2()` reads normalized counts with `FSE_readNCount_bmi2()`, builds a DTable inside caller workspace, and dispatches to the generic decoder.

## Control Flow and State
DTable construction stores an `FSE_DTableHeader` in `dt[0]`, uses a `symbolNext` array and spread buffer from workspace, reserves high table slots for `-1` low-probability symbols, and uses `FSE_TABLESTEP()` to fill the decode table. Decompression consumes the compressed bitstream from the end-oriented `BIT_DStream_t`, initializes two FSE states, emits four symbols per fast loop, then switches to a careful tail loop that checks output capacity and bitstream overflow/completion.

## Dependencies and Integration Points
The file includes `bitstream.h`, `compiler.h`, `fse.h`, `error_private.h`, `zstd_deps.h`, and `bits.h`. Workspace sizing must agree with `FSE_BUILD_DTABLE_WKSP_SIZE()` and `FSE_DECOMPRESS_WKSP_SIZE()` from `fse.h`. BMI2 dispatch is compiled only if `DYNAMIC_BMI2` is enabled, which this tree's portability macros generally disable.

## Risks and Test Signals
Primary risks are corrupted normalized counters, incorrect `highThreshold` handling, output overrun in the tail loop, and too-small workspace leading to table overlap. `FSE_decompress_usingDTable_generic()` returns the number of produced bytes but does not independently compare against an expected uncompressed size, so callers must provide the right destination capacity and higher-level frame checks. Tests should cover malformed NCount headers, tableLog above caller `maxLog`, low-probability distributions, fastMode on/off, tiny output buffers, exact bitstream completion, and BMI2 flag equivalence.
