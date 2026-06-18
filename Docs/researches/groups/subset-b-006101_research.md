# subset-b-006101 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/lz4/lz4_compress.c -->
# sources/distributed-fs/ceph-client/lib/lz4/lz4_compress.c

## Purpose
`lz4_compress.c` implements the kernel LZ4 fast compressor, including one-shot compression, destination-size-limited compression, and streaming compression with a 64 KiB history window. It is a kernel-adapted copy of Yann Collet's LZ4 block compressor and exports the kernel symbols consumed by crypto wrappers, filesystem compression users, and boot/decompression helpers.

## Important APIs, types, and functions
Public exports are `LZ4_compress_fast()`, `LZ4_compress_default()`, `LZ4_compress_destSize()`, `LZ4_resetStream()`, `LZ4_loadDict()`, `LZ4_saveDict()`, and `LZ4_compress_fast_continue()`. The central private routines are `LZ4_compress_generic()` and `LZ4_compress_destSize_generic()`. Hash-table helpers such as `LZ4_hashPosition()`, `LZ4_putPositionOnHash()`, and `LZ4_getPositionOnHash()` abstract the three table encodings: pointer table, 32-bit offset table, and 16-bit offset table. Stream state is `LZ4_stream_t_internal` from `include/linux/lz4.h`, especially `hashTable`, `currentOffset`, `dictionary`, and `dictSize`.

## Control flow
One-shot compression resets caller-provided work memory, chooses `byU16` for inputs below the 64 KiB limit and a native pointer or U32 table otherwise, then calls `LZ4_compress_generic()`. The generic loop seeds the first hash, advances through the input with an acceleration-dependent skip pattern, checks distance and dictionary validity, catches matches backward to maximize literals, emits an LZ4 token, copies literal bytes, writes the match offset, encodes the match length extension bytes, and then probes for an immediate next match. If no more match can be safely searched, `_last_literals` writes the final literal run. The destination-size variant inverts the contract: it reduces the final literal run or match length when needed and updates `*srcSizePtr` with the consumed source bytes.

## State and persistence
Non-streaming calls use only caller-supplied work memory and do not persist state after return. Streaming calls mutate `LZ4_stream_t_internal`: dictionaries are capped to 64 KiB, hash offsets are renormalized when `currentOffset` risks overflow, and `saveDict()` copies the tail dictionary into a safe caller buffer. `LZ4_compress_fast_continue()` supports prefix mode when the next source block immediately follows the previous dictionary and external-dictionary mode when it does not.

## Dependencies and integration points
The file depends on `lz4defs.h`, `linux/lz4.h`, kernel unaligned access helpers, `memset`, `memmove`, and module export infrastructure. Integration is through exported LZ4 symbols and `CONFIG_LZ4_COMPRESS`; known consumers in this tree include `crypto/lz4.c`, `lib/decompress_unlz4.c`, SquashFS, and other kernel compression front ends that allocate `LZ4_MEM_COMPRESS` work buffers.

