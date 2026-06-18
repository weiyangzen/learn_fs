# Research: subset-b-006121

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/decompress/huf_decompress.c -->
# sources/distributed-fs/ceph-client/lib/zstd/decompress/huf_decompress.c

## Purpose
Implements the Huffman literal decoder used by the in-kernel Zstandard decompressor. It builds Huffman decode tables from compressed table descriptions, selects either the single-symbol X1 or double-symbol X2 decoder, and decodes both one-stream and four-stream Huffman payloads used by Zstd literals blocks. The file is performance-sensitive: it contains generic C decoders, optional runtime/static BMI2 wrappers, optional x86-64 BMI2 assembly fast-loop hooks, and table-log tuning that favors an 11-bit fast decode table when possible.

## Important APIs, Types, and Functions
The public entry points are `HUF_readDTableX1_wksp()`, `HUF_readDTableX2_wksp()`, `HUF_decompress1X_DCtx_wksp()`, `HUF_decompress1X_usingDTable()`, `HUF_decompress1X1_DCtx_wksp()`, `HUF_decompress1X2_DCtx_wksp()`, `HUF_decompress4X_usingDTable()`, and `HUF_decompress4X_hufOnly_wksp()`. These are consumed by Zstd block decompression when literal sections are Huffman-coded and by dictionary entropy loading.

Key local types include `DTableDesc`, the first word of a `HUF_DTable` carrying `maxTableLog`, `tableType`, and `tableLog`; `HUF_DEltX1`, a single-symbol decode table entry with `nbBits` and `byte`; `HUF_DEltX2`, a double-symbol entry with a packed two-byte sequence, consumed bit count, and decoded length; `HUF_DecompressFastArgs`, the shared state passed to C or assembly four-stream fast loops; and workspace structures `HUF_ReadDTableX1_Workspace` and `HUF_ReadDTableX2_Workspace`.

Notable helpers are `HUF_selectDecoder()`, which estimates X1 versus X2 cost from compressed/decompressed size ratio; `HUF_rescaleStats()`, which raises small table logs toward `HUF_DECODER_FAST_TABLELOG`; `HUF_initFastDStream()` and `HUF_initRemainingDStream()`, which bridge between the custom fast-loop bit representation and normal `BIT_DStream_t`; and the `HUF_DGEN()` wrapper macro, which emits BMI2 and default variants when runtime BMI2 dispatch is enabled.

## Control Flow
Table construction begins by calling `HUF_readStats_wksp()` to parse Huffman weights and rank counts. X1 construction optionally rescales weights to a target table log, sorts symbols by weight, writes `DTableDesc.tableType = 0`, and fills decode-table ranges with repeated single-symbol entries. X2 construction computes sorted symbols, rank starts, and rank-value columns, writes `DTableDesc.tableType = 1`, and fills table ranges either with a first-level single symbol or with second-level entries that can emit two symbols per lookup.

Decoding has two shape variants. `1X` decoders initialize one `BIT_DStream_t`, decode until the requested output size is filled, and then require `BIT_endOfDStream()`. `4X` decoders parse the six-byte jump table, split compressed input into four bitstreams, split output into four near-equal segments, decode each segment, and validate all streams ended exactly. Fast 4X paths first call `HUF_DecompressFastArgs_init()`, require 64-bit little-endian execution, an 11-bit table log, enough input per stream, and non-tiny output, then run the C or assembly fast loop and finish the tail through the normal stream decoder. If the fast initializer returns zero, callers fall back to the generic decoder.

The universal selectors handle edge cases before table decoding: zero output is rejected, `cSrcSize == dstSize` is treated as uncompressed copy in 1X mode, `cSrcSize == 1` is treated as RLE in 1X mode, and malformed 4X jump tables or segment/output overflows return corruption errors. Compile-time macros can force only X1 or only X2, and runtime flags can disable BMI2 assembly or fast decode.

## State and Persistence Behavior
The file owns no persistent external state. State is held in caller-provided decode tables, temporary workspaces, local bitstream containers, and output buffers. `HUF_DTable` carries reusable entropy tables across literal blocks or dictionaries, with the first table word serving as a descriptor. The fast path mutates only `HUF_DecompressFastArgs` and caller buffers. Dictionary entropy persistence is external: this file builds the Huffman table that `zstd_ddict.c` and `zstd_decompress.c` store in `ZSTD_entropyDTables_t`.

