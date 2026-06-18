# sources/distributed-fs/ceph-client/tools/perf/util/lzma.c

## Purpose

`lzma.c` implements XZ/LZMA decompression helpers used by perf's compressed data paths. It can detect `.xz` magic and stream-decompress input into an output file descriptor.

## Important APIs, Types, and Functions

The public functions are `lzma_decompress_stream_to_file()`, `lzma_decompress_to_file()`, and `lzma_is_compressed()`. `lzma_strerror()` maps selected `lzma_ret` codes to debug strings. Decompression uses an `lzma_stream`, 8 KiB input/output buffers, `lzma_stream_decoder(..., LZMA_CONCATENATED)`, and perf's `writen()` helper.

## Control Flow

`lzma_decompress_to_file()` opens a named file and delegates to the stream helper. The stream helper initializes the decoder, fills input from `fread()` when needed, switches to `LZMA_FINISH` on EOF, repeatedly calls `lzma_code()`, writes full or final output buffers, and exits successfully only on `LZMA_STREAM_END`. `lzma_is_compressed()` opens the file, reads six bytes, and compares them with the XZ magic.

## State and Persistence Behavior

All decompressor state is local to the call and released with `lzma_end()`. Output is persistent only because bytes are written to the caller-provided file descriptor; this file does not own truncation, fsync, or close behavior. Debug messages are emitted on read, write, decoder, and format errors.

## Dependencies and Integration Points

The file depends on liblzma, stdio/fcntl/unistd, perf debug, internal `writen()`, and `compress.h` declarations. It integrates with DSO and data-file readers that need to unpack compressed kernel modules or perf artifacts.

## Risks and Edge Cases

Partial writes are treated as errors through `writen()` size comparison. Truncated, corrupt, unsupported, or non-XZ input all fail with debug output. `LZMA_CONCATENATED` accepts concatenated streams, which is intentional for `.xz` but should be understood by callers. `lzma_is_compressed()` returns false for unreadable or shorter-than-magic files, so callers must distinguish detection from open errors if that matters.

## Test Signals

Tests should decompress valid single and concatenated `.xz` files, reject corrupt/truncated/non-XZ inputs, simulate read and write errors, and verify magic detection on valid, short, missing, and uncompressed files.
