# Research: subset-b-000311

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/lib/common/zstd_common.c -->
# sources/compression/zstd/lib/common/zstd_common.c

## Purpose
`zstd_common.c` provides the small public/common ABI surface that must exist even when most zstd logic is compiled into other translation units. It exports version metadata, error-result classification, error-name conversion, enum-to-string conversion, and a deterministic-build probe. The file is intentionally narrow: it bridges public `zstd.h` users to internal `error_private.h` helpers without exposing private macros as the only callable interface.

## Important APIs, Types, and Functions
The exported functions are `ZSTD_versionNumber()`, `ZSTD_versionString()`, `ZSTD_isError()`, `ZSTD_getErrorName()`, `ZSTD_getErrorCode()`, `ZSTD_getErrorString()`, and `ZSTD_isDeterministicBuild()`. `ZSTD_ErrorCode` comes from the public zstd API, while the actual error mechanics come from `ERR_isError()`, `ERR_getErrorName()`, `ERR_getErrorCode()`, and `ERR_getErrorString()`. The file undefines the inline/macro `ZSTD_isError` from `zstd_internal.h` so a real external symbol is emitted.

## Control Flow, State, and Persistence
There is no mutable state, allocation, or persistence. Each function is a direct constant return or one-hop wrapper. `ZSTD_isDeterministicBuild()` is compile-time controlled by `ZSTD_IS_DETERMINISTIC_BUILD`, returning `1` or `0` based on preprocessor configuration.

## Dependencies and Integration Points
The file defines `ZSTD_DEPS_NEED_MALLOC` before including `zstd_internal.h`, so the dependency shim exposes malloc/free/calloc macros for downstream common internals. It integrates with public callers that need stable symbols for version and error handling, and with test/packaging code that needs to verify deterministic build settings.

## Risks and Test Signals
Risk is mainly ABI and macro drift: removing the `#undef ZSTD_isError` would leave external callers without the intended function symbol. Error-code wrappers must stay consistent with `error_private.h`. Test signals include checking version string/number against public macros, verifying `ZSTD_isError()` recognizes all `ERROR(...)` results, and building with deterministic mode both enabled and disabled.
<!-- END_FILE_RESEARCH: sources/compression/zstd/lib/common/zstd_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/lib/common/zstd_deps.h -->
# sources/compression/zstd/lib/common/zstd_deps.h

## Purpose
`zstd_deps.h` is zstd's libc dependency abstraction layer. It centralizes the minimum standard headers and macros needed by the library so embedders can replace or constrain libc usage, especially for freestanding or custom-allocation builds.

## Important APIs, Types, and Functions
The common section supplies `NULL`, integer limits, `size_t`, and memory operations through `ZSTD_memcpy`, `ZSTD_memmove`, and `ZSTD_memset`. Optional feature blocks are enabled by `ZSTD_DEPS_NEED_MALLOC`, `ZSTD_DEPS_NEED_MATH64`, `ZSTD_DEPS_NEED_ASSERT`, `ZSTD_DEPS_NEED_IO`, and `ZSTD_DEPS_NEED_STDINT`. These expose `ZSTD_malloc`, `ZSTD_calloc`, `ZSTD_free`, `ZSTD_div64`, `assert()`, `ZSTD_DEBUG_PRINT`, and `intptr_t` respectively.

## Control Flow, State, and Persistence
The header has no runtime control flow or state. Behavior is compile-time selected through include guards and opt-in macros. On GCC 4+, memory operations use compiler builtins; otherwise they map to libc functions. On GNU-like platforms it may define `_GNU_SOURCE` before any standard header, because zstd's combined source mode can need `qsort_r()` declarations elsewhere.

## Dependencies and Integration Points
This header is included by common and compression modules such as `zstd_common.c`, `hist.h`, `fse_compress.c`, and `huf_compress.c`. It is the integration point for custom platform layers: replacing this file or predefining equivalent macros changes allocation, memory, math, debug IO, and assertion behavior across the library.

