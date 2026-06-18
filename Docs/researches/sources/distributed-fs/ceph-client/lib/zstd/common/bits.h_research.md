# sources/distributed-fs/ceph-client/lib/zstd/common/bits.h

Purpose: Provides bit utility primitives for zstd/FSE/HUF code: count leading/trailing zeros, common-byte counts, high-bit lookup, and rotate-right operations.

Important APIs/functions:
- `ZSTD_countTrailingZeros32_fallback()`, `ZSTD_countTrailingZeros32()`.
- `ZSTD_countLeadingZeros32_fallback()`, `ZSTD_countLeadingZeros32()`.
- `ZSTD_countTrailingZeros64()`, `ZSTD_countLeadingZeros64()`.
- `ZSTD_NbCommonBytes(size_t val)`.
- `ZSTD_highbit32(U32 val)`.
- `ZSTD_rotateRight_U64/U32/U16()`.

Control flow:
- Uses compiler builtins for GCC-family builds where available; otherwise uses De Bruijn fallback tables for 32-bit cases.
- `ZSTD_NbCommonBytes()` chooses trailing-zero or leading-zero counting based on endianness and word size.
- Rotate helpers mask shift counts to generate compiler-friendly rotate patterns.

State and persistence:
- Stateless, aside from static const lookup tables inside fallback functions.

Dependencies and integration:
- Includes `mem.h` for `U32`, `U64`, `S32`, endian, and word-size helpers.
- Used by entropy parsing, match finding, and bitstream handling.

Risks:
- Functions assert nonzero inputs. Release builds may compile assertions out, so callers must guarantee nonzero values.
- Builtin behavior is undefined for zero; the assertion is not just documentation.
- Endianness-dependent common-byte logic must match the memory comparison algorithms that consume it.

Test signals:
- Unit tests for zero-excluded values, powers of two, high-bit boundaries, endian-specific common-byte behavior, and rotate counts.
- UBSAN tests for shift/count operations if enabled.