## Dependencies and Integration Points
The implementation depends on Zstd common helpers for memory, bitstreams, FSE stats parsing, Huffman declarations, errors, CPU feature attributes, and bit utilities. It integrates primarily through `../common/huf.h` declarations and is called from Zstd literal-block decompression and dictionary entropy loading. CPU-feature integration is controlled by `DYNAMIC_BMI2`, `ZSTD_ENABLE_ASM_X86_64_BMI2`, `HUF_flags_bmi2`, `HUF_flags_disableAsm`, and `HUF_flags_disableFast`.

## Risks and Edge Cases
The high-risk areas are bounds in the 4X jump-table parser, output-segment boundary checks, the fast-loop assumptions about 64-bit little-endian layout, strict-aliasing avoidance through `void*` table pointers, and bitstream tail validation after unrolled loops. X2 decoding writes up to two bytes per table lookup, so last-symbol handling and segment-end checks are critical. Table construction is sensitive to table-log limits, workspace size, rank math, and rescaling correctness. Any divergence between C and assembly fast loops can become architecture-specific corruption, so the disable-fast and disable-assembly flags are important diagnostic controls.

## Test Signals
Useful tests include Zstd frame decompression with Huffman literals across both 1X and 4X block modes, malformed jump tables with overflowing stream lengths, tiny literals that force fallback, dictionaries with precomputed Huffman tables, forced X1/X2 builds, BMI2-enabled and BMI2-disabled runs, `HUF_flags_disableFast` and `HUF_flags_disableAsm` comparisons, and fuzzing compressed literal payloads for `corruption_detected` rather than overread/overwrite. Cross-endian and 32-bit build coverage is valuable because fast decode is intentionally bypassed there.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/decompress/huf_decompress.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/decompress/zstd_ddict.c -->
# sources/distributed-fs/ceph-client/lib/zstd/decompress/zstd_ddict.c

## Purpose
Owns the internal representation and lifecycle of decompression dictionaries (`ZSTD_DDict`). A DDict is a digested dictionary object that may either copy or reference dictionary bytes, parse a conformant Zstd dictionary header, prebuild entropy decode tables, expose dictionary metadata, and quickly seed a decompression context with dictionary history and entropy.

## Important APIs, Types, and Functions
The central private type is `struct ZSTD_DDict_s`, containing `dictBuffer`, `dictContent`, `dictSize`, parsed entropy tables, `dictID`, `entropyPresent`, and custom allocator state. Public or internal entry points include `ZSTD_DDict_dictContent()`, `ZSTD_DDict_dictSize()`, `ZSTD_copyDDictParameters()`, `ZSTD_createDDict_advanced()`, `ZSTD_createDDict()`, `ZSTD_createDDict_byReference()`, `ZSTD_initStaticDDict()`, `ZSTD_freeDDict()`, `ZSTD_estimateDDictSize()`, `ZSTD_sizeof_DDict()`, and `ZSTD_getDictID_fromDDict()`. Private helpers are `ZSTD_initDDict_internal()` and `ZSTD_loadEntropy_intoDDict()`.

## Control Flow
Creation starts in `ZSTD_createDDict_advanced()`, which validates that custom allocation and free callbacks are paired, allocates a `ZSTD_DDict`, stores allocator state, and delegates to `ZSTD_initDDict_internal()`. Internal initialization either references the caller's dictionary bytes or allocates and copies them, initializes the Huffman table capacity descriptor, and calls `ZSTD_loadEntropy_intoDDict()`. Entropy loading treats `ZSTD_dct_rawContent` as content-only, rejects too-small or wrong-magic input when `ZSTD_dct_fullDict` is required, otherwise accepts non-conformant input as raw content in auto mode. For conformant dictionaries, it reads `dictID` after the magic and calls `ZSTD_loadDEntropy()` to build Huffman and FSE decode tables.

`ZSTD_copyDDictParameters()` is the hot integration path: it copies dict identity, prefix/history pointers, `previousDstEnd`, fuzzing bounds, entropy table pointers, and repeat offsets into a `ZSTD_DCtx`. If the DDict has no parsed entropy, it clears `litEntropy` and `fseEntropy` so frames load entropy from their blocks instead. Static initialization lays out the `ZSTD_DDict` at the start of a caller workspace and, for by-copy mode, stores dictionary bytes immediately after the object, then initializes by reference to that internal copy. Freeing releases the optional copied dictionary buffer and the DDict itself through the stored custom allocator.

