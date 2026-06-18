# sources/distributed-fs/ceph-client/lib/crc/x86/crc64-pclmul.S

## Purpose
This assembly stub instantiates x86 PCLMUL CRC functions for both MSB-first and LSB-first 64-bit CRCs.

## Important APIs, Types, and Functions
It invokes `DEFINE_CRC_PCLMUL_FUNCS(crc64_msb, 64, 0)` and `DEFINE_CRC_PCLMUL_FUNCS(crc64_lsb, 64, 1)`.

## Control Flow
The shared template emits the SSE, AVX2, and AVX512 bodies for each prefix.

## State and Persistence
No state is introduced.

## Dependencies and Integration Points
Generated functions are declared and dispatched by x86 `crc64.h`.

## Risks and Test Signals
Risks are instantiation correctness and x86_64 ABI handling for 64-bit CRC return values. CRC64 BE and NVMe KUnit tests under PCLMUL dispatch validate it.
