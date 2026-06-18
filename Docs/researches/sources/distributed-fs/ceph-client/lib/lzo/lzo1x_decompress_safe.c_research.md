# sources/distributed-fs/ceph-client/lib/lzo/lzo1x_decompress_safe.c

## Purpose
`lzo1x_decompress_safe.c` implements the kernel's checked LZO1X decompressor, including support for the versioned LZO-RLE zero-run extension. It is the public decode path used for potentially untrusted compressed LZO blocks and returns detailed negative error codes for malformed streams.

## Important APIs, types, and functions
The exported API is `lzo1x_decompress_safe(const unsigned char *in, size_t in_len, unsigned char *out, size_t *out_len)`. Important macros are `HAVE_IP()`, `HAVE_OP()`, `NEED_IP()`, `NEED_OP()`, and `TEST_LB()`, which enforce input availability, output capacity, and lookbehind validity. Constants from `lzodefs.h` define match classes, offsets, markers, and RLE zero-run bounds. Public error codes come from `include/linux/lzo.h`.

## Control flow
The decoder first checks for the optional version marker byte sequence beginning with `17`, then handles an initial literal run if present. The main loop reads a control byte and dispatches by range: values below 16 represent literal runs or short matches depending on `state`; values 64 and above encode M2 matches; values 32..63 encode M3 matches with optional extended length; lower marker values encode M4 matches or, in versioned streams, RLE zero-run instructions. After each match, the low bits describe how many literal bytes follow immediately, and the decoder copies those via the `match_next` path. The end-of-stream marker is detected when an M4-style match position equals the current output pointer.

## State and persistence
All state is per call: `ip`, `op`, `state`, `next`, match position, and the caller-provided output capacity. `*out_len` is updated to bytes produced on success and on error paths. There is no persistent dictionary between calls; lookbehind references must stay within the current output buffer.

## Dependencies and integration points
The file depends on `linux/lzo.h`, unaligned helpers, `lzodefs.h`, and optionally module exports unless compiled with `STATIC`. It is used by crypto LZO and LZO-RLE wrappers, Btrfs/SquashFS LZO consumers, and `lib/decompress_unlzo.c` for boot or archive decompression.

## Risks and test signals
The risk surface is malformed compressed input: input overrun, output overrun, lookbehind before output start, integer overflow while accumulating extended 255-length runs, invalid EOF, and version marker ambiguity. RLE support adds a special case for marker patterns that must only decode when the bitstream version is nonzero. Test signals include all negative `LZO_E_*` paths, successful decode of legacy and RLE streams, zero-run lengths at minimum and maximum boundaries, match copies with small overlapping distances, extended literal/match lengths near `MAX_255_COUNT`, and `LZO_E_INPUT_NOT_CONSUMED` when trailing bytes remain after EOF.
