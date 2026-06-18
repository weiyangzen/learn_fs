# sources/compression/lz4/lib/lz4file.c

## Purpose
`lz4file.c` implements a small static file-oriented wrapper around the LZ4 frame API. It exposes handle-based read and write helpers that operate on caller-owned `FILE*` streams, allocate frame contexts and work buffers internally, and translate I/O failures into `LZ4F_errorCode_t` values.

## Important APIs, Types, And Functions
The read side defines `struct LZ4_readFile_s` with an `LZ4F_dctx*`, `FILE*`, source buffer, current source cursor, current source size, and maximum source buffer size. Public functions are `LZ4F_readOpen()`, `LZ4F_read()`, and `LZ4F_readClose()`. Helpers include `freeReadFileResources()`, `freeAndNullReadFile()`, and `readAndParseHeader()`.

The write side defines `struct LZ4_writeFile_s` with an `LZ4F_cctx*`, `FILE*`, destination buffer, maximum input chunk size, destination buffer capacity, and sticky error code. Public functions are `LZ4F_writeOpen()`, `LZ4F_write()`, and `LZ4F_writeClose()`. Helpers include `freeWriteFileResources()`, `freeAndNullWriteFile()`, and `writeHeader()`.

`returnErrorCode()` and `RETURN_ERROR()` locally construct frame-style negative error codes from static-only `LZ4F_errorCodes`.

## Control Flow
`LZ4F_readOpen()` validates parameters, allocates the read handle, creates a decompression context with `LZ4F_VERSION`, reads up to `LZ4F_HEADER_SIZE_MAX` bytes, parses frame info with `LZ4F_getFrameInfo()`, sizes `srcBuf` using `LZ4F_getBlockSize()`, and preserves any bytes read past the frame header for later decompression.

`LZ4F_read()` loops until the caller's output buffer is filled or input ends. It uses any buffered compressed bytes first, refills `srcBuf` with `fread()` when empty, calls `LZ4F_decompress()`, advances the compressed-buffer cursor by the consumed count, and advances the output pointer by produced bytes. It returns either decoded byte count or an LZ4F error code encoded as `size_t`.

`LZ4F_writeOpen()` validates the output handle and `FILE*`, derives the block size from preferences or default settings, allocates the write handle and destination buffer sized by `LZ4F_compressBound(blockSize, prefsPtr)`, creates the compression context, writes the frame header with `LZ4F_compressBegin()`, and returns the handle.

`LZ4F_write()` splits the caller input into chunks no larger than the frame block size, compresses each chunk with `LZ4F_compressUpdate()`, writes compressed bytes with `fwrite()`, and returns the original input size on success. `LZ4F_writeClose()` finalizes the frame with `LZ4F_compressEnd()` unless a prior write error is sticky, writes the end bytes, releases the handle, and returns the final status.

## State And Persistence
State is per-handle and heap allocated. Read handles persist decompression context state, buffered compressed input, and file position through the underlying `FILE*`. Write handles persist compression context state, output scratch buffer, and a sticky `errCode` that suppresses frame finalization after earlier write/compression failure. The module never closes the underlying `FILE*`; ownership remains with the caller.

## Dependencies And Integration Points
The implementation includes `<stdlib.h>`, `<string.h>`, `<assert.h>`, `lz4.h`, and `lz4file.h`. It depends heavily on static-only frame helpers from `lz4frame_static.h`, including `LZ4F_errorCodes` and `LZ4F_getBlockSize()`. It integrates with any C caller that already has binary-mode `FILE*` handles and wants simple frame read/write routines without driving the lower-level streaming frame API directly.

## Risks And Edge Cases
`readAndParseHeader()` reads a fixed `LZ4F_HEADER_SIZE_MAX` chunk up front and requires at least `LZ4F_HEADER_SIZE_MIN + LZ4F_ENDMARK_SIZE` bytes, which rejects very short/truncated inputs early but also couples the wrapper to seekless forward consumption. `LZ4F_read()` breaks on EOF even if the frame has not returned a completed status, so truncated streams can look like a short read instead of a frame error unless later logic checks for frame completion externally.

There is a notable cleanup-risk path in `LZ4F_writeOpen()`: after allocating `writeFile`, if `LZ4F_createCompressionContext()` fails, it calls `freeAndNullWriteFile(lz4fWrite)` instead of `freeAndNullWriteFile(&writeFile)`. Since the caller output pointer has not been assigned yet, this can free an unrelated value supplied by the caller and leak the local allocation. The analogous read path uses the local pointer correctly.

`LZ4F_write()` treats `fwrite()` returning fewer bytes than requested as `io_write`, sets sticky error state, and returns an error code. It does not retry partial writes. All read/write functions return frame-style error codes in unsigned return types, so callers must consistently use `LZ4F_isError()`.

## Test Signals
Focused tests should cover opening null pointers, valid round-trip file compression/decompression, short headers, invalid frame headers, truncated frame bodies, frame checksum failure propagation, small caller read buffers, large writes split across multiple frame blocks, write finalization after a prior write error, partial `fwrite()` failure via a mock or fopencookie-style stream, and the `LZ4F_writeOpen()` compression-context allocation failure cleanup path.