## Risks and test signals
The highest risks are pointer arithmetic around `match + refDelta`, distance checks, output-limit checks before wild copies, and streaming dictionary transitions where old input must remain readable. Incorrect work-memory sizing or alignment is a caller bug and can corrupt compression state. Test signals include one-shot round trips across small and large inputs, incompressible data returning a valid larger block or zero under tight output limits, `LZ4_compress_destSize()` reporting partial source consumption, streaming compression across contiguous and non-contiguous blocks, dictionary save/load behavior, and malformed boundary fuzzing paired with `LZ4_decompress_safe()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/lz4/lz4_compress.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/lz4/lz4_decompress.c -->
# sources/distributed-fs/ceph-client/lib/lz4/lz4_decompress.c

## Purpose
`lz4_decompress.c` implements the kernel LZ4 block decompressor. It provides safe, partial, fast, dictionary-backed, and streaming decode entry points over one shared inlined decoder. It is the defensive side of the LZ4 implementation used by crypto, filesystems, and boot-time decompression paths.

## Important APIs, types, and functions
Public exports are `LZ4_decompress_safe()`, `LZ4_decompress_safe_partial()`, `LZ4_decompress_fast()`, `LZ4_setStreamDecode()`, `LZ4_decompress_safe_continue()`, `LZ4_decompress_fast_continue()`, `LZ4_decompress_safe_usingDict()`, and `LZ4_decompress_fast_usingDict()`. `LZ4_decompress_generic()` is the main engine and is parameterized by `endCondition_directive`, `earlyEnd_directive`, and `dict_directive` from `lz4defs.h`. Private wrappers instantiate prefix, small-prefix, external-dictionary, and double-dictionary cases. Streaming state is `LZ4_streamDecode_t_internal`, carrying `prefixEnd`, `prefixSize`, `externalDict`, and `extDictSize`.

## Control flow
The generic decoder reads a token, decodes literal length, copies literals, reads the match offset, decodes match length, and copies match bytes until the block ends. It has a fast shortcut for common small literal and match lengths when input and output have enough slack. In safe mode it validates input consumption, output capacity, offset lookbehind, and arithmetic overflow. Partial mode can stop after filling the requested target output. Dictionary handling splits matches into prefix-only, external-dictionary-only, and dictionary-plus-current-block copies. Streaming decode chooses a path based on whether `dest` directly follows the previous prefix, whether a small prefix or external dictionary is active, or whether the ring buffer/wrapped buffer requires double-dictionary mode.

## State and persistence
One-shot decode is stateless. Streaming decode persists only the location and size of the previous decoded prefix and, when buffers move, the external dictionary range. The implementation does not copy dictionary bytes itself; callers must keep prior decoded data or an explicitly supplied dictionary readable for the next block. Return values are decoded byte counts for safe modes, bytes read for fast modes, or negative error positions for malformed input.

## Dependencies and integration points
The file depends on `lz4defs.h`, `linux/lz4.h`, unaligned little-endian reads, `LZ4_wildCopy()`, `LZ4_copy8()`, and kernel module exports. It is reached from `crypto/lz4.c`, `crypto/lz4hc.c`, `lib/decompress_unlz4.c`, and filesystem wrappers. `#ifndef STATIC` allows inclusion-style builds to avoid module export boilerplate.

## Risks and test signals
The critical risk surface is malicious compressed input. Safe paths must reject input overrun, output overrun, invalid lookbehind offsets, invalid final literals, and size overflows. Fast paths deliberately trust the compressed stream and should be used only when the compressed data and original size are trusted. Dictionary tests should cover prefix, small-prefix, external-dictionary, and double-dictionary cases. Good signals include exact output lengths, negative returns for malformed blocks, partial decode stopping at target capacity, in-place/overlap literal behavior, and cross-checking data compressed by both fast and HC compressors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/lz4/lz4_decompress.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/lz4/lz4defs.h -->
# sources/distributed-fs/ceph-client/lib/lz4/lz4defs.h

## Purpose
`lz4defs.h` is the private shared implementation header for the kernel LZ4 compressor, HC compressor, and decompressor. It supplies architecture-specific constants, unaligned memory access wrappers, wild-copy primitives, byte matching helpers, and the internal directive enums used to specialize generic compression/decompression loops.

## Important APIs, types, and functions
The header defines byte-sized aliases (`BYTE`, `U16`, `U32`, `U64`, `uptrval`), block constants (`MINMATCH`, `WILDCOPYLENGTH`, `LASTLITERALS`, `MFLIMIT`, `MATCH_SAFEGUARD_DISTANCE`, masks for token literal/match lengths), and table/dictionary directives. Key helpers are `LZ4_read16()`, `LZ4_read32()`, `LZ4_read_ARCH()`, `LZ4_writeLE16()`, `LZ4_copy8()`, `LZ4_wildCopy()`, `LZ4_NbCommonBytes()`, and `LZ4_count()`. It also defines `limitedOutput_directive`, `tableType_t`, `dict_directive`, `dictIssue_directive`, `endCondition_directive`, and `earlyEnd_directive`.

## Control flow
The header itself has no standalone runtime flow, but its helpers sit directly in hot compression and decompression paths. `LZ4_count()` compares machine words while possible, uses bit-scan operations to locate the first differing byte, then finishes with 32-bit, 16-bit, and byte comparisons near the input limit. `LZ4_wildCopy()` repeatedly copies 8 bytes and intentionally permits bounded over-copy where callers have guaranteed slack.

