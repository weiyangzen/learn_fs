# Group Research: group_1666_reactos_sources_windows_reactos_drivers_filesystems_btrfs_xxhash_h__33a0d552c7d4

This group covers imported xxHash and Zstd/FSE/HUF entropy support code used by the ReactOS Btrfs filesystem driver. The files are in subset A through `sources/windows/reactos`.

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/xxhash.h -->
# File Research: sources/windows/reactos/drivers/filesystems/btrfs/xxhash.h

## Purpose

Public xxHash 0.6.2 header used by the Btrfs driver for fast non-cryptographic hashing. It declares the one-shot and streaming XXH32/XXH64 APIs, canonical big-endian hash representations, optional namespacing, and static-link/private inclusion support.

## Main Components

- Version macros: `XXH_VERSION_MAJOR`, `XXH_VERSION_MINOR`, `XXH_VERSION_RELEASE`, `XXH_VERSION_NUMBER`.
- API export/private controls: `XXH_PRIVATE_API`, `XXH_STATIC_LINKING_ONLY`, `XXH_PUBLIC_API`.
- Optional symbol prefixing through `XXH_NAMESPACE`.
- Hash types:
  - `XXH32_hash_t`
  - `XXH64_hash_t`
  - `XXH_errorcode`
- One-shot functions:
  - `XXH32`
  - `XXH64`
- Streaming state APIs:
  - `XXH32_createState`, `XXH32_freeState`, `XXH32_reset`, `XXH32_update`, `XXH32_digest`
  - `XXH64_createState`, `XXH64_freeState`, `XXH64_reset`, `XXH64_update`, `XXH64_digest`
  - `XXH32_copyState`, `XXH64_copyState`
- Canonical conversion APIs:
  - `XXH32_canonicalFromHash`, `XXH64_canonicalFromHash`
  - `XXH32_hashFromCanonical`, `XXH64_hashFromCanonical`
- Static-link-only state layouts for `XXH32_state_s` and `XXH64_state_s`.

## Dependencies and Consumers

- Includes only `<stddef.h>` in the public section.
- Includes `xxhash.c` when `XXH_PRIVATE_API` is defined.
- Included by ReactOS Btrfs files such as `btrfs.c`, `read.c`, `flushthread.c`, and `calcthread.c`.
- Used by the Btrfs checksum/calculation thread path for `calc_thread_xxhash`.

## Research Notes

- This file is API surface, not implementation.
- Static state layouts are explicitly unstable and only safe for static linking.
- Canonical representation is big-endian, intended for portable persisted hash values.
- Any signature or namespace change must stay consistent with `xxhash.c` and call sites in Btrfs checksum logic.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/xxhash.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/zstd/bitstream.h -->
# File Research: sources/windows/reactos/drivers/filesystems/btrfs/zstd/bitstream.h

## Purpose

Inline bitstream encoder/decoder used by FSE and HUF. It writes bit fields forward into memory and reads them backward, matching FSE/HUF’s LIFO entropy stream model.

## Main Components

- Constants:
  - `STREAM_ACCUMULATOR_MIN_32`
  - `STREAM_ACCUMULATOR_MIN_64`
  - `STREAM_ACCUMULATOR_MIN`
- Compression stream state:
  - `BIT_CStream_t`
  - `BIT_initCStream`
  - `BIT_addBits`
  - `BIT_addBitsFast`
  - `BIT_flushBits`
  - `BIT_flushBitsFast`
  - `BIT_closeCStream`
- Decompression stream state:
  - `BIT_DStream_t`
  - `BIT_DStream_status`
  - `BIT_initDStream`
  - `BIT_readBits`
  - `BIT_readBitsFast`
  - `BIT_reloadDStream`
  - `BIT_reloadDStreamFast`
  - `BIT_endOfDStream`
- Internal helpers:
  - `BIT_highbit32`
  - `BIT_mask`
  - `BIT_lookBits`, `BIT_lookBitsFast`
  - `BIT_skipBits`

## Dependencies