## Risks and Test Signals
The main risks are include-order sensitivity around `_GNU_SOURCE`, inconsistent macro overrides in custom builds, and assuming optional sections exist without defining the matching `ZSTD_DEPS_NEED_*` macro. Tests should compile minimal modules with only common dependencies, then with each optional block enabled. Freestanding builds should verify all required macros can be supplied without accidental libc references.
<!-- END_FILE_RESEARCH: sources/compression/zstd/lib/common/zstd_deps.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/lib/common/zstd_internal.h -->
# sources/compression/zstd/lib/common/zstd_internal.h

## Purpose
`zstd_internal.h` contains shared internal definitions that must match across compression, decompression, dictionary building, benchmarks, and tests. It defines frame/block constants, entropy coding tables, repeated-offset defaults, copy helpers, workspace heuristics, private declarations, and CPU feature dispatch helpers.

## Important APIs, Types, and Functions
Important constants include block and frame header sizes, frame checksum size, minimum match size, literal/FSE alphabet limits, default normalized LL/ML/OF tables, `ZSTD_MAX_HUF_HEADER_SIZE`, and `ZSTD_MAX_FSE_HEADERS_SIZE`. Types include `blockType_e`, `SymbolEncodingType_e`, `ZSTD_overlap_e`, `ZSTD_bufferMode_e`, `ZSTD_frameSizeInfo`, and `blockProperties_t`. Inline helpers include `ZSTD_copy8()`, `ZSTD_copy16()`, `ZSTD_wildcopy()`, `ZSTD_limitCopy()`, and `ZSTD_cpuSupportsBmi2()`. Private declarations expose `ZSTD_invalidateRepCodes()`, `ZSTD_getcBlockSize()`, and `ZSTD_decodeSeqHeaders()`.

## Control Flow, State, and Persistence
Most state is static constant lookup data. `ZSTD_wildcopy()` is the main behavioral helper: it copies in 16-byte chunks when buffers are safely separated and falls back to repeated 8-byte copies for short offset overlap where source precedes destination. It may intentionally overread/overwrite up to `WILDCOPY_OVERLENGTH`, so callers must reserve slack. `ZSTD_cpuSupportsBmi2()` probes CPUID dynamically and returns whether BMI1/BMI2 dispatch is available.

## Dependencies and Integration Points
The header pulls in compiler, CPU, memory, debug, public zstd, FSE, HUF, xxhash, and optional tracing definitions. Compression code consumes default FSE norms and copy helpers; decompression uses block parsing types and wildcopy; zstdmt/adaptive compression reach `ZSTD_invalidateRepCodes()`; fullbench uses block-size and sequence-header declarations.

## Risks and Test Signals
Risks are high because constants are format-critical. Changing LL/ML/OF defaults, block header sizes, or field sizes can break frame compatibility. `ZSTD_wildcopy()` requires precise caller preconditions around overlap and output slack; sanitizer tests should cover short offsets, vectorized paths, and boundary slack. BMI2 dispatch should be tested on forced-default and BMI2-capable builds.
<!-- END_FILE_RESEARCH: sources/compression/zstd/lib/common/zstd_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/lib/common/zstd_trace.h -->
# sources/compression/zstd/lib/common/zstd_trace.h

## Purpose
`zstd_trace.h` defines the optional weak-symbol tracing ABI for compression and decompression calls. It lets external instrumentation observe begin/end events without adding hard runtime dependencies when tracing is unavailable.

## Important APIs, Types, and Functions
The key type is `ZSTD_Trace`, carrying version, streaming flag, dictionary ID, dictionary coldness, dictionary size, uncompressed size, compressed size, resolved compression parameters, and the active compression/decompression context pointer. `ZSTD_TraceCtx` is an opaque nonzero token returned by begin hooks. Optional weak hook declarations are `ZSTD_trace_compress_begin()`, `ZSTD_trace_compress_end()`, `ZSTD_trace_decompress_begin()`, and `ZSTD_trace_decompress_end()`.

## Control Flow, State, and Persistence
The header owns no state. Preprocessor checks set `ZSTD_HAVE_WEAK_SYMBOLS` only for conservative GNU/ELF architecture and OS combinations, excluding Apple, Windows, MinGW, Cygwin, and AIX. `ZSTD_TRACE` defaults to weak-symbol availability unless explicitly overridden. When tracing is disabled, the hook declarations and trace structs are not compiled.