## State and Persistence Behavior
`ZSTD_DDict` persists dictionary bytes when loaded by copy and only borrows them when loaded by reference or static workspace. Borrowed dictionary content must outlive the DDict. Parsed entropy and `dictID` remain cached for reuse across frames. `ZSTD_copyDDictParameters()` does not clone entropy tables; it points the decompression context at DDict-owned entropy storage, so the DDict must outlive decompression. Static DDicts are not heap-owned and are returned as `const ZSTD_DDict*`; callers must not pass them to heap-free paths unless the broader API contract allows it.

## Dependencies and Integration Points
The file depends on custom allocation helpers, memory utilities, CPU/common headers, FSE and Huffman table definitions, `zstd_decompress_internal.h` for `ZSTD_DCtx` and entropy table layout, and `zstd_ddict.h` for declarations. It integrates with `zstd_decompress.c` through `ZSTD_decompressBegin_usingDDict()`, `ZSTD_DCtx_refDDict()`, multiple-DDict selection, and one-shot `ZSTD_decompress_usingDDict()`. It also depends on `ZSTD_loadDEntropy()` implemented in the decompressor file to parse full dictionary entropy.

## Risks and Edge Cases
The main correctness risks are lifetime mismatches in by-reference mode, allocator-pair mismatches, assuming non-conformant dictionaries have entropy when they are intentionally content-only, and corrupt dictionary headers causing partially initialized DDicts. `ZSTD_initStaticDDict()` requires 8-byte alignment and enough workspace for the object plus optional copy; violations return `NULL`. `ZSTD_copyDDictParameters()` installs pointers into the target context, so freeing or mutating the DDict during decompression can corrupt output. Empty or `NULL` dictionaries normalize to size zero and no entropy.

## Test Signals
Useful signals include round-trip decompression with copied DDicts, by-reference DDicts whose source buffer remains valid, static DDict workspace alignment/size failures, corrupt dictionary magic and too-small full dictionaries, dictionaries with and without entropy sections, custom allocator failure injection, `ZSTD_getDictID_fromDDict()` behavior for raw and conformant dictionaries, and repeated decompressions from the same DDict to prove entropy table reuse.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/decompress/zstd_ddict.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/decompress/zstd_ddict.h -->
# sources/distributed-fs/ceph-client/lib/zstd/decompress/zstd_ddict.h

## Purpose
Declares the private decompression-dictionary bridge used by the Zstd decompressor implementation. It keeps `ZSTD_DDict` internals opaque to most code while exposing the minimal accessors and context-copy hook needed by decompression setup.

## Important APIs, Types, and Functions
The header includes the Zstd dependency header for `size_t` and `<linux/zstd.h>` for public `ZSTD_DDict`, `ZSTD_DCtx`, and dictionary API declarations. It declares `ZSTD_DDict_dictContent()`, `ZSTD_DDict_dictSize()`, and `ZSTD_copyDDictParameters()`. Comments note that public construction, destruction, sizing, and dict-ID functions are declared in `zstd.h`; this header adds only implementation-facing accessors not intended as the broad public ABI.

## Control Flow
There is no executable control flow in the header. It only provides declarations guarded by `ZSTD_DDICT_H`. Runtime behavior is implemented by `zstd_ddict.c`, where the accessors assert a non-null DDict and where `ZSTD_copyDDictParameters()` seeds a `ZSTD_DCtx`.

## State and Persistence Behavior
The header owns no state. It exposes functions that read DDict-owned dictionary content and size, and a function that copies references and entropy pointers into a decompression context. The persistence contract is implicit: DDict storage must remain valid for users that reference its content or entropy tables.

## Dependencies and Integration Points
This header is included by `zstd_ddict.c` and `zstd_decompress.c`. It is the narrow interface between the DDict implementation and the frame/stream decompressor. It depends on public Linux Zstd declarations rather than defining `ZSTD_DDict` itself, preserving opacity outside the dictionary implementation.

## Risks and Edge Cases
Risk is mostly interface drift: if `ZSTD_DDict` fields or `ZSTD_DCtx` dictionary setup semantics change in `zstd_ddict.c` or `zstd_decompress_internal.h`, the prototypes here may no longer express enough contract for safe use. Because the accessors assert non-null input rather than returning nullable-safe defaults, callers must validate DDict pointers first unless the API explicitly permits `NULL` elsewhere.

## Test Signals
Compile coverage is the primary signal: both dictionary and decompressor translation units should build with this header, and public declarations in `<linux/zstd.h>` must remain compatible. Runtime tests are inherited from `zstd_ddict.c`: DDict creation, context seeding, by-reference lifetime, and dictionary-ID behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/decompress/zstd_ddict.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/decompress/zstd_decompress.c -->
# sources/distributed-fs/ceph-client/lib/zstd/decompress/zstd_decompress.c

