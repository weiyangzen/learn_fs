# subset-b-000316 Research

Grouped research for the listed Zstandard compression and decompression files. Each section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/lib/compress/zstdmt_compress.c -->
# sources/compression/zstd/lib/compress/zstdmt_compress.c

## Purpose
Implements Zstandard's internal multi-threaded compression backend used by `ZSTD_compress.c` when `nbWorkers > 0`. It owns the worker-thread job graph, input round buffer, output buffer recycling, per-worker `ZSTD_CCtx` reuse, optional long-distance matching sequence generation, frame checksum aggregation, rsyncable job boundaries, and ordered flushing of independently compressed chunks into one valid zstd frame.

## Important APIs, Types, And Functions
The exported internal entry points are `ZSTDMT_createCCtx_advanced()`, `ZSTDMT_freeCCtx()`, `ZSTDMT_sizeof_CCtx()`, `ZSTDMT_initCStream_internal()`, `ZSTDMT_compressStream_generic()`, `ZSTDMT_nextInputSizeHint()`, `ZSTDMT_toFlushNow()`, `ZSTDMT_updateCParams_whileCompressing()`, and `ZSTDMT_getFrameProgression()`. They are declared in `zstdmt_compress.h` and called by the single public compression layer.

Core state lives in `struct ZSTDMT_CCtx_s`: thread pool `factory`, circular job table `jobs`, `bufPool`, `cctxPool`, `seqPool`, active params, target job/prefix sizes, pending input buffer, `roundBuff`, `SerialState`, rsync rolling-hash state, job cursors, frame progress counters, dictionary handles, allocator, and ownership bit for user-provided thread pools. `ZSTDMT_jobDescription` is the per-job shared record protected by `job_mutex`/`job_cond`; it carries input/prefix ranges, output buffer, params, dictionary, frame flags, consumed/compressed byte counters, and checksum-finalization state.

Major helpers include `ZSTDMT_createBufferPool()`/`ZSTDMT_getBuffer()`/`ZSTDMT_releaseBuffer()` for reusable buffers, `ZSTDMT_createCCtxPool()`/`ZSTDMT_getCCtx()`/`ZSTDMT_releaseCCtx()` for per-worker contexts, `ZSTDMT_serialState_reset()`/`ZSTDMT_serialState_genSequences()` for ordered LDM/checksum work, `ZSTDMT_compressionJob()` for worker execution, `ZSTDMT_createCompressionJob()` for job submission, `ZSTDMT_flushProduced()` for ordered output draining, and `ZSTDMT_tryGetInputRange()` for round-buffer reuse without overlapping active jobs or LDM windows.

## Control Flow
Creation validates worker count and custom allocator pairing, creates or adopts a `POOL_ctx`, rounds the job table size to a power of two, initializes pools, and initializes serial-state locks. `ZSTDMT_initCStream_internal()` resizes pools if `nbWorkers` changed, waits out unfinished prior jobs, clamps job size, computes overlap and target section sizes, allocates the round buffer, initializes dictionary or prefix state, and resets LDM/checksum serial state.

`ZSTDMT_compressStream_generic()` is the streaming driver. It first rejects new `continue` input after frame end has started, obtains a free region from the round buffer, optionally scans for an rsync synchronization point, copies user input into `inBuff`, converts `end` to `flush` when unread input remains, creates a compression job when the buffer is full or a flush/end is requested, then calls `ZSTDMT_flushProduced()` to copy available compressed data into the caller's output buffer. If no input progress was made, flushing is allowed to block on the oldest job condition variable.

Workers run `ZSTDMT_compressionJob()`. Each worker borrows a `ZSTD_CCtx`, output buffer, and optional raw sequence buffer, performs the serial LDM/checksum step in job ID order, initializes compression with either the first-job dictionary/CDict or a raw prefix, suppresses frame checksum and LDM inside chunk jobs, compresses the job in `4 * ZSTD_BLOCKSIZE_MAX` pieces, publishes partial compressed size and consumed progress under the job mutex, and finally releases borrowed resources and signals completion.