- `mem.h` for unaligned little-endian reads/writes.
- `compiler.h` for branch hints.
- `debug.h` for assertions/logging.
- `error_private.h` for `ERROR(...)`.

## Behavior

- Encoder accumulates bits in a `size_t` register and flushes whole bytes to the destination buffer.
- `BIT_closeCStream` writes a one-bit end marker and returns zero if the destination overflowed.
- Decoder initializes from the last bytes of a stream, validates the end marker, and consumes fields in reverse order.
- Reload status distinguishes unfinished, end-of-buffer, completed, and overflow states.

## Research Notes

- The fast variants assume clean inputs and sufficient buffer/register space.
- Several callers rely on exact reverse-order semantics; changing bit layout would break FSE/HUF compatibility.
- Corruption handling depends on end marker validation and exact `BIT_endOfDStream` checks.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/zstd/bitstream.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/zstd/compiler.h -->
# File Research: sources/windows/reactos/drivers/filesystems/btrfs/zstd/compiler.h

## Purpose

Compiler abstraction header for the imported Zstd code. It centralizes inline/noinline attributes, target attributes, BMI2 dispatch configuration, prefetch helpers, vectorization suppression, branch prediction macros, and MSVC warning controls.

## Main Components

- Inlining:
  - `INLINE_KEYWORD`
  - `FORCE_INLINE_ATTR`
  - `FORCE_INLINE_TEMPLATE`
  - `HINT_INLINE`
  - `UNUSED_ATTR`
  - `FORCE_NOINLINE`
- Target and dispatch:
  - `TARGET_ATTRIBUTE`
  - `DYNAMIC_BMI2`
- Prefetch:
  - `PREFETCH_L1`
  - `PREFETCH_L2`
  - `PREFETCH_AREA`
  - `CACHELINE_SIZE`
- Optimization hints:
  - `DONT_VECTORIZE`
  - `LIKELY`
  - `UNLIKELY`
- MSVC pragmas disabling common portability warnings.

## Dependencies

- May include `<mmintrin.h>` for MSVC x86/x64 prefetch.
- Uses compiler predefined macros for GCC, Clang, ICCARM, MSVC, x86, and AArch64.

## Research Notes

- `DYNAMIC_BMI2` enables runtime BMI2-specialized paths when supported by compiler/target and BMI2 is not already globally enabled.
- This file affects generated code throughout Zstd/FSE/HUF but contains no runtime codec logic.
- Incorrect compiler macro changes can alter ABI visibility, inlining, CPU dispatch, or kernel build compatibility.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/zstd/compiler.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/zstd/cpu.h -->
# File Research: sources/windows/reactos/drivers/filesystems/btrfs/zstd/cpu.h

## Purpose

Runtime CPU feature detection helper used by Zstd, especially for BMI2-aware decompression/compression paths.

## Main Components

- `ZSTD_cpuid_t` stores CPUID feature registers:
  - `f1c`
  - `f1d`
  - `f7b`
  - `f7c`
- `ZSTD_cpuid()` gathers CPUID feature bits through:
  - MSVC `__cpuid` / `__cpuidex`
  - GCC inline assembly
  - special 32-bit PIC `ebx` save/restore handling
- Generated feature-test helpers include:
  - SSE/SSE2/SSE3/SSSE3/SSE4
  - AVX/AVX2/AVX512 variants
  - BMI1/BMI2
  - POPCNT, AES, PCLMUL, FMA
  - ADX, SHA, CLWB, and related x86 flags.

## Dependencies

- `<string.h>`
- `mem.h`
- `<intrin.h>` on MSVC.

## Consumers

- `zstd_decompress.c` uses `ZSTD_cpuid_bmi2(ZSTD_cpuid())` to initialize BMI2 capability in the decompression context.

## Research Notes

- Non-x86 builds return zeroed feature fields.
- The generated `ZSTD_cpuid_<feature>()` functions are inline/static via `MEM_STATIC`.
- Correct `ebx` preservation is important for 32-bit PIC builds.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/zstd/cpu.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/zstd/debug.h -->
# File Research: sources/windows/reactos/drivers/filesystems/btrfs/zstd/debug.h