## State and persistence
The header carries no mutable state. Its compile-time state comes from kernel architecture configuration, including `CONFIG_64BIT`, endian definitions, `BITS_PER_LONG`, and optional `LZ4_DISTANCE_MAX`. These choices affect hash width, common-byte counting, and copy width in all LZ4 objects built from the directory.

## Dependencies and integration points
Dependencies include `linux/unaligned.h`, `linux/bitops.h`, `linux/string.h`, `linux/types.h`, and `linux/lz4.h`. This header is included by all three local LZ4 implementation files and forms the private ABI between generic algorithm code and the public structures declared in `include/linux/lz4.h`.

## Risks and test signals
Because this file defines low-level memory primitives, mistakes affect every LZ4 mode. Risk areas are bounded wild-copy assumptions, unaligned read/write behavior on strict-alignment architectures, endian-specific bit scans, and token/distance constants matching the public LZ4 format. Test signals are architecture-diverse build coverage, KASAN/UBSAN or equivalent bounds testing around block ends, round trips on little- and big-endian targets, and focused tests where matches end exactly at `LASTLITERALS`, `MFLIMIT`, and `MATCH_SAFEGUARD_DISTANCE` boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/lz4/lz4defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/lz4/lz4hc_compress.c -->
# sources/distributed-fs/ceph-client/lib/lz4/lz4hc_compress.c

## Purpose
`lz4hc_compress.c` implements the high-compression LZ4 encoder for the kernel. It emits the same LZ4 block format as the fast compressor but spends more CPU on chain-table match search and multi-match selection to improve compression ratio. It supports one-shot and streaming HC compression with caller-managed work memory.

## Important APIs, types, and functions
Public exports are `LZ4_compress_HC()`, `LZ4_resetStreamHC()`, `LZ4_loadDictHC()`, `LZ4_compress_HC_continue()`, and `LZ4_saveDictHC()`. Important private routines are `LZ4HC_init()`, `LZ4HC_Insert()`, `LZ4HC_InsertAndFindBestMatch()`, `LZ4HC_InsertAndGetWiderMatch()`, `LZ4HC_encodeSequence()`, `LZ4HC_compress_generic()`, `LZ4HC_setExternalDict()`, and `LZ4_compressHC_continue_generic()`. The mutable context is `LZ4HC_CCtx_internal`, with `hashTable`, `chainTable`, `base`, `end`, `dictBase`, `dictLimit`, `lowLimit`, `nextToUpdate`, and `compressionLevel`.

## Control flow
One-shot compression checks work-memory alignment, initializes the HC context around the source buffer, chooses limited or unlimited output mode from `LZ4_compressBound()`, and enters `LZ4HC_compress_generic()`. The generic loop inserts positions into a hash table and a 64 KiB chain table, finds the best current match, searches for better second and third matches, adjusts overlaps with empirical rules, then emits one or two LZ4 sequences through `LZ4HC_encodeSequence()`. The last literal run is appended at the end. Streaming compression auto-initializes forgotten contexts, renormalizes huge histories by reloading the last dictionary, switches to external-dictionary mode when blocks are not contiguous, trims overlapping input/dictionary ranges, and then reuses the generic compressor.

## State and persistence
The HC stream context persists hash chains and dictionary boundaries across calls. Loaded dictionaries are capped to 64 KiB. `saveDictHC()` copies the active tail dictionary into caller-provided safe memory and rewrites `base`, `end`, `dictLimit`, `lowLimit`, and `nextToUpdate` so subsequent blocks can refer to the moved dictionary. As with the fast streaming compressor, previous blocks must remain readable unless saved.

## Dependencies and integration points
The file depends on `lz4defs.h`, `include/linux/lz4.h`, kernel `memset`/`memmove`, and module exports. It is built by `lib/lz4/Makefile` under `CONFIG_LZ4HC_COMPRESS` and is used by `crypto/lz4hc.c` and any kernel user that needs slower but denser LZ4 output while preserving compatibility with `LZ4_decompress_*()`.

