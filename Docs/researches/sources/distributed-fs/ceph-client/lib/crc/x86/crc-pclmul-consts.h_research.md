# sources/distributed-fs/ceph-client/lib/crc/x86/crc-pclmul-consts.h

## Purpose
This generated header defines the x86 [V]PCLMULQDQ constant tables used to fold and reduce CRC16/T10DIF, CRC32, CRC32C, CRC64 BE, and CRC64 NVMe.

## Important APIs, Types, and Functions
It defines static cacheline-aligned constant structs for `crc16_msb_0x8bb7_consts`, `crc32_lsb_0xedb88320_consts`, `crc32_lsb_0x82f63b78_consts`, `crc64_msb_0x42f0e1eba9ea3693_consts`, and `crc64_lsb_0x9a6c9329ac4bc9b5_consts`. Fields include optional `bswap_mask`, fold constants for 2048/1024/512/256/128-bit distances, a shuffle table for short tails, and Barrett reduction constants.

## Control Flow
There is no code flow. Runtime x86 CRC hooks pass pointers to the `fold_across_128_bits_consts` field; the assembly template relies on fixed negative and positive offsets from that field to access neighboring constants.

## State and Persistence
The constants are immutable static data. No mutable state exists.

## Dependencies and Integration Points
It depends on the exact layout expected by `crc-pclmul-template.S` and on generated polynomial constants from `scripts/gen-crc-consts.py`. It is included by `crc-pclmul-template.h`.

## Risks and Test Signals
Risks include struct layout drift, generator mistakes, and mismatch between constant order and assembly offset assumptions. Test signals are x86 CRC KUnit across SSE, AVX2, and AVX512 dispatch paths plus build tests with all accelerated CRC variants.