## Purpose

Debug/assertion abstraction for the imported FSE/Zstd code. It provides compile-time assertions, optional runtime assertions, and optional logging.

## Main Components

- `DEBUG_STATIC_ASSERT(c)` for function-scope compile-time checks.
- `DEBUGLEVEL`, defaulting to `0`.
- `DEBUGFILE`, defaulting to `stderr`.
- `assert()` behavior:
  - enabled when `DEBUGLEVEL >= 1`
  - compiled to no-op otherwise
- Logging when `DEBUGLEVEL >= 2`:
  - global `g_debuglevel`
  - `RAWLOG`
  - `DEBUGLOG`

## Dependencies

- `<assert.h>` when assertions are enabled.
- `<stdio.h>` when logging is enabled.

## Research Notes

- Default release behavior disables runtime checks and logging.
- `g_debuglevel` is declared but not thread-safe.
- Many codec invariants are guarded by `assert`; with default `DEBUGLEVEL=0`, production safety depends on explicit error checks elsewhere.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/zstd/debug.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/zstd/entropy_common.c -->
# File Research: sources/windows/reactos/drivers/filesystems/btrfs/zstd/entropy_common.c

## Purpose

Common FSE/HUF entropy helpers shared by compression and decompression. It exposes version/error wrappers, decodes FSE normalized count headers, and reads serialized Huffman weight tables.

## Main Components

- Version/error wrappers:
  - `FSE_versionNumber`
  - `FSE_isError`
  - `FSE_getErrorName`
  - `HUF_isError`
  - `HUF_getErrorName`
- FSE normalized count reader:
  - `FSE_readNCount`
- Huffman statistics reader:
  - `HUF_readStats`

## Behavior

`FSE_readNCount`:

- Reads the table log from the first bits of an FSE header.
- Clears missing symbols in `normalizedCounter`.
- Handles compact runs of zero frequencies.
- Decodes positive counts and `-1` low-probability counts.
- Validates that the normalized total resolves to exactly one remaining unit.
- Updates `maxSVPtr` and `tableLogPtr`.

`HUF_readStats`:

- Reads Huffman weights either as raw 4-bit packed values or as an FSE-compressed weight stream.
- Reconstructs the implied final symbol weight.
- Builds `rankStats`.
- Validates total weight shape and rank-1 constraints.

## Dependencies

- `mem.h`
- `error_private.h`
- `fse.h` with `FSE_STATIC_LINKING_ONLY`
- `huf.h` with `HUF_STATIC_LINKING_ONLY`

## Research Notes

- This file is central to validating compressed entropy table headers.
- `FSE_readNCount` has special handling for headers shorter than four bytes by copying into a temporary four-byte buffer.
- Malformed table logs, impossible totals, missing end markers, and oversized symbol ranges return private Zstd/FSE error codes.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/zstd/entropy_common.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/zstd/error_private.c -->
# File Research: sources/windows/reactos/drivers/filesystems/btrfs/zstd/error_private.c

## Purpose

Private error string implementation for Zstd/FSE/HUF error codes.

## Main Components

- `ERR_getErrorString(ERR_enum code)`

## Behavior

- If `ZSTD_STRIP_ERROR_STRINGS` is defined, always returns `"Error strings stripped"`.
- Otherwise maps `ZSTD_error_*` values to stable diagnostic strings for common failures:
  - corruption
  - wrong checksum
  - unsupported parameters
  - allocation failure
  - destination/source size errors
  - table/log/symbol bounds
  - dictionary errors
  - seekable I/O errors
- Returns `"Unspecified error code"` for unknown/default cases.

## Dependencies

- `error_private.h`
- `zstd_errors.h` through the header.

## Research Notes

- This file embeds all private error text in one translation unit.
- It is diagnostic support only; error encoding/decoding lives in `error_private.h`.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/zstd/error_private.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/zstd/error_private.h -->
# File Research: sources/windows/reactos/drivers/filesystems/btrfs/zstd/error_private.h

## Purpose

Private Zstd/FSE/HUF error-code utilities. It encodes error enums into `size_t` return values and provides helpers for testing and forwarding errors.

