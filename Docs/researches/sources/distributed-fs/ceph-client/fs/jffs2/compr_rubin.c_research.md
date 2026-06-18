# sources/distributed-fs/ceph-client/fs/jffs2/compr_rubin.c

## Purpose
`compr_rubin.c` implements legacy Rubin arithmetic-coding decompressors and a dynamic Rubin compressor. These algorithms remain primarily for compatibility with old JFFS2 images; the header disables Rubin compression by default while keeping decompression available.

## Important APIs, Types, And Functions
The file defines bitstream helper `struct pushpull`, arithmetic coder `struct rubin_state`, helpers `init_pushpull()`, `pushbit()`, `pullbit()`, `init_rubin()`, `encode()`, `decode()`, `out_byte()`, and `in_byte()`. Higher-level functions are `rubin_do_compress()`, `jffs2_dynrubin_compress()`, `rubin_do_decompress()`, `jffs2_rubinmips_decompress()`, and `jffs2_dynrubin_decompress()`. Two `struct jffs2_compressor` instances register `rubinmips` and `dynrubin`.

## Control Flow
Dynamic Rubin compression builds a byte histogram, converts it into eight bit probabilities stored in the first eight output bytes, then arithmetic-encodes input bits into the remaining output area. The fixed MIPS variant uses a hard-coded probability table and has its compressor compiled out. Decompression initializes the arithmetic decoder, optionally reads dynamic probabilities from the stream header, and emits bytes until `dstlen` is reached.

## State And Persistence Behavior
The algorithm uses stack-local coder state and static probability tables. Persistent format is the backend id plus, for dynamic Rubin, eight probability bytes at the start of compressed data. The registered compression ids are legacy-sensitive and must match historical on-flash values.

## Dependencies And Integration Points
It depends on `compr.h`, JFFS2 compression constants, and the compressor registry. Read paths use the decompress callbacks for old nodes even when compression is disabled.

## Risks And Test Signals
Risks include legacy id/name confusion, weak malformed-stream bounds in the bit pull path, divide-by-zero if a zero source length were ever passed to dynamic compression, and silent data corruption if probability headers are damaged. Tests should prioritize decompression of known Rubin/RubinMIPS images, malformed/truncated streams, and verifying disabled compressors are skipped for new writes.
