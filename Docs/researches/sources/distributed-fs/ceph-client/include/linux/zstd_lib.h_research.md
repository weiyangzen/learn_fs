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
