# sources/distributed-fs/ceph-client/lib/zlib_inflate/inffast.c

Purpose: Fast-path DEFLATE decoder used by `inflate.c` when enough input and output space is available. It decodes literal/length and distance codes with reduced boundary checks and optimized match copying.

Important APIs/functions:
- `inflate_fast(z_streamp strm, unsigned start)` decodes from `state->mode == LEN` until input/output thresholds are reached, an end-of-block is found, or an error occurs.
- `get_unaligned16()` provides endian-independent 16-bit reads for architectures without efficient unaligned access.

Control flow:
- Copies stream and inflate state fields into locals for speed.
- Maintains `last = in + avail_in - 5` and `end = out + avail_out - 257`, relying on caller preconditions for safe inner-loop decoding.
- Reads at least 15 bits for literal/length lookup, follows second-level tables when needed, decodes extra length/distance bits, then copies literals or matches.
- Match copying handles three cases: back-reference into the sliding window, direct output copy with distance greater than 2, and short repeating distances 1 or 2 using 16-bit pattern replication.
- On end-of-block it sets mode `TYPE`; on invalid code or too-far distance it sets `BAD`.
- Restores unused bytes and updates `next_in`, `next_out`, `avail_in`, `avail_out`, `hold`, and `bits`.

State and persistence:
- Mutates `struct inflate_state` via `hold`, `bits`, and `mode`, but does not update checksums or the sliding window; `inflate.c` handles that on return.
- Reads fixed/dynamic decode tables from `state->lencode` and `state->distcode`.

Dependencies and integration:
- Includes zlib utility headers and `inftrees.h`, `inflate.h`, `inffast.h`.
- Called only by `inflate.c` when `have >= 6 && left >= 258`.
- Honors `CONFIG_HAVE_EFFICIENT_UNALIGNED_ACCESS` for 16-bit copy optimization.

Risks:
- Relies on strict entry preconditions. Calling with smaller buffers risks out-of-bounds reads/writes.
- Overlapping match copy logic is subtle, especially distances 1 and 2 and window wraparound.
- Availability restoration math is non-obvious and must stay consistent with sentinel `last`/`end`.

Test signals:
- Fuzzed inflate inputs with large buffers to maximize fast-path coverage.
- Back-reference tests for window wrap, distance 1/2, and distances crossing from window into output.
- Architecture tests with efficient and inefficient unaligned access settings.
