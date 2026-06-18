# sources/compression/zlib/inffast.c

## Purpose
`inffast.c` provides the hot literal/length/distance decode loop used by `inflate()` and `inflateBack()` when enough input and output are available.

## Important APIs, Types, and Functions
The single internal API is `inflate_fast(z_streamp strm, unsigned start)`. It consumes `struct inflate_state` fields for bit accumulator, Huffman tables, sliding window, distance sanity, and mode updates. It works with `code` table entries from `inftrees.c`.

## Control Flow, State, and Persistence
On entry, callers guarantee `state->mode == LEN`, at least six input bytes, at least 258 output bytes, and fewer than eight buffered bits. The loop decodes literals directly, resolves length and distance table links, copies matches from output or the sliding window, and exits on block end, invalid code, invalid distance, insufficient input, or insufficient output. It writes updated stream pointers, remaining availability, bit state, and mode back to `strm`/`state`.

## Dependencies and Integration Points
It includes `zutil.h`, `inftrees.h`, `inflate.h`, and `inffast.h`. `ASMINF` can replace this C body with assembler. The routine is performance-critical for normal zlib inflate.

## Risks and Test Signals
Risks concentrate around pointer bounds, overlapping match copies, window wraparound, distance-too-far policy, and precondition violations by callers. Strong tests are sanitizer-backed decompression of malformed streams, boundary-sized output buffers, wraparound windows, fixed and dynamic tables, and strict versus permissive invalid-distance builds.
