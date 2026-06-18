# Group Research: group_1667_reactos_sources_windows_reactos_drivers_filesystems_btrfs_zstd_zstd_563be0732ff0

Scope checked against `Docs/research_subset_a.md`: subset A includes the complete `sources/windows/reactos` tree. Both listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/zstd/zstd.h -->
# File Research: sources/windows/reactos/drivers/filesystems/btrfs/zstd/zstd.h

Read completely: 2090 lines.

Vendored public Zstandard 1.4.5 API header used by the ReactOS Btrfs driver copy of zstd. It defines symbol visibility/export macros, version constants and queries, frame magic constants, block-size limits, and the public compression/decompression contract for one-shot, context-based, streaming, dictionary, and advanced/static-linking-only use.

Stable API surface:
- Version and constants: `ZSTD_VERSION_*`, `ZSTD_VERSION_NUMBER`, `ZSTD_VERSION_STRING`, `ZSTD_MAGICNUMBER`, skippable-frame magic range, `ZSTD_BLOCKSIZE_MAX`, and default compression level `ZSTD_CLEVEL_DEFAULT`.
- One-shot helpers: `ZSTD_compress()`, `ZSTD_decompress()`, `ZSTD_getFrameContentSize()`, obsolete `ZSTD_getDecompressedSize()`, `ZSTD_findFrameCompressedSize()`, `ZSTD_compressBound()`, error helpers, and min/max compression level queries.
- Explicit contexts: opaque `ZSTD_CCtx` and `ZSTD_DCtx` allocation/free plus `ZSTD_compressCCtx()` and `ZSTD_decompressDCtx()`.
- Advanced stable parameters: `ZSTD_strategy`, `ZSTD_cParameter`, `ZSTD_dParameter`, `ZSTD_bounds`, `ZSTD_CCtx_setParameter()`, `ZSTD_CCtx_setPledgedSrcSize()`, `ZSTD_CCtx_reset()`, `ZSTD_compress2()`, `ZSTD_DCtx_setParameter()`, and `ZSTD_DCtx_reset()`.
- Streaming API: `ZSTD_inBuffer`, `ZSTD_outBuffer`, `ZSTD_CStream`/`ZSTD_DStream` aliases, `ZSTD_compressStream2()` with `ZSTD_e_continue`, `ZSTD_e_flush`, and `ZSTD_e_end`, buffer-size recommendations, legacy `ZSTD_initCStream()`/`ZSTD_compressStream()`/`ZSTD_flushStream()`/`ZSTD_endStream()`, and decompression stream setup/use.
- Dictionary API: one-shot dictionary compression/decompression, prepared `ZSTD_CDict`/`ZSTD_DDict`, dictionary ID helpers, sticky context dictionary loading/reference, single-use prefix APIs, and `ZSTD_sizeof_*()` memory introspection.

Static-linking-only API is gated by `ZSTD_STATIC_LINKING_ONLY` and exposes implementation-sensitive constants, bounds, structures, and lower-level entry points. It includes frame header size constants, compression parameter bounds, LDM bounds, `ZSTD_compressionParameters`, `ZSTD_frameParameters`, `ZSTD_parameters`, dictionary load/content mode enums, magicless frame format selection, dictionary attach preferences, literal-compression mode, decompressed-size/bound helpers, frame-header parsing, sequence extraction, memory estimation, static-object initialization, custom allocators, by-reference dictionaries, compression parameter conversion/check/adjust helpers, deprecated advanced compression and streaming setup functions, frame progression and flush probes, buffer-less streaming compression/decompression, and raw block-level compression/decompression APIs.

Important safety/contract points documented in this header:
- `ZSTD_getFrameContentSize()` can report unknown or error, and callers must not trust untrusted frame-declared sizes without application limits.
- Streaming decompression defaults to rejecting large windows above `ZSTD_WINDOWLOG_LIMIT_DEFAULT` unless the decoder explicitly raises the limit.
- Prefix and by-reference dictionary APIs require the referenced buffer to outlive compression/decompression and remain unmodified.
- Static contexts require externally supplied 8-byte-aligned workspaces and never allocate/grow internally.
- Raw block APIs omit frame metadata; callers must manage sizes, uncompressed-block handling, history insertion, and block limits correctly.

ReactOS Btrfs integration: nearby Btrfs code includes this header from `registry.c` to clamp the mount `ZstdLevel` option against `ZSTD_maxCLevel()`. Compression/decompression paths use driver-local wrapper functions such as `zstd_compress()` and `zstd_decompress()`, which are implemented elsewhere on top of this vendored zstd library.

Risks/quirks:
- This is an upstream-style public header with many experimental/static-only APIs exposed when enabled; those symbols are explicitly unstable and should not be treated as ABI-safe.
- Several legacy/deprecated functions remain declared for compatibility.
- `ZSTD_c_nbWorkers` and related parameters are declared, but availability depends on build-time multithreading support.
- Kernel/driver users must be careful with allocator choice, size limits, and untrusted frame metadata because the public one-shot APIs can otherwise imply large destination buffers or memory budgets.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/zstd/zstd.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/zstd/zstd_common.c -->
# File Research: sources/windows/reactos/drivers/filesystems/btrfs/zstd/zstd_common.c

Read completely: 74 lines.

Small common implementation file for the vendored zstd library. It includes `<stdlib.h>`, `<string.h>`, `error_private.h`, and `zstd_internal.h`, then provides externally visible version, error, and custom-allocation helper functions.

Exports:
- `ZSTD_versionNumber()` returns `ZSTD_VERSION_NUMBER`.
- `ZSTD_versionString()` returns `ZSTD_VERSION_STRING`.
- `ZSTD_isError()` forwards to `ERR_isError()` after undefining the internal macro of the same name.
- `ZSTD_getErrorName()`, `ZSTD_getErrorCode()`, and `ZSTD_getErrorString()` forward to private error helpers.
- `ZSTD_malloc()`, `ZSTD_calloc()`, and `ZSTD_free()` call the `ZSTD_customMem` allocator/free callbacks.

Behavior notes:
- `ZSTD_calloc()` implements zero-initialization as `customAlloc()` followed by `memset(ptr, 0, size)`.
- `ZSTD_free()` skips the callback when `ptr == NULL`.
- The file assumes the effective `ZSTD_customMem` callbacks are valid. In this ReactOS vendored build, integration must ensure default/custom allocator plumbing never passes a null allocation callback into these helpers.

Risks/quirks:
- `ZSTD_calloc()` does not check whether `customAlloc()` returned `NULL` before calling `memset()`. That matches this vendored upstream code path but means callers/allocation wrappers must avoid invoking it with failing or absent allocators, or the build must provide an internal defaulting layer before this helper is reached.
- No filesystem-specific logic lives here; its role is shared zstd support for the broader Btrfs compression/decompression code.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/zstd/zstd_common.c -->