Output ordering is enforced by `doneJobID`: `ZSTDMT_flushProduced()` only inspects the oldest unfinished job, waits only when requested, handles worker errors by draining all jobs and releasing resources, appends the frame checksum on the final non-first job after worker completion, copies bytes to `ZSTD_outBuffer`, recycles job output buffers, updates global consumed/produced counters, and advances `doneJobID`. `allJobsCompleted` is only set once all jobs are flushed and the frame-ended flag is consistent.

## State And Persistence
The context is long-lived and reusable. Pools retain allocated buffers and contexts between frames, so memory may remain held after a smaller subsequent compression. `roundBuff` also persists and grows as needed. Job slots are reused circularly via `jobIDMask`; mutex and condition objects stay attached to slots while job descriptions are zeroed between uses. Dictionary state is either an internal `cdictLocal`, a referenced external `cdict`, or a raw prefix range. No on-disk persistence exists; all state is heap memory owned by the MT context or an external thread pool.

Thread-shared fields are deliberately narrow: worker-published `consumed` and `cSize` are guarded by each job mutex, serial LDM/checksum state is guarded by `SerialState` locks, and pools have their own mutexes. Input buffers are not recycled until overlap checks prove no active job or LDM window can still read them.

## Dependencies And Integration Points
This file depends on Zstd common allocation, threading, pool, memory, compression internals, LDM, rolling hash, frame checksum, CDict, and error macros. It is compiled meaningfully only when `ZSTD_MULTITHREAD` is available; otherwise `ZSTDMT_createCCtx_advanced()` returns `NULL`. The thread pool API provides `POOL_tryAdd()`, `POOL_resize()`, and optional externally supplied pools. The compressor integrates with public streaming through `ZSTD_compressStream2()`/`ZSTD_compress2()` paths rather than being public API itself.

It also integrates with LDM through `ZSTD_ldm_adjustParameters()`, `ZSTD_ldm_generateSequences()`, and `ZSTD_referenceExternalSequences()`, with dictionaries through `ZSTD_createCDict_advanced()` and `ZSTD_compressBegin_advanced_internal()`, and with frame progress reporting through `ZSTD_frameProgression`.

## Risks And Edge Cases
The main correctness risks are concurrency ordering bugs, buffer lifetime overlap, and job-slot reuse. If `doneJobID`, `nextJobID`, or `jobReady` transitions are mishandled, jobs can be overwritten, output can be flushed out of order, or callers can observe stuck progress. Round-buffer reuse is especially sensitive when wrapping and copying the prefix to the beginning, because active job prefixes and LDM windows must not overlap the candidate range.

Dictionary handling is split between a transient by-copy CDict early in initialization and a later by-reference/raw-prefix setup; changes here can introduce leaks, dangling dictionary references, or compression-ratio regressions. Frame checksum handling is also subtle: chunk jobs disable internal checksums and the main thread appends the combined checksum only when needed. Error paths must call `ZSTDMT_serialState_ensureFinished()` so later jobs do not wait forever for skipped serial work.

Rsyncable boundaries can force a flush before the nominal target size; the constraints around `RSYNC_MIN_BLOCK_SIZE`, rolling hash initialization, and unfinished input must remain aligned with job-size limits. Memory sizing risks include `ZSTD_compressBound(targetSectionSize)`, LDM window slack, 32-bit job-size caps, and buffer-pool expansion freeing existing cached buffers.

