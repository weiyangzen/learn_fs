# sources/distributed-fs/ceph-client/drivers/crypto/atmel-aes-regs.h

## Purpose

`atmel-aes-regs.h` defines the MMIO register map and bit fields for the Atmel/Microchip AES hardware accelerator. It is consumed by `atmel-aes.c` to configure cipher direction, key size, block mode, DMA/manual transfer mode, GCM, XTS, padding, interrupt status, IV/key/data/tag registers, and hardware-version discovery.

## Important APIs, Types, And Functions

There are no functions or types. Important macros include `AES_CR_*` control bits, `AES_MR_*` mode fields for encryption/decryption, source mode, key size, ECB/CBC/OFB/CFB/CTR/GCM/XTS modes, CFB size, and countermeasure key/type fields; `AES_INT_*` interrupt bits; indexed accessors `AES_KEYWR(x)`, `AES_IDATAR(x)`, `AES_ODATAR(x)`, `AES_IVR(x)`, `AES_GHASHR(x)`, `AES_TAGR(x)`, `AES_GCMHR(x)`, `AES_TWR(x)`, and `AES_ALPHAR(x)`; and extended-mode padding/PLIP macros.

## Control Flow

The header drives control flow indirectly: the driver writes `AES_MR` before IV/key registers, uses `AES_IER`/`AES_IDR`/`AES_ISR` to wait for data and tag readiness, writes `AES_CR_START` or `AES_CR_SWRST` for operation control, and reads `AES_HW_VERSION` to select algorithm capabilities.

## State And Persistence Behavior

All state represented here is hardware state. Key, IV, input, output, GHASH, tag, tweak, and alpha registers are overwritten per request. Interrupt mask/status and mode registers persist until the driver disables or reprograms them.

## Dependencies And Integration Points

The macros rely on Linux `BIT()` for extended mode fields and match the AES IP register ABI used by platform devices compatible with `atmel,at91sam9g46-aes`. `atmel-aes.c` combines these values with crypto API mode flags.

## Risks And Test Signals

Risks are wrong offsets or bit masks causing silent cryptographic corruption, especially for GCM tag generation, XTS tweak registers, and PLIP/authenc mode. Test through AES ECB/CBC/CTR/GCM/XTS/authenc selftests, interrupt-status checks, and comparing capability decisions against `AES_HW_VERSION` values on real SoCs.
