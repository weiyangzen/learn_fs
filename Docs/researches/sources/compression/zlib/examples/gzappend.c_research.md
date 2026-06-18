# sources/compression/zlib/examples/gzappend.c

## Purpose
Command-line utility that appends new uncompressed data to an existing gzip file by continuing the original raw deflate stream instead of creating another gzip member. It demonstrates `inflate(..., Z_BLOCK)`, unused-bit reporting, `deflateSetDictionary()`, and `deflatePrime()` for bit-exact deflate continuation.

## APIs, Types, And Functions
Uses public zlib APIs `inflateInit2(-15)`, `inflate(..., Z_BLOCK)`, `inflateEnd()`, `deflateInit2(-15)`, `deflateSetDictionary()`, `deflatePrime()`, `deflate()`, and `deflateEnd()`, plus `crc32()`. Local helpers include `gcd()` and `rotate()` for dictionary rotation, buffered `file` input helpers (`readin()`, `readmore()`, `skip()`, `read4()`), `gzheader()` for gzip header parsing, `gzscan()` to locate and clear the original final-block bit, and `gztack()` to append compressed data and write the new trailer.

## Control Flow
`main()` parses an optional compression level and target gzip file, calls `gzscan()` to validate and internally decompress the original gzip file, then appends named files or stdin through `gztack()`. `gzscan()` reads the gzip header, inflates raw deflate blocks while tracking block-boundary metadata from `data_type`, verifies the original trailer, warns that trailing junk will be overwritten, clears the final block bit in place, builds a dictionary from the last 32 KiB of uncompressed output, primes a new raw deflate stream with leftover bits, and returns the seeked file descriptor. `gztack()` compresses appended input and writes a new CRC/ISIZE trailer.

## State And Persistence
The utility mutates the target gzip file in place, overwriting its trailer and any trailing junk. It keeps the rolling CRC in `strm->adler` and total uncompressed size in `strm->total_in`. Failure after in-place modification can corrupt the target file, a limitation explicitly documented in the source. Temporary state is heap buffers plus zlib stream state.

## Dependencies And Integration
Depends on POSIX read/write/lseek APIs and `zlib.h`. It integrates with gzip format internals directly, not with zlib's `gzFile` abstraction. It requires zlib features introduced around 1.2.x: `Z_BLOCK` block-boundary return data and `deflatePrime()`.

## Risks And Test Signals
Risks are severe because writes are in-place and non-transactional. Bit-position handling (`lastbit`, `left`, `lastoff`, `end`) and dictionary rotation are correctness-critical. Tests should append to gzip files ending at different bit offsets, with and without extra/name/comment/header CRC fields, compare decompressed output to concatenated plaintext, validate CRC/ISIZE, test stdin and missing appended files, and simulate read/write errors to document corruption behavior.
