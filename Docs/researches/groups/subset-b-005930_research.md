# subset-b-005930 Research

Grouped research for the listed Ceph client kernel headers. Each section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/zstd_lib.h -->
# sources/distributed-fs/ceph-client/include/linux/zstd_lib.h

## Purpose
`zstd_lib.h` is the Linux-kernel copy of the public and static-linking Zstandard API header, advertising version 1.5.7. It defines the compression/decompression ABI for in-memory, context-reused, streaming, dictionary, frame-inspection, static-workspace, custom-allocation, threaded, external-sequence, and deprecated low-level block paths. The header contains no algorithm implementation, but it is the central contract between kernel zstd users and the linked zstd implementation.

## Important APIs, Types, And Data
Stable exports start with version and framing constants: `ZSTD_VERSION_*`, `ZSTD_MAGICNUMBER`, `ZSTD_MAGIC_DICTIONARY`, skippable-frame magic values, `ZSTD_BLOCKSIZE_MAX`, `ZSTD_CONTENTSIZE_UNKNOWN`, and `ZSTD_CONTENTSIZE_ERROR`. Simple APIs are `ZSTD_compress()`, `ZSTD_decompress()`, `ZSTD_compressBound()`, `ZSTD_findFrameCompressedSize()`, `ZSTD_getFrameContentSize()`, obsolete `ZSTD_getDecompressedSize()`, and error helpers `ZSTD_isError()`, `ZSTD_getErrorCode()`, and `ZSTD_getErrorName()`.

Context APIs define opaque `ZSTD_CCtx` and `ZSTD_DCtx` with create/free and one-shot context entry points `ZSTD_compressCCtx()` and `ZSTD_decompressDCtx()`. Advanced stable parameters include `ZSTD_strategy`, `ZSTD_cParameter`, `ZSTD_dParameter`, `ZSTD_bounds`, `ZSTD_CCtx_setParameter()`, `ZSTD_DCtx_setParameter()`, `ZSTD_CCtx_setPledgedSrcSize()`, `ZSTD_CCtx_reset()`, `ZSTD_DCtx_reset()`, and `ZSTD_compress2()`. The key state enum is `ZSTD_ResetDirective`, distinguishing session reset, parameter reset, and both.

Streaming APIs define `ZSTD_inBuffer`, `ZSTD_outBuffer`, `ZSTD_CStream` as `ZSTD_CCtx`, `ZSTD_DStream` as `ZSTD_DCtx`, and the compression state-machine directive `ZSTD_EndDirective` with `ZSTD_e_continue`, `ZSTD_e_flush`, and `ZSTD_e_end`. Main calls are `ZSTD_compressStream2()`, legacy `ZSTD_initCStream()`, `ZSTD_compressStream()`, `ZSTD_flushStream()`, `ZSTD_endStream()`, `ZSTD_initDStream()`, and `ZSTD_decompressStream()`, plus recommended buffer-size helpers.

Dictionary APIs define `ZSTD_CDict`, `ZSTD_DDict`, simple dictionary compression/decompression, digested dictionary create/free/use calls, dictionary ID helpers, sticky dictionary APIs `ZSTD_CCtx_loadDictionary()`, `ZSTD_CCtx_refCDict()`, `ZSTD_DCtx_loadDictionary()`, `ZSTD_DCtx_refDDict()`, and one-shot prefix APIs `ZSTD_CCtx_refPrefix()` and `ZSTD_DCtx_refPrefix()`. `ZSTD_sizeof_*()` exposes current object memory use.

The static-linking-only section adds frame header constants, compression parameter bounds, `ZSTD_Sequence`, `ZSTD_compressionParameters`, `ZSTD_frameParameters`, `ZSTD_parameters`, dictionary load/content enums, format/checksum/multiple-DDict enums, dictionary attach preferences, literal-compression mode, and `ZSTD_ParamSwitch_e`. It exports frame inspection (`ZSTD_findDecompressedSize()`, `ZSTD_decompressBound()`, `ZSTD_getFrameHeader()`), in-place decompression margin calculation, sequence generation/compression APIs, skippable-frame read/write helpers, memory estimators, `ZSTD_initStatic*()` placement constructors, `ZSTD_customMem`, thread-pool APIs, advanced dictionary constructors, `ZSTD_CCtx_params`, simple-args stream wrappers, decompression format/window controls, frame progression probes, block-level sequence producer registration, deprecated buffer-less streaming APIs, and deprecated raw block APIs.

## Control Flow
The main one-shot flow is allocate or reuse a context, optionally set parameters/dictionary, call a single compression or decompression function, then check any `size_t` result with `ZSTD_isError()`. `ZSTD_compressCCtx()` deliberately resets advanced parameters except the passed compression level; `ZSTD_compress2()` instead consumes sticky parameters already pushed into the context and starts a new frame.

Streaming compression is an explicit loop over `ZSTD_compressStream2()`. Callers advance `input.pos` and drain `output.pos`; `ZSTD_e_continue` ingests input, `ZSTD_e_flush` drains all currently buffered output, and `ZSTD_e_end` drains and closes the frame. Nonzero returns indicate more data remains to flush or process; zero after `ZSTD_e_end` means the frame is complete. After an error, the context state is undefined for continued streaming until reset.

