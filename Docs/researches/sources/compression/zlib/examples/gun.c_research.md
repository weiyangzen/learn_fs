# sources/compression/zlib/examples/gun.c

## Purpose
Implements a small gunzip/uncompress-style utility demonstrating `inflateBack()`. It decompresses gzip files, concatenated gzip members, and Unix `compress` LZW streams, optionally testing integrity only. It also copies metadata from compressed input files to decompressed output files and deletes source files on successful decompression.

## APIs, Types, And Functions
The gzip path uses `inflateBackInit()`, `inflateBack()`, `inflateBackEnd()`, and `crc32()`. `struct ind` and `in()` provide pull input callbacks. `struct outd` and `out()` provide push output callbacks with optional CRC/length accounting. The LZW path uses global prefix/suffix/match buffers and `lunpipe()`. `gunpipe()` parses gzip or LZW headers and trailers, `copymeta()` copies mode/ownership/timestamps, `gunzip()` opens/closes files and interprets zlib-style return codes, and `main()` handles suffix stripping and options.

## Control Flow
`main()` initializes a reusable `inflateBack` window, parses `-h` or `-t`, derives output names by removing gzip/compress suffixes, and invokes `gunzip()` for each file or stdin/stdout. `gunpipe()` scans for gzip magic bytes, branches to `lunpipe()` on Unix compress magic, otherwise parses gzip flags, inflates deflate payloads through callbacks, verifies CRC and length trailers, and loops for concatenated gzip members. `lunpipe()` decodes variable-width LZW codes, handles clear codes, rebuilds strings through prefix/suffix tables, and streams output through `out()`.

## State And Persistence
The program has large static buffers for input, output, LZW tables, and the inflateBack window. It persists decompressed files, may unlink original compressed files after success, and may unlink incomplete output files on failure. Metadata copy is best-effort. `strm->msg`, `strm->next_in`, `errno`, and return codes are used to distinguish data, read, write, and EOF failures.

## Dependencies And Integration
Depends on POSIX file APIs (`open`, `read`, `write`, `close`, `unlink`, `stat`, `chmod`, `chown`, `utime`) and `zlib.h`. It demonstrates low-level callback-driven inflate rather than `gz*` convenience APIs, and it intentionally supports concatenated gzip streams consistent with gzip behavior.

## Risks And Test Signals
Risks include destructive behavior on success/failure, suffix handling that assumes names are long enough for direct suffix comparisons, platform dependence on POSIX metadata calls, and LZW parser complexity around chunk boundaries and invalid codes. Test signals include gzip round trips, concatenated member tests, corrupt CRC/ISIZE tests, truncated input, trailing garbage behavior, `-t` no-write mode, LZW sample files, metadata preservation checks, and large-output files exceeding 4 GiB modulo trailer semantics.
