# sources/distributed-fs/ceph-client/drivers/crypto/atmel-tdes-regs.h

## Purpose

`atmel-tdes-regs.h` defines the register map and bit fields for the Atmel/Microchip TDES/DES/XTEA hardware accelerator. It is a hardware definition header, not an algorithm implementation, and would be consumed by a TDES driver to configure mode, keys, IVs, data registers, interrupts, and PDC transfers.

## Important APIs, Types, And Functions

There are no functions or types. Important macros include `TDES_CR_*` control bits, `TDES_MR_*` fields for encrypt/decrypt, DES/TDES/XTEA selection, two-key versus three-key TDES, source mode, operation mode ECB/CBC/OFB/CFB, CFB size, countermeasure key/type fields, interrupt status bits, key/input/output/IV registers, XTEA round count register, version register, and PDC receive/transmit pointer/count/control/status registers.

## Control Flow

The header defines the values a driver would write when resetting or starting the block, configuring transfer mode, waiting for `TDES_INT_DATARDY` or DMA/PDC completion, loading keys and IVs, moving input/output data, and enabling/disabling PDC RX/TX.

## State And Persistence Behavior

All state is hardware-backed: mode, key, IV, data, interrupt, XTEA round, and PDC registers persist until reset or reprogramming. The header contains no software persistence or runtime allocation.

## Dependencies And Integration Points

The macros are tied to Atmel TDES IP and Linux consumers that include this header. The register layout mirrors patterns used by AES/SHA register headers, especially manual/auto/PDC transfer modes and shared interrupt semantics.

## Risks And Test Signals

Risks include wrong bit masks for TDES key mode, overlapping `TDES_TNPR/TNCR` and `TDES_RNPR/RNCR` aliases, and mode fields that silently corrupt cryptographic output if misprogrammed. Test through any consuming TDES driver with DES/2-key/3-key TDES/XTEA known-answer vectors, interrupt status handling, and PDC transfer tests.