## Test Signals
Useful tests include zstd streaming round trips with `nbWorkers` from 1 to `ZSTDMT_NBWORKERS_MAX`, very small and very large job sizes, repeated context reuse with changing worker counts, external and owned thread pools, raw prefixes, full dictionaries, CDicts, checksum on/off, LDM on/off, rsyncable mode, flush/end interleavings, tiny output buffers, and injected worker allocation failures. Thread sanitizer or stress tests should target `ZSTDMT_flushProduced()`, serial LDM ordering, context free while jobs are active, and round-buffer wraparound. Compression determinism and compatibility tests should compare single-threaded and multi-threaded decompression output for the same input/dictionary combinations.
<!-- END_FILE_RESEARCH: sources/compression/zstd/lib/compress/zstdmt_compress.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/lib/compress/zstdmt_compress.h -->
# sources/compression/zstd/lib/compress/zstdmt_compress.h

## Purpose
Declares the internal multi-threaded compression interface used by Zstandard's compression frontend. The header intentionally warns that this is private API, no longer exported for direct application use, and requires `ZSTD_MULTITHREAD` support for context creation to succeed.

## Important APIs, Types, And Constants
The opaque type is `ZSTDMT_CCtx`. Construction and lifetime are handled by `ZSTDMT_createCCtx_advanced(unsigned nbWorkers, ZSTD_customMem cMem, ZSTD_threadPool *pool)`, `ZSTDMT_freeCCtx()`, and `ZSTDMT_sizeof_CCtx()`. Streaming is handled through `ZSTDMT_initCStream_internal()`, `ZSTDMT_compressStream_generic()`, and `ZSTDMT_nextInputSizeHint()`.

Constants bound the implementation: `ZSTDMT_NBWORKERS_MAX` defaults to 64 on 32-bit and 256 on wider targets, `ZSTDMT_JOBSIZE_MIN` defaults to 512 KB, `ZSTDMT_JOBLOG_MAX` is 29 or 30 depending on address width, and `ZSTDMT_JOBSIZE_MAX` is 512 MB or 1024 MB. These constants constrain allocation size, job splitting, and worker fan-out.

Progress and live tuning APIs include `ZSTDMT_toFlushNow()`, `ZSTDMT_updateCParams_whileCompressing()`, and `ZSTDMT_getFrameProgression()`. The init API accepts raw dictionaries, CDicts, content type, full `ZSTD_CCtx_params`, and pledged source size, while asserting at the contract level that callers must pass either a dict or a CDict, not both.

## Control Flow
Callers allocate a context, initialize a frame with `ZSTDMT_initCStream_internal()`, then repeatedly call `ZSTDMT_compressStream_generic()` with a `ZSTD_EndDirective`. The return value is the minimum data still needing flush, zero when fully flushed, or a zstd error code. During an active frame, callers may query immediate flushable bytes, update the subset of compression parameters compatible with the current frame, and inspect progress.

## State And Persistence
The header exposes no fields, so all state is encapsulated in the implementation. The comments document that reused contexts may retain prior allocations even when the next compression does not need them. A supplied `ZSTD_threadPool` is referenced by the MT context but not necessarily owned by it; a `ZSTD_customMem` allocator is threaded through context and pool allocations.

## Dependencies And Integration Points
It includes `zstd_deps.h` for `size_t`, defines `ZSTD_STATIC_LINKING_ONLY` to access advanced parameter types from `zstd.h`, and relies on `ZSTD_inBuffer`, `ZSTD_outBuffer`, `ZSTD_CCtx_params`, `ZSTD_customMem`, `ZSTD_threadPool`, `ZSTD_CDict`, and `ZSTD_frameProgression`. Its direct integration point is `ZSTD_compress.c`, which decides when to route compression through the MT backend.

## Risks And Edge Cases
Because this is private API, accidental external use can bind applications to unstable ABI. Compile-time overrides of worker and job-size limits can create unexpected memory profiles or violate assumptions in `zstdmt_compress.c` if set too aggressively. The dict-vs-CDict exclusivity and context-reuse comments are important caller obligations; violating them can lead to assertion failures or undefined behavior in internal builds.

