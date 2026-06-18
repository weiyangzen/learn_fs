# sources/distributed-fs/ceph-client/lib/crc/x86/crc32-pclmul.S

## Purpose
This assembly stub instantiates the x86 PCLMUL template for reflected 32-bit CRCs.

## Important APIs, Types, and Functions
It invokes `DEFINE_CRC_PCLMUL_FUNCS(crc32_lsb, 32, 1)`, generating SSE, AVX2, and AVX512 functions.

## Control Flow
All processing flow is inherited from `crc-pclmul-template.S`.

## State and Persistence
No persistent state exists.

## Dependencies and Integration Points
Generated functions are used for CRC32 LE and, on some CPUs, CRC32C through x86 `crc32.h`.

## Risks and Test Signals
Risks are wrong bit-order instantiation and template ABI mismatch. CRC32 LE/CRC32C KUnit with PCLMUL dispatch is the key signal.
