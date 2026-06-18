# sources/compression/zstd/lib/compress/hist.c

## Purpose
`hist.c` implements byte histogram construction for entropy encoders. It counts symbol frequencies, returns the largest frequency, updates the actual maximum symbol value, and offers workspace-backed and stack-backed variants.

## Important APIs, Types, and Functions
Exported functions are `HIST_isError()`, `HIST_add()`, `HIST_count_simple()`, `HIST_countFast_wksp()`, `HIST_count_wksp()`, `HIST_countFast()`, and `HIST_count()`. The internal `HIST_checkInput_e` distinguishes trusted input from checked maximum-symbol validation. Non-SVE2 builds use `HIST_count_parallel_wksp()` with four 256-entry counters; SVE2 builds use vectorized `HIST_count_sve2()` and `HIST_count_6_sve2()`.

## Control Flow, State, and Persistence
`HIST_count_simple()` zeros the count table, counts bytes linearly, trims `*maxSymbolValuePtr` down to the last nonzero symbol, and scans for the largest count. `HIST_count_parallel_wksp()` zeros four intermediate tables, reads 32-bit chunks in stripes, increments lane-specific counters, merges lanes, checks the max symbol if requested, and copies the merged result to the caller table. `HIST_count_wksp()` validates workspace alignment/size, chooses checked counting when the caller's max is below 255, and otherwise delegates to the fast path. SVE2 paths use segmented histogram instructions and clear unused ranges.

## Dependencies and Integration Points
The file depends on `mem.h` for byte and unaligned read helpers, `debug.h` for assertions/logging, `error_private.h`, and `hist.h`. FSE and HUF compression call these routines before building entropy tables. The workspace contract is exposed by `hist.h` so higher-level compressors can avoid large stack allocations.

## Risks and Test Signals
`HIST_countFast*()` trusts the caller's max symbol and can write out of bounds if misused. Workspace must be 4-byte aligned and at least `HIST_WKSP_SIZE` on non-SVE2 platforms. Boundary tests should include empty input, one-symbol input, max symbol below actual input to force `maxSymbolValue_tooSmall`, all 256 byte values, small inputs below the fast threshold, and SVE2/non-SVE2 parity where available.