Streaming decompression is a repeated `ZSTD_decompressStream()` loop. The function updates input/output positions, returns zero when a frame has fully decoded and flushed, returns positive hints when more input or output progress is needed, and returns zstd error codes on invalid input or context state. `ZSTD_d_windowLogMax` and `ZSTD_DCtx_setMaxWindowSize()` bound memory-consuming window sizes in streaming mode.

Dictionary control flow distinguishes copied dictionaries, referenced dictionaries, reusable digested dictionaries, and single-use prefixes. Sticky dictionaries stay attached across future frames until replaced, invalidated, or parameter-reset; prefixes are discarded after the next frame. Static-workspace flows require an estimate call before `ZSTD_initStatic*()` and never resize internally.

Low-level sequence and raw block flows are more fragile. `ZSTD_compressSequences*()` expects externally supplied sequence validity unless validation is enabled. The block-level sequence producer registers a callback on a context or params object, then `ZSTD_compress2()`/`ZSTD_compressStream2()` invokes it per block under documented restrictions. Deprecated buffer-less APIs require exact ordering of begin, continue, end or begin, next-size, continue.

## State And Persistence Behavior
All state is in caller-owned or library-owned contexts, dictionaries, streams, thread pools, and workspaces. Sticky compression/decompression parameters persist across frames until reset. Session state tracks in-progress frames, buffered input/output, pledged source sizes, frame checksums, dictionary references, multithreaded job queues, and stream history. Persistent storage is not used by this header.

Dictionary lifetime is a major state contract. By-copy APIs duplicate dictionary bytes internally; by-reference APIs and prefix APIs require caller buffers to outlive compression/decompression and remain unmodified. `ZSTD_CDict` and `ZSTD_DDict` are read-only for use and can be shared by multiple threads, while `ZSTD_CCtx`, `ZSTD_DCtx`, `ZSTD_CStream`, and `ZSTD_DStream` are per-thread/per-operation mutable state.

Multi-threaded compression state appears through `ZSTD_c_nbWorkers`, `ZSTD_c_jobSize`, `ZSTD_c_overlapLog`, external or internal thread pools, `ZSTD_frameProgression`, and `ZSTD_toFlushNow()`. Some parameters can change during MT compression only for future jobs. Static contexts disallow internal reallocations and are limited for dictionary creation, legacy support, and multithreading.

## Dependencies And Integration Points
The header depends on kernel `linux/types.h`, `linux/limits.h`, and `linux/zstd_errors.h`, and assumes matching zstd object code implements the prototypes. It uses symbol-visibility macros, GCC/Clang deprecation attributes, and opaque structs to keep implementation details out of callers.

Integration points in a kernel tree include compression users that need bounded allocations, filesystems or block layers that compress pages or extents, initramfs/decompression helpers, and any code using zstd dictionaries. Security-sensitive consumers should prefer `ZSTD_getFrameHeader()`/`ZSTD_DCtx_setParameter(ZSTD_d_windowLogMax, ...)` before allocating for untrusted input.

The static-only section is an integration boundary for code compiled against the same zstd implementation, not a stable dynamic ABI. Experimental enum aliases such as `ZSTD_c_rsyncable`, `ZSTD_c_stableInBuffer`, `ZSTD_d_forceIgnoreChecksum`, and raw block functions can change and must remain tightly coupled to the in-tree zstd version.

## Risks
The largest risk is treating all `size_t` returns as byte counts. Many return values encode errors and must be checked with `ZSTD_isError()`. Another high-risk pattern is trusting frame content size or window size from untrusted compressed input and allocating blindly.

Context state is easy to misuse after failures or partial flushes. Compression and decompression stream contexts may be undefined after errors, and a `ZSTD_e_end` frame is not complete until return value zero. Reusing contexts across threads violates the documented one-context-per-thread contract.

By-reference dictionaries, prefixes, stable input/output buffers, and external sequence producers push lifetime and validity obligations to callers. Modifying referenced data while compression or decompression can still use it can silently corrupt output. External sequence APIs can also create invalid compressed streams when validation is disabled.

Experimental and deprecated APIs carry compatibility risk. The static-only section warns that prototypes and enum values may change; deprecated buffer-less and raw-block APIs are less tested and require exact caller-managed metadata, contiguity, history, and incompressible-block handling.

## Test Signals
Compile tests should verify all users see the correct zstd version, prototypes, deprecation behavior, and kernel type compatibility. API tests should cover success and `ZSTD_isError()` paths for one-shot, context, streaming, dictionary, skippable-frame, static-workspace, and custom allocator calls.

Security and robustness tests should feed malformed frames, undersized headers, oversized windows, bad checksums, truncated streams, concatenated frames, skippable frames, and frames with unknown content size. Memory-bound tests should validate `ZSTD_compressBound()`, `ZSTD_decompressBound()`, `ZSTD_decompressionMargin()`, estimator functions, and max-window enforcement.

State-machine tests should verify partial output buffers, repeated flush/end calls, context reset modes, sticky parameter persistence, dictionary replacement/invalidation, by-reference lifetime assumptions, MT job progression, and post-error reset requirements. Experimental sequence tests should enable and disable validation/fallback and compare decompressed output to the original input.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/zstd_lib.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/zswap.h -->
# sources/distributed-fs/ceph-client/include/linux/zswap.h

