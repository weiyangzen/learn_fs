<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/zlibWrapper/gzcompatibility.h -->
# sources/compression/zstd/zlibWrapper/gzcompatibility.h

## Purpose
`gzcompatibility.h` supplies compatibility declarations and type definitions for older zlib versions used by the wrapper's copied `gz*` implementation.

## Important APIs, Types, and Functions
For zlib versions at or below specific `ZLIB_VERNUM` thresholds, it declares `gzclose_r()`, `gzclose_w()`, `gzbuffer()`, `gzoffset()`, `gzopen_w()`, `gzfread()`, and `gzfwrite()`. It also defines `z_off64_t` where absent and provides the older public `struct gzFile_s` layout with `have`, `next`, and `pos`.

## Control Flow
This header is entirely preprocessor-driven. Feature availability is selected by zlib version and platform macros such as `_WIN32`, `Z_LARGE64`, `Z_SOLO`, `NO_SIZE_T`, and `STDC`.

## State and Persistence
It owns no runtime state. Its declarations affect ABI compatibility and source compilation for the gzip wrapper modules.

## Dependencies and Integration Points
The header is included by `gzguts.h` after `zstd_zlibwrapper.h`. It bridges the wrapper's internal `gz_state` layout to public zlib declarations, especially for versions before zlib 1.2.11 where `z_size_t` and newer `gzf*` APIs may not exist.

## Risks
The primary risk is ABI drift across zlib versions: incorrect conditional declarations could conflict with system zlib headers or expose a mismatched `gzFile_s`. The `z_off64_t` fallback also depends on platform large-file conventions.

## Test Signals
Build matrix coverage against older and newer zlib versions is the key signal. Tests should compile both Windows and non-Windows variants and exercise `gzfread`, `gzfwrite`, wide-path open, offsets, and close variants where provided by compatibility declarations.
<!-- END_FILE_RESEARCH: sources/compression/zstd/zlibWrapper/gzcompatibility.h -->
