# Group Research: subset-b-006116

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/common/fse.h -->
# sources/distributed-fs/ceph-client/lib/zstd/common/fse.h

## Purpose
`fse.h` is the public and static-linking contract for the Finite State Entropy codec used by this kernel Zstd copy. It declares version/error helpers, compression/decompression table APIs, workspace sizing macros, and the inlined symbol encoder/decoder primitives consumed by `fse_compress.c`, `fse_decompress.c`, Huffman header compression, and Zstd sequence coding.

## Important APIs, Types, and Constants
The public surface includes `FSE_versionNumber()`, `FSE_compressBound()`, `FSE_isError()`, `FSE_getErrorName()`, `FSE_optimalTableLog()`, `FSE_normalizeCount()`, `FSE_writeNCount()`, `FSE_readNCount[_bmi2]()`, `FSE_buildCTable()`, `FSE_buildDTable_wksp()`, and `FSE_compress_usingCTable()`. Opaque table aliases `FSE_CTable` and `FSE_DTable` are allocation-only types. Static-linking macros define `FSE_CTABLE_SIZE_U32()`, `FSE_DTABLE_SIZE_U32()`, `FSE_DECOMPRESS_WKSP_SIZE_U32()`, and bounds such as `FSE_MAX_SYMBOL_VALUE`, `FSE_MAX_TABLELOG`, `FSE_MIN_TABLELOG`, and `FSE_TABLESTEP()`. Inline state types `FSE_CState_t`, `FSE_DState_t`, `FSE_symbolCompressionTransform`, `FSE_DTableHeader`, and `FSE_decode_t` define the actual table layout assumptions.

## Control Flow and State
The documented compression flow is histogram, normalize, write normalized counts, build CTable, then encode. Decompression reverses this through normalized-count read, DTable build, and bitstream decode. Inline encoding initializes a state from the table header, emits symbols in reverse order with `FSE_encodeSymbol()`, and flushes final state with `FSE_flushCState()`. Inline decoding reads the initial state from `BIT_DStream_t`, maps state to symbol/bit count/new state, and requires `FSE_endOfDState()` plus bitstream completion to validate exact consumption.

## Dependencies and Integration Points
The header depends on `zstd_deps.h`, `bitstream.h`, `mem.h` transitively, and kernel-compatible integer/memory definitions. `huf.h` includes it with `FSE_STATIC_LINKING_ONLY` for Huffman tree header compression. `zstd_internal.h` aliases `FSE_isError` to `ERR_isError`, and sequence coding uses the default normalized tables and FSE state APIs.

## Risks and Test Signals
Risks concentrate in table layout compatibility: the CTable/DTable macros, header packing, `U16`/`U32` alignment, and workspace sizes must match the implementations exactly. Fast decode is explicitly unsafe when a symbol can have probability greater than 50 percent, so DTable `fastMode` must be honored. Useful tests include FSE round trips across table logs, low-probability `-1` symbols, RLE tables, max symbol value 255, workspace under-sizing, corrupt normalized-count headers, and 32-bit/64-bit bit-container behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/common/fse.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/common/fse_decompress.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/common/fse_decompress.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/common/huf.h -->
# sources/distributed-fs/ceph-client/lib/zstd/common/huf.h

## Purpose
`huf.h` declares the Huffman codec interface used for Zstd literal block compression and decompression. It exposes static allocation macros, workspace sizes, compression table APIs, repeat-table behavior, decoder selection, and flags controlling optimal depth, repeated tables, suspected incompressibility, BMI2, assembly, and fast-loop behavior.

## Important APIs and Types
Key constants are `HUF_BLOCKSIZE_MAX`, `HUF_TABLELOG_MAX`, `HUF_TABLELOG_DEFAULT`, `HUF_SYMBOLVALUE_MAX`, `HUF_WORKSPACE_SIZE`, and `HUF_DECOMPRESS_WORKSPACE_SIZE`. `HUF_CElt` is an opaque `size_t` compression-table element, and `HUF_DTable` is a `U32` decode table. `HUF_flags_e` controls compression/decompression features. Compression APIs include `HUF_buildCTable_wksp()`, `HUF_writeCTable_wksp()`, `HUF_compress1X_usingCTable()`, `HUF_compress4X_usingCTable()`, `HUF_compress1X_repeat()`, and `HUF_compress4X_repeat()`. Decompression APIs include DTable readers, 1X/4X decode variants, and `HUF_selectDecoder()`.