## Risks and test signals
Risks include chain-table underflow or stale indexes, match references crossing `dictLimit`/`lowLimit`, output-limit checks before sequence emission, context alignment, and compression-level extremes changing search attempts exponentially. Streaming edge cases include source buffers overlapping the retained dictionary and contexts whose indexed distance grows past 2 GiB. Test signals should include round trips at levels below, within, and above supported levels; output-limit failure returning zero without treating `dst` as valid; dictionary load/save/continue cases; contiguous and external dictionary streams; and compression compatibility with the normal LZ4 safe decompressor.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/lz4/lz4hc_compress.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/lzo/Makefile -->
# sources/distributed-fs/ceph-client/lib/lzo/Makefile

## Purpose
`lib/lzo/Makefile` wires the kernel LZO library objects into Kbuild. It groups the shared compressor implementations into a composite compression object and the safe decompressor into a composite decompression object, then includes them conditionally based on kernel configuration.

## Important APIs, types, and functions
The file defines `lzo_compress-objs := lzo1x_compress.o lzo1x_compress_safe.o` and `lzo_decompress-objs := lzo1x_decompress_safe.o`. It adds `lzo_compress.o` under `CONFIG_LZO_COMPRESS` and `lzo_decompress.o` under `CONFIG_LZO_DECOMPRESS`.

## Control flow
There is no runtime control flow. At build time, Kbuild uses the composite-object variables to link the unsafe and safe compressor translation units into `lzo_compress.o`, and the decompressor translation unit into `lzo_decompress.o`. The parent `lib/Makefile` descends into this directory when the corresponding config symbols are enabled.

## State and persistence
The file does not manage runtime state. Its persistent effect is the build graph: enabling or disabling the config symbols changes which exported LZO symbols exist in the kernel image or module build.

## Dependencies and integration points
This Makefile integrates with the public prototypes in `include/linux/lzo.h`, the compression users in `crypto/lzo.c`, `crypto/lzo-rle.c`, Btrfs, SquashFS, and boot decompression code. It relies on Kbuild naming conventions where `foo-objs` lists the object files linked into `foo.o`.

## Risks and test signals
Risks are mostly build-configuration risks: omitting `lzo1x_compress_safe.o` would break callers of `_safe` compressor symbols, and omitting the decompressor object would break all LZO decode users. Test signals are `CONFIG_LZO_COMPRESS=y/m` producing both `lzo1x_1_compress*` and `lzorle1x_1_compress*` symbols, `CONFIG_LZO_DECOMPRESS=y/m` producing `lzo1x_decompress_safe`, and allmodconfig or crypto compression self-tests linking without unresolved symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/lzo/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/lzo/lzo1x_compress.c -->
# sources/distributed-fs/ceph-client/lib/lzo/lzo1x_compress.c

## Purpose
`lzo1x_compress.c` implements the kernel LZO1X-1 compressor and LZO-RLE compressor. It is designed to be included twice: once directly for the normal unchecked-output compressor symbols and once through `lzo1x_compress_safe.c` with macros that add output-capacity checks and rename the exported functions with a `_safe` suffix.

## Important APIs, types, and functions
The exported functions after macro expansion are `lzo1x_1_compress()`, `lzorle1x_1_compress()`, `lzo1x_1_compress_safe()`, and `lzorle1x_1_compress_safe()`. The private engines are `lzo1x_1_do_compress()` and `lzogeneric1x_1_compress()` after `LZO_SAFE()` name mapping. The caller supplies `wrkmem`, interpreted as a `lzo_dict_t` dictionary with `D_SIZE` entries. Important constants come from `lzodefs.h`: match classes M1-M4, dictionary hash size, maximum offsets, and zero-run lengths.

## Control flow
The generic wrapper optionally writes the LZO-RLE version marker, then processes the input in chunks no larger than the M4 maximum offset range. For each chunk it zeroes the hash dictionary and calls the inner compressor. The inner loop scans the input, hashes four-byte sequences, emits literal runs accumulated since the previous match, detects optional zero runs for the RLE bitstream, computes match length with architecture-specific word comparisons and count-trailing/leading-zero helpers, and encodes the match as M2, M3, or M4 based on distance and length. It then records the post-match literal state in `state_offset`. At the end, remaining literals are emitted and the LZO end marker is appended.

