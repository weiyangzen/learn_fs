# sources/distributed-fs/ceph-client/drivers/block/drbd/drbd_vli.h

## Purpose

`drbd_vli.h` implements DRBD's variable-length integer and bitstream helpers used to compress bitmap run lengths during replication. It is optimized for DRBD dirty-bit maps where long runs of equal polarity are common, but short noisy runs should not be much worse than plaintext.

## Important APIs and Types

`VLI_L_1_1()` is a macro table of encoding levels. Each `LEVEL(total_bits, prefix_bits, prefix_value)` defines one prefix/data-size class. `vli_decode_bits()` decodes a VLI value from the least significant bits of a `u64` input and returns consumed bits. `__vli_encode_bits()` encodes a positive `u64` into a code word and returns code length, with `-EINVAL` for zero and `-EOVERFLOW` for too-large values. `vli_encode_bits()` writes an encoded value into a bitstream.

`struct bitstream_cursor` tracks a byte pointer and bit offset. `struct bitstream` tracks the cursor, buffer, byte length, and input padding bits. Helper functions are `bitstream_cursor_reset()`, `bitstream_cursor_advance()`, `bitstream_init()`, `bitstream_rewind()`, `bitstream_put_bits()`, and `bitstream_get_bits()`.

## Control Flow

Encoding selects the first level whose cumulative maximum includes the input. It subtracts the level's adjustment base, shifts the payload above the prefix, ORs in the prefix value, and writes the low-order code bits to the bitstream. Decoding tests each level's prefix mask against the low bits of the input, reconstructs the adjusted value from the payload, and returns the level's total bit count. The level table is deliberately compile-time macro-expanded so encode/decode stay in sync.

Bitstream writes first check capacity, strip high bits above the requested width, OR the low byte into the current partial byte, then continue byte-wise and advance the cursor. Reads cap the requested width to available valid bits after padding, copy up to the needed bytes into a `u64`, convert from little endian, align by the current bit offset, mask unwanted high bits, advance the cursor, and return the actual bit count.

## State and Persistence Behavior

The helpers mutate only caller-provided bitstream buffers and cursor fields. `bitstream_rewind()` also zeroes the buffer to prepare for fresh output. There is no persistent state, but encoded streams become part of DRBD bitmap transfer payloads, so compatibility depends on the level table and little-endian least-significant-bit-first semantics remaining stable.

## Dependencies and Integration Points

The header depends on kernel integer types, `BUG()`, errno constants, `memset()`, `memcpy()`, and `le64_to_cpu()`. It integrates with bitmap send/receive code that compresses run-length encoded dirty-bit polarity. The comments explicitly frame it as a DRBD receiver/bitmap transfer support utility.

## Risks and Edge Cases

Zero cannot be encoded because run lengths are positive. Values above the maximum table coverage return `-EOVERFLOW`. `vli_decode_bits()` calls `BUG()` if no level matches, assuming the static table is correct; corrupted input must therefore be guarded by callers that provide enough bits and valid framing. `bitstream_get_bits()` has a special hazard when `bits == 64`: the final mask expression shifts by `64 - bits`, so callers and compiler behavior need scrutiny for undefined shift-by-width behavior. Capacity and padding calculations are bit-level and easy to regress with off-by-one errors.

## Test Signals

Round-trip tests should cover every VLI level boundary, zero input, maximum encodable value, overflow, short buffers, non-byte-aligned cursor positions, padding-limited reads, and repeated rewind/reuse. Interoperability tests should verify compressed bitmap streams generated on one endian architecture decode identically on another, preserving the documented little-endian bitstream order.