## Control Flow and State
The header documents the Huffman flow: count symbols, choose or refine table log, build a canonical table, serialize the tree, and encode one or four streams. Repeat state is represented by `HUF_repeat_none`, `HUF_repeat_check`, and `HUF_repeat_valid`, allowing Zstd blocks to reuse a previous Huffman table when valid and beneficial.

## Dependencies and Integration Points
It includes `zstd_deps.h`, `mem.h`, and `fse.h` with static-linking declarations. Huffman tree serialization uses FSE for compact weight compression, so `FSE_DECOMPRESS_WKSP_SIZE_U32()` also sizes `HUF_READ_STATS_WORKSPACE_SIZE_U32`. Zstd literal block code chooses between HUF raw, RLE, compressed, and repeat-table paths using these interfaces.

## Risks and Test Signals
Risks include mismatch between opaque table allocation macros and implementation layout, repeat-table misuse when new input contains symbols absent from the previous table, and flag handling divergence between compression and decompression builds. Tests should cover 1X and 4X streams, repeat valid/check/none transitions, zero-weight symbols, max table log 12, workspace alignment, compressed and raw tree headers, and decoder selection thresholds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/common/huf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/common/mem.h -->
# sources/distributed-fs/ceph-client/lib/zstd/common/mem.h

## Purpose
`mem.h` provides the kernel-adapted primitive memory I/O layer for this Zstd copy. It defines fixed-width aliases and inline unaligned native, little-endian, big-endian, and byte-swap helpers used throughout bitstream, entropy, frame, and match-finding code.

## Important APIs and Types
The file defines `BYTE`, `U8/S8`, `U16/S16`, `U32/S32`, and `U64/S64`. It exposes `MEM_32bits()`, `MEM_64bits()`, `MEM_isLittleEndian()`, native `MEM_read16/32/64/ST()` and `MEM_write16/32/64()`, endian-specific `MEM_readLE16/24/32/64/ST()`, `MEM_writeLE16/24/32/64/ST()`, `MEM_readBE32/64/ST()`, `MEM_writeBE32/64/ST()`, and `MEM_swap32/64/ST()`.

## Control Flow and State
All helpers are `static inline` and stateless. Native reads/writes use `get_unaligned()` and `put_unaligned()`. Endian helpers use Linux `get_unaligned_le*` and `get_unaligned_be*` routines. Size-t variants branch on `sizeof(size_t)` to select 32-bit or 64-bit behavior, making bitstream serialization portable across kernel architectures.

## Dependencies and Integration Points
Dependencies are Linux headers: `linux/unaligned.h`, `linux/compiler.h`, `linux/swab.h`, and `linux/types.h`, plus `debug.h` for static assertion support. Entropy code uses these helpers for table headers, jump tables, packed bit containers, and 64-bit spread writes; changing them affects almost every Zstd source file.

## Risks and Test Signals
The main risks are architecture portability and assumptions about `__LITTLE_ENDIAN`. Incorrect endian detection or unaligned behavior would corrupt frame headers and entropy streams. `MEM_writeLE24()` has a mixed 16-bit helper plus byte store, so 24-bit frame/block fields deserve coverage. Tests should run known Zstd vectors on little- and big-endian builds where available, exercise unaligned addresses, verify 32-bit versus 64-bit `size_t` paths, and compare packed table/jump-table byte output against upstream vectors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/common/mem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/common/portability_macros.h -->
# sources/distributed-fs/ceph-client/lib/zstd/common/portability_macros.h

## Purpose
`portability_macros.h` is a macro-only portability shim shared by C and assembly. In this kernel tree it mainly normalizes compiler feature probes, defines symbol-hiding annotations for assembly, controls dynamic BMI2 detection, and disables the x86-64 BMI2 assembly enable macro.

## Important Macros
Fallback definitions for `__has_attribute`, `__has_builtin`, and `__has_feature` support non-Clang compilers. `ZSTD_HIDE_ASM_FUNCTION(func)` maps to `.hidden`, `.private_extern`, or nothing depending on object format. `DYNAMIC_BMI2` becomes enabled for supported GCC/Clang x86 builds when BMI2 is not already a compile-time target. `ZSTD_ASM_SUPPORTED` is set to `1`, but `ZSTD_ENABLE_ASM_X86_64_BMI2` is set to `0` in this copy. CET support is optionally wired through `<cet.h>` and `ZSTD_CET_ENDBRANCH`.

## Control Flow and State
There is no runtime state and no C code by design. The only behavior is preprocessor selection. Downstream source files compile BMI2-targeted functions under `DYNAMIC_BMI2` and assembly code under `ZSTD_ENABLE_ASM_X86_64_BMI2`; this file's values therefore choose which implementation variants exist in the build.

