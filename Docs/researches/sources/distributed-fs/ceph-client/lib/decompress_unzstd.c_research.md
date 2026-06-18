# sources/distributed-fs/ceph-client/lib/decompress_unzstd.c

## Purpose
Provides the Zstandard decompression wrapper for compressed kernel, initramfs, and initrd payloads.

## APIs, Types, and Functions
The main implementation is `__unzstd()`. Linked builds expose `unzstd()`, while preboot builds expose `__decompress()`. Helpers include `handle_zstd_error()` for mapping zstd errors to kernel messages and `decompress_single()` for the fast single-buffer path. Constants define the maximum supported zstd window size and streaming I/O buffer size.

## Control Flow
If both `fill` and `flush` are absent, `__unzstd()` calls `decompress_single()`, which allocates a dctx workspace, finds the compressed frame size to ignore trailing junk, and decompresses into the caller buffer. Streaming mode allocates input and/or output buffers as needed, reads the frame header, validates that the window size is supported, allocates a `zstd_dstream` workspace sized to that window, then loops refilling input, calling `zstd_decompress_stream()`, flushing produced bytes, and updating `in_pos` until the frame completes. Cleanup frees all allocated buffers and workspace.

## State and Persistence
All state is per-call: zstd context/workspace, input/output buffer positions, frame header, and optional consumed-input counter. No global mutable state persists.

## Dependencies and Integration Points
Depends on Linux zstd APIs, xxhash and zstd source inclusion for static preboot builds, decompressor allocation helpers, and the generic decompressor callback ABI. It is selected by `decompress.c` for zstd magic and includes documented in-place safety margin assumptions.

## Risks and Test Signals
Risks include accepting unsupported window sizes, mishandling truncated frame headers, output buffer overflow when `out_len` is omitted, flush failures, and memory pressure from large windows. Test signals include zstd-compressed boot artifacts, single-shot and streaming decompression tests, corrupt checksum/prefix/window cases, trailing-junk handling, and comparisons with zstd reference output.