## Test Signals
Build tests should cover configurations with and without `ZSTD_MULTITHREAD`, with custom limits, and with static linking consumers that include private headers. Runtime tests should verify context creation failure in non-MT builds, successful operation with owned and supplied thread pools in MT builds, and progress/flush hints during streaming.
<!-- END_FILE_RESEARCH: sources/compression/zstd/lib/compress/zstdmt_compress.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/lib/decompress/huf_decompress.c -->
# sources/compression/zstd/lib/decompress/huf_decompress.c

## Purpose
Implements Huffman decompression for zstd/FSE literals. It builds X1 and X2 decoding tables from serialized Huffman weights, selects an appropriate decoder, handles single-stream and four-stream compressed layouts, provides fast 64-bit little-endian decode loops with optional BMI2/assembly acceleration, and falls back to portable bitstream decoders when fast-loop preconditions are not met.

## Important APIs, Types, And Functions
The key public/internal entry points are `HUF_readDTableX1_wksp()`, `HUF_readDTableX2_wksp()`, `HUF_selectDecoder()`, `HUF_decompress1X_DCtx_wksp()`, `HUF_decompress1X_usingDTable()`, `HUF_decompress1X1_DCtx_wksp()`, `HUF_decompress1X2_DCtx_wksp()`, `HUF_decompress4X_usingDTable()`, and `HUF_decompress4X_hufOnly_wksp()`. Force macros can compile only X1 or only X2 decoder paths.

`DTableDesc` overlays the first `HUF_DTable` word and carries max table log, table type, and active table log. X1 table entries are `HUF_DEltX1 { nbBits, byte }`, decoding one output symbol per lookup. X2 entries are `HUF_DEltX2 { sequence, nbBits, length }`, decoding one or two symbols per lookup. `HUF_DecompressFastArgs` is the shared C/assembly contract for fast 4-stream loops: it stores four input pointers, four output pointers, four bit containers, DTable pointer, input lower bound, output end, and stream ends.

Fast-loop helpers include `HUF_DecompressFastArgs_init()`, `HUF_initFastDStream()`, `HUF_initRemainingDStream()`, `HUF_decompress4X1_usingDTable_internal_fast()`, and `HUF_decompress4X2_usingDTable_internal_fast()`. Portable decoders are built around `BIT_DStream_t`, `BIT_initDStream()`, `BIT_reloadDStream()`, and `BIT_endOfDStream()`.

## Control Flow
For compressed streams that include a Huffman table, the DCtx workspace wrappers first read table weights through `HUF_readStats_wksp()`, build either an X1 or X2 DTable, advance past the table header, and decode the remaining payload. For prebuilt tables, `HUF_decompress1X_usingDTable()` and `HUF_decompress4X_usingDTable()` inspect `DTableDesc.tableType` and route to the matching X1/X2 implementation.

X1 table building optionally rescales weights up to the fast decoder table log, computes rank starts and sorted symbols, and fills repeated table ranges in weight order with specialized loops for lengths 1, 2, 4, 8, and larger. X2 table building sorts symbols by weight, constructs rank value columns for second-level decoding, and fills entries that can emit either one symbol or a two-symbol sequence.

Single-stream decode initializes one bitstream and decodes until the requested output size is reached, then verifies end-of-stream. Four-stream decode reads a 6-byte jump table, splits compressed input into four independent streams, divides output into four nearly equal segments, decodes all streams in lockstep when possible, finishes each stream individually, and verifies that each bitstream ended exactly.

The fast 4-stream path is attempted only for 64-bit little-endian targets, non-empty output, source sizes large enough for four 8-byte bit containers, table log `HUF_DECODER_FAST_TABLELOG`, and output segments large enough to benefit. If init returns zero, the implementation uses the portable fallback. With dynamic BMI2, BMI2-specific wrappers are called only when flags say the CPU supports it; assembly is selected unless disabled by flags and when `ZSTD_ENABLE_ASM_X86_64_BMI2` conditions are met.