## Dependencies and Integration Points
The header may include `<cet.h>` if available and `__has_include` reports it. It is consumed by compiler/cpu/assembly-adjacent code in Zstd, including HUF/FSE BMI2 dispatch paths. Kernel configuration and compiler flags can override macros before inclusion.

## Risks and Test Signals
Risk comes from configuration drift: `ZSTD_ASM_SUPPORTED` says assembly is generally supported while `ZSTD_ENABLE_ASM_X86_64_BMI2` forces the specific BMI2 assembly path off. If future code assumes these are correlated, build or dispatch bugs can appear. Tests should include x86 builds with and without `__BMI2__`, non-x86 builds, CET-enabled builds, and preprocessed checks confirming no assembly-only C constructs leak into this macro-only header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/common/portability_macros.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/common/zstd_common.c -->
# sources/distributed-fs/ceph-client/lib/zstd/common/zstd_common.c

## Purpose
`zstd_common.c` exports the common version and error-management entry points for the kernel Zstd library. It is intentionally small and wraps constants/macros from the public Linux Zstd header and the private error subsystem.

## Important Functions
`ZSTD_versionNumber()` returns `ZSTD_VERSION_NUMBER`; `ZSTD_versionString()` returns `ZSTD_VERSION_STRING`; `ZSTD_isError()` wraps `ERR_isError()` after undefining the inline alias from `zstd_internal.h`; `ZSTD_getErrorName()`, `ZSTD_getErrorCode()`, and `ZSTD_getErrorString()` expose private error names and enum conversion to external callers.

## Control Flow and State
There is no mutable state or persistence. Every function is a direct, deterministic accessor or wrapper. The only notable control-flow detail is that `ZSTD_DEPS_NEED_MALLOC` is defined before including common headers, but this kernel dependency layer maps malloc/calloc to always fail, keeping this common module free of dynamic allocation.

## Dependencies and Integration Points
The file includes `error_private.h` and `zstd_internal.h`, which pulls in `<linux/zstd.h>` and shared Zstd constants. These functions are exported ABI-like helpers for compression/decompression callers that need to identify error-coded `size_t` results.

## Risks and Test Signals
Risks are low but ABI-visible: version constants must match the bundled implementation, and error wrappers must not conflict with macro aliases. Tests should verify that known error codes are detected, names are stable/non-null, enum conversion is consistent, and the reported version matches the Linux Zstd header compiled with this source.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/common/zstd_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/common/zstd_deps.h -->
# sources/distributed-fs/ceph-client/lib/zstd/common/zstd_deps.h

## Purpose
`zstd_deps.h` centralizes libc-like dependencies for the kernel Zstd port. It replaces memory routines, allocation, 64-bit division, assertions, debug printing, and intptr support with kernel-safe equivalents or stubs selected by `ZSTD_DEPS_NEED_*` feature macros.

## Important APIs and Macros
The common section includes Linux limits/stddef and maps `ZSTD_memcpy`, `ZSTD_memmove`, and `ZSTD_memset` to compiler builtins. With `ZSTD_DEPS_NEED_MALLOC`, `ZSTD_malloc()` and `ZSTD_calloc()` return `NULL`, while `ZSTD_free()` is a no-op. `ZSTD_DEPS_NEED_MATH64` provides `ZSTD_div64()` through `div_u64()`. `ZSTD_DEPS_NEED_ASSERT` maps `assert(x)` to `WARN_ON(!(x))`. `ZSTD_DEPS_NEED_IO` maps debug printing to `pr_debug()`.

## Control Flow and State
This header has only macro-selected definitions and one static helper for 64-bit division. There is no persistent state. The important behavioral decision is that dynamic allocation is intentionally unavailable, forcing callers to use static or externally supplied workspaces.

## Dependencies and Integration Points
It is included by nearly all common/compress entropy files before they need libc-like facilities. FSE normalization depends on `ZSTD_div64()`. Compression and decompression paths depend on the memory macros. Debug and assert behavior flows through `debug.h` into this dependency layer.

## Risks and Test Signals
The largest risk is accidental use of allocation APIs in code paths that expect upstream userspace Zstd semantics; in this tree they fail by design. `assert()` as `WARN_ON()` reports but does not necessarily abort, so debug-only invariants cannot be treated as hard production validation. Tests should include allocation-failure paths, workspace-only compression/decompression, 64-bit division correctness on 32-bit kernels, and debug builds with `DEBUGLEVEL` enabling assert and print dependencies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/common/zstd_deps.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/common/zstd_internal.h -->
# sources/distributed-fs/ceph-client/lib/zstd/common/zstd_internal.h

