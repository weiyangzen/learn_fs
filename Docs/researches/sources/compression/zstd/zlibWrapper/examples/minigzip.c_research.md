# sources/compression/zstd/zlibWrapper/examples/minigzip.c

## Purpose
`minigzip.c` is a minimal gzip-like command-line utility adapted to include `zstd_zlibwrapper.h`. It tests gzip-style file and pipe compression/decompression paths through the wrapper while preserving the classic zlib example's command-line behavior.

## Important APIs, Types, and Functions
The utility defines `error()`, `gz_compress()`, optional `gz_compress_mmap()`, `gz_uncompress()`, `file_compress()`, `file_uncompress()`, and `main()`. Under `Z_SOLO` it also supplies simplified `gzopen()`, `gzdopen()`, `gzwrite()`, `gzread()`, `gzclose()`, `gzerror()`, custom allocators, and a local `gzFile_s` structure around `FILE*`, mode/error fields, and `z_stream`. It uses `gzopen()`, `gzdopen()`, `gzwrite()`, `gzread()`, `gzclose()`, `gzerror()`, `deflateInit2()`, `inflateInit2()`, `deflate()`, `inflate()`, `inflateReset()`, and platform binary-mode helpers.

## Control Flow, State, and Persistence
`main()` derives behavior from argv and executable basename (`gunzip` implies decompression, `zcat` implies decompression to stdout), parses `-c`, `-d`, strategy flags `-f`/`-h`/`-r`, and compression levels `-1` through `-9`. With no file arguments it wraps stdin/stdout using `gzdopen()` and streams data. With file arguments it either writes to stdout or creates/removes `.gz` suffixed files via `file_compress()`/`file_uncompress()`. Compression loops read 16 KiB chunks and require `gzwrite()` to consume them; decompression loops call `gzread()` until zero and write each chunk. `file_compress()` and `file_uncompress()` remove the input file after successful conversion, so the program has persistent filesystem side effects.

## Dependencies and Integration Points
It depends on the zstd zlib wrapper, standard C I/O/string/allocation, optional mmap headers, platform-specific binary mode and Windows CE error helpers, and unlink/delete/remove behavior for final file replacement. The zlibWrapper Makefile builds `minigzip` and `minigzip_zstd`, and its test target uses both to compress/decompress the example binary.

## Risks and Test Signals
Risks include deliberately limited gzip utility behavior, destructive removal of input files after successful compression/decompression, simplified `Z_SOLO` gzip wrappers that read one byte at a time on inflate, filename suffix assumptions, and platform-specific binary/error handling. Signals include pipe and file round trips, strategy/level mode parsing, correct `.gz` suffix handling, successful cross-mode decompression by `minigzip_zstd`, clean close/finalization, and no leftover corrupt output after wrapper-mode compression.
