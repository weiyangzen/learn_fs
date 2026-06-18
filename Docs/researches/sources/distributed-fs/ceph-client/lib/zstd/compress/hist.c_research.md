# sources/distributed-fs/ceph-client/lib/zstd/compress/hist.c

## Purpose
`hist.c` implements byte histogram counting for entropy compression. It provides simple and workspace-backed counting paths used by FSE and HUF to build symbol frequency tables and detect RLE or incompressible data.

## Important Functions
`HIST_isError()` wraps `ERR_isError()`. `HIST_add()` increments counts without clearing. `HIST_count_simple()` clears the caller count table, counts bytes, updates the maximum symbol value, and returns the largest frequency. `HIST_count_parallel_wksp()` uses four 256-entry intermediate tables and recombines them. `HIST_countFast_wksp()` trusts input values are within the supplied max symbol, while `HIST_count_wksp()` validates if the max is below 255.

## Control Flow and State
The simple path is used for sources smaller than 1500 bytes or by callers that need no workspace. The parallel path initializes four counting tables, reads 32-bit chunks, stripes bytes across the four tables, finishes trailing bytes, recombines counts, finds the highest present symbol, optionally validates `maxSymbolValue`, and copies results to the caller's table. All state is caller-owned; there is no persistence.

## Dependencies and Integration Points
The file depends on `mem.h` for byte types and unaligned 32-bit loads, `debug.h`, `error_private.h`, and `hist.h`. `fse_compress.c` and `huf_compress.c` use these functions before normalization/tree construction.

## Risks and Test Signals
Risks center on unsafe fast variants: `HIST_count_simple()` and `HIST_countFast_wksp()` assume input bytes are within `*maxSymbolValuePtr`. Workspace must be 4-byte aligned and at least `HIST_WKSP_SIZE`. The parallel path reads a cached 32-bit word at the start, but callers with very small inputs are routed to the simple path. Tests should cover empty input, one-symbol input, max symbol below actual byte returning `maxSymbolValue_tooSmall`, aligned and misaligned workspace, small/large threshold behavior, overlapping `count` and workspace, and all 256 byte values.