## Purpose
`zswap.h` declares the kernel zswap frontswap-like compressed swap cache interface. It lets memory-management code store swapped folios in a compressed in-memory pool, load them back, invalidate entries, account per-LRU-vector behavior, and participate in swap device on/off and memory-cgroup cleanup. When `CONFIG_ZSWAP` is disabled, the header supplies no-op inline fallbacks so callers can compile without preprocessor-heavy call sites.

## Important APIs, Types, And Data
The global `atomic_long_t zswap_stored_pages` counts pages currently stored by zswap. Under `CONFIG_ZSWAP`, `struct zswap_lruvec_state` contains `atomic_long_t nr_disk_swapins`, a per-lruvec penalty counter for pages that had to be swapped in from disk because they were not found in zswap.

Exported functions are `zswap_total_pages()`, `zswap_store(struct folio *)`, `zswap_load(struct folio *)`, `zswap_invalidate(swp_entry_t)`, `zswap_swapon(int type, unsigned long nr_pages)`, `zswap_swapoff(int type)`, `zswap_memcg_offline_cleanup(struct mem_cgroup *)`, `zswap_lruvec_state_init(struct lruvec *)`, `zswap_folio_swapin(struct folio *)`, `zswap_is_enabled()`, and `zswap_never_enabled()`. Disabled builds replace most with inline stubs: stores fail with `false`, loads return `-ENOENT`, setup/cleanup functions are no-ops, `zswap_is_enabled()` is false, and `zswap_never_enabled()` is true.

## Control Flow
Swap-out paths call `zswap_store()` with a folio. A true result means zswap accepted and compressed the folio into its pool, while false lets normal disk swap continue. Swap-in paths call `zswap_load()`; success restores the folio from memory, and `-ENOENT` means the entry was absent and disk swap must be used. `zswap_folio_swapin()` is an accounting hook for swap-in events.

Swap-device lifecycle flows through `zswap_swapon()` before use and `zswap_swapoff()` on teardown. Individual swap entries are removed with `zswap_invalidate()`. Memory-cgroup and LRU-vector lifetime flows initialize `zswap_lruvec_state` with `zswap_lruvec_state_init()` and call `zswap_memcg_offline_cleanup()` when a memcg leaves service.

## State And Persistence Behavior
Zswap state is volatile in-memory state. Stored compressed pages remain only while the kernel, swap type, zswap pool, and relevant cgroup state remain active. `zswap_stored_pages` and `zswap_total_pages()` expose global pool occupancy. Per-lruvec `nr_disk_swapins` persists as an atomic accounting value until reset by lruvec lifecycle and is used to avoid over-shrinking after zswap misses force disk swap-ins.

No data persists across reboot. `zswap_swapoff()` and invalidation paths must drop entries and accounting for a swap type. Disabled builds persist no state beyond the always-false/true behavior of capability probes.

## Dependencies And Integration Points
The header depends on `linux/types.h`, `linux/mm_types.h`, `struct folio`, `swp_entry_t`, `struct mem_cgroup`, and `struct lruvec`. It integrates with the swap subsystem, memory reclaim/shrinker logic, cgroup offlining, and folio-based MM paths.

`zswap_lruvec_state.nr_disk_swapins` is explicitly consumed by `zswap_shrinker_count()` according to the comment, so reclaim accounting and shrinker heuristics rely on this header-level state shape. The disabled stubs make higher-level swap code independent of `CONFIG_ZSWAP` at link time.

## Risks
Callers must handle `zswap_store()` returning false and `zswap_load()` returning `-ENOENT`; those outcomes are normal, not necessarily fatal. Accounting bugs in `nr_disk_swapins` can bias reclaim by making zswap shrinkers retain or evict too much memory. Swapoff and invalidation ordering is sensitive because stale compressed entries tied to reused swap offsets could restore wrong data.

The no-op disabled stubs must remain semantically aligned with real zswap failure modes. If a caller assumes `zswap_never_enabled()` is equivalent to `!zswap_is_enabled()` at runtime, it can mis-handle systems where zswap is configured but administratively disabled or enabled later.

## Test Signals
Build tests should compile MM callers with `CONFIG_ZSWAP=y` and `CONFIG_ZSWAP=n` to catch prototype drift and fallback semantics. Functional tests should cover store/load hit, load miss with disk fallback, invalidate, swapoff cleanup, memcg offline cleanup, and total-page accounting.

Reclaim tests should observe `nr_disk_swapins` effects on shrinker counts after forced disk swap-ins. Concurrency tests should stress folio swapout/swapin, invalidation, and swapoff racing with reclaim while checking atomic counters and absence of stale-entry loads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/zswap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/zutil.h -->
# sources/distributed-fs/ceph-client/include/linux/zutil.h

## Purpose
`zutil.h` is an internal zlib compatibility/configuration header in the kernel tree. It provides shared typedefs, deflate block constants, match limits, preset dictionary flag definitions, zlib checksum callback typing, and an inline Adler-32 implementation for compression-library internals. It explicitly warns applications to include public `zlib.h` instead.

## Important APIs, Types, And Data
The header includes `linux/zlib.h`, `linux/string.h`, and `linux/kernel.h`. It defines shorthand integer aliases `uch`, `ush`, and `ulg`, block-type constants `STORED_BLOCK`, `STATIC_TREES`, and `DYN_TREES`, match length bounds `MIN_MATCH` and `MAX_MATCH`, zlib header flag `PRESET_DICT`, and default `OS_CODE` as Unix (`0x03`) unless already supplied.

