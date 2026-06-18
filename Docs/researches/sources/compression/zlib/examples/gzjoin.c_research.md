# sources/compression/zlib/examples/gzjoin.c

## Purpose
Joins multiple gzip files into one gzip file whose decompressed data is the concatenation of the inputs, avoiding recompression and avoiding recalculating a full CRC over all uncompressed bytes. It demonstrates raw deflate block copying, clearing intermediate final-block bits, adding empty blocks for bit alignment, and `crc32_combine()`.

## APIs, Types, And Functions
Uses `inflateInit2(-15)`, `inflate(..., Z_BLOCK)`, `inflateEnd()`, `crc32()`, and `crc32_combine()`. `bin` wraps buffered input with `bopen()`, `bload()`, `bget()`, `bskip()`, and `bget4()`. `gzhead()` validates/skips gzip headers, `put4()` emits little-endian trailer words, `zpull()` feeds inflate, `gzinit()` writes a canonical output gzip header, and `gzcopy()` copies one gzip member's compressed payload into the joined output.

## Control Flow
`main()` writes a minimal gzip header with `gzinit()` and calls `gzcopy()` for each argument, passing `clr` true except for the final file. `gzcopy()` opens and header-skips an input gzip file, raw-inflates it using `Z_BLOCK` while writing consumed compressed bytes to stdout, clears the last-block bit on intermediate members, detects the next block's final bit at byte or bit offsets, inserts empty blocks to reach a byte boundary when needed, combines the input trailer CRC with the running CRC using the measured uncompressed length, and writes the final trailer only for the last input.

## State And Persistence
State is streaming and process-local: buffered input, a discard output buffer, zlib inflate state, running CRC, and modulo-32-bit total length. The only persistent output is stdout. Input files are read-only. The utility assumes input trailers are present and structurally usable but does not perform a full integrity check beyond header parsing and successful decompression.

## Dependencies And Integration
Depends on POSIX file reads/seeks and `zlib.h`. It integrates with gzip and raw deflate format details directly. `crc32_combine()` is the key zlib integration that avoids rereading or rechecksumming all already-compressed uncompressed data.

## Risks And Test Signals
Risks include incomplete input validation, bit-boundary mistakes when clearing final bits, empty-block insertion errors, unchecked stdout write failures in some paths, and reliance on trailer CRC/length fields from inputs. Test signals include joining one file, many files, files with stored/fixed/dynamic final blocks, files ending at every bit offset, corrupt/truncated inputs, and comparing output decompression and CRC to `cat plain... | gzip`.