## Main Components

- `ERR_STATIC` inline/static control.
- `ERR_enum` typedef to `ZSTD_ErrorCode`.
- `PREFIX(name)` and `ZSTD_ERROR(name)` error encoding.
- `ERROR(name)` macro.
- Helpers:
  - `ERR_isError`
  - `ERR_getErrorCode`
  - `ERR_getErrorString`
  - `ERR_getErrorName`
- Forwarding macros:
  - `CHECK_V_F`
  - `CHECK_F`

## Dependencies

- `<stddef.h>`
- `zstd_errors.h`

## Research Notes

- Errors are represented as negative enum values cast to `size_t`; `ERR_isError()` checks values above `ERROR(maxCode)`.
- The header is private and explicitly not intended as public API.
- Many FSE/HUF functions use `CHECK_F` and `CHECK_V_F`; changing these macros affects control flow broadly.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/zstd/error_private.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/zstd/fse.h -->
# File Research: sources/windows/reactos/drivers/filesystems/btrfs/zstd/fse.h

## Purpose

Public and static-link API header for Finite State Entropy. It declares high-level FSE compression/decompression, advanced table APIs, workspace variants, and inline symbol encode/decode primitives.

## Main Components

- Public API:
  - `FSE_compress`
  - `FSE_decompress`
  - `FSE_compressBound`
  - `FSE_isError`
  - `FSE_getErrorName`
  - `FSE_compress2`
- Detailed compression APIs:
  - `FSE_optimalTableLog`
  - `FSE_normalizeCount`
  - `FSE_NCountWriteBound`
  - `FSE_writeNCount`
  - `FSE_createCTable`
  - `FSE_freeCTable`
  - `FSE_buildCTable`
  - `FSE_compress_usingCTable`
- Detailed decompression APIs:
  - `FSE_readNCount`
  - `FSE_createDTable`
  - `FSE_freeDTable`
  - `FSE_buildDTable`
  - `FSE_decompress_usingDTable`
- Static-link-only sizing and workspace macros:
  - `FSE_NCOUNTBOUND`
  - `FSE_BLOCKBOUND`
  - `FSE_COMPRESSBOUND`
  - `FSE_CTABLE_SIZE_U32`
  - `FSE_DTABLE_SIZE_U32`
  - `FSE_WKSP_SIZE_U32`
- Inline state APIs:
  - `FSE_CState_t`
  - `FSE_DState_t`
  - `FSE_initCState`
  - `FSE_initCState2`
  - `FSE_encodeSymbol`
  - `FSE_flushCState`
  - `FSE_initDState`
  - `FSE_decodeSymbol`
  - `FSE_decodeSymbolFast`
  - `FSE_endOfDState`
- Constants:
  - `FSE_MAX_TABLELOG`
  - `FSE_DEFAULT_TABLELOG`
  - `FSE_MIN_TABLELOG`
  - `FSE_TABLELOG_ABSOLUTE_MAX`
  - `FSE_TABLESTEP`

## Dependencies

- `<stddef.h>`
- `bitstream.h` in static-link-only mode.

## Research Notes

- Encoding and decoding are reverse-order by design.
- Fast decode requires no symbol with probability over 50%.
- Table sizing macros are part of the internal ABI used by Zstd sequence coding.
- The public API deliberately does not handle raw/RLE data in `FSE_decompress`; callers must handle those cases.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/zstd/fse.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/zstd/fse_compress.c -->
# File Research: sources/windows/reactos/drivers/filesystems/btrfs/zstd/fse_compress.c

## Purpose

Finite State Entropy encoder implementation, including CTable construction, normalized-count serialization, count normalization, raw/RLE table construction, and one-shot/workspace compression.

## Main Components

- Table construction:
  - `FSE_buildCTable_wksp`
  - `FSE_buildCTable`
  - `FSE_buildCTable_raw`
  - `FSE_buildCTable_rle`
- Normalized-count writing:
  - `FSE_NCountWriteBound`
  - `FSE_writeNCount_generic`
  - `FSE_writeNCount`
