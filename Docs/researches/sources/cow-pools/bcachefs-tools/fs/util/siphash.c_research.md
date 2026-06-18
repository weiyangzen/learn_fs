# File Research: sources/cow-pools/bcachefs-tools/fs/util/siphash.c

Purpose: BSD-licensed SipHash implementation with selectable compression/finalization rounds.

Key APIs and behavior:
- `SipHash_Init()` seeds state from a 128-bit key.
- `SipHash_Update()` streams bytes through 8-byte blocks.
- `SipHash_End()` pads with message length, finalizes, zeroes context, and returns a 64-bit digest.
- `SipHash_Final()` writes little-endian digest bytes.
- `SipHash()` is the one-shot helper.

Integration:
- Implements `siphash.h`.
- Uses unaligned little-endian loads and `rol64`.

Risks and invariants:
- `ctx->bytes` is a `u32`, so very long streams wrap length encoding.
- `SipHash_Update()` copies trailing bytes into `ctx->buf[used]`; correctness depends on `used` handling across partial updates.
