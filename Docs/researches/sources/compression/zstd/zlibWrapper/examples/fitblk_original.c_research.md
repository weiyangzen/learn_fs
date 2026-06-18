# sources/compression/zstd/zlibWrapper/examples/fitblk_original.c

## Purpose
`fitblk_original.c` is the original zlib example for determining how much input can be compressed into a specified output block size. It is kept as the unmodified baseline for the wrapper-adapted `fitblk.c`.

## Important APIs, Types, and Functions
The program is organized around `quit()`, `partcompress()`, `recompress()`, and `main()`. It includes `zlib.h` directly and uses `z_stream`, `z_streamp`, `deflateInit()`, `deflate()`, `deflateReset()`, `deflateEnd()`, `inflateInit()`, `inflate()`, `inflateReset()`, and `inflateEnd()`. `RAWLEN` is 4096 bytes, `EXCESS` is 256 bytes, and `MARGIN` is 8 bytes.

## Control Flow, State, and Persistence
After parsing a requested block size of at least eight bytes, `main()` allocates `blk`, performs a first pass from stdin into `size + EXCESS` output capacity, and if the entire stream fits, writes the compressed bytes to stdout. If not, it allocates `tmp`, initializes inflate, recompresses the saved stream close to the target, resets streams, then recompresses a truncated intermediate stream into the final output buffer so completion fits within the requested size. It writes the final compressed block to stdout and emits unused-capacity stats to stderr.

## Dependencies and Integration Points
It depends only on zlib and standard C I/O/allocation/assert facilities. As a baseline example, its integration value is documenting the original algorithm and output behavior before wrapper-specific changes such as `Z_SYNC_FLUSH` in the first pass, zstd version printing, and disabled stdout writes.

## Risks and Test Signals
Risks include heuristic constants that may not fit every compressor/block behavior, assert-based invariant handling, possible write errors on stdout, and memory allocation based directly on user-provided size. Signals are valid compressed output that never exceeds the requested size, low unused-byte shortfall for sufficiently large inputs, successful decompression of emitted blocks, and no zlib stream errors or read/write failures.
