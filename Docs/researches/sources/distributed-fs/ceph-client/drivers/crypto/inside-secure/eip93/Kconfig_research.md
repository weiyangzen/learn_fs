# sources/distributed-fs/ceph-client/drivers/crypto/inside-secure/eip93/Kconfig

## Purpose
This Kconfig entry exposes the EIP93 hardware crypto accelerator driver. It controls whether the EIP93 module is built and pulls in the Crypto API primitives required by its cipher, AEAD, and hash implementations.

## Important APIs, Types, And Functions
The symbol is `CRYPTO_DEV_EIP93`, a tristate prompt described as support for EIP93 crypto hardware accelerators. It depends on `SOC_MT7621 || ARCH_AIROHA || ECONET || COMPILE_TEST`. It selects AES and DES crypto libraries, skcipher, AEAD, authenc, MD5, SHA1, and SHA256 support.

## Control Flow
There is no executable flow. Build-time configuration presents the option only on supported SoCs or compile-test builds. When enabled, `eip93/Makefile` builds the composite EIP93 driver.

## State And Persistence
No runtime state exists. The Kconfig state persists only in the kernel configuration.

## Dependencies And Integration Points
The selected Crypto API dependencies match the algorithms described in the help text: AES ECB/CBC/CTR, DES/3DES ECB/CBC, and AEAD authenc HMAC/cipher combinations. The SoC dependencies tie the driver to MediaTek/Airoha/Econet platforms while allowing broader compile coverage.

## Risks
Over-selecting crypto primitives can enlarge builds, while under-selecting would break link or runtime registration. The help text says "EIP93 have" and "this provide", but that is documentation quality rather than behavior.

## Test Signals
Kconfig tests should verify visibility under supported SoCs and `COMPILE_TEST`, dependency selection, built-in and module configurations, and allnoconfig/allmodconfig coverage.