- Allocation:
  - `FSE_createCTable`
  - `FSE_freeCTable`
- Table-log selection:
  - `FSE_minTableLog`
  - `FSE_optimalTableLog_internal`
  - `FSE_optimalTableLog`
- Count normalization:
  - `FSE_normalizeM2`
  - `FSE_normalizeCount`
- Compression:
  - `FSE_compress_usingCTable_generic`
  - `FSE_compress_usingCTable`
  - `FSE_compressBound`
  - `FSE_compress_wksp`
  - `FSE_compress2`
  - `FSE_compress`

## ReactOS Adaptation

- Includes `<ntifs.h>` and `<ntddk.h>`.
- `FSE_createCTable` allocates from `PagedPool` with tag `FSEC_ALLOC_TAG`.
- `FSE_freeCTable` uses `ExFreePool`.

## Behavior

- Builds a symbol spread table using `FSE_TABLESTEP`.
- Encodes low-probability symbols with normalized count `-1`.
- Writes FSE normalized counts into compact bit-packed headers.
- Counts input symbols through `HIST_count_wksp`.
- Rejects inputs that are too small, likely incompressible, or not worth storing compressed.
- Encodes streams backward with two FSE states and `BIT_CStream_t`.

## Research Notes

- Workspace alignment and sizing are critical; the function reuses the caller’s workspace for both CTable and scratch table symbols.
- `FSE_normalizeCount` has a primary fast normalization path and a secondary `FSE_normalizeM2` fallback for difficult rounding cases.
- Return value `0` means not compressible or not storable; return value `1` means RLE in the high-level compression path.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/zstd/fse_compress.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/zstd/fse_decompress.c -->
# File Research: sources/windows/reactos/drivers/filesystems/btrfs/zstd/fse_decompress.c

## Purpose

Finite State Entropy decoder implementation, including DTable allocation/building, raw/RLE decode tables, and workspace decompression.

## Main Components

- Allocation:
  - `FSE_createDTable`
  - `FSE_freeDTable`
- Table construction:
  - `FSE_buildDTable`
  - `FSE_buildDTable_rle`
  - `FSE_buildDTable_raw`
- Decompression:
  - `FSE_decompress_usingDTable_generic`
  - `FSE_decompress_usingDTable`
  - `FSE_decompress_wksp`
  - `FSE_decompress`

## ReactOS Adaptation

- Includes `<ntifs.h>` and `<ntddk.h>`.
- `FSE_createDTable` allocates from `PagedPool` with tag `FSED_ALLOC_TAG`.
- `FSE_freeDTable` uses `ExFreePool`.

## Behavior

- `FSE_buildDTable` lays low-probability symbols at the high threshold, spreads remaining symbols, and computes `newState`/`nbBits`.
- `fastMode` is disabled if any normalized count is at least half the table size.
- Decoder initializes two FSE states and emits up to four symbols per loop.
- `FSE_decompress_wksp` reads normalized counts, validates table log against caller maximum, builds the DTable, then decodes the payload.

## Research Notes

- `FSE_decompress()` handles only normal FSE blocks; raw and RLE must be handled by callers.
- Corruption detection depends on table spread reaching every cell and bitstream completion.
- Fast symbol decoding is selected from the DTable header’s `fastMode`.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/zstd/fse_decompress.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/zstd/hist.c -->
# File Research: sources/windows/reactos/drivers/filesystems/btrfs/zstd/hist.c

## Purpose

Byte histogram implementation used by FSE and HUF compression to count symbol frequencies and identify the most common symbol.

## Main Components

- Error wrapper:
  - `HIST_isError`
- Counting APIs:
  - `HIST_count_simple`
  - `HIST_countFast_wksp`
  - `HIST_countFast`
  - `HIST_count_wksp`
  - `HIST_count`
- Internal parallel counter:
  - `HIST_count_parallel_wksp`
- Input-check mode:
  - `trustInput`
  - `checkMaxSymbolValue`

## Behavior

