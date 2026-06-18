# sources/distributed-fs/lizardfs/external/crcutil-1.0/code/multiword_64_64_cl_i386_mmx.cc

## Purpose

This file implements the MSVC/Intel C++ i386 MMX specialization for 64-bit CRC multiword processing. It exists to work around compiler performance and code-generation limitations on 32-bit Windows-era compilers while keeping the same `GenericCrc<uint64, uint64, uint64, 4>` interface.

## Important APIs and functions

The main specialization is `GenericCrc<uint64, uint64, uint64, 4>::CrcMultiwordI386Mmx(const void *data, size_t bytes, const uint64 &start)`. The file defines the `CRC_WORD_MMX()` macro in MSVC inline assembly form and maps symbolic names such as `CRC0`, `BUF0`, `SRC`, and `TABLE` to MMX and integer registers.

## Control flow, state, and persistence

The function canonicalizes `start`, aligns the source when needed, and then enters inline assembly. The main loop processes four 64-bit buffers through four MMX CRC lanes using `crc_word_interleaved_`. It then combines those lanes through the normal word table, processes remaining 64-bit words, and leaves remaining bytes to a C loop because the byte-loop assembly variant is disabled as slower. `emms` is issued before returning to clear MMX state.

## Dependencies and integration points

It includes `generic_crc.h` and compiles only under `CRCUTIL_USE_ASM && HAVE_I386 && HAVE_MMX && defined(_MSC_VER)`. It depends on Microsoft inline assembly syntax and warning pragmas for frame-pointer/register behavior.

## Risks and test signals

The code modifies `ebp`, disables warning 4731, and relies on 32-bit MSVC inline assembly, which is not supported in x64 MSVC. The assembly stores `END` on the stack and has tight register allocation assumptions. Missing `emms` would corrupt later floating-point/MMX use; this file explicitly emits it. Test signals are MSVC i386 builds, byte-size sweeps around 0..64, unaligned buffers, comparison with generic C++ output, and tests that run floating-point code after CRC to catch MMX cleanup issues.
