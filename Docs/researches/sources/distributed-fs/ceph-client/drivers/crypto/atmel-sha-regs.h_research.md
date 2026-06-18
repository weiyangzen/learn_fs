# sources/distributed-fs/ceph-client/drivers/crypto/atmel-sha-regs.h

## Purpose

`atmel-sha-regs.h` defines the MMIO register map and mode/interrupt bits for Atmel/Microchip SHA hardware. It is used by `atmel-sha.c` and by the authenc interface to configure SHA1/SHA224/SHA256/SHA384/SHA512, HMAC, DMA/PDC transfer mode, user-initialized hash values, and digest/input register access.

## Important APIs, Types, And Functions

There are no functions or types. Important macros include `SHA_REG_DIGEST(x)`, `SHA_REG_DIN(x)`, `SHA_CR_*` control bits, `SHA_MR_*` mode, algorithm, HMAC, UIHV, and dual-buffer fields, derived `SHA_FLAGS_*` algorithm/mode combinations, interrupt bits `SHA_INT_DATARDY`, `ENDTX`, `TXBUFE`, and `URAD`, message/byte count registers, version register, and PDC/DMA pointer/count/control/status registers.

## Control Flow

The SHA driver uses these constants to reset or start first blocks, restore intermediate hash state through UIHV/UIEHV, select manual/auto/PDC/IDATAR0 transfer mode, program message sizes for automatic padding/HMAC, wait for data-ready interrupts, and configure PDC transmit registers on older hardware.

## State And Persistence Behavior

All represented state is hardware state: mode, digest/input windows, message size, byte count, DMA pointer/count, interrupt masks, and version. Digest registers may contain intermediate state between streaming updates unless UIHV is available and used to restore contexts explicitly.

## Dependencies And Integration Points

The file relies on `GENMASK()`/bit constants from Linux includes pulled by consumers. It is the shared register ABI for platform devices compatible with `atmel,at91sam9g46-sha` and for AES authenc coordination.

## Risks And Test Signals

Risks include incorrect algorithm encodings, confusion between `SHA_MR_MODE_PDC` and `SHA_MR_MODE_IDATAR0`, UIHV bit misuse, and interrupt mask mismatches. Test through standalone SHA/HMAC selftests, authenc tests, PDC/DMA and CPU paths, UIHV restore on interleaved requests, and hardware-version capability checks.