## State And Persistence
The file persists no heap state. Decode tables are caller-owned `HUF_DTable` buffers. Temporary table-building state lives in caller-provided workspaces (`HUF_ReadDTableX1_Workspace`, `HUF_ReadDTableX2_Workspace`). Fast-loop state is stored in stack-local `HUF_DecompressFastArgs` and written back from C or assembly loops before finishing through portable bitstream code.

## Dependencies And Integration Points
Dependencies include zstd common memory/dependency wrappers, compiler attributes, bitstream primitives, FSE/HUF table formats, error macros, zstd internal constants, and bit utilities such as high-bit and trailing-zero counts. The amd64 assembly file provides optional implementations of `HUF_decompress4X1_usingDTable_internal_fast_asm_loop()` and `HUF_decompress4X2_usingDTable_internal_fast_asm_loop()` using the exact `HUF_DecompressFastArgs` field layout.

This file integrates into zstd decompression literal-block handling through `huf.h` declarations. It must accept special encodings where `cSrcSize == dstSize` means uncompressed literals and `cSrcSize == 1` means RLE in the one-stream wrapper.

## Risks And Edge Cases
The highest risks are bounds errors in four-stream split handling and fast-loop state reconstruction. Jump table lengths can overflow or produce stream ranges shorter than the fast path expects; these are guarded by length checks but remain critical fuzz targets. The fast loop relies on table log 11, little-endian 64-bit loads, monotonic input pointers, and output segment limits; mismatches must cleanly return zero or corruption errors.

X2 decoding has tricky final-symbol behavior because a table entry may contain two symbols when only one byte remains. `HUF_decodeLastSymbolX2()` intentionally clamps bit consumption in this case. Table construction also has dense rank arithmetic; off-by-one errors in `rankStart`, `rankVal`, or rescaling can create wrong decodes that may only appear with unusual symbol distributions.

Compile-time force flags, dynamic BMI2, static BMI2, `HUF_flags_disableAsm`, and `HUF_flags_disableFast` create many dispatch combinations. The assembly contract is fragile because changing `HUF_DecompressFastArgs` layout or table entry packing without updating assembly breaks accelerated builds.

## Test Signals
Tests should cover one-stream and four-stream blocks, X1 and X2 selected by `HUF_selectDecoder()`, prebuilt-DTable decode, table-read workspace size failures, uncompressed/RLE shortcuts, tiny outputs, malformed jump tables, truncated streams, large 128 KB literal blocks, and randomized valid Huffman distributions. Matrix coverage should include fast enabled/disabled, assembly enabled/disabled, dynamic BMI2 on/off, forced X1/X2 builds, 32-bit builds where the fast path must be bypassed, big-endian simulation if available, and fuzzing of serialized Huffman headers.
<!-- END_FILE_RESEARCH: sources/compression/zstd/lib/decompress/huf_decompress.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/lib/decompress/huf_decompress_amd64.S -->
# sources/compression/zstd/lib/decompress/huf_decompress_amd64.S

## Purpose
Provides x86-64 BMI2 assembly implementations of the Huffman four-stream fast decode loops used by `huf_decompress.c`. It accelerates the fixed table-log fast path for X1 and X2 decoders while leaving argument setup, final stream completion, and corruption validation in C.

## Important Symbols And Macros
The exported hidden symbols are `HUF_decompress4X1_usingDTable_internal_fast_asm_loop`, `_HUF_decompress4X1_usingDTable_internal_fast_asm_loop`, `HUF_decompress4X2_usingDTable_internal_fast_asm_loop`, and `_HUF_decompress4X2_usingDTable_internal_fast_asm_loop`. Both underscored and non-underscored labels are emitted to satisfy Darwin and ELF naming conventions.