`check_func` is a function pointer type for checksum callbacks with signature `uLong (*)(uLong check, const Byte *buf, uInt len)`. Adler-32 support defines `BASE`, `NMAX`, and loop-unrolling macros `DO1`, `DO2`, `DO4`, `DO8`, and `DO16`. The only inline function is `zlib_adler32(uLong adler, const Byte *buf, uInt len)`.

## Control Flow
`zlib_adler32()` initializes `s1` and `s2` from the incoming Adler value. If `buf` is `NULL`, it returns the Adler initial value `1L`. Otherwise it processes the buffer in chunks up to `NMAX` bytes to keep intermediate sums within 32-bit bounds, uses `DO16()` for 16-byte unrolled accumulation, handles the tail one byte at a time, reduces both sums modulo `BASE`, and returns `(s2 << 16) | s1`.

The block and match constants are not executed here; they are consumed by zlib deflate/inflate implementation code to classify stored/static/dynamic blocks, match lengths, and preset-dictionary headers.

## State And Persistence Behavior
The header has no persistent state and no hidden allocation. Adler state is passed in and returned by value, so callers can compute a checksum incrementally across multiple buffer reads. All other data is compile-time macro configuration.

## Dependencies And Integration Points
This file integrates with in-kernel zlib compression and decompression sources that need internal helpers beyond the public zlib API. It depends on public zlib scalar types `uLong`, `Byte`, and `uInt`. The checksum function pointer type allows deflate/inflate code to abstract checksum selection.

Because it is internal, its macros may be included by several translation units and can affect generated code through unrolled checksum macros and `OS_CODE`. External modules should avoid relying on it as a stable API.

## Risks
The checksum loop depends on `NMAX` being small enough to prevent overflow before modulo reduction. Changes to `BASE`, `NMAX`, or the unrolled macros can silently break Adler-32 compatibility. `zlib_adler32(NULL)` intentionally returns the initializer, so callers must not treat NULL as a no-op update preserving the incoming checksum.

Macro names such as `DO1` and short typedefs are generic and can collide if this internal header is included in broad scopes. Because this is internal API, external consumers risk breakage if they depend on these names.

## Test Signals
Checksum tests should compare `zlib_adler32()` against known Adler-32 vectors, including empty input, NULL initialization, one-byte updates, incremental multi-buffer updates, and buffers crossing `NMAX` boundaries. Build tests should compile deflate/inflate users with this header and public `linux/zlib.h` to catch type drift or macro conflicts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/zutil.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/math-emu/double.h -->
# sources/distributed-fs/ceph-client/include/math-emu/double.h

## Purpose
`double.h` defines the soft-float IEEE-754 double-precision format layer for the kernel math-emulation framework. It maps a native `double` bit layout into the generic `_FP_*` macro machinery, chooses one-word or two-word fraction storage depending on `_FP_W_TYPE_SIZE`, and exposes double-specific operations such as unpack, pack, compare, arithmetic, sqrt, integer conversion, and NaN/sign helpers.

## Important APIs, Types, And Data
The header defines double format constants: `_FP_FRACBITS_D` as 53, `_FP_EXPBITS_D` as 11, `_FP_EXPBIAS_D` as 1023, `_FP_EXPMAX_D` as 2047, `_FP_QNANBIT_D`, `_FP_IMPLBIT_D`, and `_FP_OVERFLOW_D`. `_FP_FRACTBITS_D`, `_FP_FRACXBITS_D`, `_FP_WFRACBITS_D`, and `_FP_WFRACXBITS_D` depend on host limb width and `_FP_WORKBITS`.

`union _FP_UNION_D` overlays a native `double` with packed sign, exponent, and fraction bitfields. The layout is endian-sensitive: big-endian orders sign/exp/fraction from the high bits, while little-endian places low fraction bits first. On hosts with `_FP_W_TYPE_SIZE < 64`, the fraction is split into `frac0` and `frac1`; on 64-bit-word hosts it uses one `unsigned long frac`.

Public macro front ends include `FP_DECL_D`, `FP_UNPACK_RAW_D`, `FP_UNPACK_RAW_DP`, `FP_PACK_RAW_D`, `FP_PACK_RAW_DP`, `FP_UNPACK_D`, `FP_UNPACK_DP`, `FP_PACK_D`, `FP_PACK_DP`, `FP_ISSIGNAN_D`, `FP_NEG_D`, `FP_ADD_D`, `FP_SUB_D`, `FP_MUL_D`, `FP_DIV_D`, `FP_SQRT_D`, `FP_CMP_D`, `FP_CMP_EQ_D`, `FP_TO_INT_D`, `FP_TO_INT_ROUND_D`, `FP_FROM_INT_D`, `_FP_FRAC_HIGH_D`, and `_FP_FRAC_HIGH_RAW_D`.

## Control Flow
Double emulation users declare operands with `FP_DECL_D()`, unpack native double inputs with raw or canonical unpack macros, run arithmetic through the generic `_FP_ADD`, `_FP_SUB`, `_FP_MUL`, `_FP_DIV`, `_FP_SQRT`, compare, or conversion macros, and pack the result back through raw or canonical pack macros. Pointer variants ending in `P` read or write through a caller-provided memory address.