## Dependencies and Integration Points
It includes `<stddef.h>` and forward declares zstd context/parameter structs. `zstd_internal.h` includes it unless `ZSTD_NO_TRACE` is defined; compression/decompression implementations can call begin/end hooks guarded by `ZSTD_TRACE`. External profilers or observability libraries can define the weak symbols to receive events.

## Risks and Test Signals
The ABI is intentionally version-sensitive: `version` must remain the first field so consumers can reject unknown layouts. Weak-symbol support is platform-sensitive, so build tests should cover enabled and disabled tracing targets. Runtime tests can define hooks, ensure begin nonzero tokens are passed to matching end calls, and verify tracing compiles out cleanly under `ZSTD_NO_TRACE`.
<!-- END_FILE_RESEARCH: sources/compression/zstd/lib/common/zstd_trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/lib/compress/clevels.h -->
# sources/compression/zstd/lib/compress/clevels.h

## Purpose
`clevels.h` stores zstd's pre-defined compression-parameter table. It maps source-size bands and compression levels to `ZSTD_compressionParameters`, providing the baseline policy used when callers request numeric compression levels instead of explicit tuning.

## Important APIs, Types, and Functions
The header defines `ZSTD_MAX_CLEVEL` as `22` and the static `ZSTD_defaultCParameters[4][ZSTD_MAX_CLEVEL+1]` table. Each row entry contains window log, chain log, hash log, search log, minimum match length, target length, and strategy. The four size bands are default for inputs larger than 256 KB, inputs up to 256 KB, inputs up to 128 KB, and inputs up to 16 KB. Entry zero is the base for negative levels.

## Control Flow, State, and Persistence
There is no runtime control flow. The table is read-only static data selected by higher-level parameter selection code based on source size and requested level. Strategies progress from `ZSTD_fast` and `ZSTD_dfast` through greedy/lazy modes to binary-tree optimal modes (`ZSTD_btopt`, `ZSTD_btultra`, `ZSTD_btultra2`) as levels increase.

## Dependencies and Integration Points
The header defines `ZSTD_STATIC_LINKING_ONLY` before including `../zstd.h` to expose `ZSTD_compressionParameters` and strategy enums. Compression context initialization and parameter adjustment code consume this table as the canonical built-in level policy.

## Risks and Test Signals
Changing values affects compression ratio, speed, memory use, and compatibility with published level expectations. Table dimensions must stay aligned with `ZSTD_MAX_CLEVEL`; off-by-one errors would mis-map levels. Test signals include snapshotting parameters for representative levels and sizes, verifying negative-level base behavior, and performance/regression tests for boundary sizes around 16 KB, 128 KB, and 256 KB.
<!-- END_FILE_RESEARCH: sources/compression/zstd/lib/compress/clevels.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/lib/compress/fse_compress.c -->
# sources/compression/zstd/lib/compress/fse_compress.c

## Purpose
`fse_compress.c` implements the Finite State Entropy encoder used by zstd for sequence-code streams and by Huffman header compression. It builds compression tables from normalized symbol counts, serializes normalized counts, chooses table logs, normalizes histograms, and encodes symbols into a reverse bitstream.

## Important APIs, Types, and Functions
Key exported functions are `FSE_buildCTable_wksp()`, `FSE_NCountWriteBound()`, `FSE_writeNCount()`, `FSE_optimalTableLog_internal()`, `FSE_optimalTableLog()`, `FSE_normalizeCount()`, `FSE_buildCTable_rle()`, `FSE_compress_usingCTable()`, and `FSE_compressBound()`. Important internal helpers are `FSE_writeNCount_generic()`, `FSE_minTableLog()`, `FSE_normalizeM2()`, and `FSE_compress_usingCTable_generic()`.

## Control Flow, State, and Persistence
`FSE_buildCTable_wksp()` lays out the CTable header, cumulative counts, symbol spread table, state table, and symbol transform table using caller-provided workspace. Low-probability symbols are placed in a high-threshold area; other symbols are distributed by `FSE_TABLESTEP()`. `FSE_writeNCount_generic()` bit-packs table log and normalized counts with compact zero-run encoding. `FSE_normalizeCount()` scales raw counts to sum to `1 << tableLog`, assigning low-probability symbols as `-1` or `1` and falling back to `FSE_normalizeM2()` for difficult rounding cases. `FSE_compress_usingCTable_generic()` initializes two encoder states from the input tail, walks input backwards, emits symbols into `BIT_CStream_t`, flushes states, and closes the stream.