The file includes `portability_macros.h` for symbol visibility and CET branch macros. `LOCAL_LABEL()` abstracts Darwin versus ELF private-label syntax. Register aliases map four output pointers, four input pointers, four bit containers, the DTable pointer, and an output limit to named registers. The loops use BMI2 instructions such as `shrxq` and `shlxq`, plus `bsfq` for consumed-bit counting.

## Control Flow
Each function starts with `ZSTD_CET_ENDBRANCH`, emits CFI unwind metadata, saves all general-purpose registers, reads the single `HUF_DecompressFastArgs*` argument from `%rdi` on System V or `%rcx` on Windows, loads `ip[]`, `op[]`, `bits[]`, and `dt`, and stores bounds values on the stack.

The X1 loop computes a safe `olimit` from the remaining output bytes in stream 4 divided by 5 and remaining input bytes divided by 7. It exits if no full iteration is safe or if input pointers are no longer ordered. Each iteration performs five table lookups per stream from the top 11 bits, writes one byte per lookup, reloads bit containers according to trailing-zero counts, advances outputs by five, and repeats until `op3` reaches the computed limit.

The X2 loop computes safe iterations from all four output segment ends divided by 10 and input bytes divided by 7. Each decode lookup reads a 32-bit DTable entry, writes up to two output bytes, shifts the bit container by encoded `nbBits`, and advances the output pointer by encoded length. After five lookups per stream, it reloads all bit containers and loops until the safe limit is reached.

On exit, both functions restore stack temporaries, write updated `ip[]`, `op[]`, and `bits[]` back into `HUF_DecompressFastArgs`, restore all registers, and return to C. The C caller then validates stream positions and completes remaining bytes with portable bitstream decoders.

## State And Persistence
No persistent state or heap allocation exists. The only state transfer is through the `HUF_DecompressFastArgs` memory layout defined in `huf_decompress.c`. The assembly deliberately preserves all registers for a conservative ABI boundary and assumes no red zone.

## Dependencies And Integration Points
The file is guarded by `ZSTD_ENABLE_ASM_X86_64_BMI2`, so it is only active when the build enables this optimized path. It integrates directly with `HUF_decompress4X1_usingDTable_internal_fast()` and `HUF_decompress4X2_usingDTable_internal_fast()`, which have already validated that the machine is little-endian 64-bit, the table log is the fast decoder log, and enough input/output exists for the loop.

ELF builds emit `.note.GNU-stack` to avoid executable-stack markings. There is also an aarch64 GNU property note inside an ELF/aarch64 guard because this file may be assembled empty on that target and still needs BTI/PAC metadata.

## Risks And Edge Cases
The central risk is ABI and structure-layout coupling. Any change to `HUF_DecompressFastArgs` field order, DTable entry packing, or fast decoder table log must be mirrored here. The loops rely on BMI2 instruction availability; incorrect dispatch can crash with illegal instructions. Bounds are conservative but manual: the safe-iteration math must keep input reads above `ilowest` and output writes within the four output segments.

Portability risks include assembler syntax differences, Windows versus System V argument registers, CFI correctness, CET branch support, and Darwin symbol prefixes. Because the loop exits before finishing streams, C-side reconstruction of `BIT_DStream_t` must continue to agree with how this assembly reloads bit containers and counts consumed bits.

## Test Signals
Build tests should assemble this file on ELF and Darwin x86-64 BMI2 targets and verify non-x86 targets tolerate the guarded empty body. Runtime tests should compare decompression output with `HUF_flags_disableAsm` versus assembly enabled across X1/X2 table types, random literal blocks, corrupted jump tables, short streams that force fallback, and CPU feature dispatch modes. Sanitizer/fuzzer signal is strongest when exercising boundaries where the loop exits and C finishing code resumes.
<!-- END_FILE_RESEARCH: sources/compression/zstd/lib/decompress/huf_decompress_amd64.S -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/lib/decompress/zstd_ddict.c -->
# sources/compression/zstd/lib/decompress/zstd_ddict.c