Canonical unpack/pack macros call `_FP_UNPACK_CANONICAL()` and `_FP_PACK_CANONICAL()` around the raw union conversion so classification, normalization, rounding, exception flags, NaNs, infinities, denormals, and inhibited-result handling stay centralized in the broader math-emu framework. `_FP_SQRT_MEAT_D` maps to the one- or two-limb square-root implementation selected for the host word size.

## State And Persistence Behavior
This header has no runtime persistence. State exists only in macro-expanded local variables generated by `_FP_DECL()` and related fraction declarations. `FP_PACK_RAW_DP` and `FP_PACK_DP` honor `FP_INHIBIT_RESULTS` by avoiding stores when result writes are inhibited by exception/control state.

## Dependencies And Integration Points
`double.h` depends on the generic soft-float environment defining `_FP_W_TYPE_SIZE`, `_FP_W_TYPE`, `_FP_WORKBITS`, `_FP_DECL`, `_FP_UNPACK_RAW_1/2`, `_FP_PACK_RAW_1/2`, canonicalization macros, arithmetic macros, comparison macros, and conversion macros. It also depends on `__BYTE_ORDER`, `__BIG_ENDIAN`, and compiler support for packed bitfield structs.

It integrates with architecture math-emulation code implementing double-precision instructions in software. The one-word path expects `_FP_MUL_D` and `_FP_DIV_D` meat selection to be provided by the target when necessary; the two-word path directly maps multiply/divide/sqrt to two-limb helpers.

## Risks
Bitfield layout is inherently compiler- and ABI-sensitive. Any mismatch in endian definitions, packed struct behavior, `_FP_W_TYPE_SIZE`, or `unsigned long` width can unpack or pack the wrong sign/exponent/fraction bits. The header refuses word sizes below 32 bits, and double support assumes the rest of math-emu provides consistent limb macros.

NaN quiet/signaling bits, implicit-bit handling, overflow bit location, and work-bit widths are subtle. A bad constant can produce incorrect exceptions or rounding. Pointer pack/unpack macros cast raw addresses to `union _FP_UNION_D *`, so alignment and aliasing assumptions must match kernel/architecture rules.

## Test Signals
Architecture soft-float tests should cover double add, subtract, multiply, divide, sqrt, compare, negate, conversions to and from signed/unsigned integers, raw bit round-trips, NaNs, infinities, signed zero, subnormals, overflow, underflow, and rounding modes. Build tests should exercise both one-word and two-word configurations where architectures support them, and endian-specific tests should verify exact bit patterns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/math-emu/double.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/math-emu/op-1.h -->
# sources/distributed-fs/ceph-client/include/math-emu/op-1.h

## Purpose
`op-1.h` implements the one-word fraction backend for the kernel software floating-point emulation framework. It provides declaration, assignment, shifts with sticky bits, arithmetic predicates, raw native-float pack/unpack helpers, multiply/divide/sqrt algorithms, integer assembly/disassembly, and one-word-to-one-word fraction conversion.

## Important APIs, Types, And Data
The one-word fraction is represented as a single `_FP_W_TYPE X_f`. Core macros include `_FP_FRAC_DECL_1`, `_FP_FRAC_COPY_1`, `_FP_FRAC_SET_1`, `_FP_FRAC_HIGH_1`, `_FP_FRAC_LOW_1`, `_FP_FRAC_WORD_1`, `_FP_FRAC_ADDI_1`, `_FP_FRAC_SLL_1`, `_FP_FRAC_SRL_1`, `_FP_FRAC_SRS_1`, `_FP_FRAC_ADD_1`, `_FP_FRAC_SUB_1`, `_FP_FRAC_DEC_1`, `_FP_FRAC_CLZ_1`, and predicates for negative, zero, overflow, equality, greater-than, and greater-or-equal.

Raw conversion macros `_FP_UNPACK_RAW_1`, `_FP_UNPACK_RAW_1_P`, `_FP_PACK_RAW_1`, and `_FP_PACK_RAW_1_P` use `union _FP_UNION_<fs>` fields `frac`, `exp`, and `sign`. Arithmetic meat macros include `_FP_MUL_MEAT_1_imm`, `_FP_MUL_MEAT_1_wide`, `_FP_MUL_MEAT_1_hard`, `_FP_DIV_MEAT_1_imm`, `_FP_DIV_MEAT_1_udiv_norm`, `_FP_DIV_MEAT_1_udiv`, and `_FP_SQRT_MEAT_1`. Conversion helpers are `_FP_FRAC_ASSEMBLE_1`, `_FP_FRAC_DISASSEMBLE_1`, and `_FP_FRAC_CONV_1_1`.

## Control Flow
Callers use this header indirectly through format headers such as `double.h` or other precision definitions. The generic arithmetic layer declares operands, unpacks raw bits, canonicalizes them, and then calls the selected one-word meat macro for multiply, divide, or sqrt.

Left and right shifts mutate the single fraction word. Sticky right shift sets the low bit if any discarded bit was nonzero, preserving rounding information. Multiplication either uses immediate host multiplication, a supplied wide multiply primitive, or a manual half-word split/reassemble algorithm. Division either uses a host divide helper or `udiv_qrnnd` in normalized or non-normalized forms. Square root performs an iterative restoring algorithm, adding work-round/sticky bits if a remainder remains.

