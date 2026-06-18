# sources/distributed-fs/ceph-client/lib/crc/riscv/crc16_msb.c

## Purpose
This file instantiates the RISC-V carryless-multiply template for a most-significant-bit-first 16-bit CRC, used by CRC-T10DIF.

## Important APIs, Types, and Functions
It sets `typedef u16 crc_t` and `#define LSB_CRC 0`, includes `crc-clmul-template.h`, and defines `u16 crc16_msb_clmul(...)`.

## Control Flow
The wrapper simply returns `crc_clmul(crc, p, len, consts)`. The template handles alignment, full-long folding, partial tails, and reduction.

## State and Persistence
No state persists beyond stack/register temporaries in the checksum call.

## Dependencies and Integration Points
It depends on `crc-clmul.h` and the template. `crc-t10dif.h` calls this function when Zbc is present.

## Risks and Test Signals
Risks are template parameter drift and incorrect polynomial constants supplied by callers. CRC-T10DIF KUnit, known-vector tests, and builds with `CONFIG_CRC_T10DIF` are the main signals.
