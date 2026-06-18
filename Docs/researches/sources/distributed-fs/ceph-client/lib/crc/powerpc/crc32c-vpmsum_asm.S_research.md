# sources/distributed-fs/ceph-client/lib/crc/powerpc/crc32c-vpmsum_asm.S

## Purpose

`sources/distributed-fs/ceph-client/lib/crc/powerpc/crc32c-vpmsum_asm.S` supplies the concrete PowerPC VPMSUM constants and function instantiation for accelerated CRC32C.

## Important APIs, Types, and Functions

The emitted function is `__crc32c_vpmsum`, created by defining `CRC_FUNCTION_NAME __crc32c_vpmsum`, defining `REFLECT`, and including `crc-vpmsum-template.S`. The file provides `.byteswap_constant`, a large `.constants` table for reducing large inputs, `.short_constants` for 1024-2048 bit reductions, and `.barrett_constants` for reflected CRC32C reduction.

## Control Flow

Runtime control flow is in the included template. This file contributes the constants that let the template reduce chunks of CRC32C data using reflected polynomial arithmetic, byte-swap as needed, process large aligned multiples in parallel lanes, handle short inputs, and perform final Barrett reduction.

## State and Persistence Behavior

All data in this file is read-only assembly constant data. There is no mutable state beyond the included function's register-local execution.

## Dependencies and Integration Points

It depends on the VPMSUM template and the PowerPC CRC32 dispatch header. `powerpc/crc32.h` calls `__crc32c_vpmsum()` only after alignment, length, feature, and SIMD-context checks.

## Risks and Edge Cases

The constant table is mathematically tied to the CRC32C reflected polynomial; any value corruption causes silent checksum failures. Because the template is included after data definitions, label names and section layout must remain compatible. The function assumes caller-enforced 16-byte alignment and length multiple.

## Test Signals

Signals include CRC32C known vectors, generic-vs-VPMSUM equivalence over large and short aligned inputs, endian builds with byte-swap behavior, table integrity checks through KUnit, and wrapper tests for unaligned/tail bytes.

## Read Coverage

Source read size: 842 lines, 27724 bytes.