## Purpose
Implements the internals of `ZSTD_DDict`, the pre-digested decompression dictionary object. It owns dictionary content copying or referencing, parses zstd dictionary headers and entropy tables, exposes dictionary metadata to decompression contexts, and implements allocation, static initialization, sizing, and ID lookup for decompression dictionaries.

## Important APIs, Types, And Functions
`struct ZSTD_DDict_s` contains `dictBuffer`, `dictContent`, `dictSize`, preloaded `ZSTD_entropyDTables_t entropy`, `dictID`, `entropyPresent`, and allocator `cMem`. Accessors `ZSTD_DDict_dictContent()` and `ZSTD_DDict_dictSize()` expose internal dictionary bytes to other decompression code.

`ZSTD_copyDDictParameters()` copies dictionary identity, prefix/window pointers, previous-destination pointer, and optional entropy table pointers from a DDict into a `ZSTD_DCtx`. `ZSTD_loadEntropy_intoDDict()` parses dictionary magic, dict ID, and decompression entropy tables. `ZSTD_initDDict_internal()` handles by-copy versus by-reference setup and initializes the HUF table sentinel before entropy loading.

Public constructors and lifetime functions include `ZSTD_createDDict_advanced()`, `ZSTD_createDDict()`, `ZSTD_createDDict_byReference()`, `ZSTD_initStaticDDict()`, `ZSTD_freeDDict()`, `ZSTD_estimateDDictSize()`, `ZSTD_sizeof_DDict()`, and `ZSTD_getDictID_fromDDict()`.

## Control Flow
Dynamic construction validates that custom alloc/free are either both present or both absent, allocates the DDict object, stores allocator state, then calls the internal initializer. The initializer either references the caller dictionary directly or allocates/copies it into `dictBuffer`, records size/content pointers, initializes the HUF table first entry, and parses entropy unless the caller explicitly requested raw content.

Entropy loading treats empty/small dictionaries and non-magic dictionaries as content-only when `ZSTD_dct_auto` allows it. If `ZSTD_dct_fullDict` is requested, those same cases are dictionary corruption. For valid zstd dictionary magic, it reads the 32-bit dict ID after the frame ID field and calls `ZSTD_loadDEntropy()` to populate LL/ML/OF/HUF tables and repeat offsets, then marks `entropyPresent`.

Static initialization validates 8-byte alignment, checks that the supplied buffer can hold the DDict and optional dictionary copy, places copied bytes immediately after the object when requested, then delegates to the same internal initializer by reference. Freeing releases the owned dictionary buffer if any and then the object itself; static DDicts must not be passed to the dynamic free path unless they were dynamically allocated.

## State And Persistence
DDict state is immutable after initialization except for object destruction. `dictBuffer` is non-null only for owned by-copy dictionaries; `dictContent` may point into owned memory, caller memory, or static-buffer trailing memory. Entropy tables live inside the DDict and are shared by pointer into a `ZSTD_DCtx` during decompression. There is no persistence outside process memory.

`ZSTD_copyDDictParameters()` mutates a decompression context by installing dictionary range pointers and entropy table pointers. If entropy is absent, it clears `litEntropy` and `fseEntropy`, telling the decompressor to use frame-provided or default entropy instead.

## Dependencies And Integration Points
The file depends on custom allocation helpers, zstd memory wrappers, CPU feature declarations, low-level endian helpers, FSE/HUF static interfaces, decompression internals, `zstd_ddict.h`, and optional legacy support headers. It integrates with `ZSTD_DCtx` internals through `zstd_decompress_internal.h`, especially prefix/window fields and entropy table pointer fields.

DDict creation APIs are declared publicly in `zstd.h`, while the internal content/size/copy helpers are declared in `zstd_ddict.h`. Dictionary parsing depends on common constants such as `ZSTD_MAGIC_DICTIONARY`, `ZSTD_FRAMEIDSIZE`, and `ZSTD_loadDEntropy()`.