- `HIST_count_simple` zeroes `count`, scans byte-by-byte, trims `maxSymbolValuePtr`, and returns the largest frequency.
- Larger inputs use four 256-entry counters updated in stripes from 32-bit loads, then recombined.
- Checked mode validates that no symbol exceeds the requested maximum.
- Workspace must be 4-byte aligned and at least `HIST_WKSP_SIZE`.

## Dependencies

- `mem.h`
- `debug.h`
- `error_private.h`
- `hist.h`

## Research Notes

- The threshold for simple counting is `sourceSize < 1500`.
- `HIST_countFast` trusts input range and can write out of bounds if called with a too-small max symbol value.
- The max-symbol trimming loop assumes at least one counted symbol when source size is nonzero.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/zstd/hist.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/zstd/hist.h -->
# File Research: sources/windows/reactos/drivers/filesystems/btrfs/zstd/hist.h

## Purpose

Public header for histogram counting utilities used by FSE/HUF compression.

## Main Components

- `HIST_count`
- `HIST_isError`
- `HIST_WKSP_SIZE_U32`
- `HIST_WKSP_SIZE`
- `HIST_count_wksp`
- `HIST_countFast`
- `HIST_countFast_wksp`
- `HIST_count_simple`

## API Semantics

- `HIST_count` and workspace variants update `*maxSymbolValuePtr` to the highest observed symbol.
- Return value is the largest symbol frequency, or an error code for checked/workspace variants.
- `HIST_countFast` and `HIST_count_simple` trust that source bytes are no larger than `*maxSymbolValuePtr`.

## Dependencies

- `<stddef.h>`

## Research Notes

- Workspace is caller-owned, writable, 4-byte aligned, and must be at least `HIST_WKSP_SIZE`.
- Unsafe variants are performance helpers and should only be used when byte range is already guaranteed.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/zstd/hist.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/zstd/huf.h -->
# File Research: sources/windows/reactos/drivers/filesystems/btrfs/zstd/huf.h

## Purpose

Public and static-link API header for Huffman entropy compression/decompression used by Zstd literals.

## Main Components

- Public API:
  - `HUF_compress`
  - `HUF_decompress`
  - `HUF_compressBound`
  - `HUF_isError`
  - `HUF_getErrorName`
  - `HUF_compress2`
  - `HUF_compress4X_wksp`
- Public constants:
  - `HUF_BLOCKSIZE_MAX`
  - `HUF_WORKSPACE_SIZE`
  - `HUF_WORKSPACE_SIZE_U32`
- Static-link constants:
  - `HUF_TABLELOG_MAX`
  - `HUF_TABLELOG_DEFAULT`
  - `HUF_SYMBOLVALUE_MAX`
  - `HUF_TABLELOG_ABSOLUTEMAX`
  - `HUF_CTABLEBOUND`
  - `HUF_COMPRESSBOUND`
- Table allocation macros:
  - `HUF_CTABLE_SIZE_U32`
  - `HUF_CREATE_STATIC_CTABLE`
  - `HUF_DTABLE_SIZE`
  - `HUF_CREATE_STATIC_DTABLEX1`
  - `HUF_CREATE_STATIC_DTABLEX2`
- Compression internals:
  - `HUF_optimalTableLog`
  - `HUF_buildCTable`
  - `HUF_writeCTable`
  - `HUF_readCTable`
  - `HUF_compress1X/4X`
  - repeat-table APIs
- Decompression internals:
  - `HUF_readStats`
  - `HUF_selectDecoder`
  - `HUF_readDTableX1/X2`
  - `HUF_decompress1X/4X`
  - BMI2-aware wrappers.

## Behavior

- Supports both single-stream and four-stream Huffman coding.
- Supports X1 single-symbol and X2 double-symbol decode table formats.
- Public `HUF_decompress` handles raw and RLE cases because original size is known.

## Research Notes

- The static-link section is explicitly unstable and not suitable for dynamic-library ABI.
- Many APIs require exact compressed and decompressed sizes.
- Decoder selection is heuristic unless `HUF_FORCE_DECOMPRESS_X1` or `HUF_FORCE_DECOMPRESS_X2` is defined.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/zstd/huf.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/zstd/huf_compress.c -->
# File Research: sources/windows/reactos/drivers/filesystems/btrfs/zstd/huf_compress.c

