# File Research: sources/cow-pools/bcachefs-tools/fs/util/siphash.h

Purpose: Public SipHash types, constants, and round-profile macros.

Key APIs and behavior:
- Defines block, key, and digest lengths.
- `SIPHASH_CTX` stores state words, partial block buffer, and byte count.
- `SIPHASH_KEY` stores two little-endian 64-bit key words.
- Declares generic `SipHash_*` functions and convenience macros for SipHash-2-4 and SipHash-4-8.

Integration:
- Implemented by `siphash.c`.
- Uses Linux integer types.

Risks and invariants:
- Callers must provide a 16-byte key.
- Macro profiles pass fixed round counts into generic functions.
