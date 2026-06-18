# sources/distributed-fs/lizardfs/external/crcutil-1.0/code/multiword_64_64_gcc_amd64_asm.cc

## Purpose

This file implements the GCC amd64 assembly specialization for 64-bit CRCs using 64-bit table lookups and four-way interleaving. It is selected for `GenericCrc<uint64, uint64, uint64, 4>` when GCC, amd64, and `CRCUTIL_USE_ASM` are available.

## Important APIs and functions

It specializes `CrcMultiword()` and declares/defines `CrcMultiwordGccAmd64()`. The public specialization uses an unrolled C++ fast path for inputs up to `6 * sizeof(Word) - 1`, then delegates to the assembly implementation for larger inputs. The `CRC_WORD_ASM()` macro updates a 64-bit CRC from one 64-bit buffer using `crc_word_`, while the main loop uses `crc_word_interleaved_`.

## Control flow, state, and persistence

Persistent state remains in the parent `GenericCrc` tables. Runtime flow aligns input, initializes four CRC lanes, loads four 64-bit buffers, iterates over 32-byte chunks, computes table lookups byte by byte with optimized register usage, combines lanes with four `CRC_WORD_ASM()` calls, then processes remaining words and bytes. The result is de-canonicalized before return.

## Dependencies and integration points

It includes `generic_crc.h` and is gated by `defined(__GNUC__) && CRCUTIL_USE_ASM && HAVE_AMD64`. It relies on GNU extended inline assembly, x86-64 register names, and table layout from `GenericCrc`.

## Risks and test signals

The assembly clobbers fixed registers including `%rbx`, which is callee-saved under the SysV ABI; correctness depends on GCC saving/restoring around the inline asm according to constraints. Comments indicate performance tradeoffs and compiler sensitivity. Test signals include ABI-sensitive tests under optimized builds, comparison against `CRCUTIL_USE_ASM=0`, unaligned buffers, tail sizes around the C++ fast-path threshold, and sanitizer or valgrind runs to catch out-of-bounds tail handling.
