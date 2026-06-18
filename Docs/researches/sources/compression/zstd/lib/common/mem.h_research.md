# sources/compression/zstd/lib/common/mem.h

## Purpose
`mem.h` centralizes zstd's fixed-width integer typedefs and unaligned memory access helpers. It gives entropy, block, checksum, and frame code a portable way to read and write native, little-endian, and big-endian integers without scattering aliasing and endian assumptions.

## Important APIs, Types, and Functions
The header defines `BYTE`, `U8`, `S8`, `U16`, `S16`, `U32`, `S32`, `U64`, and `S64`, falling back to limits-based typedefs for older C environments. It declares and implements `MEM_32bits()`, `MEM_64bits()`, `MEM_isLittleEndian()`, native `MEM_read16/32/64/ST()` and `MEM_write16/32/64()`, little-endian `MEM_readLE16/24/32/64/ST()` and `MEM_writeLE16/24/32/64/ST()`, big-endian `MEM_readBE32/64/ST()` and `MEM_writeBE32/64/ST()`, byte swaps `MEM_swap32()`, `MEM_swap64()`, `MEM_swapST()`, and `MEM_check()`.

## Control Flow, State, and Persistence
All helpers are `MEM_STATIC` inline functions with no stored state. Compile-time macro `MEM_FORCE_MEMORY_ACCESS` selects one of three unaligned-access strategies: safe `ZSTD_memcpy()`, compiler-specific packed/aligned(1) typedefs, or direct pointer casts. Endian helpers check compile-time endian macros where possible and fall back to a stack union probe. Read/write functions either use native access directly on little-endian systems or byte-swap/manual byte assembly on big-endian systems.

## Dependencies and Integration Points
It includes `<stddef.h>`, `compiler.h`, `debug.h`, and `zstd_deps.h`, with compiler-specific headers for MSVC and ICC ARM byte-swap intrinsics. `fse.h`, `huf.h`, bitstream code, xxhash, frame parsing, and sequence encoding all rely on these helpers for stable on-wire little-endian formats and fast unaligned loads.

## Risks and Test Signals
The deliberate performance/portability tradeoff around `MEM_FORCE_MEMORY_ACCESS` is the main risk: method 2 can violate the C standard and fault or miscompile on strict-alignment targets. Big-endian and 32-bit paths are easy to regress because most development happens on little-endian 64-bit machines. Test signals include cross-endian frame/header parsing, UBSan/ASan runs with `MEM_FORCE_MEMORY_ACCESS=0`, alignment stress tests on unaligned buffers, 32-bit builds, and checks that 24-bit reads/writes preserve only the expected bytes.
