# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/atom-bits.h

Purpose: This header provides small helpers and macros for reading little-endian byte, word, and dword values from an ATOM BIOS image.

Important APIs, types, and functions: Inline functions `get_u8()`, `get_u16()`, and `get_u32()` read from a BIOS byte pointer. Macros `U8/U16/U32` access `ctx->ctx->bios`, `CU8/CU16/CU32` access `ctx->bios`, and `CSTR()` returns a char pointer into `ctx->bios`.

Control flow: Reads are simple byte-indexed loads composed into little-endian integers. There is no bounds checking; callers provide valid BIOS offsets and context shape.

State and persistence: No owned state. The functions read immutable or caller-managed BIOS memory.

Dependencies and integration points: Used by Radeon ATOM interpreter/parser code. The macros assume specific local variable names and nested context structure, making this a parser-internal header rather than a generic utility.

Risks: Lack of bounds checking means malformed BIOS offsets can read outside the mapped image unless callers validate table sizes. The macros depend on implicit `ctx` names and structure layout. Endianness is hard-coded little-endian by byte composition, which is correct for ATOM BIOS but must not be replaced with native casts.

Test signals: ATOM BIOS parser tests on valid and malformed images; fuzz table offsets; build on big-endian and little-endian architectures; static analysis for unchecked offsets before macro use.