## Purpose

Huffman encoder implementation for Zstd literal compression. It builds canonical Huffman tables, serializes table weights, and encodes data as one stream or four parallel streams.

## Main Components

- Utility:
  - `HUF_optimalTableLog`
  - `HUF_compressBound`
  - `HUF_getNbBits`
- Weight/table serialization:
  - `HUF_compressWeights`
  - `HUF_writeCTable`
  - `HUF_readCTable`
- CTable construction:
  - `HUF_setMaxHeight`
  - `HUF_sort`
  - `HUF_buildCTable_wksp`
  - `HUF_buildCTable`
- CTable analysis:
  - `HUF_estimateCompressedSize`
  - `HUF_validateCTable`
- Bitstream encoding:
  - `HUF_encodeSymbol`
  - `HUF_compress1X_usingCTable_internal_body`
  - `HUF_compress1X_usingCTable`
  - `HUF_compress4X_usingCTable_internal`
  - `HUF_compress4X_usingCTable`
- High-level compression:
  - `HUF_compress_internal`
  - `HUF_compress1X_wksp`
  - `HUF_compress1X_repeat`
  - `HUF_compress1X`
  - `HUF_compress4X_wksp`
  - `HUF_compress4X_repeat`
  - `HUF_compress2`
  - `HUF_compress`

## Behavior

- Counts input with `HIST_count_wksp`.
- Returns RLE marker size `1` when input is a single repeated byte.
- Rejects likely incompressible data via frequency and final-size heuristics.
- Builds a Huffman tree from sorted frequencies, then limits maximum bit height with `HUF_setMaxHeight`.
- Serializes Huffman weights using FSE when beneficial, otherwise raw 4-bit packed weights.
- Four-stream compression writes a 6-byte jump table containing the first three stream sizes.

## Dependencies

- `compiler.h`
- `bitstream.h`
- `hist.h`
- `fse.h`
- `huf.h`
- `error_private.h`

## Research Notes

- Dynamic BMI2 wrappers compile specialized bodies only when `DYNAMIC_BMI2` is enabled.
- Repeat-table paths can reuse a previous Huffman table when valid and estimated cheaper.
- The compressor requires source blocks no larger than `HUF_BLOCKSIZE_MAX` and workspace aligned on 4-byte boundaries.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/zstd/huf_compress.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/zstd/huf_decompress.c -->
# File Research: sources/windows/reactos/drivers/filesystems/btrfs/zstd/huf_decompress.c

## Purpose

Huffman decoder implementation for Zstd literals. It builds X1 and X2 decode tables, decodes one-stream and four-stream payloads, handles raw/RLE shortcuts, and selects decoder variants using precomputed heuristics.

## Main Components

- Table metadata:
  - `DTableDesc`
  - `HUF_getDTableDesc`
- BMI2 wrappers:
  - `HUF_DGEN`
- X1 single-symbol decoder:
  - `HUF_DEltX1`
  - `HUF_readDTableX1_wksp`
  - `HUF_readDTableX1`
  - `HUF_decodeSymbolX1`
  - `HUF_decodeStreamX1`
  - `HUF_decompress1X1_usingDTable_internal_body`
  - `HUF_decompress4X1_usingDTable_internal_body`
  - public/DCtx wrappers
- X2 double-symbol decoder:
  - `HUF_DEltX2`
  - `sortedSymbol_t`
  - `rankVal_t`
  - `HUF_fillDTableX2Level2`
  - `HUF_fillDTableX2`
  - `HUF_readDTableX2_wksp`
  - `HUF_readDTableX2`
  - `HUF_decodeSymbolX2`
  - `HUF_decodeLastSymbolX2`
  - `HUF_decodeStreamX2`
  - `HUF_decompress1X2_usingDTable_internal_body`
  - `HUF_decompress4X2_usingDTable_internal_body`
  - public/DCtx wrappers
