# sources/distributed-fs/ceph-client/lib/lzo/lzo1x_compress.c

## Purpose
`lzo1x_compress.c` implements the kernel LZO1X-1 compressor and LZO-RLE compressor. It is designed to be included twice: once directly for the normal unchecked-output compressor symbols and once through `lzo1x_compress_safe.c` with macros that add output-capacity checks and rename the exported functions with a `_safe` suffix.

## Important APIs, types, and functions
The exported functions after macro expansion are `lzo1x_1_compress()`, `lzorle1x_1_compress()`, `lzo1x_1_compress_safe()`, and `lzorle1x_1_compress_safe()`. The private engines are `lzo1x_1_do_compress()` and `lzogeneric1x_1_compress()` after `LZO_SAFE()` name mapping. The caller supplies `wrkmem`, interpreted as a `lzo_dict_t` dictionary with `D_SIZE` entries. Important constants come from `lzodefs.h`: match classes M1-M4, dictionary hash size, maximum offsets, and zero-run lengths.

## Control flow
The generic wrapper optionally writes the LZO-RLE version marker, then processes the input in chunks no larger than the M4 maximum offset range. For each chunk it zeroes the hash dictionary and calls the inner compressor. The inner loop scans the input, hashes four-byte sequences, emits literal runs accumulated since the previous match, detects optional zero runs for the RLE bitstream, computes match length with architecture-specific word comparisons and count-trailing/leading-zero helpers, and encodes the match as M2, M3, or M4 based on distance and length. It then records the post-match literal state in `state_offset`. At the end, remaining literals are emitted and the LZO end marker is appended.

## State and persistence
Compression state is local to each call except for caller-provided output length and work memory. `*out_len` is both input capacity for safe builds and output length on success. `wrkmem` is cleared per chunk and does not persist useful state across calls. The direct build sets `HAVE_OP(x)` to true, so it relies on callers providing worst-case output capacity; the safe inclusion checks `op_end - op` before each write and returns `LZO_E_OUTPUT_OVERRUN`.

## Dependencies and integration points
The file depends on `linux/lzo.h`, `linux/unaligned.h`, `lzodefs.h`, Kbuild's paired safe wrapper, and GPL symbol exports. It integrates with crypto compression (`crypto/lzo.c` and `crypto/lzo-rle.c`), filesystem compressors, and boot tooling that expects the Linux LZO block format plus optional versioned RLE extension.

## Risks and test signals
Risk is concentrated in output bounds for the non-safe build, match-length scanning near `ip_end`, versioned RLE ambiguity avoidance for specific M4 distances and lengths, and architecture-specific unaligned/ctz paths. The compressor must also keep the v0 and v1 bitstreams distinguishable. Test signals include round trips for empty, tiny, incompressible, repetitive, long literal, long match, and long zero-run inputs; explicit safe-output-overrun tests; validating v0 and v1 streams through `lzo1x_decompress_safe()`; and comparison with known crypto test vectors.
