# sources/distributed-fs/ceph-client/lib/crc/riscv/crc-t10dif.h

## Purpose
This arch header wires the generic CRC-T10DIF library to the RISC-V Zbc implementation when the CPU likely supports scalar carryless multiplication.

## Important APIs, Types, and Functions
The single public hook is `static inline u16 crc_t10dif_arch(u16 crc, const u8 *p, size_t len)`. It calls `crc16_msb_clmul()` with `crc16_msb_0x8bb7_consts` or falls back to `crc_t10dif_generic()`.

## Control Flow
At each call, `riscv_has_extension_likely(RISCV_ISA_EXT_ZBC)` gates the accelerated path. If false, execution immediately delegates to the generic CRC-T10DIF code.

## State and Persistence
No per-call state persists. CPU feature state is maintained by the RISC-V hwcap/alternative framework outside this header.

## Dependencies and Integration Points
It includes `asm/hwcap.h`, `asm/alternative-macros.h`, and `crc-clmul.h`. It is pulled into the generic CRC-T10DIF library as its RISC-V arch override.

## Risks and Test Signals
Risks are feature-detection false positives, missing Zbc assembler support, and divergence from generic T10DIF on unaligned buffers. Test signals include booting on RISC-V with and without Zbc and KUnit CRC-T10DIF comparisons.
