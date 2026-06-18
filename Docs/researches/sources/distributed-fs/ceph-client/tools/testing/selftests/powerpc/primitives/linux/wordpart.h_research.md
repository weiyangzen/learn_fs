# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/primitives/linux/wordpart.h

## Purpose
`wordpart.h` defines small word-splitting and byte-repetition macros used by copied kernel string/word-at-a-time helpers.

## Important APIs, Types, and Functions
It provides `upper_32_bits()`, `lower_32_bits()`, `upper_16_bits()`, `lower_16_bits()`, `REPEAT_BYTE()`, and `REPEAT_BYTE_U32()`.

## Control Flow and State
All behavior is macro expansion at compile time or inline expression evaluation. No persistent state is held.

## Dependencies and Integration Points
It is included by `word-at-a-time.h` and supports endian/word-size independent byte-mask calculations in the primitive test.

## Risks and Test Signals
Risks include incorrect casts or shifts on 32-bit versus 64-bit builds. Test signals are correct zero-byte detection and load_unaligned_zeropad results at every page offset.