- Selector and universal APIs:
  - `HUF_decompress1X_usingDTable`
  - `HUF_decompress4X_usingDTable`
  - `HUF_selectDecoder`
  - `HUF_decompress`
  - `HUF_decompress4X_DCtx`
  - `HUF_decompress4X_hufOnly`
  - `HUF_decompress1X_DCtx`
  - BMI2 variants.

## Behavior

- Reads Huffman weights via `HUF_readStats`.
- X1 tables map bit prefixes to one byte and bit length.
- X2 tables can emit one or two bytes per lookup.
- Four-stream decoding reads a 6-byte jump table, initializes four `BIT_DStream_t` streams, decodes segments in parallel, then validates all streams ended exactly.
- `HUF_decompress` treats `cSrcSize == dstSize` as raw copy and `cSrcSize == 1` as RLE fill.
- `HUF_decompress4X_hufOnly*` rejects raw/RLE shortcuts and expects a real Huffman payload.

## Dependencies

- `compiler.h`
- `bitstream.h`
- `fse.h`
- `huf.h`
- `error_private.h`

## Research Notes

- `HUF_selectDecoder` chooses X1 or X2 using a static timing table based on compression ratio and output size.
- Workspace layout in `HUF_readDTableX1_wksp` and `HUF_readDTableX2_wksp` is manually packed and alignment-sensitive.
- Corruption checks include stream size bounds, segment overflow, output segment overrun, and exact bitstream completion.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/zstd/huf_decompress.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/zstd/mem.h -->
# File Research: sources/windows/reactos/drivers/filesystems/btrfs/zstd/mem.h

## Purpose

Low-level memory, type, endian, byte-swap, and unaligned-access helper header for the imported Zstd/FSE/HUF code.

## Main Components

- Static inline control:
  - `MEM_STATIC`
  - `MEM_STATIC_ASSERT`
  - `MEM_check`
- Sanitizer declarations:
  - MemorySanitizer helpers
  - AddressSanitizer poison/unpoison helpers
- Fixed-width types:
  - `BYTE`
  - `U16`, `S16`
  - `U32`, `S32`
  - `U64`, `S64`
- Architecture helpers:
  - `MEM_32bits`
  - `MEM_64bits`
  - `MEM_isLittleEndian`
- Unaligned memory access:
  - `MEM_read16`, `MEM_read32`, `MEM_read64`, `MEM_readST`
  - `MEM_write16`, `MEM_write32`, `MEM_write64`
- Byte swapping:
  - `MEM_swap32`
  - `MEM_swap64`
  - `MEM_swapST`
- Little-endian helpers:
  - `MEM_readLE16`, `MEM_writeLE16`
  - `MEM_readLE24`, `MEM_writeLE24`
  - `MEM_readLE32`, `MEM_writeLE32`
  - `MEM_readLE64`, `MEM_writeLE64`
  - `MEM_readLEST`, `MEM_writeLEST`
- Big-endian helpers:
  - `MEM_readBE32`, `MEM_writeBE32`
  - `MEM_readBE64`, `MEM_writeBE64`
  - `MEM_readBEST`, `MEM_writeBEST`

## Behavior

- Selects unaligned access strategy through `MEM_FORCE_MEMORY_ACCESS`:
  - `0`: portable `memcpy`
  - `1`: packed structs
  - `2`: direct unaligned loads/stores
- Defaults to packed-struct access on GCC/ICC-style compilers, direct access on some ARMv6 cases, and portable `memcpy` otherwise.
- Provides endian-neutral helpers used by bitstream, FSE, HUF, and Zstd frame/sequence code.

## Dependencies

- `<stddef.h>`
- `<string.h>`
- `<stdint.h>` when available
- MSVC byteswap/intrinsic headers when building under MSVC.

## Research Notes

- This file assumes 32-bit or 64-bit `size_t` and exactly 8-bit bytes.
- Unaligned access mode is a portability/performance tradeoff and can affect strict-aliasing/alignment behavior.
- The bitstream layer depends on `MEM_readLEST` and `MEM_writeLEST` matching the platform `size_t` width.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/zstd/mem.h -->