## State and persistence
Compression state is local to each call except for caller-provided output length and work memory. `*out_len` is both input capacity for safe builds and output length on success. `wrkmem` is cleared per chunk and does not persist useful state across calls. The direct build sets `HAVE_OP(x)` to true, so it relies on callers providing worst-case output capacity; the safe inclusion checks `op_end - op` before each write and returns `LZO_E_OUTPUT_OVERRUN`.

## Dependencies and integration points
The file depends on `linux/lzo.h`, `linux/unaligned.h`, `lzodefs.h`, Kbuild's paired safe wrapper, and GPL symbol exports. It integrates with crypto compression (`crypto/lzo.c` and `crypto/lzo-rle.c`), filesystem compressors, and boot tooling that expects the Linux LZO block format plus optional versioned RLE extension.

## Risks and test signals
Risk is concentrated in output bounds for the non-safe build, match-length scanning near `ip_end`, versioned RLE ambiguity avoidance for specific M4 distances and lengths, and architecture-specific unaligned/ctz paths. The compressor must also keep the v0 and v1 bitstreams distinguishable. Test signals include round trips for empty, tiny, incompressible, repetitive, long literal, long match, and long zero-run inputs; explicit safe-output-overrun tests; validating v0 and v1 streams through `lzo1x_decompress_safe()`; and comparison with known crypto test vectors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/lzo/lzo1x_compress.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/lzo/lzo1x_compress_safe.c -->
# sources/distributed-fs/ceph-client/lib/lzo/lzo1x_compress_safe.c

## Purpose
`lzo1x_compress_safe.c` builds the bounded-output variant of the LZO compressor by defining safety macros and including `lzo1x_compress.c`. This avoids duplicating the compressor algorithm while producing `_safe` entry points that honor the caller's destination length.

## Important APIs, types, and functions
This file defines `LZO_SAFE(name) name##_safe` and `HAVE_OP(x) ((size_t)(op_end - op) >= (size_t)(x))`, then includes the main compressor source. As a result, the generated exported symbols are `lzo1x_1_compress_safe()` and `lzorle1x_1_compress_safe()`. All helper functions from the included source are renamed consistently through the same macro.

## Control flow
The runtime control flow is inherited from `lzo1x_compress.c`. The important behavioral difference is that every `NEED_OP(x)` in the included file becomes a real capacity check against `op_end`. On failure, control jumps to the included source's `output_overrun` label and returns `LZO_E_OUTPUT_OVERRUN`.

## State and persistence
The safe object maintains no additional state beyond the included compressor's local variables and caller work memory. It treats `*out_len` as the destination capacity on entry and rewrites it to the produced compressed length on success. On output overrun, callers should treat destination contents as incomplete.

## Dependencies and integration points
The file is tightly coupled to the macro structure of `lzo1x_compress.c`; changes to helper names or output-check conventions there affect this object. It is linked into `lzo_compress.o` by `lib/lzo/Makefile` and is the variant used by crypto front ends that cannot assume worst-case destination sizing.