## Risks And Edge Cases
By-reference DDicts rely on caller-owned dictionary memory outliving the DDict and any decompression using it. Static DDict initialization requires 8-byte-aligned storage and exact sizing; misuse can return `NULL` or create lifetime hazards if later freed incorrectly. The distinction between `ZSTD_dct_auto`, `ZSTD_dct_fullDict`, and `ZSTD_dct_rawContent` is security-relevant because malformed dictionaries are either accepted as raw content or rejected as corruption depending on caller intent.

Entropy table pointers copied into `ZSTD_DCtx` point back into the DDict. A DCtx must not keep using those pointers after the DDict is freed. Fuzzing-only dictionary range fields are updated under `FUZZING_BUILD_MODE_UNSAFE_FOR_PRODUCTION`; tests that inspect those fields depend on compile mode.

## Test Signals
Tests should create DDicts by copy, by reference, with custom allocators, with static buffers, with empty dictionaries, raw-content dictionaries, malformed full dictionaries, and valid full dictionaries with entropy tables. They should verify dictionary ID extraction, memory-size estimates, `ZSTD_sizeof_DDict()`, null-free/null-size behavior, DCtx parameter copying with and without entropy, allocator failure cleanup, and lifetime behavior for by-reference dictionaries.
<!-- END_FILE_RESEARCH: sources/compression/zstd/lib/decompress/zstd_ddict.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/lib/decompress/zstd_ddict.h -->
# sources/compression/zstd/lib/decompress/zstd_ddict.h

## Purpose
Declares the decompression-side internal helpers for `ZSTD_DDict`. The public constructor/destructor/sizing APIs are declared in `zstd.h`; this header adds the private accessors and DCtx-copy helper needed by decompression internals.

## Important APIs And Types
The header includes `zstd_deps.h` for `size_t` and `zstd.h` for `ZSTD_DDict`, `ZSTD_DCtx`, and public DDict prototypes. It declares `ZSTD_DDict_dictContent(const ZSTD_DDict*)`, `ZSTD_DDict_dictSize(const ZSTD_DDict*)`, and `ZSTD_copyDDictParameters(ZSTD_DCtx*, const ZSTD_DDict*)`.

The comments enumerate the public functions already declared elsewhere: `ZSTD_createDDict()`, `ZSTD_createDDict_byReference()`, `ZSTD_createDDict_advanced()`, `ZSTD_freeDDict()`, `ZSTD_initStaticDDict()`, `ZSTD_sizeof_DDict()`, `ZSTD_estimateDDictSize()`, and `ZSTD_getDictID_fromDict()`.

## Control Flow
There is no executable control flow in the header. Callers include it when they need to inspect dictionary byte ranges or install DDict-derived state into a decompression context before decoding.

## State And Persistence
No state is defined here. The functions operate on opaque `ZSTD_DDict` and `ZSTD_DCtx` objects whose fields are defined in decompression implementation headers and `zstd_ddict.c`.

## Dependencies And Integration Points
This header is the boundary between the DDict implementation and decompression code that should not know the full `struct ZSTD_DDict_s` layout. It integrates with `zstd_decompress.c` and related internal decompression paths that need dictionary content, size, entropy tables, and prefix/window parameters.

## Risks And Edge Cases
The helpers assume non-null arguments in the implementation. Since they are internal, callers are expected to validate object lifetimes and not use DDict pointers after free. Adding fields to `ZSTD_DDict` does not require changing this header, but changing these helper contracts affects all decompression dictionary users.

## Test Signals
Compile coverage should ensure internal decompression users can include the header without exposing private struct layout. Runtime coverage comes from DDict decompression tests that exercise helper calls through dictionary-based decompression, including by-copy, by-reference, raw-content, and full-dictionary modes.
<!-- END_FILE_RESEARCH: sources/compression/zstd/lib/decompress/zstd_ddict.h -->