## Dependencies and Integration Points
The file depends on memory helpers, bitstream writing, FSE public/static definitions, error macros, `ZSTD_div64`, and `ZSTD_highbit32`. `huf_compress.c` reuses this encoder to compress Huffman weight tables. Zstd block compression uses these routines after histograms have been collected by `hist.c`.

## Risks and Test Signals
Risks include workspace misalignment/size errors, invalid normalized distributions, tableLog underflow/overflow, bitstream buffer exhaustion, and subtle off-by-one issues in zero-run and low-probability encoding. Strong tests cover RLE inputs, incompressible distributions, tiny source sizes, maximum alphabet/table log, safe versus fast destination capacity paths, round-trip decode of NCount headers, and sanitizer runs over workspace overlap cases.
<!-- END_FILE_RESEARCH: sources/compression/zstd/lib/compress/fse_compress.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/lib/compress/hist.c -->
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
<!-- END_FILE_RESEARCH: sources/compression/zstd/lib/compress/hist.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/lib/compress/hist.h -->
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
<!-- END_FILE_RESEARCH: sources/compression/zstd/lib/compress/hist.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/lib/compress/huf_compress.c -->
# sources/compression/zstd/lib/compress/huf_compress.c

## Purpose
`huf_compress.c` implements zstd's Huffman encoder for literals. It builds canonical Huffman compression tables, writes/reads table descriptions, estimates compressed sizes, validates repeat tables, and compresses data using either one bitstream or four independently compressed segments.

## Important APIs, Types, and Functions
Important exported functions include `HUF_writeCTable_wksp()`, `HUF_readCTable()`, `HUF_getNbBitsFromCTable()`, `HUF_buildCTable_wksp()`, `HUF_estimateCompressedSize()`, `HUF_validateCTable()`, `HUF_compressBound()`, `HUF_compress1X_usingCTable()`, `HUF_compress4X_usingCTable()`, `HUF_cardinality()`, `HUF_minTableLog()`, `HUF_optimalTableLog()`, `HUF_compress1X_repeat()`, and `HUF_compress4X_repeat()`. Internal types include `nodeElt`, `rankPos`, `HUF_CStream_t`, `HUF_CompressWeightsWksp`, `HUF_WriteCTableWksp`, and `HUF_compress_tables_t`.

## Control Flow, State, and Persistence
Workspace is caller-owned and aligned by `HUF_alignUpWorkspace()`. Table construction starts with a histogram from `hist.c`, sorts symbols by count with bucketed ranking plus per-bucket sorting, builds an unlimited-depth Huffman tree, enforces a maximum height through `HUF_setMaxHeight()`, then emits canonical values by rank. `HUF_writeCTable_wksp()` converts bit lengths to weights and tries FSE compression for the weight table, falling back to raw 4-bit weights. Encoding uses a custom high-bit-first `HUF_CStream_t`; symbols are encoded backwards, flushed with table-log-specific unroll choices, and closed with a one-bit end mark. The 4X path divides input into four segments, stores the first three compressed sizes as a 6-byte jump table, and compresses each segment with the 1X encoder.

## Dependencies and Integration Points
The file depends on zstd dependency macros, compiler helpers, bitstream/memory primitives, `hist.h`, static FSE APIs, `huf.h`, error handling, and `ZSTD_highbit32`. It integrates with zstd block compression through repeat-table state (`HUF_repeat`) and flags such as BMI2 dispatch, optimal-depth probing, prefer-repeat, and suspect-incompressible sampling. It also uses FSE to compress Huffman weights.

## Risks and Test Signals
Risks include canonical-code correctness, height-limiting edge cases, workspace sizing/alignment, destination-bound fast paths, repeat-table validation, and incompressibility heuristics returning zero. Tests should cover single-symbol RLE, tiny inputs, all-symbol alphabets, repeat table reuse/check/invalid transitions, 1X and 4X output round trips, optimal-depth probing, BMI2 and default dispatch, raw versus FSE-compressed table headers, and sanitizer coverage of tight destination buffers.
<!-- END_FILE_RESEARCH: sources/compression/zstd/lib/compress/huf_compress.c -->
