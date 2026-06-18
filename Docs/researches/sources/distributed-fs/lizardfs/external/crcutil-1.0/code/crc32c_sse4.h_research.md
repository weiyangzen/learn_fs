# sources/distributed-fs/lizardfs/external/crcutil-1.0/code/crc32c_sse4.h

## Purpose

`crc32c_sse4.h` declares the SSE4.2-oriented CRC32C implementation and its rolling CRC companion. It fixes the generating polynomial to Castagnoli CRC32C, exposes a `GenericCrc`-compatible interface, and abstracts hardware versus software byte/word updates through macros.

## Important APIs, types, and macros

`Crc32cSSE4` exports `typedef size_t Crc`, `Word`, and `TableEntry`. Key methods are `Init(bool canonical)`, compatibility `Init(const Crc&, size_t, bool)`, `FixedGeneratingPolynomial()` returning `0x82f63b78`, `FixedDegree()` returning 32, `Base()`, `CrcDefault()`, and `IsSSE42Available()`. `RollingCrc32cSSE4` provides `Init()`, `Start()`, `Roll()`, `StartValue()`, and `WindowBytes()`.

`CRC_UPDATE_WORD` maps to `_mm_crc32_u32` on i386 or `_mm_crc32_u64` on non-i386 x86 when `CRCUTIL_USE_MM_CRC32` is enabled. Otherwise it falls back to `CRC_WORD` and `CRC_BYTE` from `generic_crc.h`. The block enumeration macros define the tuned block sizes and stripe counts used in table declarations and implementation.

## Control flow, state, and persistence

The header describes per-instance state. `Crc32cSSE4` owns multiplication tables for every enumerated block size and the `GfUtil` base object. The fallback software path also stores `crc_word_` tables and grants friend access to `RollingCrc32cSSE4`. `RollingCrc32cSSE4` stores an outgoing-byte table and a borrowed pointer to the initialized CRC instance; the caller must keep that instance alive.

## Dependencies and integration points

The file depends on `gf_util.h`, `crc32c_sse4_intrin.h`, and conditionally `generic_crc.h`. It is only active under `HAVE_I386 || HAVE_AMD64`. It is designed to be used by higher-level crcutil interfaces, examples, and tests that select the fastest CRC32C backend after runtime CPU detection.

## Risks and test signals

The rolling class has a lifetime dependency on the referenced `Crc32cSSE4`. The compatibility `Init(generating_polynomial, degree, canonical)` silently does nothing if the polynomial or degree do not match the fixed CRC32C parameters, which can leave an object uninitialized if misused. Test signals include compile coverage for both `CRCUTIL_USE_MM_CRC32` paths, runtime dispatch checks, rolling CRC equivalence with recomputing each window, and ABI checks for alignment-sensitive table storage.