## State And Persistence Behavior
There is no persistent state. Every macro mutates caller-provided macro variables in the current expression/block. Rounding state is carried in work bits inside the fraction word, especially `_FP_WORK_ROUND` and `_FP_WORK_STICKY`, and exception/result inhibition is managed outside this file.

## Dependencies And Integration Points
This backend depends on `_FP_W_TYPE`, `_FP_WS_TYPE`, `_FP_W_TYPE_SIZE`, `_FP_I_TYPE`, `_FP_WORK_ROUND`, `_FP_WORK_STICKY`, `_FP_WFRACBITS_<fs>`, `_FP_WFRACXBITS_<fs>`, `__FP_CLZ`, `udiv_qrnnd`, and optional wide multiply/divide helpers from architecture longlong support. It also depends on format-specific unions with `bits.frac`, `bits.exp`, and `bits.sign`.

It integrates with higher-level math-emu headers that select one-limb storage for formats whose working fraction fits in one machine word, especially on 64-bit hosts for double precision.

## Risks
Macro arguments are evaluated in mutable contexts, so callers must pass simple operand names with the expected suffix variables. Shift counts must stay within assumptions; sticky-shift expressions use `_FP_W_TYPE_SIZE - N` and are unsafe if passed invalid counts. Carry, borrow, and sticky propagation errors directly cause wrong rounding.

The `_FP_MUL_MEAT_1_hard` fallback relies on splitting a word exactly in half and reassembling products without overflow beyond modeled limbs. Division helpers depend on architecture-specific `udiv_qrnnd` semantics, including whether normalization is required.

## Test Signals
Unit-level macro tests can compare one-word operations against high-precision integer arithmetic for shifts, sticky shifts, add/subtract, multiply, divide, sqrt, and conversions. Floating-point instruction emulation tests should stress halfway rounding, sticky-bit tails, exact/inexact division, square-root remainders, overflow-bit clearing, and raw pack/unpack round-trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/math-emu/op-1.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/math-emu/op-2.h -->
# sources/distributed-fs/ceph-client/include/math-emu/op-2.h

## Purpose
`op-2.h` implements the two-word fraction backend for software floating-point emulation. It extends the one-word macro contract to fractions stored as low/high limbs, provides two-limb shifts and comparisons, raw pack/unpack helpers, multiple multiplication and division algorithms, square root, integer assembly/disassembly, and conversions between one- and two-word formats.

## Important APIs, Types, And Data
Two-word values are represented as `_FP_W_TYPE X_f0` and `X_f1`. Core macros include `_FP_FRAC_DECL_2`, `_FP_FRAC_COPY_2`, `_FP_FRAC_SET_2`, `_FP_FRAC_HIGH_2`, `_FP_FRAC_LOW_2`, `_FP_FRAC_WORD_2`, `_FP_FRAC_SLL_2`, `_FP_FRAC_SRL_2`, `_FP_FRAC_SRS_2`, `_FP_FRAC_ADDI_2`, `_FP_FRAC_ADD_2`, `_FP_FRAC_SUB_2`, `_FP_FRAC_DEC_2`, `_FP_FRAC_CLZ_2`, predicates, and constants `_FP_ZEROFRAC_2`, `_FP_MINFRAC_2`, and `_FP_MAXFRAC_2`.

Internal helpers define `__FP_FRAC_SET_2` and `__FP_CLZ_2`. Add/subtract/dec macros are mapped to `add_ssaaaa` and `sub_ddmmss` in the active branch, while an unused `#if 0` branch documents portable C fallbacks. Raw pack/unpack macros map `frac0`, `frac1`, `exp`, and `sign` fields from format-specific unions.

Multiplication options include `_FP_MUL_MEAT_2_wide`, `_FP_MUL_MEAT_2_wide_3mul`, `_FP_MUL_MEAT_2_gmp`, and `_FP_MUL_MEAT_2_120_240_double`. Division options include `_FP_DIV_MEAT_2_udiv` and `_FP_DIV_MEAT_2_gmp`. Square-root is `_FP_SQRT_MEAT_2`. Conversion helpers are `_FP_FRAC_ASSEMBLE_2`, `_FP_FRAC_DISASSEMBLE_2`, `_FP_FRAC_CONV_1_2`, and `_FP_FRAC_CONV_2_1`.

## Control Flow
Generic math-emu code performs fraction operations by invoking these macros on named operands. Shifts move bits across the low/high limb boundary, and sticky right shifts OR low discarded bits into the resulting least-significant bit. Add/subtract use longlong primitives to propagate carry or borrow across two limbs.

Wide multiplication computes partial products into a four-word temporary, accumulates cross terms, sticky-right-shifts the product to the target working precision, and stores the low two limbs into the result. The three-multiply variant trades more additions/subtractions for fewer multiplications. GMP variants delegate to `mpn_mul_n()` or `mpn_divrem()` when available. The 120x240 double algorithm uses floating-point arithmetic with controlled exceptions/rounding for certain 64-bit, 106-to-120-bit working fractions.

