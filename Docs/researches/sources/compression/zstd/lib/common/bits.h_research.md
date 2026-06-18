# sources/compression/zstd/lib/common/bits.h

Purpose: provides low-level bit counting, common-byte counting, high-bit, and rotate helpers used by zstd compression, decompression, and entropy code.

Important functions: `ZSTD_countTrailingZeros32/64`, `ZSTD_countLeadingZeros32/64`, fallback De Bruijn implementations, `ZSTD_NbCommonBytes`, `ZSTD_highbit32`, and `ZSTD_rotateRight_U64/U32/U16`.

Control flow: functions prefer compiler intrinsics on MSVC/GCC/ICCARM and fall back to portable arithmetic. 64-bit versions use native 64-bit intrinsics when available, otherwise split into high/low 32-bit words. `ZSTD_NbCommonBytes()` chooses trailing or leading zero count depending on endian. Rotate helpers mask counts to encourage compiler recognition and avoid undefined shift counts, while asserting valid ranges.

State and persistence: no mutable state; all helpers are inline/static.

Dependencies/integration: includes `mem.h` for integer types, endian/word-size helpers, and assertions. Used by match finding, entropy parsing, bitstream handling, and table decoding.

Risks: most count functions assert input is nonzero; passing zero in release builds can still invoke undefined compiler intrinsic behavior. Architecture conditional paths must match compiler support. Rotate functions assert count bounds but rely on callers to avoid invalid counts.

Test signals: unit tests for zero-excluded inputs, endian-dependent common-byte results, 32/64-bit builds, MSVC/GCC/Clang fallback configurations, and rotate outputs for boundary counts.