## Risks and test signals
The main risk is macro-inclusion fragility: adding a new output write in `lzo1x_compress.c` without `NEED_OP()` would silently bypass safe bounds here. Another risk is divergence between direct and safe symbol behavior beyond capacity handling. Test signals are deliberate tiny output buffers returning `LZO_E_OUTPUT_OVERRUN`, adequate worst-case buffers producing streams byte-compatible with the normal compressor for the same version, and build checks that both safe symbols export under `CONFIG_LZO_COMPRESS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/lzo/lzo1x_compress_safe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/lzo/lzo1x_decompress_safe.c -->
# sources/distributed-fs/ceph-client/lib/lzo/lzo1x_decompress_safe.c

## Purpose
`lzo1x_decompress_safe.c` implements the kernel's checked LZO1X decompressor, including support for the versioned LZO-RLE zero-run extension. It is the public decode path used for potentially untrusted compressed LZO blocks and returns detailed negative error codes for malformed streams.

## Important APIs, types, and functions
The exported API is `lzo1x_decompress_safe(const unsigned char *in, size_t in_len, unsigned char *out, size_t *out_len)`. Important macros are `HAVE_IP()`, `HAVE_OP()`, `NEED_IP()`, `NEED_OP()`, and `TEST_LB()`, which enforce input availability, output capacity, and lookbehind validity. Constants from `lzodefs.h` define match classes, offsets, markers, and RLE zero-run bounds. Public error codes come from `include/linux/lzo.h`.

## Control flow
The decoder first checks for the optional version marker byte sequence beginning with `17`, then handles an initial literal run if present. The main loop reads a control byte and dispatches by range: values below 16 represent literal runs or short matches depending on `state`; values 64 and above encode M2 matches; values 32..63 encode M3 matches with optional extended length; lower marker values encode M4 matches or, in versioned streams, RLE zero-run instructions. After each match, the low bits describe how many literal bytes follow immediately, and the decoder copies those via the `match_next` path. The end-of-stream marker is detected when an M4-style match position equals the current output pointer.

## State and persistence
All state is per call: `ip`, `op`, `state`, `next`, match position, and the caller-provided output capacity. `*out_len` is updated to bytes produced on success and on error paths. There is no persistent dictionary between calls; lookbehind references must stay within the current output buffer.

## Dependencies and integration points
The file depends on `linux/lzo.h`, unaligned helpers, `lzodefs.h`, and optionally module exports unless compiled with `STATIC`. It is used by crypto LZO and LZO-RLE wrappers, Btrfs/SquashFS LZO consumers, and `lib/decompress_unlzo.c` for boot or archive decompression.

## Risks and test signals
The risk surface is malformed compressed input: input overrun, output overrun, lookbehind before output start, integer overflow while accumulating extended 255-length runs, invalid EOF, and version marker ambiguity. RLE support adds a special case for marker patterns that must only decode when the bitstream version is nonzero. Test signals include all negative `LZO_E_*` paths, successful decode of legacy and RLE streams, zero-run lengths at minimum and maximum boundaries, match copies with small overlapping distances, extended literal/match lengths near `MAX_255_COUNT`, and `LZO_E_INPUT_NOT_CONSUMED` when trailing bytes remain after EOF.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/lzo/lzo1x_decompress_safe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/lzo/lzodefs.h -->
# sources/distributed-fs/ceph-client/lib/lzo/lzodefs.h

## Purpose
`lzodefs.h` is the private constants and architecture helper header for the kernel LZO implementation. It defines copy primitives, architecture feature switches, match-class constants, RLE versioning, and dictionary sizing shared by the compressor and decompressor.

## Important APIs, types, and functions
The header defines `LZO_VERSION` as `1` for the RLE-capable stream format, `COPY4()` and `COPY8()` unaligned copy helpers, `LZO_USE_CTZ32`, `LZO_USE_CTZ64`, and `LZO_FAST_64BIT_MEMORY_ACCESS` feature macros based on architecture configuration. It declares match offset and length ranges for M1, M2, M3, and M4, marker values for each match class, RLE zero-run limits, `lzo_dict_t`, and dictionary hash parameters `D_BITS`, `D_SIZE`, `D_MASK`, and `D_HIGH`.

## Control flow
The header has no standalone control flow. Its macros select compressor and decompressor fast paths at compile time. For example, `COPY8()` uses one 64-bit unaligned copy on x86_64 and arm64, but falls back to two 32-bit copies elsewhere. The ctz/clz feature macros determine how the compressor scans equal bytes and zero runs.

## State and persistence
There is no mutable state. The persistent effect is the binary format contract encoded by match markers, maximum offsets, and the LZO-RLE version. `D_SIZE` determines the compressor work-memory dictionary layout and must remain consistent with `LZO1X_1_MEM_COMPRESS` in `include/linux/lzo.h`.

## Dependencies and integration points
The file relies on kernel unaligned helpers and architecture configuration macros. It is included by `lzo1x_compress.c` and `lzo1x_decompress_safe.c` and aligns with the public LZO API in `include/linux/lzo.h`. The RLE constants also align with `Documentation/staging/lzo.rst` and crypto LZO-RLE test vectors.

## Risks and test signals
Risks include changing marker or offset constants in a way that breaks on-disk or wire compatibility, choosing unsafe copy behavior on strict-alignment architectures, and mismatching dictionary size with caller-allocated work memory. Test signals are cross-architecture builds, byte-for-byte decode of historical LZO streams, RLE stream tests with version marker `1`, compressor memory-size assertions, and sanitizer/fuzz coverage of match classes around every maximum offset and length boundary.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/lzo/lzodefs.h -->