Division normalizes or aligns the numerator based on operand comparison, estimates quotient limbs with `udiv_qrnnd`, multiplies back to correct overestimates, adjusts quotient words, and sets sticky if a remainder remains. Square root iterates from high to low quotient bits, subtracting trial values and setting round/sticky on leftover remainder.

## State And Persistence Behavior
No persistent state exists. The macros mutate local two-word operand variables and temporary declarations. Exponent adjustments are made through `R_e` in division paths when quotient normalization changes. Rounding information is stored in low-limb work bits.

## Dependencies And Integration Points
`op-2.h` depends on `_FP_W_TYPE`, `_FP_WS_TYPE`, `_FP_W_TYPE_SIZE`, `UWtype`, `UDItype`, `DItype`, longlong primitives `add_ssaaaa`, `sub_ddmmss`, `umul_ppmm`, `udiv_qrnnd`, optional GMP `mpn_mul_n()`/`mpn_divrem()`, and caller-supplied FPU environment macros for the double-based multiplication path. It also depends on four-word operations from `op-4.h` for multiplication temporaries.

It integrates with double precision on 32-bit-word configurations and with wider emulated formats whose working fractions need two machine words.

## Risks
Carry and borrow handling across limbs is the main correctness risk. The active branch assumes architecture longlong primitives are correct and available. Shift macros have separate paths for counts below or above one word and must not be called with invalid counts outside the modeled fraction size.

The double-based multiply path is highly specialized: it aborts if `wfracbits` is outside 106 to 120, requires exception masking and round-toward-zero setup, and relies on exact properties of double arithmetic and 24-bit chunks. GMP paths depend on array limb order matching the `_f0`/`_f1` convention.

## Test Signals
Macro tests should compare two-limb add, subtract, shifts, sticky shifts, CLZ, comparisons, multiply, divide, sqrt, and conversions against arbitrary-precision reference arithmetic. Architecture tests should exercise exact one-word-boundary shifts, quotient correction cases, nonzero remainders, NaN conversion without sticky rounding, and both 32-bit and 64-bit limb builds where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/math-emu/op-2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/math-emu/op-4.h -->
# sources/distributed-fs/ceph-client/include/math-emu/op-4.h

## Purpose
`op-4.h` implements the four-word fraction backend for the software floating-point emulator. It supports wider formats and also provides intermediate storage for two-word multiplication. The header defines four-limb declaration/copy/access operations, multiword shifts with sticky support, add/subtract/borrow helpers, comparisons, raw pack/unpack, four-word multiply/divide/sqrt, integer assembly/disassembly, and conversions to and from one- and two-word formats.

## Important APIs, Types, And Data
Four-word fractions are stored as `_FP_W_TYPE X_f[4]`, low limb at index 0 and high limb at index 3. Core macros include `_FP_FRAC_DECL_4`, `_FP_FRAC_COPY_4`, `_FP_FRAC_SET_4`, `_FP_FRAC_HIGH_4`, `_FP_FRAC_LOW_4`, `_FP_FRAC_WORD_4`, `_FP_FRAC_SLL_4`, `_FP_FRAC_SRL_4`, `_FP_FRAC_SRS_4`, `_FP_FRAC_ADD_4`, `_FP_FRAC_SUB_4`, `_FP_FRAC_DEC_4`, `_FP_FRAC_ADDI_4`, `_FP_FRAC_ZEROP_4`, `_FP_FRAC_NEGP_4`, `_FP_FRAC_OVERP_4`, `_FP_FRAC_CLEAR_OVERP_4`, `_FP_FRAC_EQ_4`, `_FP_FRAC_GT_4`, `_FP_FRAC_GE_4`, and `_FP_FRAC_CLZ_4`.

Raw conversion uses `_FP_UNPACK_RAW_4`, `_FP_UNPACK_RAW_4_P`, `_FP_PACK_RAW_4`, and `_FP_PACK_RAW_4_P`, expecting union fields `frac0` through `frac3`, `exp`, and `sign`. Arithmetic meat macros are `_FP_MUL_MEAT_4_wide`, `_FP_MUL_MEAT_4_gmp`, helper `umul_ppppmnnn`, `_FP_DIV_MEAT_4_udiv`, and `_FP_SQRT_MEAT_4`. Internal add/subtract helpers include `__FP_FRAC_ADD_3`, `__FP_FRAC_ADD_4`, `__FP_FRAC_SUB_3`, `__FP_FRAC_SUB_4`, `__FP_FRAC_DEC_3`, `__FP_FRAC_DEC_4`, and `__FP_FRAC_ADDI_4`.

Conversion helpers include `_FP_FRAC_CONV_1_4`, `_FP_FRAC_CONV_2_4`, `_FP_FRAC_ASSEMBLE_4`, `_FP_FRAC_DISASSEMBLE_4`, `_FP_FRAC_CONV_4_1`, and `_FP_FRAC_CONV_4_2`.

## Control Flow
Shift operations compute a word skip and intra-word shift, then copy limbs in high-to-low or low-to-high order to avoid clobbering source limbs before zero-filling the remainder. Sticky right shift collects all bits shifted out and ORs the final least-significant bit after the shifted result is stable.

Four-word multiplication expands partial products into an eight-word temporary, accumulating all cross terms with three-word and two-word add helpers. It then sticky-right-shifts the eight-word product to working precision and stores the low four limbs in the result. The GMP path delegates to `mpn_mul_n()` on four-limb arrays and then normalizes through the eight-word shift helper.

