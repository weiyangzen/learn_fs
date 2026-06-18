# sources/distributed-fs/lizardfs/external/crcutil-1.0/code/multiword_64_64_gcc_i386_mmx.cc

## Purpose

This file implements the GCC i386 MMX assembly specialization for 64-bit CRCs. It accelerates `GenericCrc<uint64, uint64, uint64, 4>` on 32-bit x86 by keeping four CRC lanes in MMX registers.

## Important APIs and functions

It specializes `CrcMultiword()` and `CrcMultiwordI386Mmx()`. The top-level specialization handles inputs of 7 bytes or less with `CRC_BYTE`, otherwise calls the MMX routine. `CRC_WORD_MMX()` is the inline assembly macro for consuming one 64-bit word with the word table.

## Control flow, state, and persistence

The function canonicalizes the start CRC, aligns to a 64-bit boundary if the size threshold requires it, then executes GNU inline assembly. The main loop processes 32 bytes per iteration with four 64-bit MMX buffers and four CRC lanes using interleaved tables. It combines lane CRCs, processes full 64-bit tail words, then handles byte tails in assembly. `asm volatile("emms")` clears MMX state before returning.

## Dependencies and integration points

It includes `generic_crc.h` and compiles only when `defined(__GNUC__) && CRCUTIL_USE_ASM && HAVE_I386 && HAVE_MMX`. It uses `GCC_OMIT_FRAME_POINTER` on the function declaration to free registers and optionally emits SSE prefetch instructions if configured.

## Risks and test signals

The code is tightly coupled to GCC i386 register constraints, MMX availability, and frame-pointer omission. The trailing comment incorrectly names `HAVE_AMD64`, but the actual preprocessor guard is i386/MMX. MMX state cleanup is mandatory. Test signals include GCC i386 optimized builds, asm-disabled comparisons, CRC vectors over small and large buffers, unaligned input tests, and post-CRC floating-point/MMX state checks.
