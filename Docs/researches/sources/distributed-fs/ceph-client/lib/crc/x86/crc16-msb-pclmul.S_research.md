# sources/distributed-fs/ceph-client/lib/crc/x86/crc16-msb-pclmul.S

## Purpose
This assembly stub instantiates the x86 PCLMUL template for MSB-first 16-bit CRCs.

## Important APIs, Types, and Functions
It includes `crc-pclmul-template.S` and invokes `DEFINE_CRC_PCLMUL_FUNCS(crc16_msb, 16, 0)`.

## Control Flow
Generated SSE, AVX2, and AVX512 functions are produced by the template; this file contributes no separate logic.

## State and Persistence
No persistent state exists.

## Dependencies and Integration Points
It provides the generated functions declared by `crc-t10dif.h`.

## Risks and Test Signals
Risks are limited to instantiation arguments and template compatibility. CRC-T10DIF KUnit and link tests are the main signals.
