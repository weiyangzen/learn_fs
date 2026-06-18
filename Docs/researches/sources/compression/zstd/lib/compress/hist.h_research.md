# sources/compression/zstd/lib/compress/hist.h

## Purpose
`hist.h` declares the histogram API used by zstd's entropy compressors. It documents safe, fast, workspace-backed, and lowest-level additive counting variants.

## Important APIs, Types, and Functions
The public declarations are `HIST_count()`, `HIST_isError()`, `HIST_count_wksp()`, `HIST_countFast()`, `HIST_countFast_wksp()`, `HIST_count_simple()`, and `HIST_add()`. It defines `HIST_WKSP_SIZE_U32` as `1024` normally and `0` when compiling for ARM SVE2, with `HIST_WKSP_SIZE` as the byte-size equivalent.

## Control Flow, State, and Persistence
The header has no runtime state. Its comments define important behavior: `HIST_count()` returns the most frequent symbol count or an error, `HIST_countFast()` and `HIST_count_simple()` trust that all input bytes are within `*maxSymbolValuePtr`, and `HIST_add()` increments an existing table without clearing it.

## Dependencies and Integration Points
It includes `../common/zstd_deps.h` for `size_t` only. `hist.c` implements the declarations, while FSE/HUF compression include the header to collect symbol statistics. The workspace macros are part of the integration contract with higher-level workspace unions.

## Risks and Test Signals
The biggest API risk is the distinction between checked and unchecked counting. Callers using the fast/simple variants must size `count` for the actual maximum byte value. Tests should verify workspace size macros match implementation expectations on SVE2 and non-SVE2 builds, and that header declarations remain usable from C and C++ translation units.