## Purpose
Implements the main Zstandard frame decompressor, including context allocation, frame-header parsing, skippable-frame handling, frame-size queries, one-shot and multi-frame decompression, dictionary insertion and DDict selection, bufferless continuation APIs, and buffered streaming decompression. It is the top-level integration point between the public Linux Zstd decompression API and lower-level block, Huffman, FSE, checksum, allocation, and dictionary code.

## Important APIs, Types, and Functions
Context lifecycle APIs include `ZSTD_createDCtx()`, `ZSTD_createDCtx_advanced()`, `ZSTD_initStaticDCtx()`, `ZSTD_freeDCtx()`, `ZSTD_sizeof_DCtx()`, and `ZSTD_estimateDCtxSize()`. Frame introspection APIs include `ZSTD_isFrame()`, `ZSTD_isSkippableFrame()`, `ZSTD_frameHeaderSize()`, `ZSTD_getFrameHeader_advanced()`, `ZSTD_getFrameHeader()`, `ZSTD_getFrameContentSize()`, `ZSTD_findDecompressedSize()`, `ZSTD_getDecompressedSize()`, `ZSTD_findFrameCompressedSize()`, `ZSTD_decompressBound()`, `ZSTD_decompressionMargin()`, `ZSTD_getDictID_fromDict()`, and `ZSTD_getDictID_fromFrame()`.

Decompression APIs include `ZSTD_decompress()`, `ZSTD_decompressDCtx()`, `ZSTD_decompress_usingDict()`, `ZSTD_decompress_usingDDict()`, `ZSTD_decompressBegin()`, `ZSTD_decompressBegin_usingDict()`, `ZSTD_decompressBegin_usingDDict()`, `ZSTD_decompressContinue()`, `ZSTD_nextSrcSizeToDecompress()`, and `ZSTD_nextInputType()`. Streaming APIs include `ZSTD_createDStream()`, `ZSTD_initStaticDStream()`, `ZSTD_createDStream_advanced()`, `ZSTD_freeDStream()`, `ZSTD_DStreamInSize()`, `ZSTD_DStreamOutSize()`, `ZSTD_initDStream_usingDict()`, `ZSTD_initDStream_usingDDict()`, `ZSTD_initDStream()`, `ZSTD_resetDStream()`, `ZSTD_decompressStream()`, and `ZSTD_decompressStream_simpleArgs()`.

Dictionary and parameter APIs include `ZSTD_DCtx_loadDictionary_advanced()`, `ZSTD_DCtx_loadDictionary_byReference()`, `ZSTD_DCtx_loadDictionary()`, `ZSTD_DCtx_refPrefix_advanced()`, `ZSTD_DCtx_refPrefix()`, `ZSTD_DCtx_refDDict()`, `ZSTD_DCtx_setMaxWindowSize()`, `ZSTD_DCtx_setFormat()`, `ZSTD_dParam_getBounds()`, `ZSTD_DCtx_getParameter()`, `ZSTD_DCtx_setParameter()`, and `ZSTD_DCtx_reset()`. Internal helpers include the multiple-DDict open-addressed hash set functions, `ZSTD_decodeFrameHeader()`, `ZSTD_decompressFrame()`, `ZSTD_decompressMultiFrame()`, `ZSTD_loadDEntropy()`, and streaming buffer-size/oversize helpers.

## Control Flow
Frame parsing begins by validating the magic number unless magicless format is selected, distinguishing normal and skippable frames, and decoding frame descriptor fields into `ZSTD_FrameHeader`: window size, block size max, frame content size, dictionary ID, checksum flag, header size, and frame type. Size-query helpers repeatedly parse headers and block headers to skip frames and compute compressed size, decompressed bounds, or decompression margin.

One-shot decompression enters `ZSTD_decompressMultiFrame()`, optionally maps a DDict to dictionary content, skips skippable frames, initializes the context with raw dict or DDict for each real frame, checks output continuity, and calls `ZSTD_decompressFrame()`. `ZSTD_decompressFrame()` decodes the header, optionally shrinks max block size from a parameter, loops over block headers, dispatches compressed blocks to `ZSTD_decompressBlock_internal()`, raw blocks to `ZSTD_copyRawBlock()`, RLE blocks to `ZSTD_setRleBlock()`, updates checksum state, enforces frame content size, verifies frame checksum, advances input pointers, and returns produced output size.

