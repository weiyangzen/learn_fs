# sources/distributed-fs/ceph-client/lib/crc/x86/crc-t10dif.h

## Purpose
This x86 arch header accelerates CRC-T10DIF with PCLMULQDQ or VPCLMULQDQ when available.

## Important APIs, Types, and Functions
It defines static key `have_pclmulqdq`, declares generated `crc16_msb` functions via `DECLARE_CRC_PCLMUL_FUNCS`, defines `crc_t10dif_arch()`, and provides `crc_t10dif_mod_init_arch()`.

## Control Flow
`crc_t10dif_arch()` uses `CRC_PCLMUL()` with `crc16_msb_0x8bb7_consts`; fallback is `crc_t10dif_generic()`. Init enables the PCLMUL static key when the CPU has `X86_FEATURE_PCLMULQDQ`, then updates the static call to AVX512 or AVX2 VPCLMUL when available.

## State and Persistence
Runtime state is the static key and static-call target chosen at module init. Per-call state is local.

## Dependencies and Integration Points
It depends on x86 CPU feature detection, the PCLMUL template header, and generic CRC-T10DIF hooks.

## Risks and Test Signals
Risks include CPU feature selection bugs and CRC16 constant layout assumptions. KUnit T10DIF tests and feature-specific x86 boot coverage validate it.
