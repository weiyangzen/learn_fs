# sources/distributed-fs/ceph-client/lib/decompress.c

## Purpose
Detects a compressed stream's format from its leading magic bytes and returns the matching kernel decompressor callback.

## APIs, Types, and Functions
Defines `struct compress_format` with two magic bytes, a display name, and a `decompress_fn`. `compressed_formats[]` maps gzip, bzip2, lzma, xz, lzo, lz4, and zstd magic prefixes to configured decompressor functions, or `NULL` when a format is not built. The exported local API is `decompress_method(const unsigned char *inbuf, long len, const char **name)`.

## Control Flow
`decompress_method()` rejects buffers shorter than two bytes, logs the magic bytes at debug level, scans the sentinel-terminated table with `memcmp()`, stores the matched name if requested, and returns the decompressor function pointer. If the magic is unknown, both name and decompressor come from the sentinel and are `NULL`.

## State and Persistence
The format table is `__initconst` read-only data. No mutable state is maintained.

## Dependencies and Integration Points
Depends on the generic decompression API and optional per-format headers controlled by `CONFIG_DECOMPRESS_*`. It is used by initramfs, initrd, and boot-time decompression dispatch code that has already read the stream prefix.

## Risks and Test Signals
Risks include ambiguous two-byte magic matches, disabled format support returning a name with a `NULL` function, and callers passing too-short input. Test signals include boot/initramfs tests for every configured compression format, unknown-format handling, and configuration-matrix builds with individual decompressors disabled.