The bufferless continuation API is a state machine over `ZSTDds_getFrameHeaderSize`, `ZSTDds_decodeFrameHeader`, `ZSTDds_decodeBlockHeader`, `ZSTDds_decompressBlock`, `ZSTDds_decompressLastBlock`, `ZSTDds_checkChecksum`, `ZSTDds_decodeSkippableHeader`, and `ZSTDds_skipFrame`. Callers must provide exactly the byte count requested by `ZSTD_nextSrcSizeToDecompress()`, except raw blocks may stream partial input through `ZSTD_nextSrcSizeToDecompressWithInputSize()`. Each step updates `expected`, block type, checksum, decoded size, and history pointers.

`ZSTD_decompressStream()` wraps the continuation API with buffered input/output management. Its higher-level stream stages are `zdss_init`, `zdss_loadHeader`, `zdss_read`, `zdss_load`, and `zdss_flush`. It accumulates frame headers, uses a single-pass shortcut when the full frame and output capacity are available, enforces max window size, allocates or resizes input/output ring buffers, reads directly when enough input is available, otherwise loads into `inBuff`, flushes `outBuff` to the caller, uses a hostage byte to avoid returning frame completion before all output is flushed, and tracks no-forward-progress calls.

## State and Persistence Behavior
`ZSTD_DCtx` is the persistent state holder. It stores format and decompression parameters, custom allocator, current DDict or local DDict, multiple-DDict hash set, input/output streaming buffers, frame parameters, checksum state, entropy tables, repeat offsets, prefix/history pointers, expected input size, frame/block stage, streaming stage, decoded and processed sizes, oversized-buffer duration, and no-forward-progress counter. Session reset clears frame and streaming state; parameter reset also clears dictionaries and restores defaults. Static contexts borrow caller workspace and cannot allocate features such as multiple-DDict hash sets.

Dictionary state can be installed as raw content, full dictionary entropy, local copied DDict, by-reference DDict, one-shot prefix, or multiple referenced DDicts selected by frame `dictID`. `ZSTD_loadDEntropy()` parses full dictionary entropy tables and repeat offsets, while `ZSTD_copyDDictParameters()` installs prebuilt entropy from a DDict. History pointers (`prefixStart`, `virtualStart`, `dictEnd`, `previousDstEnd`) persist across blocks within a frame and are refreshed by continuity checks and inserted dictionaries.

Streaming buffers persist between calls and may be resized when a new frame needs larger buffers or when prior buffers remain oversized for too long. Stable output buffer mode stores `expectedOutBuffer` and rejects later calls with a changed output buffer during the same session. Checksum state persists from frame header decode until checksum verification.

## Dependencies and Integration Points
The file depends on Zstd common allocation, memory, error, internal-format, bit, FSE, and HUF helpers; Linux xxhash for frame checksums; `zstd_decompress_internal.h` for `ZSTD_DCtx`; `zstd_ddict.h` for DDict access; and `zstd_decompress_block.h` for compressed block decoding. It is the public API implementation used by Ceph/client kernel code that needs Zstd decompression, and it integrates directly with `zstd_ddict.c`, `huf_decompress.c`, FSE tables, and block sequence/literal decoding.

## Risks and Edge Cases
Risk concentrates around bounds and state transitions: frame header partial reads, skippable-frame length overflow, block compressed-size validation, in-place decompression output limiting, raw-block partial streaming, content-size and checksum enforcement, max-window rejection, and stable-output-buffer invariants. Multiple-DDict support uses open addressing and treats dict ID zero as empty/terminating during lookup, so dictionaries with no usable ID cannot be selected through the hash set. The hash-set probe increments after masking, relying on power-of-two table sizes and later masked uses. Static contexts cannot support allocations needed for multiple DDicts or oversized buffer growth beyond workspace. The no-forward-progress guard is important for callers that repeatedly provide full output or empty input.

## Test Signals
High-value tests include valid frames with and without known content size, multi-frame streams with skippable frames, checksum success and failure, wrong dictionary ID, raw-content dictionaries, full dictionaries with entropy tables, DDict reuse and multiple-DDict selection, in-place decompression margins, raw/RLE/compressed block combinations, max-window and max-block-size parameter rejection, magicless format parsing, stable output buffer mode, static workspace success/failure, partial streaming across every state transition, no-forward-progress errors for full output or empty input, and fuzzing malformed headers/block sizes/skippable lengths for clean Zstd errors rather than memory faults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/decompress/zstd_decompress.c -->
