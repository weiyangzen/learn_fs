<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/zlibWrapper/gzguts.h -->
# sources/compression/zstd/zlibWrapper/gzguts.h

## Purpose
`gzguts.h` is the internal header for the wrapper's zlib-derived `gz*` file implementation. It centralizes platform compatibility, gzip state layout, constants, and helper declarations.

## Important APIs, Types, and Functions
The key internal type is `gz_state`, which embeds the public `gzFile_s` fields, file descriptor, path, buffers, direct/copy/decompress state, position, error information, and an in-place `z_stream`. `gz_statep` is a union of `gz_state *` and `gzFile`, a wrapper-specific change to reduce strict-aliasing issues. Constants define modes (`GZ_READ`, `GZ_WRITE`, `GZ_APPEND`) and read states (`LOOK`, `COPY`, `GZIP`). Shared declarations include `gz_error()` and Windows CE `gz_strwinerror()`.

## Control Flow
The header has no runtime flow but shapes all runtime flow in `gzlib.c`, `gzread.c`, `gzwrite.c`, and `gzclose.c`. Platform preprocessor branches select file APIs, large-file seek behavior, Windows wide-char support, snprintf/vsnprintf workarounds, and error-string sources.

## State and Persistence
`gz_state` is the persistent state for each `gzFile`. It tracks both compressed file offset via descriptor and uncompressed position via `x.pos`, pending seeks via `seek` and `skip`, read progression via `how`, `eof`, and `past`, and write behavior via compression `level` and `strategy`.

## Dependencies and Integration Points
Unlike upstream zlib, this header includes `zstd_zlibwrapper.h` instead of `zlib.h`, so `inflate` and `deflate` calls can resolve through wrapper symbols. It also includes `gzcompatibility.h` for older zlib interfaces and system headers for descriptors and errors.

## Risks
The internal state is tightly coupled to zlib's `gzFile` ABI and macro expectations. Any mismatch in `gz_statep` use can produce aliasing or invalid pointer behavior. File offset behavior depends on large-file macros being set before system headers. The direct/copy/gzip state machine must remain synchronized with `gzread.c`.

## Test Signals
Useful signals include builds across zlib versions and platforms, large-file seek/tell/offset tests, transparent reads, gzip/ZSTD reads, write modes, append mode, Windows wide-character paths, and strict-aliasing builds.
<!-- END_FILE_RESEARCH: sources/compression/zstd/zlibWrapper/gzguts.h -->
