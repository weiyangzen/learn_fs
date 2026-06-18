# sources/distributed-fs/ceph-client/lib/crc/x86/crc64.h

## Purpose
This x86 arch header accelerates CRC64 BE and CRC64 NVMe with PCLMULQDQ/VPCLMULQDQ.

## Important APIs, Types, and Functions
It defines static key `have_pclmulqdq`, declares `crc64_msb` and `crc64_lsb` generated functions, provides `crc64_be_arch()`, `crc64_nvme_arch()`, and `crc64_mod_init_arch()`.

## Control Flow
Each arch hook invokes `CRC_PCLMUL()` with the corresponding 64-bit constants and falls back to generic CRC64. Init enables the PCLMUL static key and updates both static-call targets to AVX512 or AVX2 variants when VPCLMUL is supported.

## State and Persistence
Runtime dispatch persists in static key/static-call state. Per-call checksum state is local.

## Dependencies and Integration Points
It depends on the x86 PCLMUL template and generic CRC64 library. It integrates both reflected and non-reflected CRC64 variants.

## Risks and Test Signals
Risks include wrong reflected/non-reflected function pairing, FPU context issues, and AVX512 selection on CPUs with poor wide-vector behavior. CRC64 KUnit and feature-specific boot tests are key.
