# sources/distributed-fs/ceph-client/lib/zstd/compress/hist.h

## Purpose
`hist.h` declares the histogram API used by FSE and HUF compression. It defines the caller contract for precise byte counting, fast unsafe counting, workspace-backed variants, and additive counting.

## Important APIs and Constants
`HIST_count()` and `HIST_count_wksp()` provide checked counting that updates `*maxSymbolValuePtr` and returns the most frequent count. `HIST_countFast()` and `HIST_countFast_wksp()` skip input validation and require all source bytes to be at most the caller-provided maximum. `HIST_count_simple()` is a no-extra-memory unsafe path. `HIST_add()` accumulates counts into an existing table. `HIST_WKSP_SIZE_U32` is `1024`, exactly four 256-entry `unsigned` tables.

## Control Flow and State
The header itself has no implementation state. It documents that count arrays must be preallocated to at least `maxSymbolValue + 1`, that workspace must be writable and 4-byte aligned, and that a return equal to `srcSize` signals a single-symbol distribution suitable for RLE handling.

## Dependencies and Integration Points
It includes `../common/zstd_deps.h` for `size_t`. `fse_compress.c` and `huf_compress.c` include it to build frequency distributions before entropy table construction. The workspace size is embedded into compression workspace unions, so changes affect memory layout.

## Risks and Test Signals
The chief risk is caller misuse of unsafe APIs with an undersized count table or too-small `maxSymbolValue`. Because return values may be error-coded `size_t`, callers must use `HIST_isError()` or `CHECK_*` macros. Tests should verify API contracts around max-symbol updates, RLE detection, zero-sized input, workspace size/alignment errors, and consistency between simple, fast, and checked paths for valid data.