Division normalizes the denominator, then iterates quotient limbs from high to low using `udiv_qrnnd()` and `umul_ppppmnnn()` to estimate and correct each quotient word. It shifts state through `X_f[]` and an auxiliary `_n` array, decrements overestimated quotient words when multiply-back exceeds the remainder, and sets sticky on the low quotient limb when the final remainder is nonzero. Square root is an iterative restoring algorithm that walks high-to-low limbs and sets round/sticky bits if a remainder remains.

## State And Persistence Behavior
There is no persistent state. The header mutates caller-provided fraction arrays and local temporaries. It may adjust result exponent state through `R_e` inside division. Work bits in the low limb carry rounding information for later generic packing.

## Dependencies And Integration Points
`op-4.h` depends on `_FP_W_TYPE`, `_FP_WS_TYPE`, `_FP_I_TYPE`, `_FP_W_TYPE_SIZE`, `UWtype`, `udiv_qrnnd`, `umul_ppmm`, optional `mpn_mul_n()`, and the eight-word primitives declared by `op-8.h`. It expects caller format unions with four fraction fields.

It integrates with wide soft-float formats and with `op-2.h` as a multiplication scratch backend. Because many helper macros are conditionally defined with `#ifndef`, architecture-specific code can override some carry/borrow operations.

## Risks
The implementation is sensitive to limb order, loop bounds, and shift counts. A notable risk is `_FP_FRAC_CLZ_4()` using `X_f[2]` in the branch where `X_f[1]` is nonzero, which looks inconsistent with the intended leading-zero count over limb 1 and should be checked against upstream or tests. Comments also note some conversion macros may be "somewhat bogus" because they depend on internal variable shapes.

Carry/borrow propagation and quotient correction bugs can create one-bit rounding errors that only appear on edge cases. Assembly/disassembly paths for integer sizes above two words rely on shifts by multiples of `_FP_W_TYPE_SIZE`, so target integer widths and compiler behavior matter.

## Test Signals
Tests should cover exact word-boundary shifts, sticky shifts with discarded bits in every limb, comparisons, add/subtract carry chains, multiply cross terms, division quotient correction, sqrt remainders, and conversions between one-, two-, and four-word representations. A targeted CLZ test should exercise nonzero values exclusively in each limb to detect the apparent limb-1 typo. End-to-end soft-float tests should validate wide-format operations against high-precision references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/math-emu/op-4.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/math-emu/op-8.h -->
# sources/distributed-fs/ceph-client/include/math-emu/op-8.h

## Purpose
`op-8.h` supplies the minimal eight-word fraction helpers needed by the wider math-emulation backends, especially as temporary product storage for four-word multiplication. It defines eight-limb declaration/access macros and left, right, and sticky-right shifts.

## Important APIs, Types, And Data
Eight-word values are represented as `_FP_W_TYPE X_f[8]`, with low limb at index 0 and high limb at index 7. Exposed macros are `_FP_FRAC_DECL_8`, `_FP_FRAC_HIGH_8`, `_FP_FRAC_LOW_8`, `_FP_FRAC_WORD_8`, `_FP_FRAC_SLL_8`, `_FP_FRAC_SRL_8`, and `_FP_FRAC_SRS_8`.

Unlike the smaller operation headers, this file intentionally omits add/subtract, predicates, pack/unpack, multiplication, division, sqrt, and conversion helpers. Its comment states only a few pieces are needed for `op-4`, and more can be added later.

## Control Flow
The shift macros compute the number of whole limbs to skip and the intra-limb shift. Left shifts copy from lower to higher indices, right shifts copy from higher to lower indices, and then zero-fill vacated limbs. Sticky right shift first ORs together all fully discarded low limbs plus the partially discarded bits, performs the right shift, zero-fills high limbs, and ORs the final low bit if any discarded bit was nonzero.

## State And Persistence Behavior
There is no runtime persistence. The macros mutate caller-provided `X_f[8]` arrays and local loop variables only. Sticky information is carried in the shifted result's low bit for downstream rounding.

## Dependencies And Integration Points
The header depends on `_FP_W_TYPE`, `_FP_I_TYPE`, and `_FP_W_TYPE_SIZE`. Its primary integration point is `op-4.h`, where `_FP_FRAC_DECL_8`, `_FP_FRAC_WORD_8`, and `_FP_FRAC_SRS_8` hold and normalize full-width four-by-four-limb products.

## Risks
Shift correctness is the dominant risk. The macros assume valid shift counts for the modeled eight-limb value; out-of-range counts could index beyond the array or perform undefined-width shifts. Sticky-right shift accesses `X_f[_i]` after scanning fully skipped limbs, so callers must not request a shift that skips all eight limbs without guarding elsewhere.

Because the header provides only shift primitives, any future expansion must preserve the low-limb-first convention used by `op-4.h` and GMP-style multiplication arrays.

## Test Signals
Tests should shift eight-limb values by zero, one, word-size minus one, exactly one word, multiple words, and near the full width. Sticky-right tests should place a single set bit in each discarded limb or partial-limb position and verify only the final low bit records discarded data. Integration tests should multiply four-limb fractions in `op-4.h` and verify the eight-limb normalization path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/math-emu/op-8.h -->