## Purpose
`zstd_internal.h` is the shared private contract across Zstd compression, decompression, and dictionary-related code. It defines common constants, default FSE distributions, block metadata, copy helpers, workspace heuristics, and private declarations that must stay consistent across modules.

## Important APIs, Types, and Constants
Key constants include block/frame header sizes, checksum size, minimum compressed block sizes, literal and sequence symbol limits, default FSE logs/norms for literal length, match length, and offset codes, plus maximum entropy header sizes. Types include `blockType_e`, `SymbolEncodingType_e`, `ZSTD_overlap_e`, `ZSTD_bufferMode_e`, `ZSTD_frameSizeInfo`, and `blockProperties_t`. Important helpers are `ZSTD_copy8()`, `ZSTD_copy16()`, `ZSTD_wildcopy()`, `ZSTD_limitCopy()`, and `ZSTD_cpuSupportsBmi2()`. Private declarations include `ZSTD_invalidateRepCodes()`, `ZSTD_getcBlockSize()`, and `ZSTD_decodeSeqHeaders()`.

## Control Flow and State
The header is mostly stateless, but it defines shared default tables and repcode initial values used to initialize or reset compression/decompression state. `ZSTD_wildcopy()` performs intentionally over-copying loops for speed and switches behavior based on overlap type. `ZSTD_cpuSupportsBmi2()` reads CPU feature state through `ZSTD_cpuid()`.

## Dependencies and Integration Points
It includes compiler, CPU, memory, debug, error, Linux Zstd public API, FSE, HUF, and Linux xxhash headers. It is an integration hub: entropy modules depend on its constants, block parsers use its block metadata, and compressor/decompressor implementations share its default normalized distributions.

## Risks and Test Signals
Risks are high because constants define wire-format limits and table sizes. `ZSTD_wildcopy()` can overread/overwrite by design, so callers must reserve `WILDCOPY_OVERLENGTH` slack and obey overlap preconditions. Copy helpers differ by architecture and compiler, including a GCC-specific temporary-buffer workaround. Tests should cover block header parsing, default sequence table decoding, small-offset overlap copies, 32-bit and 64-bit builds, BMI2 feature detection, and frame/literal edge cases around minimum sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/common/zstd_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/compress/clevels.h -->
# sources/distributed-fs/ceph-client/lib/zstd/compress/clevels.h

## Purpose
`clevels.h` provides the static table mapping Zstd compression levels to `ZSTD_compressionParameters`. It is the policy table that selects window, chain, hash, search, minimum match, target length, and strategy defaults based on compression level and source-size class.

## Important Data
`ZSTD_MAX_CLEVEL` is `22`. `ZSTD_defaultCParameters[4][ZSTD_MAX_CLEVEL+1]` contains four source-size bands: default for inputs over 256 KiB, at most 256 KiB, at most 128 KiB, and at most 16 KiB. Each row has an index 0 base for negative levels and levels 1 through 22. Strategies progress from `ZSTD_fast` and `ZSTD_dfast` through greedy/lazy variants to `ZSTD_btopt`, `ZSTD_btultra`, and `ZSTD_btultra2`.

## Control Flow and State
The file has no functions and no mutable state. Runtime parameter selection elsewhere indexes this constant table after choosing the size band and clamping the requested compression level. The `__attribute__((__unused__))` marker suppresses warnings when not all builds use the table directly.

## Dependencies and Integration Points
It includes `<linux/zstd.h>` with `ZSTD_STATIC_LINKING_ONLY` so `ZSTD_compressionParameters` and strategy enums are visible. Compressor context initialization and parameter derivation depend on this table to convert user-facing compression levels into concrete algorithm settings.

## Risks and Test Signals
Risks are parameter drift and out-of-range indexing. If public strategy enums or `ZSTD_compressionParameters` layout changes, the initializer must be updated. Tests should verify level clamping, negative-level base behavior, size-band selection at 16 KiB/128 KiB/256 KiB boundaries, max level 22, and representative compression/decompression round trips at low, medium, and ultra levels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/compress/clevels.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/compress/fse_compress.c -->
# sources/distributed-fs/ceph-client/lib/zstd/compress/fse_compress.c

## Purpose
`fse_compress.c` implements FSE compression table construction, normalized-count serialization, normalization, RLE table creation, and bitstream encoding. It supplies the compressor-side entropy primitive used by Zstd sequence coding and by `huf_compress.c` to compress Huffman weight headers.

