<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/zlibWrapper/gzclose.c -->
# sources/compression/zstd/zlibWrapper/gzclose.c

## Purpose
`gzclose.c` provides the public `gzclose()` dispatcher for gzip-style file handles in the zlib wrapper. It is kept separate so programs that explicitly use `gzclose_r()` or `gzclose_w()` can avoid linking unneeded read or write code.

## Important APIs, Types, and Functions
The only exported function is `gzclose(gzFile file)`. It uses the `gz_statep` union from `gzguts.h` to reinterpret the public `gzFile` as internal `gz_state`. Depending on `state.state->mode`, it dispatches to `gzclose_r()` for `GZ_READ` or `gzclose_w()` otherwise, unless `NO_GZCOMPRESS` forces read-only behavior.

## Control Flow
The function rejects `NULL` with `Z_STREAM_ERROR`. With compression enabled, it reads the internal mode and delegates to the read or write close path. With compression disabled, it always calls `gzclose_r()`.

## State and Persistence
This file owns no persistent state. It triggers cleanup in the delegated close routines, including stream finalization, buffer release, path-message release, descriptor close, and `gz_state` free.

## Dependencies and Integration Points
It includes `gzguts.h`, which brings in wrapper-aware zlib declarations and the internal gzip state definition. It integrates the read implementation in `gzread.c` and write implementation in `gzwrite.c`.

## Risks
If a `gzFile` has corrupted mode state or is not actually a wrapper `gz_state`, dispatch can call the wrong close path. The function intentionally treats any non-read mode as write mode when compression is enabled, relying on `gzclose_w()` to validate `GZ_WRITE`.

## Test Signals
Coverage should include closing read handles, write handles, `NULL`, invalid mode handles, and builds with `NO_GZCOMPRESS`.
<!-- END_FILE_RESEARCH: sources/compression/zstd/zlibWrapper/gzclose.c -->
