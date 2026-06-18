# sources/distributed-fs/ceph-client/include/linux/zstd.h

## Purpose
Defines the kernel wrapper API around upstream Zstandard. It exposes selected compression, decompression, streaming, dictionary, frame-inspection, parameter-selection, and external-sequence APIs with kernel-style names because the upstream symbols are not exported directly.

## Important APIs, Types, and Functions
Helper APIs include `zstd_compress_bound()`, `zstd_is_error()`, `zstd_get_error_code()`, `zstd_get_error_name()`, and compression-level limit helpers. The header typedefs upstream types into kernel names: custom memory, dictionary load/content types, strategies, compression/frame/combined parameters, contexts, dictionaries, streams, buffers, frame headers, and sequences. Parameter APIs include `zstd_get_params()`, `zstd_get_cparams()`, and `zstd_cctx_set_param()`. Single-pass compression uses workspace-bound helpers, `zstd_init_cctx()`, `zstd_compress_cctx()`, advanced context creation/free, dictionary creation/free, and `zstd_compress_using_cdict()`. Single-pass decompression mirrors this with `zstd_dctx_workspace_bound()`, `zstd_init_dctx()`, `zstd_decompress_dctx()`, advanced dctx/ddict APIs, and `zstd_decompress_using_ddict()`. Streaming APIs include cstream/dstream workspace bounds, init/reset, `zstd_compress_stream()`, `zstd_flush_stream()`, `zstd_end_stream()`, and `zstd_decompress_stream()`. Inspection and advanced compression include `zstd_find_frame_compressed_size()`, `zstd_get_frame_header()`, `zstd_register_sequence_producer()`, and `zstd_compress_sequences_and_literals()`.

## Control Flow
Workspace-mode callers compute a bound for chosen parameters, allocate workspace, initialize a context inside that workspace, call compression/decompression, then free the workspace when the context is no longer used. Advanced allocation-mode callers create contexts or dictionaries with `zstd_custom_mem` and free them explicitly. Streaming compression initializes a stream with parameters and optional pledged source size, feeds buffers until input is consumed, flushes as needed, and calls `zstd_end_stream()` until it returns zero. Streaming decompression initializes with a maximum window, loops over input/output buffers, and treats return zero as a fully decoded and flushed frame.

## State and Persistence
Contexts, streams, and dictionaries persist compression tables, window state, frame state, loaded dictionaries, and custom allocator ownership. By-reference dictionary APIs require the dictionary buffer to outlive the dictionary object. Streaming input/output buffers carry mutable `pos` fields. Workspace-backed contexts are valid only while the caller-provided workspace remains alive and sufficiently sized.

## Dependencies and Integration Points
Depends on Linux types, `linux/zstd_errors.h`, and `linux/zstd_lib.h`. Integrates with kernel filesystems, initramfs and module compression, Btrfs/EROFS/SquashFS-style compressed data paths, dictionary users, and code that needs frame metadata or external sequence production.

## Risks
Almost all size-returning functions can encode errors and must be checked with `zstd_is_error()`. Workspace bounds must match the actual parameters and external-sequence usage; too-small workspaces fail at init or operation time. Decompression without a known output bound should use streaming APIs. Maximum window limits are critical for untrusted data. By-reference dictionaries create lifetime hazards. Streaming callers must continue flush/end loops until zero and must honor partial input consumption.

## Test Signals
Signals include zstd known-vector compression/decompression, workspace-bound tests across levels and strategies, dictionary lifetime tests, streaming partial-buffer tests, max-window rejection, frame-header/skippable-frame inspection tests, external sequence producer tests, and fuzzing corrupt frames with error-code validation.