## Important Functions
`FSE_buildCTable_wksp()` lays out the CTable header, state table, and symbol transform table from normalized counts. `FSE_NCountWriteBound()` and `FSE_writeNCount()` serialize normalized distributions. `FSE_optimalTableLog[_internal]()` chooses table log based on source size and symbol range. `FSE_normalizeCount()` and fallback `FSE_normalizeM2()` convert raw counts to a power-of-two distribution. `FSE_buildCTable_rle()` builds a single-symbol table. `FSE_compress_usingCTable()` selects checked or fast bit flushing based on destination capacity.

## Control Flow and State
CTable construction first computes cumulative positions, reserves high slots for low-probability `-1` entries, spreads symbols via `FSE_TABLESTEP()`, fills the sorted state table, then builds per-symbol transforms used by inline `FSE_encodeSymbol()`. Normalization assigns zeros, low-probability weights, scaled probabilities, then adjusts the largest symbol or falls back to method M2 for corner cases. Compression initializes two states from the last one or two input symbols and encodes input backward, flushing states at the end.

## Dependencies and Integration Points
The file depends on `hist.h`, `bitstream.h`, `fse.h`, `error_private.h`, `zstd_deps.h`, and `bits.h`. `ZSTD_div64()` is required for normalization scaling. `HUF_compressWeights()` depends on the NCount writer and CTable builder. Zstd sequence encoding relies on normalized count output matching `FSE_readNCount()`.

## Risks and Test Signals
Risks include workspace under-sizing, distribution sums not equaling `1 << tableLog`, buffer-bound mistakes in `FSE_writeNCount_generic()`, and reverse-encoding mistakes for odd input sizes. Low-probability handling differs depending on `useLowProbCount`, affecting decoder speed and compressed size. Tests should round-trip varied histograms, all-zero except one symbol, low-frequency sparse alphabets, small inputs under three bytes, insufficient destination buffers, max table logs, and normalized-count corruption.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/compress/fse_compress.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/compress/hist.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/compress/hist.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/compress/hist.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/compress/hist.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/compress/huf_compress.c -->
# sources/distributed-fs/ceph-client/lib/zstd/compress/huf_compress.c

## Purpose
`huf_compress.c` implements Huffman table construction, table serialization/deserialization for compression tables, one-stream and four-stream Huffman bitstream encoding, repeat-table handling, and incompressibility heuristics for Zstd literal compression.

## Important Functions and Types
`nodeElt` represents Huffman tree nodes. `HUF_compressWeights()` uses FSE to compress Huffman weights. `HUF_writeCTable_wksp()` serializes a CTable as FSE-compressed or raw 4-bit weights. `HUF_readCTable()` reconstructs a compression table from serialized weights. `HUF_setMaxHeight()`, `HUF_sort()`, `HUF_buildTree()`, and `HUF_buildCTable_wksp()` build canonical Huffman tables within `HUF_TABLELOG_MAX`. `HUF_CStream_t` and helpers `HUF_addBits()`, `HUF_flushBits()`, and `HUF_closeCStream()` implement a custom high-bit-first encoder. `HUF_compress1X_usingCTable()` and `HUF_compress4X_usingCTable()` encode data, while `HUF_compress_internal()` handles histogramming, repeat tables, table choice, and output-size checks.

## Control Flow and State
Compression starts by validating workspace, block size, table log, and symbol range. Optional sampling skips likely incompressible large inputs. The full histogram then detects RLE and low-gain data. If a previous table is valid and preferred or cheaper, the old CTable is reused. Otherwise the code chooses an optimal table log, builds a new canonical table, writes its description, saves it into `oldHufTable`, and encodes either a single reverse stream or four independently compressed segments with a 6-byte jump table. Repeat state is caller-owned through `HUF_repeat`.

## Dependencies and Integration Points
The file depends on `zstd_deps.h`, `compiler.h`, `bitstream.h`, `hist.h`, `fse.h`, `huf.h`, `error_private.h`, and `bits.h`. It integrates tightly with FSE for weight header compression, with histogram counting for table construction, and with Zstd literal block encoding for repeat-table and RLE/raw decisions.

## Risks and Test Signals
Risks include workspace alignment and union sizing, canonical tree height repair in `HUF_setMaxHeight()`, quicksort/bucket sorting correctness, bit-container overflow in fast flush paths, jump-table segment size limits of 65535 bytes, and repeat-table validation when symbols appear that the old table cannot encode. Tests should cover empty input, RLE input, incompressible sampling, single-stream and four-stream outputs, max block size 128 KiB, optimal-depth flag, prefer-repeat behavior, zero-weight tables, insufficient output buffers, 32-bit versus 64-bit bit containers, and round trips against known Zstd vectors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/compress/huf_compress.c -->
